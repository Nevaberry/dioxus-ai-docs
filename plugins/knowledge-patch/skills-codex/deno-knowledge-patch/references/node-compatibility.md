# Node Compatibility

Use this reference for the following topic-specific compatibility details.

## `nextTick` async-hook tracking (2.5.0)

`node:async_hooks` now reports `process.nextTick()` work as `TickObject` resources, allowing Node-compatible instrumentation to follow those callbacks.

## `node:sqlite` (2.2-guide)

Deno implements the synchronous `node:sqlite` API, including `DatabaseSync`, prepared statements, and local or in-memory databases; file-backed databases need read and write permissions.

```ts
import { DatabaseSync } from "node:sqlite";

const db = new DatabaseSync("data.db");
db.exec("CREATE TABLE IF NOT EXISTS items (name TEXT)");
db.prepare("INSERT INTO items VALUES (?)").run("one");
db.close();
```

## Additional Node API surface (2.3.0)

Newly supported surface includes `FileHandle.createReadStream()` and `createWriteStream()`, `DatabaseSync.loadExtension()`, `Buffer.copyBytesFrom()`, `process.loadEnvFile()`, `util.getCallSites()`, negative options in `util.parseArgs()`, `spawnSync()` input, and the previous-value argument to `process.cpuUsage()`. Event-loop delay histograms gain `reset()`, `dns` accepts `ttl`, `stream.finished()` accepts Web streams, and SQLite databases can be forced to remain in memory.

## Additional Node runtime APIs (2.9-guide)

Node compatibility now includes `process.resourceUsage()` and `worker_threads.isInternalThread`; `AsyncLocalStorage` context is also retained across `node:net` callbacks.

## Async context in rejection handlers (2.7.0)

`AsyncLocalStorage` context is now preserved inside `unhandledRejection` handlers, so Node-compatible request or task context remains available there.

## Automatic CommonJS package detection (2.1-guide)

A `.js` file is treated as CommonJS when its nearest `package.json` has `"type": "commonjs"`; the earlier detection flag is no longer needed, and static analysis often avoids a read-permission grant for these modules.

```json
{ "type": "commonjs" }
```

## CommonJS and module syntax (2.0.0)

Deno can directly import `.cjs` files, and CommonJS `require()` can load ES modules. Import assertions are deprecated.

## CommonJS loading of ES modules (2.3.0)

When CommonJS `require()` loads an ES module, it now prefers an explicit `module.exports` export; generated ESM-to-CJS wrapper modules also expose that export. Code relying on Node's newer `require(esm)` interop therefore receives the intended value instead of only the namespace wrapper.

## CommonJS preloads (2.6-guide)

`--require` is the CommonJS counterpart to `--preload`, executing a CommonJS setup module before the main module.

```sh
deno run --require ./setup.cjs main.ts
```

## Default Node typings (2.6-guide)

`@types/node` is now included automatically, while an explicitly installed project version still takes precedence.

## Deno subcommands through Node child processes (2.9.1)

`node:child_process` can now spawn the Deno executable with Deno subcommands.

```ts
import { spawn } from "node:child_process";
spawn(Deno.execPath(), ["task", "build"]);
```

## Existing Node lockfiles and pnpm workspaces (2.9-guide)

When no `deno.lock` exists, `deno install` can seed one without re-resolving from `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, or `bun.lock`, preserving resolved versions and integrity hashes. It also detects `pnpm-workspace.yaml`, migrates its `packages`, `catalog`, and `catalogs` into `package.json` or `deno.json`, and asks for a rerun.

```sh
deno install
```

## Expanded Node API surface (2.7-guide)

New compatibility includes Zstd in `node:zlib`; `DatabaseSync.setAuthorizer()` and `SQLTagStore` in `node:sqlite`; `PerformanceObserver`; `process.constrainedMemory()`; stream `hasColors()`; `util.parseEnv()` and `process.loadEnvFile()`; `tls.setDefaultCACertificates()`; inspector open, close, and URL APIs; `node:fs` `openAsBlob`; `FileHandle.readableWebStream()` and `readv()`; the `node:test` mock API; and named-pipe listen, connect, and open support.

## Expanded Node compatibility (2.2-guide)

New surface includes `process.cpuUsage()`, file-descriptor input to `fs.readFile()` and `fs.readFileSync()`, recursive `fs.readdir()`, and `FileHandle` methods for `chmod`, `chown`, `stat`, `sync`, `truncate`, `utimes`, and `writev`. `node:http` gains the `createConnection` request option and proxy requests; crypto gains AES-CTR, arbitrary-length AES-GCM IVs, `crypto.hash()`, `X509Certificate.checkHost()`, and populated `getCiphers()` results.

`node:inspector/promises` is available, `node:v8` serializes `Float16Array`, pending async worker work keeps the event loop alive, and child processes no longer unconditionally inherit the parent environment. Changing `TZ` also updates the timezone used by JavaScript APIs.

## Expanded Node compatibility surface (2.6-guide)

Added Node surface includes `FileHandle.appendFile()` and `readLines()`, `statfs` from `node:fs/promises`, `process.ppid`, `process.seteuid()`, `setegid()`, `setuid()`, and `setgid()`, plus SQLite backup, aggregate, function, column, unknown-named-parameter, and explicit-disposal support. Advanced IPC serialization, `dns.lookupService()`, `path.matchesGlob()`, `performance.timerify()`, `util.getSystemErrorMessage()`, `ArrayBuffer` input to `crypto.timingSafeEqual()`, abortable promisified timers, and `#/` package subpath imports are also supported.

