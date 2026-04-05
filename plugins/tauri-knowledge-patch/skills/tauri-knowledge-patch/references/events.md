# Event System Changes

`Emitter` and `Listener` are now traits. Import with `use tauri::{Emitter, Listener}`.

## Key Changes

| v1 | v2 |
|---|---|
| Methods on structs directly | Import `Emitter`/`Listener` traits |
| `listen_global` | `listen_any` |
| `emit` (implicit target) | `emit` sends to all listeners |
| No targeted emit | `emit_to` targets a specific webview |
| No filter emit | `emit_filter` filters by `EventTarget` |

## Pre-serialized Events (v2.3+)

`emit_str*` methods allow sending pre-serialized JSON events for performance.
