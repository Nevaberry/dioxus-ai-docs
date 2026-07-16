# Node.js compatibility

Use this reference when porting Node.js code or relying on core modules, module loading, native addons, workers, VM APIs, and compatibility boundaries.

Entries are grouped by developer task. When entries describe evolving behavior, the later attribution supersedes earlier defaults or limitations.

## Compatibility boundaries and reported baseline

### Node.js compatibility additions *(1.2-guide)*

Bun can now create `node:http2` servers (enabling gRPC servers), use `node:dgram` UDP sockets, and run `node:cluster` workers. Cluster shared-port load balancing uses `reusePort`, which is only effective on Linux; `node:zlib` also gains Brotli, `node:v8` gains `getHeapSnapshot()`/`writeHeapSnapshot()`, and partial support for addons using V8's public C++ API lets more pre-N-API packages load.

### Node.js 24 compatibility baseline *(since 1.2.18)*

Bun now reports Node.js 24.3.0 through `process.version` and `process.versions.node` and updates its reported N-API version. Native addons can therefore select prebuilt binaries targeting Node.js 24.

### Node.js compatibility additions *(since 1.2.23)*

`node:http` servers now handle `CONNECT`, enabling HTTP proxies. `dns.resolve()` no longer passes an extra hostname to callbacks, promised A/AAAA resolutions return string arrays, and `process.report.getReport()` is now available on Windows.

### Diagnostics and tracing modules *(nodejs-compatibility)*

`node:diagnostics_channel` and `node:trace_events` are documented as fully implemented, so Node instrumentation using these standard surfaces does not require Bun-specific replacements.

### Low-level async hooks *(nodejs-compatibility)*

`node:async_hooks` implements `AsyncLocalStorage` and `AsyncResource`, but does not invoke V8 promise hooks. Low-level instrumentation that depends on those hooks is not Node-compatible.

### Child-process IPC limitations *(nodejs-compatibility)*

`node:child_process` omits `proc.gid`, `proc.uid`, and the exported `Stream` class, and its IPC cannot transfer socket handles. Node-to-Bun IPC can use JSON serialization.

### Worker-thread option gaps *(nodejs-compatibility)*

`node:worker_threads` workers do not support the `stdin`, `stdout`, `stderr`, `trackedUnmanagedFds`, or `resourceLimits` options. The module also lacks `markAsUntransferable()` and `moveMessagePortToContext()`.

### Module-loader compatibility *(nodejs-compatibility)*

Overriding `require.cache` works for both ESM and CommonJS modules, but `node:module` lacks `syncBuiltinESMExports()`, `Module#load()`, and `module.register()`. Its `_extensions`, `_pathCache`, and `_cache` internals are no-ops; use `Bun.plugin()` instead of `module.register()`.

### Cryptography compatibility gaps *(nodejs-compatibility)*

`node:crypto` does not implement `secureHeapUsed()`, `setEngine()`, or `setFips()`. Software that requires OpenSSL engine or FIPS controls cannot rely on those Node APIs under Bun.

### Other core-module omissions *(nodejs-compatibility)*

`node:tls` lacks `createSecurePair()`, while `node:domain` lacks `Domain` and `active`. `node:util` lacks `getCallSite()`, `getCallSites()`, `getSystemErrorMap()`, `getSystemErrorMessage()`, `transferableAbortSignal()`, and `transferableAbortController()`.

### V8 serialization format *(nodejs-compatibility)*

`node:v8`'s `serialize()` and `deserialize()` use JavaScriptCore's wire format rather than V8's, so their serialized data is not a Node-compatible interchange format. Most other `node:v8` methods remain unavailable; use `bun:jsc` for profiling.

### Process compatibility gaps *(nodejs-compatibility)*

`process.binding()` is only partially implemented, and `process.title` is a no-op on macOS and Linux. `getActiveResourcesInfo()`, `setActiveResourcesInfo()`, `getActiveResources()`, and `setSourceMapsEnabled()` are stubs, while `process.loadEnvFile()` is not implemented.

### Unsupported Node modules *(nodejs-compatibility)*

The Node-compatible `node:repl` and `node:sqlite` modules are not implemented, even though Bun provides separate native REPL and SQLite facilities.

### Inspector coverage boundary *(nodejs-compatibility)*

Other `node:inspector` APIs remain unavailable beyond the previously documented Profiler support.

### Modules without full compatibility guarantees *(nodejs-compatibility)*

`node:wasi` is only partially implemented. `node:perf_hooks` exposes its APIs, but its Node.js test suite does not pass, so packages that require exact behavior need validation.

