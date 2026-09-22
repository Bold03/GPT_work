from __future__ import annotations
import json
from pathlib import Path

def load_profiles(path:Path): return json.loads(path.read_text(encoding="utf-8"))

def choose_profile(profiles:dict, telemetry:dict, requested="auto"):
    if requested!="auto": return requested
    desc=str(telemetry.get("acf_desc") or "").lower()
    if "zibo" in desc or "b737-800x" in desc: return "zibo"
    if "levelup" in desc or "737ng" in desc or "737-600ng" in desc or "737-700ng" in desc or "737-900" in desc: return "levelup"
    return profiles.get("default","zibo")
