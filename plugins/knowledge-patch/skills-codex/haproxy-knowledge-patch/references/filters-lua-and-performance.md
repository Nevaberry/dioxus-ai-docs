# Filters, Lua, and Performance

## CPU placement and thread defaults

HAProxy 3.2.0 made automatic CPU binding topology-aware: it considers CPU
packages, NUMA nodes, CCXs, L3 caches, cores, and hardware threads. Its default
placement remained within one NUMA node, hosts with more than 64 threads needed
explicit configuration to use them all, and the ceilings increased to 1024
threads and 32 thread groups.

In 3.3.0, `cpu-policy` began defaulting to `performance`, which selects only
performance cores on heterogeneous CPUs. Automatic placement also began using
all cores and NUMA nodes and removed the earlier 64-thread limitation. Pin an
explicit policy and bindings when an upgrade must preserve placement.

## Compression thresholds and directional filters

Since 3.2.0, request and response compression can skip bodies smaller than a
configured byte threshold. For the then-shared response filter, use:

```haproxy
filter compression
compression direction response
compression minsize-res 256
```

In 3.4.0, request and response compression split into `filter comp-req` and
`filter comp-res`; the old `compression-direction` directive is deprecated.

```haproxy
backend webservers
    filter comp-res
    compression algo gzip
    compression type text/html text/plain application/json
```

Migrate size thresholds along with the corresponding directional filter.

## Explicit filter order

The 3.4.0 `filter-sequence` directive defines execution order independently
of declaration order. Any declared filter absent from the sequence is skipped.
Use this to order compression and bandwidth limiting deliberately, or to
disable a filter temporarily without deleting its declaration.

## Shared idle connection pools

The 3.4.0 global `tune.idle-pool.shared` accepts:

- `on` to share idle server connections within a thread group;
- `full` to share them across all threads;
- `off` to disable sharing for diagnostics.

It supersedes and deprecates `tune.takeover-other-tg-connections`.

## Kernel-side buffering

Since 3.2.0, `tune.notsent-lowat.client` and
`tune.notsent-lowat.server` can reduce kernel socket-buffer occupancy and
unacknowledged data. Tune them only with workload measurements because they
trade buffering for memory reduction.

## Pausing policy execution

The 3.2.0 `pause` action delays request or response processing by either a
fixed millisecond value or a sample expression. It is suitable for slowing
rate-limit offenders without immediately rejecting them.

```haproxy
http-request pause 250
http-response pause 250
```

## Lua pattern references

HAProxy 3.2.0 adds mutable Lua pattern references through
`core.get_patref`. A reference can add or remove ACL/Map patterns, replace Map
values, perform bulk additions, replace a whole file through `prepare()` and
`commit()`, and register event callbacks.

```lua
local ref = core.get_patref("virt@cached_paths.txt")
if ref ~= nil then
    ref:add(txn.f:path())
end
```

Treat whole-file replacement as a transaction: prepare all changes before
committing the new view.

## Lua boolean sample conversion

Lua fetches still convert boolean samples to integers `0` and `1` by default.
Since 3.2.0, opt into actual Lua booleans explicitly:

```haproxy
global
    tune.lua.bool-sample-conversion normal
```

Audit comparisons when changing this setting because numeric and boolean
truth handling can differ in Lua code.

## Timed Lua TCP receives

`AppletTCP:receive()` accepts an optional timeout since 3.2.0. Use it for
interactive TCP applets that must wake periodically rather than block
indefinitely waiting for input.

## Stable fast-forward control

As of 3.3.0, `tune.disable-fast-forward` is stable and no longer requires
`expose-experimental-directives`.
