from copilot.intents import parse_intent

def test_indonesian_lights(): assert parse_intent("nyalakan lampu pendaratan").name=="landing_lights_on"
def test_heading():
    i=parse_intent("set heading 275"); assert i.name=="set_heading" and i.value==275

def test_gear_id(): assert parse_intent("turunkan roda").name=="gear_down"
