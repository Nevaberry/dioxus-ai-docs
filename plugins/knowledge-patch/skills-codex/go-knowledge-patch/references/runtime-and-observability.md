# Runtime and Observability

## Garbage collection and process sizing

### Experimental Green Tea garbage collector (`1.25-guide`)

The initial Green Tea collector is selected at build time with
`GOEXPERIMENT=greenteagc`. This version is opt-in and does not include the
later vector acceleration.

### Container-aware `GOMAXPROCS` (`1.25.0`)

On Linux, the default `GOMAXPROCS` is capped by a lower cgroup CPU bandwidth
limit. On every OS, the runtime periodically updates its default as CPU
availability changes. Explicit `GOMAXPROCS` settings disable this behavior;
`containermaxprocs=0` and `updatemaxprocs=0` disable its two parts, while
`runtime.SetDefaultGOMAXPROCS` restores the runtime-selected value.

### Green Tea garbage collection by default (`1.26.0`)

Green Tea is the default collector. `GOEXPERIMENT=nogreenteagc` temporarily
restores the former collector for diagnostics in toolchains that still provide
the switch; the 1.26 guidance describes this opt-out as expected to disappear
in 1.27.

### Randomized 64-bit heap bases (`1.26.0`)

The runtime randomizes the heap base at startup on 64-bit platforms. Tools and
cgo code must not assume predictable heap addresses.
`GOEXPERIMENT=norandomizedheapbase64` temporarily disables randomization at
build time.

## Tracing, profiling, and metrics

### Recoverable crash traces (`1.23.0`)

The runtime flushes active trace data during an uncaught panic, and the trace
tool attempts to recover usable events from a partially broken trace. Events
leading up to a crash are therefore usually inspectable.

### Runtime trace flight recorder (`1.25.0`)

`runtime/trace.FlightRecorder` retains a configurable recent window in an
in-memory ring. Call `WriteTo` after a significant event to save the preceding
trace instead of continuously writing a full trace.

### Linux runtime mapping labels (`1.25.0`)

On kernels with anonymous VMA-name support, mappings receive labels such as
`[anon: Go: heap]`. Set `GODEBUG=decoratemappings=0` to suppress them.

### Experimental goroutine-leak profiles (`1.26.0`)

`GOEXPERIMENT=goroutineleakprofile` adds the `runtime/pprof` profile
`goroutineleak` and `/debug/pprof/goroutineleak`. Detection finds goroutines
blocked on unreachable synchronization primitives, but can miss primitives
reachable through globals or runnable goroutines.

### Scheduler metrics (`1.26.0`)

`runtime/metrics` exposes goroutine-state counts under `/sched/goroutines`,
known OS threads under `/sched/threads:threads`, and the lifetime count under
`/sched/goroutines-created:goroutines`.

### Local-only trace listener shorthand (`1.27.0`)

`go tool trace -http=:6060` listens only on localhost. Use an explicit address
such as `-http=0.0.0.0:6060` when remote access is intended.

### Goroutine labels in tracebacks (`1.27.0`)

Programs selecting language version 1.27 or later include goroutine labels in
traceback header lines by default. Labels may contain sensitive data; use
`GODEBUG=tracebacklabels=0` to suppress them.

### Stable goroutine-leak profiling (`1.27.0`)

The `goroutineleak` pprof profile and HTTP endpoint are generally available.
The `GOEXPERIMENT=goroutineleakprofile` setting is deleted.

## Cleanup, finalizers, and sensitive execution

### Cleanup and finalizer diagnostics (`1.25.0`)

`runtime.AddCleanup` callbacks run concurrently and in parallel. Callbacks must
tolerate concurrent execution and should hand off long blocking work.
`GODEBUG=checkfinalizers=1` checks common finalizer and cleanup mistakes on each
GC cycle and periodically reports queue lengths.

### Secret-mode inheritance (`1.27.0`)

Under experimental `runtime/secret`, goroutines created while secret mode is
active execute in secret mode themselves.
