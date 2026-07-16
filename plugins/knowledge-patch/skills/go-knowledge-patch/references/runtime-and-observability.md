# Runtime and Observability

Batch coverage: `1.23.0`, `1.25-guide`, `1.25.0`, `1.26.0`.

## Contents

- [Garbage collection](#garbage-collection)
- [Scheduling](#scheduling)
- [Tracing and profiles](#tracing-and-profiles)
- [Memory layout and diagnostics](#memory-layout-and-diagnostics)
- [Signals and scheduler metrics](#signals-and-scheduler-metrics)

## Garbage collection

### Green Tea rollout

Green Tea was opt-in at build time in Go 1.25:

```sh
GOEXPERIMENT=greenteagc go build ./...
```

That implementation did not yet contain the later vector acceleration. Green Tea is the default collector in Go 1.26. Use `GOEXPERIMENT=nogreenteagc` to disable it temporarily at build time; this opt-out is expected to disappear in Go 1.27.

## Scheduling

### Container-aware `GOMAXPROCS`

On Linux, the default `GOMAXPROCS` is capped by a lower cgroup CPU bandwidth limit. On every OS, the runtime periodically updates the default as CPU availability changes.

Any explicit `GOMAXPROCS` setting disables automatic selection. `GODEBUG=containermaxprocs=0` disables the cgroup-aware cap, and `GODEBUG=updatemaxprocs=0` disables periodic updates. Call `runtime.SetDefaultGOMAXPROCS` to restore the runtime-selected value after an override.

### Timer channel compatibility

Go 1.27 is scheduled to ignore `asynctimerchan`, after which timers will always use synchronous channels.

## Tracing and profiles

### Recoverable crash traces

The runtime flushes active trace data on an uncaught panic. The trace tool attempts to recover usable events from partially broken traces, so events leading up to a crash are usually inspectable.

### Flight recorder

`runtime/trace.FlightRecorder` continuously retains a configurable recent window in an in-memory ring buffer. Call `WriteTo` after a significant event to save only the preceding trace instead of continuously writing a full trace.

### Experimental goroutine-leak profile

Build with `GOEXPERIMENT=goroutineleakprofile` to add the `runtime/pprof` profile named `goroutineleak` and the `/debug/pprof/goroutineleak` endpoint.

Detection identifies goroutines blocked on unreachable synchronization primitives. It can miss primitives still reachable through globals or runnable goroutines, so an empty profile does not prove the absence of leaks.

## Memory layout and diagnostics

### Randomized 64-bit heap bases

The runtime randomizes the heap base at startup on 64-bit platforms. Fix tools and cgo code that assume predictable addresses. `GOEXPERIMENT=norandomizedheapbase64` temporarily restores the older build-time behavior.

### Linux mapping labels

On Linux kernels that support anonymous VMA names, runtime mappings have labels such as `[anon: Go: heap]`. Set `GODEBUG=decoratemappings=0` to suppress them.

### Cleanup and finalizer checks

`runtime.AddCleanup` callbacks execute concurrently and in parallel. Make callbacks safe for concurrent execution and continue to hand off long blocking work rather than performing it inline.

Set `GODEBUG=checkfinalizers=1` to check common finalizer and cleanup mistakes on every GC cycle and periodically report queue lengths.

## Signals and scheduler metrics

### Signal cancellation causes

`signal.NotifyContext` records an error identifying the received signal as the context's cancellation cause. Retrieve it with `context.Cause`.

### Scheduler metrics

`runtime/metrics` adds:

- `/sched/goroutines` for goroutine-state counts.
- `/sched/threads:threads` for known OS threads.
- `/sched/goroutines-created:goroutines` for the total number of goroutines created.
