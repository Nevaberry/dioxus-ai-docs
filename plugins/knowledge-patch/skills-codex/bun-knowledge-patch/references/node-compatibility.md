# Node.js compatibility

Use this reference for Node core modules, process behavior, workers, native addons, VM and inspector APIs, and documented compatibility boundaries.

## `$NODE_PATH` module resolution

*Batch: `1.2.2`.*

Bun now searches the module directories listed in `$NODE_PATH`, matching Node.js resolution for packages outside an ancestor `node_modules` directory.

```sh
export NODE_PATH="/path/to/global/modules"
bun run my-script.js
```

## `fs.watchFile` event semantics

*Batch: `1.2.18`.*

Reading a watched file and changing only its access time no longer triggers a change event. Calling `stop()` on its `StatWatcher` emits `stop` asynchronously on the next tick.

## `node:net` block lists

*Batch: `1.2.12`.*

`node:net` now implements `BlockList` for matching individual IP addresses, address ranges, and subnets.

```js
import { BlockList } from "node:net";

const blocked = new BlockList();
blocked.addRange("10.0.0.1", "10.0.0.10");
blocked.addSubnet("8.8.8.8", 24);
blocked.check("8.8.8.9"); // true
```

## `node:net` compatibility controls

*Batch: `1.2.16`.*

`node:net` now honors `server.maxConnections`, resolves hostnames through `dns.lookup()` in the Node-compatible path, and supports applying a `net.BlockList` to `net.Socket` and `net.Server`.

## `node:net` validation and rejection handling

*Batch: `1.2.18`.*

Non-string `host` or IPC `path` options now throw `ERR_INVALID_ARG_TYPE`; nonexistent IPC paths emit `ENOENT`, and a custom lookup returning a non-string address emits `ERR_INVALID_IP_ADDRESS`. With `events.captureRejections` enabled, a rejected async `net.Server` connection listener is emitted as an error on and destroys the incoming socket instead of becoming an unhandled rejection.

## `util.promisify()` compatibility

*Batch: `1.2.13`.*

Promisified functions now preserve the wrapped function's `name`. Promisifying a function that already returns a promise also emits a warning, matching Node.js behavior.

## `vm.compileFunction()`

*Batch: `1.2.6`.*

`node:vm` now implements `compileFunction()` for compiling source into a callable function with named parameters.

```ts
import * as vm from "node:vm";

const add = vm.compileFunction("return left + right", ["left", "right"]);
console.log(add(20, 22)); // 42
```

## Additional `node:crypto` APIs

*Batch: `1.2.6`.*

Bun now implements asynchronous and synchronous HKDF key derivation with `hkdf()`/`hkdfSync()`, plus prime generation and checking with `generatePrime()`/`generatePrimeSync()` and `checkPrime()`/`checkPrimeSync()`.

```ts
import { checkPrimeSync, generatePrimeSync, hkdfSync } from "node:crypto";

const key = hkdfSync("sha256", "secret", "salt", "context", 32);
const prime = generatePrimeSync(512);
console.log(checkPrimeSync(prime)); // true
```

## Additional CommonJS resolution paths

*Batch: `1.2.9`.*

`require.resolve()` now accepts a `paths` option containing additional directories to search.

```js
const path = require.resolve("module", { paths: ["./lib", "./src"] });
```

## Array patterns in `fs.glob`

*Batch: `1.2.19`.*

`node:fs` `glob()`, `globSync()`, and `promises.glob()` accept an array as the pattern argument, and `exclude` accepts an array of patterns.

```js
import { globSync } from "node:fs";
const files = globSync(["**/*.js", "**/*.ts"], { exclude: ["vendor/**"] });
```

## Async iteration of process output

*Batch: `1.2.20`.*

`process.stdout` and `process.stderr` now implement `[Symbol.asyncIterator]` when backed by a TTY or pipe, enabling Node-compatible `for await` consumers.

## Buffer and Node-API compatibility

*Batch: `1.2.3`.*