## Modules, loading, and resolution

### `$NODE_PATH` module resolution *(since 1.2.2)*

Bun now searches the module directories listed in `$NODE_PATH`, matching Node.js resolution for packages outside an ancestor `node_modules` directory.

```sh
export NODE_PATH="/path/to/global/modules"
bun run my-script.js
```

### CommonJS module metadata and built-in identity *(since 1.2.6)*

Bun now populates `module.children`, reports `module.id` as `"."` for the entry module, and preserves the `node:` prefix during resolution. An unknown prefixed built-in now throws `ERR_UNKNOWN_BUILTIN_MODULE` instead of being treated as an ordinary package name.

### Custom CommonJS extension loaders *(since 1.2.9)*

Bun now supports `require.extensions`, allowing CommonJS code to register a loader for a file extension.

```js
require.extensions[".custom"] = (module, filename) => {
  module._compile('module.exports = "loaded";', filename);
};
const value = require("./file.custom");
```

### Additional CommonJS resolution paths *(since 1.2.9)*

`require.resolve()` now accepts a `paths` option containing additional directories to search.

```js
const path = require.resolve("module", { paths: ["./lib", "./src"] });
```

### Symlink-preserving module resolution *(since 1.2.9)*

Pass `--preserve-symlinks` or set `NODE_PRESERVE_SYMLINKS=1` to resolve modules from the symlink path instead of the symlink target's real path, preserving access to dependencies located beside the symlink.

### Node source-map APIs *(since 1.2.19)*

`node:module` now provides the `SourceMap` class and `findSourceMap()`. A `SourceMap` exposes its payload and can map generated positions with `findEntry()`.

### Consistent module-resolution errors *(since 1.2.20)*

Failures from `Bun.resolve()` and `Bun.resolveSync()` now consistently throw `Error` instances rather than potentially throwing raw values.

## Filesystem APIs

### Node-compatible filesystem stats *(since 1.2.1)*

`fs.fstatSync()` now honors `{ bigint: true }` and returns `BigIntStats`. Constructing `new fs.Stats()` also matches Node by leaving numeric fields undefined and producing invalid date fields instead of zero-valued epoch data.

```js
import fs from "node:fs";
const stats = fs.fstatSync(0, { bigint: true });
```

### Node-compatible filesystem globbing *(since 1.2.2)*

`node:fs` now provides `glob()` and `globSync()`, while `node:fs/promises` provides an async-iterable `glob()`. Only one pattern is currently supported; pattern arrays and the `withFileTypes` option are not yet available.

```ts
import { glob } from "node:fs/promises";

for await (const file of glob("**/*.js", { cwd: "./src" })) {
  console.log(file);
}
```

### Embedded files through `node:fs` *(since 1.2.3)*

Files embedded in a compiled executable with a `file` import can now be passed to async `fs.readFile()` and `fs.stat()`, as well as sync `readFileSync()`, `statSync()`, and `existsSync()`.

```ts
import { promises as fs } from "node:fs";
import asset from "./asset.txt" with { type: "file" };

const contents = await fs.readFile(asset);
const stats = await fs.stat(asset);
```

### Windows recursive-mkdir return paths *(since 1.2.13)*

On Windows, recursive `fs.mkdirSync()` with an absolute path now returns the first created directory with its NT path prefix, such as `\\?\C:\path`, matching newer Node.js versions. Code comparing or reusing that return value must account for the prefixed form.

### Directory-inclusive filesystem globs *(since 1.2.18)*

`fs.glob()`, `fs.globSync()`, and `fs.promises.glob()` now include matching directories by default, equivalent to `Bun.Glob` scanning with `onlyFiles: false`.

```js
import { globSync } from "node:fs";
const entries = globSync("**/*", { cwd: "/tmp/project" });
```

### `fs.watchFile` event semantics *(since 1.2.18)*

Reading a watched file and changing only its access time no longer triggers a change event. Calling `stop()` on its `StatWatcher` emits `stop` asynchronously on the next tick.

### Array patterns in `fs.glob` *(since 1.2.19)*

`node:fs` `glob()`, `globSync()`, and `promises.glob()` accept an array as the pattern argument, and `exclude` accepts an array of patterns.

```js
import { globSync } from "node:fs";
const files = globSync(["**/*.js", "**/*.ts"], { exclude: ["vendor/**"] });
```

### Async line iteration from file handles *(since 1.3.1)*

`FileHandle.readLines()` from `node:fs/promises` provides backpressure-aware async iteration, handles empty and CRLF lines, and accepts `createReadStream` options such as `encoding`.