## Hoisted `node_modules` (2.8-guide)

`nodeModulesLinker` selects either the default isolated dependency layout or an npm-style flat `"hoisted"` layout for legacy tools that expect undeclared packages at the top level.

```json
{
  "nodeModulesDir": "manual",
  "nodeModulesLinker": "hoisted"
}
```

## Iterable `NodeListOf` typings (2.6.0)

`NodeListOf<T>` now declares `[Symbol.iterator]`, allowing TypeScript to type-check direct iteration of DOM query results.

## JSR packages in `node_modules` (2.9-guide)

Opt-in `jsrDepsInNodeModules` installs `jsr:` dependencies through JSR's npm-compatibility registry, materializes their complete tarballs so packages can read bundled assets and use `import.meta.dirname`, and links them under their original scoped names for Node-oriented tools. It is off by default; without it, JSR dependencies retain their HTTPS-backed resolution behavior.

```json
{
  "jsrDepsInNodeModules": true
}
```

## Mock-timer reset behavior (2.9.1)

In `node:test`, `mock.reset()` now resets `MockTimers` as well as the other mocks, returning mocked timer state to normal.

## Named process-report export (2.9.1)

The Node compatibility layer exposes `report` as a named export from `node:process`.

```ts
import { report } from "node:process";
const diagnostic = report.getReport();
```

## Node 26 baseline and bare built-ins (2.9-guide)

Deno now targets and reports Node 26.3.0 and N-API 10. Bare built-in imports such as `import "fs"` resolve to `node:fs` without a flag and cannot be shadowed by `node_modules`, although explicit `deno.json` imports and `package.json` dependency mappings still take precedence.

## Node compatibility additions (2.0.0)

The `process` global is available everywhere. Added Node surface includes `rootCertificates` in `node:tls`, `Buffer.transcode()`, `promises` from `node:timers`, `FileHandle.writeFile()`, `node:wasi`, and detached child processes.

## Node diagnostics and profiling (2.8.0)

New diagnostics surface includes `perf_hooks.createHistogram()`, active-process-resource APIs, `v8.GCProfiler`, `v8.queryObjects()`, `util.queryObjects()`, and the `v8.startupSnapshot` API.

## Node event-loop delay monitoring (2.1.0)

`node:perf_hooks` now implements `monitorEventLoopDelay()`, so Node-targeted diagnostics can collect event-loop latency histograms under Deno.

```ts
import { monitorEventLoopDelay } from "node:perf_hooks";

const delay = monitorEventLoopDelay();
delay.enable();
await new Promise((resolve) => setTimeout(resolve, 10));
delay.disable();
console.log(delay.mean);
```

## Node executable shim (2.9-guide)

If a project tool invokes `node` but no real Node executable is installed, Deno places a forwarding shim on `PATH` and translates Node CLI arguments. A real Node installation is never shadowed, and `DENO_DISABLE_NODE_SHIM=1` disables the shim.

## Node file-reading options (2.6.0)

`FileHandle.readFile()` now honors its abort signal, while `fs.readFile()` and `fs.readFileSync()` respect the supplied `flag` option.

## Node globals in application code (2.4-guide)

`Buffer`, `global`, `setImmediate`, and `clearImmediate` are now always exposed to user code as well as npm dependencies; `--unstable-node-globals` is no longer needed for them.

## Node host architecture metadata (2.7.0)

`process.config.variables.host_arch` is now populated for Node-compatible code that inspects the architecture used to build the runtime.

## Node module and VM APIs (2.8.0)

The compatibility layer implements the `node:module` `SourceMap` API and compile-cache APIs, including `module.enableCompileCache()`. It also adds `vm.SourceTextModule` support for `microtaskMode: "afterEvaluate"`, the VM linking and instantiation APIs, and the `vm.SyntheticModule` constructor.

