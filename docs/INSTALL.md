# Installation and first run

## Prerequisites

- X-Plane 11.50+ or X-Plane 12.
- Current X-Plane Plugin SDK for building the C++ bridge.
- CMake and a 64-bit C++ compiler supported by your platform.
- Python 3.10+ recommended for the external copilot service.
- Optional voice: Vosk models for Indonesian and/or English, plus `vosk`, `sounddevice`, and `pyttsx3`.
- Optional UI: .NET 8 SDK.

## Build the native bridge

Windows PowerShell:

```powershell
./scripts/build_bridge.ps1 -Sdk "C:\SDK\XPSDK430"
```

Linux/macOS:

```bash
./scripts/build_bridge.sh /path/to/XPSDK430
```

Copy the resulting `AICopilotBridge.xpl` into the XPLM 3.x platform folder: `Resources/plugins/AICopilotBridge/win_x64/`, `mac_x64/`, or `lin_x64/`. The helper `scripts/install.py` selects the correct platform folder and performs the copy.

## Run Python core

From the `python` directory:

```bash
python -m venv .venv
# activate it, then only if voice is required:
pip install -r requirements.txt
python -m copilot --config ../config/copilot.json
```

Voice is disabled by default so the core MVP can run without native audio dependencies. To enable it, edit `config/copilot.json`, set `voice.enabled` to true, and provide paths to downloaded Vosk Indonesian/English model directories.

## Test without voice

With X-Plane and the bridge running:

```bash
curl http://127.0.0.1:8765/status
curl -X POST http://127.0.0.1:8765/command -H "Content-Type: application/json" -d '{"text":"set heading 270"}'
```

Or run the C# console:

```bash
dotnet run --project ui_csharp/CopilotConsole
```

## Aircraft mapping validation

Before enabling broad cockpit automation, validate each command/dataref against your installed Zibo or LevelUp release using DataRefTool/DataRefEditor. In particular, custom `laminar/B738/...` interfaces can change or differ between aircraft builds. Update only `config/aircraft_profiles.json`; the copilot code does not need recompilation.