```ts
import { open } from "node:fs/promises";
const file = await open("file.txt");
try {
  for await (const line of file.readLines({ encoding: "utf8" })) console.log(line);
} finally {
  await file.close();
}
```

### Recursive Linux file watching *(since 1.3.14)*

On Linux, `fs.watch(path, { recursive: true })` now begins watching directories created after the watcher starts. Deleting and recreating a watched file also re-establishes its watch, so later modifications emit `change` events again.

## Cryptography

### X25519 key generation *(since 1.2.1)*

`node:crypto` key-pair generation now supports X25519 for Diffie-Hellman key exchange; both encoded keys can be requested with the usual Node options.

```ts
import crypto from "node:crypto";

const keys = crypto.generateKeyPairSync("x25519", {
  publicKeyEncoding: { type: "spki", format: "der" },
  privateKeyEncoding: { type: "pkcs8", format: "der" },
});
```

### Additional `node:crypto` APIs *(since 1.2.6)*

Bun now implements asynchronous and synchronous HKDF key derivation with `hkdf()`/`hkdfSync()`, plus prime generation and checking with `generatePrime()`/`generatePrimeSync()` and `checkPrime()`/`checkPrimeSync()`.

```ts
import { checkPrimeSync, generatePrimeSync, hkdfSync } from "node:crypto";

const key = hkdfSync("sha256", "secret", "salt", "context", 32);
const prime = generatePrimeSync(512);
console.log(checkPrimeSync(prime)); // true
```

### Clonable Node crypto keys *(since 1.2.11)*

`KeyObject` instances now use the full `SecretKeyObject`, `PublicKeyObject`, and `PrivateKeyObject` hierarchy, and both `KeyObject` and `CryptoKey` instances can be passed to `structuredClone()`. Separately, `crypto.generatePrime()` and `crypto.generatePrimeSync()` now return `ArrayBuffer` rather than `Buffer`.

```js
import crypto from "node:crypto";

const secret = crypto.generateKeySync("aes", { length: 128 });
const clone = structuredClone(secret);
console.log(secret.equals(clone)); // true

const prime = crypto.generatePrimeSync(512);
console.log(prime instanceof ArrayBuffer); // true
```

### SHA-3 crypto algorithms *(since 1.3.13)*

WebCrypto and `node:crypto` support SHA3-224, SHA3-256, SHA3-384, and SHA3-512 for digests and HMAC operations. The names work with `createHash()`, `createHmac()`, `getHashes()`, `SubtleCrypto.digest()`, and HMAC signing and verification.

```ts
const digest = await crypto.subtle.digest(
  "SHA3-256",
  new TextEncoder().encode("hello"),
);
```

### X25519 WebCrypto key agreement *(since 1.3.13)*

`SubtleCrypto.deriveBits()` now accepts X25519 keys and rejects small-order public keys as required by RFC 7748. A `null` or zero bit length returns the complete 32-byte shared secret.

```ts
const local = await crypto.subtle.generateKey("X25519", false, ["deriveBits"]);
const remote = await crypto.subtle.generateKey("X25519", false, ["deriveBits"]);
const secret = await crypto.subtle.deriveBits(
  { name: "X25519", public: remote.publicKey },
  local.privateKey,
  256,
);
```

## VM, V8, inspector, and performance APIs

### `vm.compileFunction()` *(since 1.2.6)*

`node:vm` now implements `compileFunction()` for compiling source into a callable function with named parameters.

```ts
import * as vm from "node:vm";

const add = vm.compileFunction("return left + right", ["left", "right"]);
console.log(add(20, 22)); // 42
```

### Cached `node:vm` scripts *(since 1.2.12)*

`vm.Script` now supports the `produceCachedData` and `cachedData` options plus `createCachedData()`, allowing compiled JavaScript bytecode to be reused.

```js
import { Script } from "node:vm";

const source = 'console.log("Hello world!")';
const script = new Script(source, { produceCachedData: true });
const cachedData = script.createCachedData();
const reused = new Script(source, { cachedData });
```

### ECMAScript modules in `node:vm` *(since 1.2.15)*

`vm.SourceTextModule` can now evaluate ECMAScript modules in separate contexts, including linked imports, cached modules, and propagated errors.

```js
import vm from "node:vm";

const context = vm.createContext({ value: 21 });
const module = new vm.SourceTextModule("export const answer = value * 2", {
  context,
});
await module.link(() => {
  throw new Error("unexpected import");
});
await module.evaluate();
console.log(module.namespace.answer); // 42
```

### Worker heap snapshots *(since 1.2.15)*

