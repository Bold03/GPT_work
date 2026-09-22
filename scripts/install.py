from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description="Install AI Copilot bridge into X-Plane")
    ap.add_argument("xplane",type=Path); ap.add_argument("--plugin",type=Path,required=True,help="Built .xpl file")
    args=ap.parse_args(); xp=args.xplane.resolve(); plugin=args.plugin.resolve()
    if not (xp/"Resources"/"plugins").exists(): sys.exit("Invalid X-Plane directory")
    platform_dir={"win32":"win_x64","darwin":"mac_x64"}.get(sys.platform,"lin_x64")
    dest=xp/"Resources"/"plugins"/"AICopilotBridge"/platform_dir
    dest.mkdir(parents=True,exist_ok=True); target=dest/"AICopilotBridge.xpl"; shutil.copy2(plugin,target)
    print(f"Installed bridge: {target}")
    print("Run Python service separately: python -m copilot --config <project>/config/copilot.json")
if __name__=="__main__": main()
