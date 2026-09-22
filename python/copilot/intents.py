from __future__ import annotations
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Intent:
    name:str
    value:object=None
    language:str="en"

NUM=r"(-?\d+(?:\.\d+)?)"

def parse_intent(text:str)->Intent:
    raw=text.strip().lower(); lang="id" if any(w in raw for w in ["nyalakan","matikan","setel","lampu","roda","turunkan","naikkan","ketinggian","kecepatan"]) else "en"
    s=(raw.replace("nyalakan","on").replace("matikan","off").replace("lampu pendaratan","landing lights")
       .replace("lampu taxi","taxi lights").replace("sabuk pengaman","seat belts").replace("autopilot hidup","autopilot on")
       .replace("autopilot mati","autopilot off").replace("roda naik","gear up").replace("roda turun","gear down")
       .replace("turunkan roda","gear down").replace("naikkan roda","gear up").replace("setel","set"))
    fixed={
      "battery on":"battery_on","on battery":"battery_on","battery off":"battery_off","off battery":"battery_off","beacon on":"beacon_on","on beacon":"beacon_on","beacon off":"beacon_off","off beacon":"beacon_off",
      "landing lights on":"landing_lights_on","on landing lights":"landing_lights_on","landing lights off":"landing_lights_off","off landing lights":"landing_lights_off","taxi lights on":"taxi_lights_on","on taxi lights":"taxi_lights_on","taxi lights off":"taxi_lights_off","off taxi lights":"taxi_lights_off",
      "seat belts on":"seat_belts_on","seat belts off":"seat_belts_off","autopilot on":"autopilot_on","autopilot off":"autopilot_off",
      "lnav on":"lnav_on","vnav on":"vnav_on","approach mode":"approach_on","gear up":"gear_up","gear down":"gear_down",
    }
    for phrase,name in fixed.items():
        if phrase in s: return Intent(name,language=lang)
    patterns=[
      (rf"(?:set )?(?:heading|hdg)\s*{NUM}","set_heading"),
      (rf"(?:set )?(?:altitude|ketinggian)\s*{NUM}","set_altitude"),
      (rf"(?:set )?(?:speed|airspeed|kecepatan)\s*{NUM}","set_speed"),
      (rf"(?:set )?(?:vertical speed|v/?s)\s*{NUM}","set_vspeed"),
    ]
    for pat,name in patterns:
        m=re.search(pat,s)
        if m: return Intent(name,float(m.group(1)),lang)
    if "status" in s or "situasi" in s: return Intent("status",language=lang)
    if "checklist" in s: return Intent("checklist",language=lang)
    return Intent("unknown",raw,lang)
