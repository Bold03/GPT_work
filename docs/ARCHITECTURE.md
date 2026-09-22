# Architecture

## 1. X-Plane bridge (C++17)

The native plugin owns all XPLM access. It resolves datarefs once, caches handles, retries missing custom datarefs periodically, publishes telemetry at 10 Hz, executes commands, and writes only explicitly requested writable datarefs. Network access is loopback-only.

## 2. Copilot core (Python)

The Python process contains four layers:

1. **Aircraft profile** — maps semantic actions to Zibo/LevelUp datarefs and commands.
2. **Context engine** — derives flight phase from ground state, speed, radio altitude, vertical speed, engine N1, and parking brake.
3. **Intent/action layer** — bilingual rule parser plus deterministic execution and guards.
4. **Voice/UI adapters** — optional Vosk STT, pyttsx3 TTS, and localhost HTTP API.

This separation prevents slow STT/TTS/AI work from running in X-Plane's plugin callback.

## 3. C# client

The .NET console is intentionally thin. It talks to Python's localhost HTTP API and can later be replaced by WinUI/WPF/Avalonia without changing simulator integration.

## Safety/stability model

- No background thread calls XPLM.
- No arbitrary remote network control; both bridge and HTTP API bind to localhost.
- Semantic action allow-list: voice text cannot execute arbitrary command/dataref paths.
- Guard examples: gear-up is blocked on/near ground; AP engagement is blocked below 400 ft AGL.
- Custom aircraft mappings live in JSON and are version-adjustable.