`node:buffer` now handles resizable `ArrayBuffer`s and growable shared buffers. For native addons, `napi_is_buffer()` recognizes typed arrays, `Buffer`, and `DataView`, while `napi_is_typedarray()` recognizes typed arrays.

## Buffer search boundaries

*Batch: `1.4-3`.*

`Buffer.indexOf()`, `lastIndexOf()`, and `includes()` accept an `end` boundary, while concatenation, copying, byte lengths, and UTF-16 searches follow Node's range and encoding behavior.

## Cached `node:vm` scripts

*Batch: `1.2.12`.*

`vm.Script` now supports the `produceCachedData` and `cachedData` options plus `createCachedData()`, allowing compiled JavaScript bytecode to be reused.

```js
import { Script } from "node:vm";

const source = 'console.log("Hello world!")';
const script = new Script(source, { produceCachedData: true });
const cachedData = script.createCachedData();
const reused = new Script(source, { cachedData });
```

## Cgroup-scoped subprocesses

*Batch: `1.4-2`.*

On Linux, `Bun.spawn()` and `Bun.spawnSync()` accept an existing cgroup directory or descriptor through `cgroup`, placing the child there before it executes so memory, PID, and inherited-child limits apply immediately; `node:child_process` forwards the option and other platforms ignore it. An already-aborted `signal` now throws `AbortError` without creating a process.

## Child process identities

*Batch: `1.4-3`.*

`Bun.spawn()`, `Bun.spawnSync()`, and `node:child_process` honor `uid` and `gid`, applying supplementary groups, group ID, and user ID before exec on POSIX and reporting `ENOTSUP` on Windows.

## Child-process IPC limitations

*Batch: `nodejs-compatibility`.*

`node:child_process` omits `proc.gid`, `proc.uid`, and the exported `Stream` class, and its IPC cannot transfer socket handles. Node-to-Bun IPC can use JSON serialization.

## Child-process stdio and detachment

*Batch: `1.4-4`.*

`node:child_process` accepts the `stdio: "overlapped"` shorthand, applies kernel backpressure to piped output, and forwards `detached` through `spawnSync()`. `Bun.spawn()` can use `Bun.file()` at descriptor 3 and above and exposes caller-supplied descriptors through `proc.stdio`.

## Clonable Node crypto keys

*Batch: `1.2.11`.*

`KeyObject` instances now use the full `SecretKeyObject`, `PublicKeyObject`, and `PrivateKeyObject` hierarchy, and both `KeyObject` and `CryptoKey` instances can be passed to `structuredClone()`. Separately, `crypto.generatePrime()` and `crypto.generatePrimeSync()` now return `ArrayBuffer` rather than `Buffer`.

```js
import crypto from "node:crypto";

const secret = crypto.generateKeySync("aes", { length: 128 });
const clone = structuredClone(secret);
console.log(secret.equals(clone)); // true

const prime = crypto.generatePrimeSync(512);
console.log(prime instanceof ArrayBuffer); // true
```

## CommonJS module metadata and built-in identity

*Batch: `1.2.6`.*

Bun now populates `module.children`, reports `module.id` as `"."` for the entry module, and preserves the `node:` prefix during resolution. An unknown prefixed built-in now throws `ERR_UNKNOWN_BUILTIN_MODULE` instead of being treated as an ordinary package name.

## CommonJS transforms for `import.meta`

*Batch: `1.3.1`.*

With `--format=cjs`, the bundler now replaces `import.meta.path`, `import.meta.dirname`, and `import.meta.file` with CommonJS-compatible equivalents based on `__filename`, `__dirname`, and `path.basename(module.filename)`. Packages using these properties no longer leave invalid `import.meta` syntax in CommonJS output.

```sh
bun build ./entry.ts --format=cjs --outfile=entry.cjs
```

## Consistent module-resolution errors

*Batch: `1.2.20`.*

Failures from `Bun.resolve()` and `Bun.resolveSync()` now consistently throw `Error` instances rather than potentially throwing raw values.

## CPU profiling through `node:inspector`

*Batch: `1.3.7`.*

Bun now implements `Profiler.enable`, `disable`, `start`, `stop`, and `setSamplingInterval` through both `node:inspector` callback sessions and `node:inspector/promises`.

