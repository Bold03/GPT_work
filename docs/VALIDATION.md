# Validation status

## Verified in the generation environment

- Python source compiles with Python 3.13.
- Configuration JSON parses successfully.
- Unit tests: 8 passed.
- Local HTTP service starts and serves `/status` and `/command` without X-Plane present.
- C++ source passes C++17 syntax checking with minimal XPLM API stubs.

## Requires target-machine validation

- Final `.xpl` link/build against the actual X-Plane SDK on Windows/macOS/Linux.
- Runtime load in X-Plane 11.50+ and X-Plane 12.
- Exact Zibo and LevelUp custom command/dataref compatibility for the aircraft release installed by the user.
- Vosk recognition accuracy with the user's microphone, cockpit noise, and selected Indonesian/English models.
- pyttsx3 voice availability depends on voices installed by the operating system.
- C# console build requires the .NET 8 SDK.

## Acceptance measurements for the next release gate

Measure end-of-utterance -> recognized intent -> bridge ACK, not just STT time. Record p50 and p95 separately for Indonesian and English. The <2 s target should be treated as an empirical release criterion, not assumed from the implementation.
