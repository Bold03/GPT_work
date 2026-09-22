#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then echo "Usage: $0 /path/to/XPSDK [build-dir]"; exit 2; fi
SDK="$1"; BUILD="${2:-build-bridge}"
cmake -S "$(dirname "$0")/../bridge_cpp" -B "$BUILD" -DXPLANE_SDK="$SDK" -DCMAKE_BUILD_TYPE=Release
cmake --build "$BUILD" --config Release