```ts
import inspector from "node:inspector/promises";
const session = new inspector.Session();
session.connect();
await session.post("Profiler.enable");
await session.post("Profiler.start");
const { profile } = await session.post("Profiler.stop");
```

## Cryptography compatibility gaps

*Batch: `nodejs-compatibility`.*

`node:crypto` does not implement `secureHeapUsed()`, `setEngine()`, or `setFips()`. Software that requires OpenSSL engine or FIPS controls cannot rely on those Node APIs under Bun.

## Deterministic worker termination

*Batch: `1.4-3`.*

`await worker.terminate()` now resolves only after the worker and its nested workers have stopped, returning the exit code after messages posted before exit are delivered. No new timer, socket, or thread-pool callback is dispatched once shutdown begins.

## Diagnostics and tracing modules

*Batch: `nodejs-compatibility`.*

`node:diagnostics_channel` and `node:trace_events` are documented as fully implemented, so Node instrumentation using these standard surfaces does not require Bun-specific replacements.

## Direct `ReadableStream` consumption and subprocess input

*Batch: `1.2.18`.*

`ReadableStream` now directly provides async `.text()`, `.json()`, `.bytes()`, and `.blob()` methods. `Bun.spawn()` also accepts a `ReadableStream` as `stdin`, allowing input to be piped without buffering it first.

```ts
const input = new Blob(["hello"]).stream();
const child = Bun.spawn({ cmd: ["cat"], stdin: input, stdout: "pipe" });
console.log(await child.stdout.text());
```

## Directory-inclusive filesystem globs

*Batch: `1.2.18`.*

`fs.glob()`, `fs.globSync()`, and `fs.promises.glob()` now include matching directories by default, equivalent to `Bun.Glob` scanning with `onlyFiles: false`.

```js
import { globSync } from "node:fs";
const entries = globSync("**/*", { cwd: "/tmp/project" });
```

## ECMAScript modules in `node:vm`

*Batch: `1.2.15`.*

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

## ES module evaluation semantics

*Batch: `1.4-3`.*

The runtime's module loader now follows modern ESM evaluation ordering for dependency graphs containing top-level await, and dynamic-import resolution failures propagate according to the current ECMAScript rules.

## Eval source process metadata

*Batch: `1.2.17`.*

When Bun runs code with `-e` or `--eval`, `process._eval` now contains the evaluated source string for Node-compatible tooling that inspects it.

```sh
bun -e 'console.log(process._eval)'
```

## Expanded V8 addon compatibility

*Batch: `1.2.19`.*

The V8 C++ compatibility layer now implements core addon operations including `v8::Array::New`, `v8::Object::Get`, `v8::Object::Set`, and `v8::Value::StrictEquals`.

## Experimental `node:quic`

*Batch: `1.4-3`.*

Bun implements the experimental Node 26 `node:quic` API for listening and connecting, bidirectional and unidirectional streams, HTTP/3 and raw QUIC, datagrams, 0-RTT, path migration, stateless resets, per-SNI certificates, qlog, and keylog.

## File-watch overflow reporting

*Batch: `1.4-4`.*

When the Linux or Windows kernel watch queue overflows, `fs.watch()` emits `("change", null)` to every live watcher. Treat a null filename as a signal to rescan the watched tree rather than as a single-file change.

```ts
import { watch } from "node:fs";

watch(".", (_event, filename) => {
  if (filename === null) console.log("rescan required");
});
```

## Filesystem watchers and disposable handles

*Batch: `1.4-3`.*

Filesystem watchers support an `ignore` predicate, and `fs.promises.watch()` accepts an `AbortSignal`. Bun also implements `fs.mkdtempDisposable()` and `FileHandle.prototype.pull()`/`writer()`.

## Forked-process runtime arguments

*Batch: `1.2.17`.*

`child_process.fork()` now honors `execArgv`, passing Bun runtime flags to the child and exposing them through the child's `process.execArgv`.

```js
import { fork } from "node:child_process";

fork("./child.js", { execArgv: ["--smol"] });
```

