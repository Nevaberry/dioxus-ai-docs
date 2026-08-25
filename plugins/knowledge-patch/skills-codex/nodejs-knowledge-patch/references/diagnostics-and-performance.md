# Diagnostics and Performance

## CPU and heap profiling

- In 23.1.0, `--heap-prof` is allowed in `NODE_OPTIONS`, for example
  `NODE_OPTIONS=--heap-prof node app.js`.
- In 23.9.0, the `--cpu-prof*` flag family is allowed in `NODE_OPTIONS`.
- In 24.5.0, `${pid}` in `--cpu-prof-name` is replaced with the process ID,
  preventing concurrent processes from writing the same profile filename.
- In 24.6.0, `Worker.prototype.cpuUsage()` reports a particular worker's CPU
  consumption from the parent. `process.threadCpuUsage()` has reported the
  calling thread's CPU use since 23.9.0.
- In 24.8.0, `Worker.prototype.startCpuProfile()` returns a handle whose
  `stop()` resolves to that worker's captured CPU profile.
- In 24.9.0, `Worker.prototype.startHeapProfile()` similarly profiles one
  worker's heap.
- In 25.0.0, `node:v8` adds programmatic CPU profiling as an in-process
  alternative to startup flags.
- In 24.18.0, Inspector precise coverage can begin from JavaScript at runtime
  instead of being active from process startup.

## Heap and event-loop metrics

- In 23.10.0, `v8.getCppHeapStatistics()` reports C++ heap statistics alongside
  the existing V8 heap APIs.
- In 25.2.0, `v8.getHeapStatistics()` includes `total_allocated_bytes`.
- In 24.13.0, the 24.13.1 release promotes `--heapsnapshot-near-heap-limit` and
  `v8.queryObjects()` to stable.
- In 26.5.0, event-loop delay monitoring takes one sample per event-loop
  iteration; account for the changed histogram semantics when comparing across
  upgrades. `node:perf_hooks` also adds
  `NODE_PERFORMANCE_GC_MINOR_MARK_SWEEP` to distinguish minor mark-sweep GC.
- Event-loop delay histograms support `Symbol.dispose` since 24.2.0.

## Inspector and debugger tooling

- In 23.8.0, Inspector exposes `Network.Initiator`, allowing tools to identify
  what initiated a network request.
- In 24.1.0, Chrome DevTools can inspect worker threads associated with the
  inspected process.
- In 24.4.0, inspector network tooling can inspect Undici traffic.
- In 24.7.0, initial WebSocket traffic inspection is available.
- In 24.8.0, network tracking includes HTTP/2 client calls. Start with
  `--inspect-wait --experimental-network-inspection` and open the dedicated
  Node DevTools from Chrome's `about:inspect` page.
- In 25.2.0, inspector network tooling can inspect HTTP response bodies and
  HTTP/2 request and response bodies.
- In 25.5.0, Inspector gains initial storage inspection.
- In 25.9.0, the protocol supports `Target.getTargets` for enumerating
  available debugging targets.
- In 26.4.0, debugger probe mode accepts `--max-hit` to cap processed hits. In
  26.7.0, `node inspect` probe mode adds `--cond` for conditional probes.

## Network and lock diagnostics channels

- In 23.2.0, `http.client.request.created` and
  `http.server.response.created` expose core HTTP object creation.
- In 24.1.0, `http2.client.stream.created` and
  `http2.client.stream.start` expose HTTP/2 client stream creation and startup.
- In 24.2.0, server-stream channels add `created`, `start`, `error`, and
  `finish`; client-stream channels add `close`, `error`, and `finish`.
- In 24.3.0, `http2.server.stream.close` exposes server-side stream closure.
- In 25.2.0, HTTP/2 adds diagnostics channels for client-stream request bodies.
- In 25.9.0, diagnostics channels expose Web Lock activity.
- In 24.8.0, DEP0163 is revoked: `Channel.prototype.subscribe()` and
  `unsubscribe()` are not deprecated and need no migration for that reason.

## Reports, call sites, and console output

- In 23.3.0, a CLI option can preserve environment variables in diagnostic
  reports when that process context is required.
- In 23.5.0, misspelled diagnostic-report keys are corrected and the report
  version is bumped. Consumers should branch on the report version instead of
  assuming the earlier spellings.
- In 24.7.0, diagnostic reports include a worker's configured name.
- In 23.3.0, plural `util.getCallSites()` can resolve locations through source
  maps. In 23.7.0, call-site `column` is renamed to `columnNumber` and
  `scriptId` is added. In 24.10.0, singular `util.getCallSite()` is removed;
  use `util.getCallSites()`.
- In 24.10.0, `Console` accepts an `inspectOptions` `Map` keyed by output
  stream, allowing stdout and stderr to use different formatting settings.
- In 24.13.0, the 24.13.1 `util.inspect()` correction limits property output to
  own properties. In 26.0.0, it identifies proxied objects as proxies; both can
  change logs and snapshots.

## Runtime tracing and reporting helpers

- In 24.6.0, `util.setTraceSigInt()` changes SIGINT stack-trace behavior at
  runtime instead of requiring startup-only selection.
- In 23.11.0, `util.diff()` exposes the assertion-style value formatter for
  custom checks and test tooling.
- In 24.18.0, `fs.Stats` date properties such as `atime`, `mtime`, `ctime`, and
  `birthtime` are enumerable and therefore appear in `Object.keys()` and object
  spreads.
- In 26.7.0, Node adds Perfetto build integration and a trace agent for
  compatible builds.
