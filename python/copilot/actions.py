from __future__ import annotations
from dataclasses import dataclass
from .context import Situation
from .intents import Intent

@dataclass
class ActionResult:
    ok:bool; message_en:str; message_id:str

class ActionExecutor:
    def __init__(self,bridge,profile:dict): self.bridge=bridge; self.profile=profile
    def _cmd(self,key):
        spec=self.profile["actions"].get(key)
        if not spec: raise KeyError(key)
        cmds=spec.get("commands",[])
        if isinstance(cmds,str): cmds=[cmds]
        for c in cmds: self.bridge.command(c)
    def _set(self,key,val):
        spec=self.profile["actions"].get(key)
        if not spec: raise KeyError(key)
        lo,hi=spec.get("range",[-1e9,1e9]); val=max(lo,min(hi,float(val)))
        self.bridge.set_dataref(spec["dataref"],val,spec.get("type","float"))
    def execute(self,intent:Intent,s:Situation)->ActionResult:
        n=intent.name
        try:
            if n=="status":
                en=f"Phase {s.phase.value}, ground speed {s.groundspeed:.0f} knots, radio altitude {s.radio_alt:.0f} feet."
                idn=f"Fase {s.phase.value}, ground speed {s.groundspeed:.0f} knot, radio altitude {s.radio_alt:.0f} kaki."
                return ActionResult(True,en,idn)
            if n=="gear_up" and (s.on_ground or s.radio_alt<50):
                return ActionResult(False,"Gear up inhibited: aircraft is on or too near the ground.","Gear up diblokir: pesawat masih di darat atau terlalu dekat dengan darat.")
            if n=="autopilot_on" and (s.on_ground or s.radio_alt<400):
                return ActionResult(False,"Autopilot engagement inhibited below 400 feet AGL.","Autopilot diblokir di bawah 400 kaki AGL.")
            setters={"set_heading":"heading","set_altitude":"altitude","set_speed":"speed","set_vspeed":"vspeed"}
            if n in setters:
                self._set(setters[n],intent.value)
                return ActionResult(True,f"{setters[n].title()} set to {intent.value:g}.",f"{setters[n].title()} disetel ke {intent.value:g}.")
            if n=="checklist":
                return ActionResult(True,"Checklist mode is available; say a named checklist in the next milestone.","Mode checklist tersedia; checklist bernama ditambahkan pada milestone berikutnya.")
            if n=="unknown": return ActionResult(False,"Command not recognized.","Perintah tidak dikenali.")
            self._cmd(n)
            return ActionResult(True,f"Executed {n.replace('_',' ')}.",f"Menjalankan {n.replace('_',' ')}.")
        except KeyError:
            return ActionResult(False,f"Action {n} is not mapped for this aircraft profile.",f"Aksi {n} belum dipetakan untuk profil pesawat ini.")
