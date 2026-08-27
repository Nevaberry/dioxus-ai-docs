# Node.js compatibility

## Compatibility boundary

### Known differences (`nodejs-compatibility`)

The compatibility snapshot measured Bun against Node.js v23. Later releases
closed several gaps, so distinguish persistent differences below from the
closures in the next section.

- `node:wasi` remains partial.
- `module.register()` is not implemented; use `Bun.plugin`. CJS
  `module._extensions`, `_pathCache`, and `_cache` exist but are no-ops.
  Overriding `require.cache` works for ESM and CJS. `syncBuiltinESMExports` and
  `Module#load()` are missing.
- `node:v8` serialize/deserialize use JavaScriptCore structured-clone bytes,
  not V8's wire format. Do not persist or exchange them across Node and Bun.
- Promise hooks behind `async_hooks.createHook()` do not fire; APIs built on
  `AsyncLocalStorage` or `AsyncResource` work.
- Worker options `stdin` and `trackedUnmanagedFds` remain ignored;
  `moveMessagePortToContext` is missing. Child-process `Stream`, `proc.uid`, and
  `proc.gid` were listed as missing; spawning now accepts uid/gid, but no later
  entry adds the result properties or Stream export.
- `process.loadEnvFile` is absent. `getActiveResourcesInfo`,
  `getActiveResources`, and `setSourceMapsEnabled` are no-op stubs.
- Assigning `process.title` was a no-op on macOS and Linux in the compatibility
  snapshot; later guidance changes its default value but does not state that
  assignment became effective.
- Missing exports include util `getSystemErrorMap`, `getSystemErrorMessage`,
  `transferableAbortSignal`, and `transferableAbortController`; crypto
  `secureHeapUsed`, `setEngine`, and `setFips`; TLS `createSecurePair`.

### Gaps closed (`1.4`, `1.4-3`)

`node:sqlite`, `node:repl`, `node:trace_events`, and `node:domain` are
implemented. Worker `resourceLimits`, `stdout`, `stderr`, and `eval` now work.
Socket STARTTLS supports `upgradeTLS({ isServer: true })`, and cluster shares
listeners.

The direct socket-based `node:http` client closes earlier buffering and custom
Agent gaps. Worker transfer marking, cross-thread messaging, IPC socket-handle
passing through cluster, and util `getCallSites` also arrived later.

Playwright, vitest pools/coverage, Datadog profiling, and OpenTelemetry HTTP/fs
instrumentation consequently run under Bun.

## Reported Node version and ABI

### Version transitions (`1.2.18`, `1.4-2`, `1.4-3`)

Bun first moved its reported Node version to v24.3.0 so Node 24 prebuilds could
load. Bun 1.4 reports Node.js 26, `process.versions.modules` 147, and Node-API
version 10 with Node 26 headers and five experimental `node_api_*` functions.
Native addons therefore need the corresponding ABI build.

`res.writeHeader()` is gone; use `res.writeHead()`. In paused streams,
`readable.read()` without a size returns one buffered chunk rather than all
content, unless `setEncoding()` is active.

## Modules and resolution

### Node path and CommonJS hooks (`1.2.2`, `1.2.9`)

- Runtime bare imports search `NODE_PATH`; `bun build` also honors it
  (`1.2.18`).
- `--preserve-symlinks` and `NODE_PRESERVE_SYMLINKS=1` make a symlinked package
  resolve dependencies from its real location.
- `require.extensions[ext]` may call `module._compile`, and
  `require.resolve(id, { paths })` works.

### Module metadata and hooks (`1.2.6`, `1.2.19`, `1.3.2`)

`module.children` is populated. `node:module` exports `SourceMap` and
`findSourceMap()` with payload and line/column lookup.

`Module._resolveFilename` overrides receive `options`, and Bun honors
`options.paths`, rejecting non-arrays with `ERR_INVALID_ARG_TYPE`.

`process.binding("http_parser")` exposes the llhttp-backed `HTTPParser`, also
re-exported by `node:_http_common` (`1.2.16`).

### Namespace and feature properties (`1.2.19`, `1.2.21`)

`process.features.typescript` is `"transform"`; `require_module` and
`openssl_is_boringssl` are true. ESM namespace objects do not inherit
`Object.prototype`, so properties such as `toString` are absent.

`@types/bun` detects whether `tsconfig.json` includes DOM libs. Without them,
EventSource, Performance, and BroadcastChannel extend Node-compatible types
rather than empty interfaces. The types also work with TypeScript 5.9 without
`skipLibCheck`; sqlite transaction return types infer from callbacks
(`1.2.20`).

