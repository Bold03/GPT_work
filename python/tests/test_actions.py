from copilot.actions import ActionExecutor
from copilot.context import Situation, FlightPhase
from copilot.intents import Intent

class B:
    def __init__(self): self.calls=[]
    def command(self,n,phase="once"): self.calls.append(("cmd",n,phase))
    def set_dataref(self,n,v,t="float"): self.calls.append(("set",n,v,t))

P={"actions":{"gear_up":{"commands":"gear/up"},"heading":{"dataref":"hdg","range":[0,359],"type":"float"}}}
def sit(on=True,ra=0): return Situation(FlightPhase.PREFLIGHT,on,0,0,ra,0,0,0,True)

def test_gear_guard():
    r=ActionExecutor(B(),P).execute(Intent("gear_up"),sit(True,0)); assert not r.ok

def test_heading_write():
    b=B(); r=ActionExecutor(b,P).execute(Intent("set_heading",400),sit()); assert r.ok and b.calls[-1][2]==359