## Node module loader hooks (2.8-guide)

`node:module` implements synchronous `module.registerHooks()` callbacks for custom resolution and loading; preload a hook module with `--import`, and the hooks also work in compiled executables. Node's deprecated `module.register()` is intentionally unavailable.

```ts
import module from "node:module";

module.registerHooks({
  load(url, context, nextLoad) {
    if (!url.endsWith(".css")) return nextLoad(url, context);
    return {
      format: "module",
      source: `export default ${JSON.stringify(Deno.readTextFileSync(new URL(url)))}`,
      shortCircuit: true,
    };
  },
});
```

```sh
deno run --allow-read --import ./loader.ts main.ts
```

## Node worker and IPC compatibility (2.8.0)

`node:worker_threads` adds `postMessageToThread()`, and `KeyObject` values can be cloned through `MessagePort`. `node:cluster` now works on Unix, while IPC can pass `dgram.Socket` handles plus `net.Socket` and `net.Server` handles to child processes on Unix.

## Node-aware built-in tools (2.0-guide)

`deno lint` includes Node-specific rules and quick fixes, `deno test` can run `node:test` tests, and `deno task` can execute scripts from `package.json`.

## Node-compatible edge-case behavior (2.6.0)

Invalid input to `url.domainToASCII()` now returns an empty string, hex decoding with `Buffer.from()` stops at the first non-hex character, and `assert.deepStrictEqual()` correctly handles boxed `Number` values. `process.argv` contains only strings, `server.address().family` is a string, and `process.stdin.isTTY` is writable.

## Node-compatible timer globals (2.5-guide)

The reintroduced `--unstable-node-globals` flag switches `setTimeout`, `setInterval`, and their clear functions from Web-style numeric IDs to Node-style timer objects with methods such as `ref()` and `unref()`. `DENO_COMPAT=1` selects the same timer behavior.

```sh
deno run --unstable-node-globals main.ts
```

## Node-project compatibility (2.0-guide)

Deno 2 can run ESM Node projects using `package.json`, `node_modules`, npm workspaces, and Node-API native addons. Node programs and imported npm modules still run under Deno's opt-in permission model, and `deno lint --fix` can repair minor compatibility syntax issues.

## Node-style timers by default (2.6.0)

Global `setTimeout()` and `setInterval()` now return Node-compatible timer objects by default rather than Web-style numeric IDs. Code can call methods such as `unref()` without enabling `--unstable-node-globals`, but code that assumes timer handles are numbers must be updated.

```ts
const timer = setTimeout(() => {}, 1_000);
timer.unref();
```

## npm and CommonJS resolution (2.2-guide)

`.npmrc` is now discovered in both the home and project directories, and the repurposed `--unstable-detect-cjs` flag is an explicit fallback when automatic CommonJS detection is insufficient. Workspace-member imports accept `workspace:^` and `workspace:~` constraints, and TypeScript inside npm packages is handled for type checking only.

## npm type resolution (2.3.0)

Type checking npm dependencies now understands `types@` export conditions and `typesVersions`, preventing their version-specific declarations from being missed.

## Opt-in Node globals and compatibility surface (2.1-guide)

`--unstable-node-globals` exposes `Buffer`, `global`, `setImmediate`, and `clearImmediate` to application code. Added compatibility includes `node:module`'s `findSourceMap`, `process.getBuiltinModule()`, `node:zlib`'s `crc32()`, `net.createConnection({ autoSelectFamily: true })`, and async-iterable `fetch` bodies; npm packages and tasks also receive `npm_config_user_agent`.

```sh
deno --unstable-node-globals main.js
```

## Removed nonstandard promises API (2.7.0)

The nonstandard `fstat` export has been removed from `node:fs/promises`; open the file and call `FileHandle.stat()` instead.

```ts
import { open } from "node:fs/promises";

const file = await open("data.bin");
const stats = await file.stat();
await file.close();
```

## Reusable SQLite statement iterators (2.6.0)

Each call to `StatementSync.iterate()` now resets its completion state, so the same prepared statement can be iterated more than once.

## Synchronous Node loader hooks (2.9.0)

Synchronous `module.registerHooks()` resolve hooks now apply to nested imports, and ESM load hooks support import attributes and custom module types. A hook registration may omit either `resolve` or `load`.

## Timer and standard-library typings (2.8.0)

Timer handles are now typed as `NodeJS.Timeout`, matching the Node-style objects returned by the default timers. The bundled types also expose `Math.sumPrecise()` and `Intl.Locale.prototype.variants`.