## In-place process replacement

*Batch: `1.3.14`.*

The POSIX-only `process.execve(execPath, args, env)` replaces the current process image and never returns on success, preserving standard streams while marking other descriptors close-on-exec. It emits an experimental warning and is unavailable in workers and on Windows.

```ts
process.execve("/usr/bin/echo", ["echo", "hello"], {
  PATH: process.env.PATH,
});
```

## Inspector coverage boundary

*Batch: `nodejs-compatibility`.*

Other `node:inspector` APIs remain unavailable beyond the previously documented Profiler support.

## Low-level async hooks

*Batch: `nodejs-compatibility`.*

`node:async_hooks` implements `AsyncLocalStorage` and `AsyncResource`, but does not invoke V8 promise hooks. Low-level instrumentation that depends on those hooks is not Node-compatible.

## Module-loader compatibility

*Batch: `nodejs-compatibility`.*

Overriding `require.cache` works for both ESM and CommonJS modules, but `node:module` lacks `syncBuiltinESMExports()`, `Module#load()`, and `module.register()`. Its `_extensions`, `_pathCache`, and `_cache` internals are no-ops; use `Bun.plugin()` instead of `module.register()`.

## Modules without full compatibility guarantees

*Batch: `nodejs-compatibility`.*

`node:wasi` is only partially implemented. `node:perf_hooks` exposes its APIs, but its Node.js test suite does not pass, so packages that require exact behavior need validation.

## Negative `util.parseArgs` options

*Batch: `1.2.11`.*

`util.parseArgs()` accepts `allowNegative: true`, mapping `--no-foo` to `foo: false`; when `args` is omitted, Bun now parses `process.argv` by default.

```js
const { values } = require("util").parseArgs({
  args: ["--no-foo"],
  allowNegative: true,
  options: { foo: { type: "boolean" } },
});
console.log(values.foo); // false
```

## Node 26 VM modules

*Batch: `1.4-3`.*

`node:vm` adds `linkRequests()`, `instantiate()`, `moduleRequests`, and `hasTopLevelAwait()`, and contexts support `microtaskMode: "afterEvaluate"`. Top-level await in `SourceTextModule` now resumes correctly after suspension.

## Node filesystem write semantics

*Batch: `1.4-3`.*

`fs.write()`, `fs.writeSync()`, and `FileHandle.write()` now honor the requested string encoding. `fs.writeFile()` and `writeFileSync()` preserve existing contents when opened with non-truncating flags such as `r+`, `rs+`, or numeric `O_RDWR`.

## Node process-stream compatibility

*Batch: `1.2.1`.*

`process.stdin.ref()` and `process.stdin.unref()` are now available, and pending `process.stdout.write()` operations keep the process alive until their output is handled.

## Node-API version 10

*Batch: `1.4-3`.*

Bun reports Node-API version 10, ships Node 26 public headers, and implements the five new experimental `node_api_*` functions so addons can target the newer native API surface.

## Node-compatible filesystem globbing

*Batch: `1.2.2`.*

`node:fs` now provides `glob()` and `globSync()`, while `node:fs/promises` provides an async-iterable `glob()`. Only one pattern is currently supported; pattern arrays and the `withFileTypes` option are not yet available.

```ts
import { glob } from "node:fs/promises";

for await (const file of glob("**/*.js", { cwd: "./src" })) {
  console.log(file);
}
```

## Node-compatible filesystem stats

*Batch: `1.2.1`.*

`fs.fstatSync()` now honors `{ bigint: true }` and returns `BigIntStats`. Constructing `new fs.Stats()` also matches Node by leaving numeric fields undefined and producing invalid date fields instead of zero-valued epoch data.

```js
import fs from "node:fs";
const stats = fs.fstatSync(0, { bigint: true });
```

## Node-mode environment loading

*Batch: `1.4-2`.*

When Bun is invoked as `node` through `bun --bun`, `bunx --bun`, or a `node` symlink, it no longer auto-loads `.env*` files. Pass `node --env-file=.env script.js` when that mode still needs an environment file.

