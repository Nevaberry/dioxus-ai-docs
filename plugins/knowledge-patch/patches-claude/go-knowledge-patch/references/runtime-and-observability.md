# Runtime and Observability

## Garbage collection and heap behavior

### Green Tea rollout (1.25-guide, 1.26.0)

Green Tea first appeared as an opt-in collector under
`GOEXPERIMENT=greenteagc`; that early implementation did not include later
vector acceleration. It is now the default collector. The temporary
`GOEXPERIMENT=nogreenteagc` opt-out was expected to disappear, so do not make
production behavior depend on it.

### Container-aware processor selection (1.25.0)

On Linux, the default `GOMAXPROCS` is capped by a lower cgroup CPU bandwidth
limit. On every OS the runtime periodically refreshes its default as CPU
availability changes. An explicit `GOMAXPROCS` disables automatic selection;
`containermaxprocs=0` and `updatemaxprocs=0` disable its two parts.
`runtime.SetDefaultGOMAXPROCS` restores runtime selection after an override.

### Random heap bases (1.26.0)

The runtime randomizes the heap base on 64-bit platforms. Tools and cgo code
must not assume predictable addresses. `GOEXPERIMENT=norandomizedheapbase64`
was only a temporary build-time escape hatch.

## Tracing and crash diagnostics

### Recoverable crash traces (1.23.0)

The runtime flushes active trace data on an uncaught panic, and `go tool trace`
attempts to recover events from partially broken traces. Inspect the trace
leading up to a crash even when termination was unclean.

### Flight recording (1.25.0)

`runtime/trace.FlightRecorder` retains a configurable recent window in an
in-memory ring. Call `WriteTo` after a significant event to preserve preceding
activity without continuously writing a full trace.

### Listener exposure and traceback labels (1.27.0)

`go tool trace -http=:6060` binds only to localhost. Use an explicit address
such as `-http=0.0.0.0:6060` only when remote exposure is intended.

Modules selecting Go 1.27 or later include goroutine labels in traceback
headers. Labels may contain sensitive data; set `GODEBUG=tracebacklabels=0` to
suppress them.

## Profiles and metrics

### Goroutine-leak profile lifecycle (1.26.0, 1.27.0)

The `runtime/pprof` `goroutineleak` profile and
`/debug/pprof/goroutineleak` endpoint are stable; the earlier
`GOEXPERIMENT=goroutineleakprofile` gate has been deleted. Detection finds
goroutines blocked on unreachable synchronization primitives, but can miss a
primitive reachable through a global or runnable goroutine.

### Scheduler metrics (1.26.0)

Use these `runtime/metrics` names:

- `/sched/goroutines` for goroutine state counts.
- `/sched/threads:threads` for known OS threads.
- `/sched/goroutines-created:goroutines` for lifetime goroutine creation.

## Mappings, cleanup, and secrets

### Linux mapping labels (1.25.0)

On Linux kernels with anonymous VMA names, runtime mappings are labeled, for
example `[anon: Go: heap]`. Set `GODEBUG=decoratemappings=0` when a consumer
cannot tolerate the labels.

### Concurrent cleanup callbacks (1.25.0)

`runtime.AddCleanup` callbacks may execute concurrently and in parallel. Make
them concurrency-safe and hand off long blocking work. `GODEBUG=checkfinalizers=1`
checks common cleanup and finalizer mistakes at each GC and periodically
reports queue lengths.

### Secret mode and inheritance (1.26.0, 1.27.0)

`GOEXPERIMENT=runtimesecret` exposes `runtime/secret` for erasing secret-bearing
temporaries from registers, stacks, and new heap allocations. Its initial
support is limited to Linux amd64 and arm64. Goroutines created while secret
mode is active inherit secret mode. Treat the facility as experimental and
platform-sensitive.
