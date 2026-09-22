from copilot.context import ContextEngine, FlightPhase

def test_preflight():
    c=ContextEngine(); s=c.update({"on_ground":1,"park_brake":1,"gs_mps":0,"n1_1":0,"n1_2":0})
    assert s.phase==FlightPhase.PREFLIGHT

def test_takeoff():
    c=ContextEngine(); s=c.update({"on_ground":1,"park_brake":0,"gs_mps":35,"ias":80,"n1_1":92,"n1_2":92})
    assert s.phase==FlightPhase.TAKEOFF

def test_climb():
    c=ContextEngine(); s=c.update({"on_ground":0,"radio_alt":5000,"vvi":1500,"n1_1":85,"n1_2":85})
    assert s.phase==FlightPhase.CLIMB