## Node.js 24 compatibility baseline

*Batch: `1.2.18`.*

Bun now reports Node.js 24.3.0 through `process.version` and `process.versions.node` and updates its reported N-API version. Native addons can therefore select prebuilt binaries targeting Node.js 24.

## Node.js 26 compatibility boundary

*Batch: `1.4-2`.*

Bun now reports Node.js 26 and native-addon module ABI `147`, so ABI-selected prebuilds need that target. The obsolete `res.writeHeader()` alias is removed in favor of `writeHead()`, and paused `readable.read()` without a size returns one buffered chunk rather than the entire buffer.

## Node.js compatibility additions

*Batch: `1.2-guide`.*

Bun can now create `node:http2` servers (enabling gRPC servers), use `node:dgram` UDP sockets, and run `node:cluster` workers. Cluster shared-port load balancing uses `reusePort`, which is only effective on Linux; `node:zlib` also gains Brotli, `node:v8` gains `getHeapSnapshot()`/`writeHeapSnapshot()`, and partial support for addons using V8's public C++ API lets more pre-N-API packages load.

## Node.js compatibility additions

*Batch: `1.2.23`.*

`node:http` servers now handle `CONNECT`, enabling HTTP proxies. `dns.resolve()` no longer passes an extra hostname to callbacks, promised A/AAAA resolutions return string arrays, and `process.report.getReport()` is now available on Windows.

## Node.js compatibility additions

*Batch: `1.4`.*

Workers now accept `resourceLimits`, `stdout`, `stderr`, and `eval`; `ws` supports the `upgrade` and `unexpected-response` events; and `socket.upgradeTLS({ isServer: true })` enables server-side STARTTLS. `node:cluster` can share listening sockets between workers, and `node:repl` and `node:domain` are now implemented.

## Non-contextified VM globals

*Batch: `1.2.19`.*

`node:vm` now supports `vm.constants.DONT_CONTEXTIFY`. Passing it to `vm.createContext()` produces a context whose `globalThis` is the same ordinary object visible to the parent.

```js
import vm from "node:vm";
const context = vm.createContext(vm.constants.DONT_CONTEXTIFY);
console.log(vm.runInContext("globalThis", context) === context); // true
```

## Other core-module omissions

*Batch: `nodejs-compatibility`.*

`node:tls` lacks `createSecurePair()`, while `node:domain` lacks `Domain` and `active`. `node:util` lacks `getCallSite()`, `getCallSites()`, `getSystemErrorMap()`, `getSystemErrorMessage()`, `transferableAbortSignal()`, and `transferableAbortController()`.

## Parent-death process cleanup

*Batch: `1.3.14`.*

`--no-orphans` makes Bun exit when its parent dies, even from `SIGKILL`, and recursively kills its own descendants on exit; nested Bun processes inherit the mode. It is available on Linux and macOS, is a no-op on Windows, and can also be set with `[run] noOrphans = true` or `BUN_FEATURE_FLAG_NO_ORPHANS=1`.

```sh
bun --no-orphans run app.ts
```

## Post-quantum cryptography

*Batch: `1.4-2`.*

WebCrypto supports ML-DSA-44/65/87 signing and ML-KEM-768/1024 encapsulation through `encapsulateBits`, `encapsulateKey`, `decapsulateBits`, and `decapsulateKey`. `node:crypto` supports the corresponding `ml-dsa-*` and `ml-kem-*` key-pair names, ML-DSA signing, and PEM, DER, PKCS#8, and `AKP` JWK key imports.

## Process compatibility gaps

*Batch: `nodejs-compatibility`.*

`process.binding()` is only partially implemented, and `process.title` is a no-op on macOS and Linux. `getActiveResourcesInfo()`, `setActiveResourcesInfo()`, `getActiveResources()`, and `setSourceMapsEnabled()` are stubs, while `process.loadEnvFile()` is not implemented.

## Process compatibility metadata and warnings

*Batch: `1.2.19`.*

`process.features.typescript` is `"transform"`, while `process.features.require_module` and `process.features.openssl_is_boringssl` are `true`. The runtime now also respects `NODE_NO_WARNINGS`.

