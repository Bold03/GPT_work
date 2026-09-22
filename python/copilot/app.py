from __future__ import annotations
import argparse, json, signal, time
from pathlib import Path
from .bridge import XPlaneBridge, Subscription
from .context import ContextEngine
from .intents import parse_intent
from .profiles import load_profiles, choose_profile
from .actions import ActionExecutor
from .voice import Speaker, VoskListener
from .http_api import StatusServer

class CopilotApp:
    def __init__(self,config_path:Path):
        self.cfg=json.loads(config_path.read_text(encoding="utf-8")); root=config_path.parent
        self.profiles=load_profiles((root/self.cfg["profiles_file"]).resolve())
        self.bridge=XPlaneBridge(listen_port=self.cfg.get("python_udp_port",49051)); self.ctx=ContextEngine()
        self.situation=self.ctx.update({}); self.profile_name=None; self.profile=None; self.executor=None
        self.speaker=Speaker(self.cfg.get("tts",{}).get("enabled",True)); self.voice=None
        self.http=StatusServer(self,port=self.cfg.get("http_port",8765))
    def start(self):
        self.bridge.start(); self.bridge.clear_subscriptions()
        for alias,spec in self.profiles["common_telemetry"].items():
            self.bridge.subscribe(Subscription(alias,spec["dataref"],spec.get("type","float"),spec.get("index",-1)))
        self.bridge.listeners.append(self._on_tlm); self.http.start(); time.sleep(.3); self._select_profile()
        vcfg=self.cfg.get("voice",{})
        if vcfg.get("enabled"):
            models={k:v for k,v in vcfg.get("vosk_models",{}).items() if v}
            if models:
                self.voice=VoskListener(models,self._voice_command,vcfg.get("require_wake_word",True)); self.voice.start()
    def stop(self):
        if self.voice: self.voice.stop()
        self.http.stop(); self.bridge.close()
    def _select_profile(self):
        name=choose_profile(self.profiles,self.bridge.telemetry,self.cfg.get("aircraft_profile","auto"))
        if name==self.profile_name: return
        self.profile_name=name; self.profile=self.profiles["profiles"][name]; self.executor=ActionExecutor(self.bridge,self.profile)
        for alias,spec in self.profile.get("telemetry",{}).items(): self.bridge.subscribe(Subscription(alias,spec["dataref"],spec.get("type","float"),spec.get("index",-1)))
    def _on_tlm(self,t): self._select_profile(); self.situation=self.ctx.update(t)
    def _voice_command(self,text,lang): self.handle_text(text,lang,speak=True)
    def handle_text(self,text,language=None,speak=False):
        intent=parse_intent(text)
        if language: intent=intent.__class__(intent.name,intent.value,language)
        result=self.executor.execute(intent,self.situation) if self.executor else None
        if not result: return {"ok":False,"message":"No aircraft profile active"}
        msg=result.message_id if intent.language=="id" else result.message_en
        if speak: self.speaker.say(msg,intent.language)
        return {"ok":result.ok,"message":msg,"intent":intent.name,"phase":self.situation.phase.value,"profile":self.profile_name}
    def status(self):
        s=self.situation
        return {"bridge_connected":self.bridge.connected,"profile":self.profile_name,"phase":s.phase.value,"on_ground":s.on_ground,
                "groundspeed":s.groundspeed,"ias":s.ias,"radio_alt":s.radio_alt,"altitude":s.altitude,"vvi":s.vvi,"telemetry":self.bridge.telemetry}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",default=str(Path(__file__).resolve().parents[2]/"config"/"copilot.json")); args=ap.parse_args()
    app=CopilotApp(Path(args.config)); app.start(); print("AI Copilot running. HTTP: http://127.0.0.1:8765/status")
    stop=False
    def sig(*_): nonlocal stop; stop=True
    signal.signal(signal.SIGINT,sig); signal.signal(signal.SIGTERM,sig)
    try:
        while not stop: time.sleep(.5)
    finally: app.stop()
if __name__=="__main__": main()