`Worker.getHeapSnapshot()` from `node:worker_threads` now captures a V8 heap snapshot for an individual worker, enabling worker-specific memory investigation.

### Performance histograms *(since 1.2.15)*

`createHistogram()` from `node:perf_hooks` records sampled integer distributions with configured bounds and precision, exposing statistics such as minimum, maximum, mean, standard deviation, count, and percentiles.

```js
import { createHistogram } from "perf_hooks";

const histogram = createHistogram({ lowest: 1, highest: 1_000_000, figures: 3 });
histogram.record(100);
histogram.record(200);
console.log(histogram.percentile(50), histogram.totalCount);
```

### Synthetic VM modules *(since 1.2.16)*

`vm.SyntheticModule` creates modules whose exports are populated by a callback, complementing source-text modules when values originate in host code.

```js
import vm from "node:vm";

const module = new vm.SyntheticModule(["answer"], function () {
  this.setExport("answer", 42);
});
await module.link(() => {});
await module.evaluate();
console.log(module.namespace.answer); // 42
```

### Non-contextified VM globals *(since 1.2.19)*

`node:vm` now supports `vm.constants.DONT_CONTEXTIFY`. Passing it to `vm.createContext()` produces a context whose `globalThis` is the same ordinary object visible to the parent.

```js
import vm from "node:vm";
const context = vm.createContext(vm.constants.DONT_CONTEXTIFY);
console.log(vm.runInContext("globalThis", context) === context); // true
```

### Event-loop delay histograms *(since 1.2.22)*

`monitorEventLoopDelay()` from `node:perf_hooks` returns an `IntervalHistogram` that samples event-loop delay in nanoseconds and supports `enable()`, `disable()`, percentile queries, and `reset()`.

```ts
import { monitorEventLoopDelay } from "node:perf_hooks";
const delay = monitorEventLoopDelay({ resolution: 20 });
delay.enable();
await Bun.sleep(100);
delay.disable();
console.log(delay.percentile(99));
```

### CPU profiling through `node:inspector` *(since 1.3.7)*

Bun now implements `Profiler.enable`, `disable`, `start`, `stop`, and `setSamplingInterval` through both `node:inspector` callback sessions and `node:inspector/promises`.

```ts
import inspector from "node:inspector/promises";
const session = new inspector.Session();
session.connect();
await session.post("Profiler.enable");
await session.post("Profiler.start");
const { profile } = await session.post("Profiler.stop");
```

## Workers, processes, and timers

### Node process-stream compatibility *(since 1.2.1)*

`process.stdin.ref()` and `process.stdin.unref()` are now available, and pending `process.stdout.write()` operations keep the process alive until their output is handled.

### Process-level ref controls *(since 1.2.11)*

`process.ref(object)` and `process.unref(object)` control whether an object keeps the event loop alive. They dispatch to its `ref()`/`unref()` methods or the corresponding `Symbol.for("nodejs.ref")`/`Symbol.for("nodejs.unref")` hooks and also work with native timers.

```js
const interval = setInterval(() => {}, 1_000);
process.unref(interval);
```

### Worker environment data *(since 1.2.13)*

`node:worker_threads` now implements `setEnvironmentData()` and `getEnvironmentData()`, allowing a parent thread to make keyed data available to subsequently created workers.

```js
// main.js
import { Worker, setEnvironmentData } from "node:worker_threads";
setEnvironmentData("config", { timeout: 1_000 });
new Worker("./worker.js");

// worker.js
import { getEnvironmentData } from "node:worker_threads";
const config = getEnvironmentData("config");
```

### Worker creation events *(since 1.2.13)*

Creating a `Worker` now emits a `"worker"` event on `process`; the listener receives the worker and can inspect properties such as `threadId`.

```js
process.on("worker", worker => console.log(worker.threadId));
```

### Worker-thread error objects *(since 1.2.14)*

An unhandled exception in a `node:worker_threads` worker now emits an actual `Error` to the worker's `"error"` listener instead of the string-only `ErrorEvent` used by Web Workers.

```js
import { Worker } from "node:worker_threads";
new Worker("./worker.js").on("error", error => {
  console.log(error instanceof Error); // true
});
```

### Forked-process runtime arguments *(since 1.2.17)*

`child_process.fork()` now honors `execArgv`, passing Bun runtime flags to the child and exposing them through the child's `process.execArgv`.

```js
import { fork } from "node:child_process";

fork("./child.js", { execArgv: ["--smol"] });
```

### Eval source process metadata *(since 1.2.17)*

When Bun runs code with `-e` or `--eval`, `process._eval` now contains the evaluated source string for Node-compatible tooling that inspects it.

