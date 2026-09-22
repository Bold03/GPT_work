from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class FlightPhase(str, Enum):
    COLD_DARK="cold_dark"; PREFLIGHT="preflight"; ENGINE_START="engine_start"
    TAXI_OUT="taxi_out"; TAKEOFF="takeoff"; CLIMB="climb"; CRUISE="cruise"
    DESCENT="descent"; APPROACH="approach"; LANDING_ROLL="landing_roll"
    TAXI_IN="taxi_in"; PARKED="parked"

@dataclass
class Situation:
    phase: FlightPhase
    on_ground: bool
    groundspeed: float
    ias: float
    radio_alt: float
    altitude: float
    vvi: float
    n1_max: float
    parking_brake: bool

class ContextEngine:
    def __init__(self): self.phase=FlightPhase.COLD_DARK; self.was_airborne=False
    @staticmethod
    def f(t,k,default=0.0):
        v=t.get(k); return default if v is None else float(v)
    def update(self,t:dict[str,object])->Situation:
        on_ground=self.f(t,"on_ground",1)>0.5
        gs=(self.f(t,"gs_mps")*1.943844 if t.get("gs_mps") is not None else self.f(t,"gs")); ias=self.f(t,"ias"); ra=max(0,self.f(t,"radio_alt"))
        alt=self.f(t,"altitude"); vvi=self.f(t,"vvi")
        n1=max(self.f(t,"n1_1"),self.f(t,"n1_2")); pb=self.f(t,"park_brake")>0.5
        if not on_ground: self.was_airborne=True
        if on_ground:
            if self.was_airborne and gs>30: p=FlightPhase.LANDING_ROLL
            elif self.was_airborne and gs>3: p=FlightPhase.TAXI_IN
            elif self.was_airborne and pb and gs<1: p=FlightPhase.PARKED
            elif n1>35 and ias>40: p=FlightPhase.TAKEOFF
            elif gs>3: p=FlightPhase.TAXI_OUT
            elif n1>20: p=FlightPhase.ENGINE_START
            elif pb: p=FlightPhase.PREFLIGHT
            else: p=FlightPhase.COLD_DARK
        else:
            if ra<2500 and vvi<200: p=FlightPhase.APPROACH
            elif vvi>300: p=FlightPhase.CLIMB
            elif vvi<-300: p=FlightPhase.DESCENT
            else: p=FlightPhase.CRUISE
        self.phase=p
        return Situation(p,on_ground,gs,ias,ra,alt,vvi,n1,pb)
