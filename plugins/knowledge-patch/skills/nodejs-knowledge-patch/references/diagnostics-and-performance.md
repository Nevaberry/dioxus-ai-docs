# Diagnostics and Performance

Inspector capabilities, diagnostics channels, reports, profiling, heap data, and performance metrics.

## Contents

- [Inspector and debugger](#inspector-and-debugger)
- [CPU and heap profiling](#cpu-and-heap-profiling)
- [Performance metrics](#performance-metrics)
- [Diagnostics channels and reports](#diagnostics-channels-and-reports)
- [Runtime inspection utilities](#runtime-inspection-utilities)

## Inspector and debugger

### Debugger probe hit limits (since 26.4.0)

Debugger probe mode now accepts `--max-hit`, allowing a run to cap the number of probe hits.

### Inspector flags for single-executable applications (since 24.8.0)

Single-executable applications now allow inspector command-line flags such as `--inspect` and `--inspect-brk`, so a packaged executable can be debugged through the inspector.

### Inspector payload retrieval (since 24.3.0)

The inspector protocol now exposes methods for retrieving sent and received data, allowing protocol clients to fetch payloads instead of relying only on event metadata.

### Inspector resource loading (since 24.5.0)

The inspector has initial support for the `Network.loadNetworkResource` protocol method, allowing inspector clients to retrieve a network resource through that command.

### Inspector storage inspection (since 25.5.0)

The inspector has initial support for storage inspection, extending its debugging coverage to stored application data.

### Programmatic precise coverage (since 24.18.0)

The JavaScript inspector surface can now start precise coverage directly, allowing in-process tooling to initiate exact coverage collection without an external inspector controller.


## CPU and heap profiling

### C++ heap statistics (since 23.10.0)

`node:v8` now exports `getCppHeapStatistics()` for inspecting V8's C++ heap statistics: `import { getCppHeapStatistics } from 'node:v8'; console.log(getCppHeapStatistics());`.

### CPU profiling through `node:v8` (since 25.0.0)

`node:v8` now provides CPU-profile support for the current isolate, complementing the per-worker profiling API when profiling the main thread without driving the Inspector protocol directly.

### CPU profiling through `NODE_OPTIONS` (since 23.9.0)

The `--cpu-prof` family of CLI options is now accepted in `NODE_OPTIONS`, so profiling can be enabled by deployment configuration.

```console
NODE_OPTIONS='--cpu-prof --cpu-prof-dir=./profiles' node app.js
```

### Heap profiling through `NODE_OPTIONS` (since 23.1.0)

`--heap-prof` is now permitted in `NODE_OPTIONS`, so heap profiling can be enabled with `NODE_OPTIONS=--heap-prof node app.js`.

### Heap snapshots on out-of-memory failures (since 24.11.0)

The V8 flag `--heap-snapshot-on-oom` is supported for writing a heap snapshot when an out-of-memory failure occurs.

```console
node --heap-snapshot-on-oom app.js
```

### Overall heap-size limit (since 25.9.0)

The new `--max-heap-size` CLI option caps the V8 heap directly, rather than requiring the limit to be expressed only through the existing heap-space-specific options.

```console
node --max-heap-size=<size> app.js
```

### Per-thread CPU usage (since 23.9.0)

`process.threadCpuUsage()` reports CPU time consumed by the current thread rather than the whole process, allowing worker-heavy programs to measure threads separately.

### Per-worker CPU profiles (since 24.8.0)

`Worker.startCpuProfile()` starts profiling a particular worker and returns a handle whose `stop()` method resolves to the captured profile, making it possible to isolate worker activity rather than profile only the complete process.

```js
const handle = await worker.startCpuProfile();
await runWork(worker);
const profile = await handle.stop();
```

### Per-worker CPU usage (since 24.6.0)

`Worker` instances now expose `cpuUsage()` for querying an individual worker's CPU consumption, complementing the current-thread-only `process.threadCpuUsage()` API.

### Per-worker heap profiles (since 24.9.0)

`Worker.startHeapProfile()` starts a heap profile for one worker and returns a handle stopped with `await handle.stop()`, complementing per-worker CPU profiling for allocation investigations.

### PID-specific CPU profile names (since 24.5.0)

`--cpu-prof-name` now expands a `${pid}` placeholder, allowing concurrent processes to avoid overwriting one another's profiles: `node --cpu-prof --cpu-prof-name='CPU.${pid}.cpuprofile' app.js`.

### Total allocated bytes in heap statistics (since 25.2.0)

`getHeapStatistics()` from `node:v8` now includes `total_allocated_bytes`, exposing the total allocated-byte count to JavaScript diagnostics.


## Performance metrics

### Disposable event-loop delay histograms (since 24.2.0)

Histograms returned by `monitorEventLoopDelay()` now implement `Symbol.dispose`, so a `using` declaration can disable the histogram automatically at scope exit.

```js
import { monitorEventLoopDelay } from 'node:perf_hooks';

using histogram = monitorEventLoopDelay();
histogram.enable();
```

### Event-loop delay sampling (since 26.5.0)

Event-loop delay measurement in `node:perf_hooks` now samples once per event-loop iteration, which changes how its histogram sample counts and distributions should be interpreted.

### Minor mark-sweep GC classification (since 26.5.0)

`node:perf_hooks` adds `NODE_PERFORMANCE_GC_MINOR_MARK_SWEEP`, allowing GC performance observers to identify minor mark-sweep collections.

### Removed `perf_hooks` accessors (since 25.0.0)

The deprecated `kind` and `flags` accessors on garbage-collection `PerformanceEntry` objects have been removed. Read `entry.detail.kind` and `entry.detail.flags` instead.


## Diagnostics channels and reports

### Environment-free diagnostic reports (since 23.3.0)

The new `--report-exclude-env` CLI option omits environment variables from generated diagnostic reports, allowing reports to be collected without embedding the process environment.

### Environment-variable access tracing (since 23.4.0)

The new `--trace-env`, `--trace-env-js-stack`, and `--trace-env-native-stack` CLI switches trace environment-variable access, optionally with JavaScript or native stack information.

```console
node --trace-env-js-stack app.js
```

### Revoked diagnostics-channel deprecation (since 24.8.0)

DEP0163 has been revoked, so the `Channel.prototype.subscribe()` and `Channel.prototype.unsubscribe()` instance methods are no longer deprecated and do not require migration solely because of that deprecation.

### Web Lock diagnostics (since 25.9.0)

`node:diagnostics_channel` now exposes diagnostics channels for Web Lock activity, allowing lock behavior to be observed without instrumenting application calls directly.


## Runtime inspection utilities

### Call-site property changes (since 23.7.0)

Objects returned by `util.getCallSites()` now expose `columnNumber` instead of `column` and add `scriptId`; consumers of this experimental API must update the old property name.

### Plural and source-mapped call sites (since 23.3.0)

The experimental utility API is now named `util.getCallSites()` rather than `util.getCallSite()`, and can resolve original locations through source maps by passing `{ sourceMap: true }` as its options argument.
