# Roadmap from MVP to full copilot

## Milestone 1 — bridge + semantic controls (included)
- 10 Hz situational telemetry
- bilingual text intents
- MCP heading/altitude/speed/V/S control
- selected lights, AP modes, landing gear
- local HTTP status/command API
- basic action guards

## Milestone 2 — production voice
- benchmark Vosk Indonesian and English models with cockpit noise
- push-to-talk and wake-word modes
- confidence threshold / rejection handling
- selectable TTS voices and audio ducking
- latency instrumentation from end-of-utterance to command execution

## Milestone 3 — checklist engine
- JSON checklist definitions per phase
- challenge/response state machine
- automatic item verification from datarefs
- callouts (80 knots, V1, rotate, positive rate, 1000 stable, minimums)

## Milestone 4 — adaptive copilot
- aircraft-system observation graph
- anomaly detection (configuration disagreement, missed phase actions)
- policy layer for proactive suggestions vs. automatic execution
- user preferences and SOP packs

## Milestone 5 — ATC/FMS integration
- optional read-only CDU/FMS awareness first
- SimBrief import adapter
- ATC transcript adapter (do not automatically transmit without an explicit user action)
- runway/SID/STAR briefing generation

## Release criteria
- soak test of at least several complete sectors per supported aircraft/version
- zero simulator crashes attributable to bridge
- command audit log and replayable test corpus
- measured p50/p95 voice-command latency
- per-language word/intent accuracy test set