```sh
bun -e 'console.log(process._eval)'
```

### Timer cancellation boundaries *(since 1.2.18)*

`clearImmediate()` no longer clears timeouts or intervals. `clearTimeout()` and `clearInterval()` continue to clear either kind of timer.

### Process compatibility metadata and warnings *(since 1.2.19)*

`process.features.typescript` is `"transform"`, while `process.features.require_module` and `process.features.openssl_is_boringssl` are `true`. The runtime now also respects `NODE_NO_WARNINGS`.

### Async iteration of process output *(since 1.2.20)*

`process.stdout` and `process.stderr` now implement `[Symbol.asyncIterator]` when backed by a TTY or pipe, enabling Node-compatible `for await` consumers.

## Native addon compatibility

### Buffer and Node-API compatibility *(since 1.2.3)*

`node:buffer` now handles resizable `ArrayBuffer`s and growable shared buffers. For native addons, `napi_is_buffer()` recognizes typed arrays, `Buffer`, and `DataView`, while `napi_is_typedarray()` recognizes typed arrays.

### Additional libuv symbols for native add-ons *(since 1.2.9)*

N-API modules can now use `uv_mutex_destroy`, `uv_mutex_init`, `uv_mutex_init_recursive`, `uv_mutex_lock`, `uv_mutex_trylock`, `uv_mutex_unlock`, `uv_hrtime`, and `uv_once`.

### Disabling native addons *(since 1.2.13)*

The `--no-addons` flag prevents native addon loading: `process.dlopen()` throws `ERR_DLOPEN_DISABLED`, and package resolution disables the `"node-addons"` export condition so packages can select a non-native fallback.

```sh
bun --no-addons app.js
```

### Shared Node-API buffers *(since 1.2.18)*

`napi_create_buffer_from_arraybuffer` now shares the input `ArrayBuffer` memory instead of cloning it, so mutations through either view affect the same backing storage.

### Expanded V8 addon compatibility *(since 1.2.19)*

The V8 C++ compatibility layer now implements core addon operations including `v8::Array::New`, `v8::Object::Get`, `v8::Object::Set`, and `v8::Value::StrictEquals`.

### V8 addon value-type checks *(since 1.3.5)*

Bun's V8 C++ compatibility layer now implements `v8::Value::IsMap()`, `IsArray()`, `IsInt32()`, and `IsBigInt()`, allowing native Node.js addons that use those checks to run without replacing them.

## Utilities, globals, and API compatibility

### Zero-filled unsafe buffers *(since 1.2.1)*

Bun now accepts Node's `--zero-fill-buffers` flag; with it enabled, allocations such as `Buffer.allocUnsafe()` contain zeros rather than arbitrary memory.

```sh
bun --zero-fill-buffers script.js
```

### Negative `util.parseArgs` options *(since 1.2.11)*

`util.parseArgs()` accepts `allowNegative: true`, mapping `--no-foo` to `foo: false`; when `args` is omitted, Bun now parses `process.argv` by default.

```js
const { values } = require("util").parseArgs({
  args: ["--no-foo"],
  allowNegative: true,
  options: { foo: { type: "boolean" } },
});
console.log(values.foo); // false
```

### `util.promisify()` compatibility *(since 1.2.13)*

Promisified functions now preserve the wrapped function's `name`. Promisifying a function that already returns a promise also emits a warning, matching Node.js behavior.

### `DOMException` options *(since 1.2.13)*

`DOMException` accepts an options object containing `name` and `cause`, making the causal error available on the resulting exception.

```js
const error = new DOMException("Request failed", {
  name: "CustomError",
  cause: new Error("Connection closed"),
});
```

### Fluent `BroadcastChannel.unref()` *(since 1.2.14)*

`BroadcastChannel.prototype.unref()` now returns the channel instance rather than `undefined`, so it can be used in a method chain.

### Abort controllers as promise-timer options *(since 1.2.16)*

The promise-based timers accept an `AbortController` itself as their options object, using its `signal` property to cancel the timer.

```js
import { setTimeout } from "node:timers/promises";

const controller = new AbortController();
const pending = setTimeout(100, undefined, controller);
controller.abort();
await pending; // rejects with AbortError
```

### Zstandard in `node:zlib` *(since 1.2.17)*

`node:zlib` now supports Zstandard compression and decompression through synchronous, callback-based, and streaming APIs.

```js
import { zstdCompressSync, zstdDecompressSync } from "node:zlib";

const compressed = zstdCompressSync(Buffer.from("hello"));
console.log(zstdDecompressSync(compressed).toString());
```
