# WASI Interface Migration

## WASI 0.2 interoperation (`wasi-0.3-guide`)

WASI 0.3 is additive, not a mandatory migration. A host may keep exposing
WASI 0.2. A 0.3 runtime may also polyfill 0.2 by translating the component's
imports into native 0.3 primitives at the host boundary.

Migrate primarily when a component needs composable async across component
boundaries or needs the reshaped 0.3 interfaces.

## Replacing `wasi:io`

There is no 0.3 release of `wasi:io`. Translate its resources and operations
as follows:

| WASI 0.2 | WASI native async |
| --- | --- |
| `pollable` | `future<T>` |
| `input-stream` | `stream<u8>` |
| `output-stream` | `stream<u8>` passed into a call |
| polling | awaiting a future |
| `subscribe()` | returning a future from the operation |

## HTTP reshaping

`wasi:http` reduces nine request, response, body, out-parameter, and future
resources to `request` and `response`. Bodies are `stream<u8>` values, and
trailers use a future. The handler directly returns its response:

```wit
handle: async func(request: request) -> result<response, error-code>;
```

The `proxy` world is replaced by `service`. The `middleware` world both imports
and exports the handler.

## Socket capabilities and interfaces

`wasi:sockets` removes the `network` resource that WASI 0.2 passed through
bind, connect, and name lookup. Grant network access at the world level.

The previous seven interfaces consolidate into `types` and `ip-name-lookup`.
TCP `listen` directly returns `stream<tcp-socket>` instead of requiring a
separate accept loop.

## Filesystem, clocks, and CLI changes

- Some filesystem methods become `async func`.
- `wasi:clocks/wall-clock` becomes `system-clock`.
- The clocks `datetime` type becomes `instant`.
- CLI interfaces share the new `wasi:cli/types` interface.

## Stable compatibility line (`wasi-0.3.0`)

WASI 0.3.0 is ratified as stable. A component compiled for it remains
compatible as later 0.3.x patch releases ship.

## HTTP service and middleware roles

The `service` world imports the HTTP `client` and exports the incoming
`handler`. The `middleware` world includes `service` and additionally imports
a downstream `handler`, making it the successor to the WASI 0.2 `proxy` world.

```wit
world service {
    import client;
    export handler;
}

world middleware {
    include service;
    import handler;
}
```