### Compile cache (`1.4-3`)

`module.enableCompileCache(dir)` and `NODE_COMPILE_CACHE` persist bytecode
between runs. This is separate from `bun build --bytecode`.

## HTTP, HTTPS, HTTP/2, and cluster

### Direct Node HTTP client (`1.4-3`)

`http.ClientRequest` now uses net/TLS sockets, Node's parser, and an Agent pool.
Bodies stream, custom Agents and lookup functions are honored, and keepalive,
Upgrade, CONNECT, 1xx information events and `createConnection` behave like
Node.

On the server, `headersTimeout`, `requestTimeout`, and `keepAliveTimeout` fire;
timeouts emit raw 408 responses and use `connectionsCheckingInterval`.
Pipelining and `maxRequestsPerSocket` work, sockets are real `net.Socket`s, and
per-server `insecureHTTPParser`/`maxHeaderSize` are respected.

### Earlier HTTP additions (`1.2-guide`, `1.2.10`, `1.2.23`)

- `node:http2` secure servers and gRPC work; `node:dgram` and `node:cluster`
  are available. Cluster `reusePort` was Linux-only at introduction.
- `createServer({ rejectNonStandardBodyWrites: true })` throws when writing a
  body for HEAD; default behavior discards it.
- HTTP servers handle CONNECT.
- `http.Server.closeIdleConnections()` is implemented (`1.2.22`).

### HTTP/2 and cluster expansion (`1.4-3`)

- HTTP/2 supports push, HTTP/1 fallback, AltSvc/Origin frames, extended
  CONNECT, and diagnostics channels.
- Cluster implements round-robin descriptor passing, `SCHED_NONE`, UDP
  clustering, and `worker.send(message, socket)` handle passing.

## Workers and child processes

### Worker environment and events (`1.2.13`)

`setEnvironmentData` snapshots values into workers created later;
`getEnvironmentData` reads them. `process` emits `worker` on creation. Worker
was not marked stable at that point.

Worker error events carry a real `Error` rather than a Web Worker `ErrorEvent`
string (`1.2.14`). `Worker.getHeapSnapshot()` arrived in `1.2.15`.

### Cross-thread behavior (`1.4-3`)

- `postMessageToThread(threadId, value)` delivers a `workerMessage` event to
  another thread.
- `env: SHARE_ENV` makes process environments live and shared.
- `markAsUntransferable` and `markAsUncloneable` work.
- Workers expose heap statistics, CPU usage, and CPU profiling.
- `terminate()` resolves only after descendant workers stop, with queued
  messages delivered first.
- Unsettled top-level await exits 13; worker `process.abort()` stops only that
  worker; positional postMessage transfer lists transfer rather than clone.

### Spawn and fork compatibility (`1.2.9`, `1.2.17`, `1.3.2`, `1.4-3`)

- `maxBuffer` applies to Bun and child-process spawn APIs and kills the child
  after the threshold.
- `child_process.fork()` honors `execArgv`; `process._eval` contains `-e` code.
- Synchronous spawn uses an isolated event loop, so timers/microtasks do not run
  during it. Types expose `detached`, `lazy`, and `onDisconnect` under
  `Bun.Spawn.BaseOptions`; `Spawn.OptionsObject` is deprecated.
- Bun and child-process spawn honor uid/gid, drop supplementary groups first,
  throw `EPERM` synchronously, and return `ENOTSUP` on Windows.
- `child_process.spawn()` ignores `options.encoding`; output streams always
  emit Buffer objects (`1.4-2`).

### No native addons (`1.2.13`)

`--no-addons` makes `process.dlopen()` throw `ERR_DLOPEN_DISABLED` and disables
the `node-addons` export condition so packages may choose JS fallbacks.

## Test API

### Initial implementation (`1.2.6`)

`node:test` runs through Bun's test runner. At introduction, subtests, mocks,
snapshots, timers, reporters and the programmatic API were missing.

### Expanded Node test support (`1.4-3`)

Subtests through `t.test`, `t.describe`, or nested top-level test calls execute
inline. Supported additions include plans, waitFor, getTestContext, mock timers,
mocked properties, runtime skip/todo, tags, registered assertions, callback
tests, and a per-test `t.mock` tracker.

Programmatic `run()` launches one child per file and returns a TestsStream with
Node event ordering. `expectFailure` treats a throw as success and a pass as
`expectedFailure`.

## Filesystem and path APIs

### Glob evolution (`1.2.2`, `1.2.17`, `1.2.18`, `1.2.19`)

