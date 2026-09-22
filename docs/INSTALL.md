# Installation and first run

## Prerequisites

- X-Plane 11.50+ or X-Plane 12.
- Python 3.10+ recommended for the external copilot service.
- Optional voice: Vosk models for Indonesian and/or English, plus `vosk`, `sounddevice`, and `pyttsx3`.
- Optional UI: .NET 8 runtime/SDK.
- CMake, a 64-bit C++ compiler, and the X-Plane Plugin SDK are only required when compiling the bridge locally.

## Recommended: download the Windows bridge from GitHub Actions

Every push to `main` runs the `CI` workflow. The `cpp-windows-build` job downloads the official X-Plane SDK, builds the 64-bit Windows bridge, and uploads an artifact named:

`AICopilotBridge-Windows-x64`

In GitHub, open **Actions → latest successful CI run → Artifacts**, then download that artifact. Its layout is ready for installation:

```text
AICopilotBridge/
├── win_x64/
│   └── AICopilotBridge.xpl
└── config/
```

Copy the `AICopilotBridge` folder into:

```text
X-Plane 12/Resources/plugins/
```

The final plugin path should therefore be:

```text
X-Plane 12/Resources/plugins/AICopilotBridge/win_x64/AICopilotBridge.xpl
```

## Build the native bridge locally

Download/extract the current X-Plane Plugin SDK first.

Windows PowerShell:

```powershell
./scripts/build_bridge.ps1 -Sdk "C:\SDK\XPSDK430\SDK"
```

Linux/macOS:

```bash
./scripts/build_bridge.sh /path/to/XPSDK430/SDK
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