## Process environment and warning controls

*Batch: `1.4-3`.*

Assigning to `process.env` now coerces values to strings, `structuredClone(process.env)` works, and changing `process.env.TZ` updates existing `Date` objects. Bun also implements `--no-warnings`, `--trace-warnings`, `--trace-deprecation`, `--redirect-warnings`, and `--disable-warning`.

## Process-level ref controls

*Batch: `1.2.11`.*

`process.ref(object)` and `process.unref(object)` control whether an object keeps the event loop alive. They dispatch to its `ref()`/`unref()` methods or the corresponding `Symbol.for("nodejs.ref")`/`Symbol.for("nodejs.unref")` hooks and also work with native timers.

```js
const interval = setInterval(() => {}, 1_000);
process.unref(interval);
```

## Process-wide CLI options

*Batch: `1.2.15`.*

`BUN_OPTIONS` supplies persistent arguments to every Bun command without changing scripts or `bunfig.toml`. Its value follows shell-like quoting rules and is prepended to the explicit command-line arguments.

```sh
BUN_OPTIONS="--config='./my config.toml' --silent" bun run dev.ts
```

## Pseudo-terminal subprocesses

*Batch: `1.3.5`.*

`Bun.spawn()` accepts a `terminal` option that attaches a real PTY, so interactive programs see TTY streams and can use prompts, colors, and cursor control. The spawned process exposes the terminal for input, resizing, raw-mode control, event-loop ref control, and closing; PTY support is limited to Linux and macOS.

```ts
const proc = Bun.spawn(["bash"], {
  terminal: {
    cols: 80,
    rows: 24,
    data(_terminal, data) {
      process.stdout.write(data);
    },
  },
});

proc.terminal.write("echo hello\n");
proc.terminal.resize(100, 30);
await proc.exited;
proc.terminal.close();
```

A standalone `new Bun.Terminal()` can instead be passed to multiple sequential subprocesses; it supports `await using` for automatic disposal.

## SHA-3 crypto algorithms

*Batch: `1.3.13`.*

WebCrypto and `node:crypto` support SHA3-224, SHA3-256, SHA3-384, and SHA3-512 for digests and HMAC operations. The names work with `createHash()`, `createHmac()`, `getHashes()`, `SubtleCrypto.digest()`, and HMAC signing and verification.

```ts
const digest = await crypto.subtle.digest(
  "SHA3-256",
  new TextEncoder().encode("hello"),
);
```

## Shared Node-API buffers

*Batch: `1.2.18`.*

`napi_create_buffer_from_arraybuffer` now shares the input `ArrayBuffer` memory instead of cloning it, so mutations through either view affect the same backing storage.

## Subprocess option typings

*Batch: `1.3.2`.*

The subprocess declarations now expose the runtime-supported `detached`, `onDisconnect`, and `lazy` options; `lazy` defers stdout and stderr reads until accessed. Common option shapes use `Bun.Spawn.BaseOptions`, and the older `Bun.Spawn.OptionsObject` alias is deprecated.

```ts
const child = Bun.spawn({
  cmd: ["worker"],
  detached: true,
  lazy: true,
  onDisconnect() {},
});
```

## Subprocess output limits

*Batch: `1.2.9`.*

`maxBuffer` caps subprocess output in bytes and kills the process when the cap is exceeded. It works with `Bun.spawn()`, `Bun.spawnSync()`, `node:child_process.spawn()`, and `node:child_process.spawnSync()`.

```ts
const result = Bun.spawnSync({ cmd: ["yes"], maxBuffer: 100 });
```

## Symlink-preserving module resolution

*Batch: `1.2.9`.*

Pass `--preserve-symlinks` or set `NODE_PRESERVE_SYMLINKS=1` to resolve modules from the symlink path instead of the symlink target's real path, preserving access to dependencies located beside the symlink.

## Synchronous subprocess isolation

*Batch: `1.3.2`.*

