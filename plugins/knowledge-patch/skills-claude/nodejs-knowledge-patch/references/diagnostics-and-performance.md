# Diagnostics and Performance

Use this reference for diagnostics and performance work.

## Additional HTTP/2 stream diagnostics (`24.2.0`)

Diagnostics channels now cover server-stream `created`, `start`, `error`, and `finish` events, plus client-stream `close`, `error`, and `finish` events. Instrumentation can observe these lifecycle points without wrapping HTTP/2 APIs.

## Bounded debugger probes (`26.4.0`)

Debugger probe mode adds `--max-hit`, allowing a session to cap the number of probe hits it processes.

## C++ heap statistics (`23.10.0`)

`v8.getCppHeapStatistics()` exposes C++ heap statistics for native-memory diagnostics alongside the existing V8 heap APIs.

```js
import { getCppHeapStatistics } from 'node:v8';

const statistics = getCppHeapStatistics();
```

## Call-site metadata (`23.7.0`)

Call sites rename the `column` property to `columnNumber` and expose `scriptId`; consumers of `util.getCallSites()` must use the new property name.

## Conditional debugger probes (`26.7.0`)

`node inspect` probe mode adds `--cond`, allowing a probe to be limited by a condition in addition to its existing hit-count controls.

## Diagnostic-report environment preservation (`23.3.0`)

The CLI gains an option to preserve environment variables in diagnostic reports, allowing generated reports to retain that process context when it is needed.

## HTTP body diagnostics (`25.2.0`)

Inspector network tooling can now inspect HTTP response bodies and both HTTP/2 request and response bodies. HTTP/2 also adds diagnostics channels for client-stream request bodies.

## HTTP creation diagnostic channels (`23.2.0`)

Instrumentation can subscribe to the new `http.client.request.created` and `http.server.response.created` diagnostic channels to observe HTTP object creation.

```js
import { channel } from 'node:diagnostics_channel';

channel('http.client.request.created').subscribe((message) => {
  console.log(message);
});
```

## HTTP/2 client-stream diagnostics (`24.1.0`)

The diagnostics channel adds `http2.client.stream.created` and `http2.client.stream.start` events for observing HTTP/2 client stream creation and startup.

```js
import { channel } from 'node:diagnostics_channel';

for (const name of [
  'http2.client.stream.created',
  'http2.client.stream.start',
]) {
  channel(name).subscribe((message) => console.log(name, message));
}
```

## HTTP/2 server-stream close diagnostics (`24.3.0`)

The `http2.server.stream.close` diagnostics channel exposes server-side HTTP/2 stream closure to instrumentation.

## HTTP/2 traffic in inspector network tools (`24.8.0`)

Inspector network tracking now includes HTTP/2 client calls. Start the process with the experimental network inspector enabled, then open the dedicated Node DevTools from Chrome's `about:inspect` page.

```sh
node --inspect-wait --experimental-network-inspection app.js
```

## Inspector storage inspection (`25.5.0`)

The inspector adds initial support for storage inspection, allowing inspector clients to examine runtime storage.

## Inspector target enumeration (`25.9.0`)

The inspector protocol now supports `Target.getTargets`, allowing inspector clients to enumerate the runtime's available debugging targets.

## Minor mark-sweep GC classification (`26.5.0`)

`node:perf_hooks` adds `NODE_PERFORMANCE_GC_MINOR_MARK_SWEEP`, allowing performance observers to distinguish minor mark-sweep collections.

## Network initiators in the inspector (`23.8.0`)

The inspector protocol now exposes `Network.Initiator`, allowing tooling to report what initiated a network request.

## Node-specific Performance extensions (`24.12.0`)

Non-standard `performance` properties now belong to the `node:perf_hooks` surface. Import its `performance` export when using Node-specific extensions instead of relying on the browser-compatible global.

```js
import { performance } from 'node:perf_hooks';

console.log(performance.nodeTiming);
```

## Overall heap-size limit (`25.9.0`)

The new `--max-heap-size` option limits the overall V8 heap rather than only its old-space portion.

```sh
node --max-heap-size=2048 app.js
```

## Per-iteration event-loop delay sampling (`26.5.0`)

Event-loop delay measurement in `node:perf_hooks` now takes one sample per event-loop iteration. Monitoring code should account for the resulting histogram semantics when comparing data across upgrades.

## Per-stream console inspection options (`24.10.0`)

The `Console` constructor's `inspectOptions` can now be a `Map` keyed by output stream, so stdout and stderr can use different object-formatting settings.

```js
import { Console } from 'node:console';
import { stderr, stdout } from 'node:process';

const log = new Console({
  stdout,
  stderr,
  inspectOptions: new Map([
    [stdout, { colors: false }],
    [stderr, { colors: true }],
  ]),
});
```

## Percentage-based old-space limits (`24.6.0`)

`--max-old-space-size` now accepts a percentage as well as a fixed MiB value, allowing the V8 old-space limit to scale with available memory.

```sh
node --max-old-space-size=50% app.js
```

## Perfetto tracing support (`26.7.0`)

Node.js adds Perfetto build integration and a trace agent, allowing compatible builds to integrate with Perfetto tracing tooling.

## PID-aware CPU profile filenames (`24.5.0`)

`--cpu-prof-name` now replaces a `${pid}` placeholder with the process ID, preventing concurrent profilers from writing the same filename.

```sh
node --cpu-prof '--cpu-prof-name=CPU.${pid}.cpuprofile' app.js
```

## Programmatic V8 CPU profiling (`25.0.0`)

`node:v8` adds a CPU-profiling facility, providing an in-process alternative to enabling CPU profiling only through startup flags.

## Proxy inspection output (`26.0.0`)

`util.inspect()` now identifies proxied objects as proxies, which can change logs and snapshots after upgrading.

## Revoked diagnostics-channel deprecation (`24.8.0`)

DEP0163 has been revoked, so `Channel.prototype.subscribe()` and `Channel.prototype.unsubscribe()` are no longer deprecated and need no migration solely because of that deprecation.

## Singular call-site helper removed (`24.10.0`)

`util.getCallSite()` is removed. Code using the singular API must switch to the existing `util.getCallSites()` API.

## Source-mapped call sites (`23.3.0`)

`util.getCallSites()`—using the plural API name—now supports resolving call-site locations through source maps.

```js
import { getCallSites } from 'node:util';

const sites = getCallSites(10, { sourceMap: true });
```

## Total allocated bytes in heap statistics (`25.2.0`)

`v8.getHeapStatistics()` now includes `total_allocated_bytes` for allocation monitoring.

```js
import { getHeapStatistics } from 'node:v8';

const { total_allocated_bytes } = getHeapStatistics();
```

## Undici traffic in the inspector (`24.4.0`)

Inspector network tooling can now inspect traffic produced through Undici.

## Versioned diagnostic-report key corrections (`23.5.0`)

Misspelled diagnostic-report keys are corrected and the report version is bumped. Report consumers should branch on the report version rather than assuming the older key spellings.
