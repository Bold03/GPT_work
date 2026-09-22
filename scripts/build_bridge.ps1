param([Parameter(Mandatory=$true)][string]$Sdk, [string]$Build="build-bridge")
$root = Resolve-Path "$PSScriptRoot\.."
cmake -S "$root\bridge_cpp" -B $Build -DXPLANE_SDK="$Sdk" -DCMAKE_BUILD_TYPE=Release
cmake --build $Build --config Release