`Bun.spawnSync()` and `child_process.spawnSync()` now run on an event loop isolated from the rest of the process. JavaScript timers and microtasks no longer fire during the blocking call, bringing stdio interaction and timeout behavior in line with Node.js.

## Synthetic VM modules

*Batch: `1.2.16`.*

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

## TTY streams after standard input closes

*Batch: `1.2.22`.*

After piped `stdin` reaches EOF, an application can open and read `/dev/tty` without an `ESPIPE` error, enabling the usual pipe-then-interact TUI pattern. `tty.ReadStream` also supports `ref()` and `unref()` for event-loop control.

## Unsupported Node modules

*Batch: `nodejs-compatibility`.*

The Node-compatible `node:repl` and `node:sqlite` modules are not implemented, even though Bun provides separate native REPL and SQLite facilities.

## Utility and V8 diagnostics

*Batch: `1.4-3`.*

`node:util` adds hexadecimal colors in `styleText()`, `getCallSites()`, regular-expression highlighting, and `tty.WriteStream` support. `node:v8` adds `GCProfiler` and `isStringOneByteRepresentation()`.

## V8 addon value-type checks

*Batch: `1.3.5`.*

Bun's V8 C++ compatibility layer now implements `v8::Value::IsMap()`, `IsArray()`, `IsInt32()`, and `IsBigInt()`, allowing native Node.js addons that use those checks to run without replacing them.

## V8 serialization format

*Batch: `nodejs-compatibility`.*

`node:v8`'s `serialize()` and `deserialize()` use JavaScriptCore's wire format rather than V8's, so their serialized data is not a Node-compatible interchange format. Most other `node:v8` methods remain unavailable; use `bun:jsc` for profiling.

## Worker creation events

*Batch: `1.2.13`.*

Creating a `Worker` now emits a `"worker"` event on `process`; the listener receives the worker and can inspect properties such as `threadId`.

```js
process.on("worker", worker => console.log(worker.threadId));
```

## Worker environment data

*Batch: `1.2.13`.*

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

## Worker heap snapshots

*Batch: `1.2.15`.*

`Worker.getHeapSnapshot()` from `node:worker_threads` now captures a V8 heap snapshot for an individual worker, enabling worker-specific memory investigation.

## Worker-thread error objects

*Batch: `1.2.14`.*

An unhandled exception in a `node:worker_threads` worker now emits an actual `Error` to the worker's `"error"` listener instead of the string-only `ErrorEvent` used by Web Workers.

```js
import { Worker } from "node:worker_threads";
new Worker("./worker.js").on("error", error => {
  console.log(error instanceof Error); // true
});
```

## Worker-thread messaging and isolation

*Batch: `1.4-3`.*

`node:worker_threads` adds `postMessageToThread()` with the `workerMessage` event, `markAsUntransferable()`, `markAsUncloneable()`, `SHARE_ENV`, and worker heap, CPU, and profiling inspection. An unsettled top-level await exits a worker with code 13, `process.abort()` terminates only that worker, and the positional `postMessage(value, transferList)` overload now transfers rather than clones its entries.

## Worker-thread option gaps

*Batch: `nodejs-compatibility`.*

`node:worker_threads` workers do not support the `stdin`, `stdout`, `stderr`, `trackedUnmanagedFds`, or `resourceLimits` options. The module also lacks `markAsUntransferable()` and `moveMessagePortToContext()`.

## X25519 WebCrypto key agreement

*Batch: `1.3.13`.*

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

## Zero-filled unsafe buffers

*Batch: `1.2.1`.*

Bun now accepts Node's `--zero-fill-buffers` flag; with it enabled, allocations such as `Buffer.allocUnsafe()` contain zeros rather than arbitrary memory.

```sh
bun --zero-fill-buffers script.js
```

## Zstandard in `node:zlib`

*Batch: `1.2.17`.*

`node:zlib` now supports Zstandard compression and decompression through synchronous, callback-based, and streaming APIs.

```js
import { zstdCompressSync, zstdDecompressSync } from "node:zlib";

const compressed = zstdCompressSync(Buffer.from("hello"));
console.log(zstdDecompressSync(compressed).toString());
```