Node `fs.glob`, sync glob, and promise glob are implemented. The promise form is
an async iterator. Initially one pattern was accepted and `withFileTypes` was
missing; options later became optional, results began including directories,
and the pattern argument gained arrays. `exclude` accepts a predicate or glob
array, with `ignore` as an alias.

### Watches and file handles (`1.3.1`, `1.3.14`, `1.4-3`, `1.4-4`)

- `FileHandle.readLines()` gives backpressure-aware async line iteration.
- Recursive Linux watches include directories created after start and
  re-created files emit changes.
- `fs.watch` accepts an ignore predicate; promise watch accepts AbortSignal.
- On Linux/Windows kernel queue overflow, every live watcher receives
  `("change", null)` rather than silently losing events.
- `fs.mkdtempDisposable()` and FileHandle `pull()`/`writer()` are implemented.

### Filesystem behavior changes (`1.2.13`, `1.4-2`, `1.4-3`)

- Recursive `mkdirSync` on Windows returns the first created directory with the
  `\\?\` prefix.
- `fs.rmdir({ recursive: true })` rejects; use `fs.rm`.
- `appendFile({ flag: "w" })` truncates. `fs.rm` rejects explicitly undefined
  options; `fs.open` rejects an object `flags` value.
- Errors expose Node's stable syscall names such as `stat` or `utime`, not raw
  platform calls.

## Crypto, V8, VM, and WebAssembly

### Crypto additions (`1.2.1`, `1.2.6`, `1.2.11`, `1.3.13`, `1.4`)

- X25519 key-pair generation works; it previously threw NotSupportedError.
- HKDF, prime generation/checking, and `vm.compileFunction()` are implemented.
- Crypto key objects are real Secret/Public/PrivateKeyObject instances;
  KeyObject and CryptoKey survive structured cloning and cloned keys compare
  equal through `.equals()`.
- SHA3-224/256/384/512 work in hashes, HMAC and WebCrypto. X25519
  `deriveBits()` accepts null or zero length for all 32 bytes.
- WebCrypto and node crypto expose post-quantum ML-DSA signatures and ML-KEM
  encapsulation.

### VM modules and bytecode (`1.2.12`, `1.2.15`, `1.2.16`, `1.2.19`, `1.4-3`)

- `vm.Script` can produce, create, and consume cached data.
- `SourceTextModule` and `SyntheticModule` support linking, evaluation and
  namespaces; vm.Module cached-data properties are implemented.
- `vm.constants.DONT_CONTEXTIFY` creates a normally behaving global context.
- Node 26 linking adds `linkRequests`, `instantiate`, `moduleRequests`,
  `hasTopLevelAwait`, and `microtaskMode: afterEvaluate`.

### V8 and inspector (`1.2-guide`, `1.3.7`, `1.4-3`)

Heap snapshots are available through `node:v8`; some V8 C++ API addons work
despite JavaScriptCore. Inspector supports callback/promise Profiler-domain
sampling. Later it adds a CDP server through `open`, `url`, `close`, and
`waitForDebugger`, and v8 adds `GCProfiler` and
`isStringOneByteRepresentation`.

### Async local storage (`1.4-3`)

`new AsyncLocalStorage({ name, defaultValue })` supports Node 26 constructor
options. `withScope(value)` returns a disposable scope, so `using` can delimit
storage without nesting a `run()` callback.

### WebAssembly (`1.2.20`, `1.4-3`)

Streaming compile/instantiate accept a Fetch promise. JavaScript Promise
Integration is enabled by default through `WebAssembly.Suspending` and
`WebAssembly.promising`. Memory64, multi-memory, relaxed SIMD, interpreter SIMD,
and streaming `compileOptions` are implemented.

## Streams, timers, and event loop

### Stream operators (`1.4-3`)

With `--experimental-stream-iter`, `node:stream/iter` and `node:zlib/iter`
provide iterator-style operators such as map and filter.

### Socket half-close (`1.4-3`)

`net.Socket.end()` half-closes; call `destroy()` if complete teardown was
intended. Net and Bun connect accept `localAddress`/`localPort`.

### Timers (`1.2.16`, `1.2.18`, `1.3.7`)

`node:timers/promises` accepts an AbortController directly in the options slot.
`clearImmediate` no longer clears timeouts or intervals, although timeout and
interval clear functions still clear all three. Timer handles expose Node's
`_idleStart` monotonic timestamp.

### Compression streams and zlib (`1.2-guide`, `1.2.17`, `1.3.3`, `1.4-3`)

Node zlib supports Brotli and zstd, including streaming, and later their
dictionaries. Web `CompressionStream`/`DecompressionStream` support standard
gzip/deflate formats plus Bun-only `brotli` and `zstd` names.

## Process, OS, and diagnostics

### Process ref control (`1.2.11`)

`process.ref()`/`unref()` invoke an object's methods or its
`Symbol.for("nodejs.ref")`/`unref` hooks and accept native handles.

`util.parseArgs({ allowNegative: true })` makes `--no-foo` set a boolean option
false; omitted `args` defaults to `process.argv`.

### Process behavior (`1.2.4`, `1.2.19`, `1.3.13`, `1.3.14`, `1.4-2`)

- Eval/print `process.argv` omits the old cwd `[eval]` placeholder and retains
  all user arguments.
- IPv6 network-interface `scope_id` became `scopeid`.
- `process.ppid` calls `getppid()` on access so orphan detection stays current.
- `process.execve()` replaces the process image, inherits stdio, closes other
  fds, resets the signal mask, warns once, rejects workers, and is unavailable
  on Windows. Worker use throws `ERR_WORKER_UNSUPPORTED_OPERATION`; Windows
  throws `ERR_FEATURE_UNAVAILABLE_ON_PLATFORM`, and first use emits an
  ExperimentalWarning.
- `process.title` defaults to invoked `argv[0]`; `reallyExit()` does not emit
  exit. Warnings print in Node format and listeners do not suppress default
  output; use `--no-warnings`.

### Environment and time zone (`1.4-3`)

Changing `process.env.TZ` affects existing Date objects. Assigned environment
values coerce to strings and structured cloning works. Warning-control flags
for suppression, traces, redirect, and selected disabling are wired up.

### OS values (`1.3.12`, `1.3.13`)

Linux availableParallelism/hardwareConcurrency and Bun's worker/JIT pools honor
cgroup CPU quotas. `os.freemem()` uses Linux `MemAvailable`, including
reclaimable page cache.

### Diagnostics and tracing (`1.2.15`, `1.2.22`, `1.4-3`)

`perf_hooks.createHistogram()` was initially unavailable, then gained
`record`, `min`, `max`, `mean`, `stddev`, `totalCount`, and `percentile`, with
`lowest`, `highest`, and `figures` options. `monitorEventLoopDelay()` was later
implemented too. Trace events write Chrome-format logs under the standard Node
flags and categories.

### TLS APIs (`1.4-3`)

`node:tls` adds session and keylog events, `SNICallback`, `ALPNCallback`, PFX,
structured OpenSSL errors with code/library/reason, per-context
`addCACert()`, and process-wide `setDefaultCACertificates()`.

## Utilities and web-platform compatibility

### Utility functions (`1.2.11`, `1.2.13`, `1.4-2`, `1.4-3`)

- `util.parseArgs` accepts `allowNegative`; omitted args default to
  `process.argv`.
- `util.promisify()` warns on promise-returning functions and preserves name.
- `util.styleText()` returns plain text for a non-TTY unless
  `validateStream: false`.
- `node:util` adds getCallSites, hex styleText colors, and `tty.WriteStream`.

### Text and Buffer (`1.2.12`, `1.4-3`)

TextDecoder rejects labels with NUL, normalizes `.encoding`, and coerces
`fatal`. It later supports every WHATWG encoding and all documented labels.
Buffer search methods accept an `end` parameter.

`node:dns/promises` exports `getDefaultResultOrder()` and `getServers()`
(`1.4-3`).

### TTY lifecycle (`1.2.22`)

Opening `/dev/tty` after stdin closes no longer fails with `ESPIPE`, and
`tty.ReadStream` exposes `ref()` and `unref()`.

### Structured clone and namespace values (`1.4-2`)

`structuredClone` preserves shared identity for Date, RegExp, Error subclasses,
Blob, File, CryptoKey and similar values, and rejects non-object transfer-list
entries with TypeError.

### Miscellaneous additions

- `node:net` exports `SocketAddress.parse()` (`1.2.4`).
- `DOMException` accepts `{ name, cause }` as its second argument (`1.2.13`).
- `URLPattern` is built in with test, exec, component patterns and regexp-group
  reporting (`1.3.4`).
- `readline/promises` interfaces are disposable; stdout/stderr are async
  iterable (`1.3-guide`).
- `--zero-fill-buffers` makes unsafe Buffer allocation zero-filled (`1.2.1`).
- `Math.sumPrecise()` performs precise summation (`1.2.18`).
- Iterator helpers include `Iterator.prototype.includes`; cyclic Array join or
  toString throws RangeError (`1.4-4`).
