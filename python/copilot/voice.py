from __future__ import annotations
import json, queue, threading

class Speaker:
    def __init__(self,enabled=True):
        self.enabled=enabled; self.engine=None
        if enabled:
            try:
                import pyttsx3; self.engine=pyttsx3.init()
            except Exception: self.engine=None
    def say(self,text:str,lang="en"):
        if not self.engine: return
        voices=self.engine.getProperty("voices") or []
        for v in voices:
            meta=(str(getattr(v,"name","")).lower()+str(getattr(v,"languages","")).lower())
            if (lang=="id" and ("indones" in meta or "id_" in meta)) or (lang=="en" and "english" in meta):
                self.engine.setProperty("voice",v.id); break
        self.engine.say(text); self.engine.runAndWait()

class VoskListener:
    def __init__(self,models:dict[str,str],callback,require_wake_word=True):
        self.models=models; self.callback=callback; self.require_wake=require_wake_word
        self.q=queue.Queue(); self.running=False; self.thread=None
    def start(self):
        try: import sounddevice, vosk
        except Exception as e: raise RuntimeError("Install vosk and sounddevice for voice input") from e
        self.running=True; self.thread=threading.Thread(target=self._run,daemon=True); self.thread.start()
    def stop(self): self.running=False
    def _run(self):
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer
        recs={lang:KaldiRecognizer(Model(path),16000) for lang,path in self.models.items() if path}
        for r in recs.values(): r.SetWords(True)
        def cb(indata,frames,time,status): self.q.put(bytes(indata))
        with sd.RawInputStream(samplerate=16000,blocksize=4000,dtype="int16",channels=1,callback=cb):
            while self.running:
                data=self.q.get()
                candidates=[]
                for lang,r in recs.items():
                    if r.AcceptWaveform(data):
                        obj=json.loads(r.Result()); text=obj.get("text","").strip()
                        words=obj.get("result",[]); conf=sum(w.get("conf",0) for w in words)/max(1,len(words))
                        if text: candidates.append((conf,lang,text))
                if not candidates: continue
                _,lang,text=max(candidates)
                if self.require_wake:
                    lowered=text.lower(); wakes=("copilot","co pilot","kopilot")
                    if not any(w in lowered for w in wakes): continue
                    for w in wakes: lowered=lowered.replace(w,"")
                    text=lowered.strip()
                if text: self.callback(text,lang)
