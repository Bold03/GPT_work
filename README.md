# X-Plane AI Copilot MVP — Zibo / LevelUp 737

A production-oriented **MVP scaffold** for an external bilingual copilot with a native X-Plane bridge. It is deliberately split so X-Plane's plugin callback does only simulator I/O while Python handles context, intent logic, STT/TTS, and APIs.

## Included

- **C++17 XPLM bridge**: local UDP telemetry/action bridge, 10 Hz subscriptions, command execution, writable-dataref access, no worker-thread XPLM calls.
- **Python copilot core**: flight-phase inference, bilingual Indonesian/English command parsing, action guards, aircraft profiles, optional Vosk STT and pyttsx3 TTS, localhost HTTP API.
- **Zibo + LevelUp profiles**: baseline mappings stored in JSON so addon-version differences can be fixed without rebuilding.
- **C#/.NET 8 console UI**: status viewer and text-command client.
- **Tests, build scripts, installer helper, architecture/install/roadmap documentation**.

## Current semantic commands

Examples: `battery on`, `landing lights on`, `nyalakan lampu pendaratan`, `set heading 270`, `set altitude 10000`, `set speed 220`, `set vertical speed -1200`, `LNAV on`, `VNAV on`, `approach mode`, `gear up/down`, `status`.

## Important scope boundary

This repository is an **MVP, not a claimed final certified mapping for every Zibo/LevelUp release**. Custom addon datarefs/commands must be validated against the exact aircraft build. The architecture makes this a configuration task rather than a code rewrite.

See `docs/INSTALL.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.
