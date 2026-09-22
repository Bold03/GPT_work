# Local bridge protocol

Transport: UDP, loopback only. C++ bridge listens on `127.0.0.1:49050`; Python listens on `127.0.0.1:49051`.

Client -> bridge:

- `PING`
- `UNSUBALL`
- `SUB|alias|type|index|dataref_name`
- `CMD|command_name|once|begin|end`
- `SET|dataref_name|float|int|double|value`

Bridge -> client:

- `PONG|1`
- `ACK|...`
- `ERR|reason|name`
- `TLM|epoch_ms|alias=value|alias=value...`

Missing datarefs are transmitted as `~`. String telemetry is percent-escaped. The bridge accepts packets only from IPv4 loopback and accesses XPLM APIs only from its flight-loop callback.
