# Runtime API and Lua

## Master CLI sessions

### Persistent worker selection (since 3.2.0)

Select a worker by relative PID with `@@` instead of `@` to keep the Master
CLI session interactive until exit or command completion. This also carries
the master's prompt mode into the worker.

The `prompt` command accepts `n`, `i`, and `p`. Persistent mode can subscribe
to event rings, including the `dpapi` ring initially used for ACME
notifications.

## Runtime backend lifecycle

### Creating and publishing a backend (since 3.4.0)

The Runtime API can add, publish, unpublish, and delete a complete backend
without a reload. Publication is required before the backend is available for
routing.

```text
add backend test-backend from mydefaults mode http
add server test-backend/server1 127.0.0.1:3000 check
enable server test-backend/server1
enable health test-backend/server1
publish backend test-backend
```

Disabled or unpublished backends selected by `use_backend` or
`default_backend` are skipped unless `force-be-switch` is set.

For safe removal, set each server to maintenance, wait for `srv-removable`,
and delete it. Unpublish the backend, wait for `be-removable`, then delete the
backend.

## Certificate operations

### Certificate-list aliases (since 3.3.0)

`add ssl crt-list` no longer checks whether a certificate's filesystem path
matches its in-memory name, allowing `crt-store` aliases to work with
`crt-list`. The caller must ensure that the supplied path or alias identifies
the intended certificate.

### Certificate dumping utility (since 3.3.0)

The `haproxy-dump-certs` script writes certificates obtained through the stats
or master socket to the filesystem.

## Runtime diagnostics

### Thread and map/ACL diagnostics (since 3.3.0)

`show dev` reports thread-to-CPU bindings. `show info` reports added and
removed line counts for map and ACL files. These counters can identify
automation that continually adds entries without removing them.

## Lua mutable pattern references

### The `patref` API (since 3.2.0)

Use `core.get_patref` to obtain a mutable reference to an ACL or Map file. A
reference supports:

- adding and removing patterns;
- replacing Map values;
- bulk additions;
- whole-file replacement through `prepare()` and `commit()`;
- event callbacks.

```lua
local ref = core.get_patref("virt@cached_paths.txt")
if ref ~= nil then
    ref:add(txn.f:path())
end
```

## Lua sample conversion

### Boolean samples (since 3.2.0)

Lua fetches continue to convert boolean samples to integers `0` and `1` by
default. Opt in to actual Lua booleans with:

```haproxy
global
    tune.lua.bool-sample-conversion normal
```

## Lua TCP applets

### Timed receives (since 3.2.0)

`AppletTCP:receive()` accepts an optional timeout. An interactive TCP service
can therefore resume periodic work instead of waiting indefinitely for input.
