---
name: nodejs-knowledge-patch
description: Node.js 23.0.0–26.5.0 compatibility. Use for Node.js work.
license: MIT
version: 26.5.0
metadata:
  author: Nevaberry
---

# Node.js Knowledge Patch

Baseline: Node.js through 22.x LTS. Covered range: 23.0.0 through 26.5.0, plus the release-schedule update published 2026-07-12.

Use this patch to account for behavior added, changed, deprecated, or removed after the baseline. Match guidance to the exact deployed release line: several APIs changed more than once across Node.js 23–26.

## Reference index

| Reference | Topics |
| --- | --- |
| [modules-and-typescript.md](references/modules-and-typescript.md) | ESM and CommonJS interop, loader hooks, package resolution, compile caches, built-in TypeScript, VM modules, WebAssembly |
| [testing-and-assertions.md](references/testing-and-assertions.md) | `node:test`, assertions, mocks, snapshots, discovery, coverage, reporters |
| [filesystem-and-streams.md](references/filesystem-and-streams.md) | Filesystem migrations, paths, directories, globs, watches, buffers, Node streams, Web streams, VFS |
| [networking-http-and-tls.md](references/networking-http-and-tls.md) | TCP, UDP, DNS, HTTP/1, HTTP/2, QUIC, proxies, TLS, CA stores |
| [crypto-and-compression.md](references/crypto-and-compression.md) | Classic crypto, WebCrypto, post-quantum keys, hashing, password derivation, zstd, Brotli, zlib |
| [sqlite.md](references/sqlite.md) | Connections, statements, sessions, tagged templates, functions, extensions, backups, build options |
| [diagnostics-and-performance.md](references/diagnostics-and-performance.md) | Inspector, diagnostics channels, reports, CPU and heap profiling, performance metrics |
| [process-workers-and-permissions.md](references/process-workers-and-permissions.md) | Processes, worker threads, async context, locks, signals, Permission Model |
| [runtime-and-web-platform.md](references/runtime-and-web-platform.md) | V8 and language features, Web globals, storage, events, URLs, utilities, REPL |
| [cli-config-sea-and-releases.md](references/cli-config-sea-and-releases.md) | CLI flags, JSON config, `.env`, watch mode, SEA, LTS and Alpha policy |
| [native-addons-and-builds.md](references/native-addons-and-builds.md) | Build requirements, platform support, addon ABI, Node-API, embedding, FFI |

## Apply the patch

1. Identify the exact Node.js version and whether it is an official or custom build.
2. Read the breaking-change sections below before changing code or dependencies.
3. Open every indexed reference relevant to the task; the quick reference intentionally omits lower-frequency details.
4. Preserve version guards when supporting multiple release lines. Do not infer availability only from a major version when a minor release introduced or reverted behavior.
5. Feature-detect optional build components such as `node:sqlite`, QUIC, and experimental surfaces.

## Breaking changes and deprecations

### Migrating to Node.js 23

- Replace removed `process.assert()` with `assert.ok()` and removed legacy `util.is*()` helpers with language checks, `Buffer.isBuffer()`, or `util.types` predicates.
- Replace removed `zlib.bytesRead` with `zlib.bytesWritten`; stop passing the removed fetch, global WebCrypto, and `CustomEvent` opt-out flags.
- Validate `Buffer.write()` offsets: an out-of-bounds starting offset now throws instead of producing a zero-byte write.
- Expect distinct `WeakMap` and `WeakSet` instances to compare unequal, dependent abort signals to update before source listeners, and stream cancellation to retain the abort reason.
- Read `StatementSync.sourceSQL` and `expandedSQL` as properties, not methods. Account for SQLite foreign keys being enabled and double-quoted string literals being disabled by default.
- Request TAP explicitly when tooling consumes it; the `spec` test reporter is the default even when output is not a TTY.

### Migrating to Node.js 24

- Replace `Dirent.path` with `Dirent.parentPath`, descriptor calls to `fs.truncate()` with `fs.ftruncate()`, and top-level filesystem access constants with `fs.constants`.
- Replace removed `tls.createSecurePair()` and `tls.Server.prototype.setOptions()`; migrate from runtime-deprecated `url.parse()` to `URL`.
- Keep using `SlowBuffer` only as a temporary compatibility measure in 24.x; it remains present but runtime-deprecated after the 24.0.1 reversal.
- Do not use HTTP/2 priority signaling or `selectPadding`; Node.js 24 removed both after the underlying implementation dropped support.
- Handle `fs.Dir.read()` failures asynchronously and explicitly close directory handles rather than relying on garbage collection.
- Account for the 24.0.0 test return-value change only on that range: 24.3.0 restored completion promises from `test()` and `t.test()`.
- Upgrade past 24.4.0 for the RapidHash HashDoS and Windows reserved-name path-normalization fixes.

### Migrating to Node.js 25

- Replace removed `SlowBuffer`, recursive `fs.rmdir()`, top-level filesystem access constants, `assert.CallTracker`, and the legacy multi-argument `assert.fail()` form.
- Explicitly close every `FileHandle`; garbage collection no longer closes leaked handles. Replace removed stream `open()` methods with new streams and their `open` events.
- Await `worker.terminate()`; its callback form is removed. Replace the removed `multipleResolves` process event with other diagnostics.
- Read GC data from `PerformanceEntry.detail.kind` and `.flags`; the old direct accessors are removed.
- Omit falsy hostnames from `dns.lookup()` calls and do not put IP addresses in TLS `servername`.
- Specify `outputLength` for SHAKE hashes, use `hashAlgorithm` and `mgf1HashAlgorithm` for RSA-PSS generation, and migrate away from `ECDH.setPublicKey()`.
- Treat distinct promises as unequal in deep comparisons; treat invalid dates as equal unless their own properties differ.

### Migrating to Node.js 26

- Supply `authTagLength` for short GCM tags; DEP0182 is end-of-life.
- Replace removed `response.writeHeader()` with `response.writeHead()` and private `_stream_*` imports with `node:stream`.
- Stop passing `--experimental-transform-types`; extensionless files inside `"type": "module"` packages now follow ESM interpretation.
- Do not depend on readable streams coalescing buffered chunks: reads now preserve one buffered chunk at a time.
- Expect `util.inspect()` and snapshots to identify proxies explicitly.
- Include `node_api.h` directly when an addon needs the complete Node-API surface; `node.h` no longer includes it transitively.
- Account for seed-only PKCS#8 exports of ML-KEM and ML-DSA private keys and added OpenSSL detail on asynchronous crypto errors.

## High-use module and TypeScript changes

- Use stable JSON import attributes:

```js
import config from './config.json' with { type: 'json' };
```

- Use stable `import.meta.dirname` and `import.meta.filename`, and guard direct execution with `import.meta.main`.
- Use `module.registerHooks()` for synchronous in-thread resolve/load hooks that must cover both `require()` and `import`.
- Migrate from dedicated-thread `module.register()` where possible: it is deprecated in 25.9.0 and runtime-deprecated in 26.0.0.
- Use stable `require(esm)` in 25.4.0+, with `--require-module` or `--no-require-module` for explicit control.
- Use `module.enableCompileCache({ directory, portable: true })` for caches that move with an application.
- Treat built-in TypeScript as type stripping, not type checking. Catch `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` for syntax that requires transformation.
- Use package `#/` imports in 25.4.0+ and deferred static imports in 26.4.0+:

```js
import defer * as feature from './feature.js';
feature.run();
```

## Permission Model and process isolation

- Enable stable restrictions with `--permission`; grant filesystem, addon, network, and inspector access explicitly.

```console
node --permission --allow-fs-read=./config \
  --allow-net=api.example.com app.js
```

- Do not add the entry point to `--allow-fs-read` on 24.2.0+; it receives implicit read permission.
- Expect active permission flags to propagate to spawned Node.js children on 24.4.0+.
- Expect permission checks on pipe connections, pipe mode changes, `realpath.native()`, affected promise filesystem paths, symlink operations, and diagnostic-report paths in the documented security releases.
- Use `process.permission.has('addon')` before loading native addons in restricted processes.
- Use `process.execve()` for in-place process replacement and await worker disposal or termination.

## Test runner and assertions

- Use stable mock timers, test plans, snapshots, isolation, and `assert.partialDeepStrictEqual()` on releases where they have graduated.
- Use `TestContext.waitFor()`, `t.assert.fileSnapshot()`, and registered custom assertions instead of rebuilding their control flow.
- Configure global setup and teardown with `--test-global-setup`.
- Pass `env` to programmatic `run()` for per-run environments; use its coverage, `cwd`, `argv`, and summary-event controls as needed.
- Migrate module mocks in 25.9.0 from `defaultExport` and `namedExports` to one `exports` object:

```js
t.mock.module('./dependency.mjs', {
  exports: { default: defaultMock, named: namedMock },
});
```

- Expect suite-level errors to set a non-zero exit code. Use expected-failure cases and failed-test reruns when supported.

## SQLite

- Open `node:sqlite` without the old startup flag, but feature-detect it because custom builds can omit SQLite.
- Choose connection behavior explicitly when compatibility matters:

```js
const db = new DatabaseSync('app.db', {
  readOnly: false,
  timeout: 5_000,
  readBigInts: true,
});
```

- Expect foreign-key enforcement, disabled double-quoted string literals, and—by 25.5.0—defensive mode by default.
- Use `iterate()`, `columns()`, return-array mode, numbered parameters, typed-array bindings, and connection-wide bigint reads as appropriate.
- Prefer `DatabaseSync.createTagStore()` for cached parameterized template queries.
- Use disposable exported sessions, changeset conflict types, online backup, authorization callbacks, custom scalar and aggregate functions, and explicit extension entry points where needed.

## Networking, HTTP, and TLS

- Enable environment proxies for built-in `fetch()` and core HTTP clients with `NODE_USE_ENV_PROXY=1` or `--use-env-proxy`; use `setGlobalProxyFromEnv()` for programmatic global activation.
- Configure server and agent keep-alive timeout buffers to avoid edge-of-expiry socket reuse.
- Use raw alternating header arrays where HTTP/2 request, response, push, or trailer APIs support them.
- Treat `headersDistinct` and `trailersDistinct` as null-prototype objects in 25.8.2+; inspect them with `Object.hasOwn()`.
- Use `shouldUpgradeCallback` to select upgrade requests and `writeInformation()` for arbitrary informational responses.
- Use system CAs with `--use-system-ca` or `NODE_USE_SYSTEM_CA=1`; inspect and replace default CA sets through the TLS APIs when required.
- Account for OpenSSL security level 2, stricter SNI and hostname validation, session-to-host binding, and certificate compression support.

## Crypto and compression

- Prefer feature detection with `SubtleCrypto.supports()` for modern WebCrypto algorithms.
- Use built-in Argon2, ML-KEM encapsulation/decapsulation, ML-DSA and SLH-DSA signatures, SHA-3/SHAKE, KMAC, AES-OCB, and ChaCha20-Poly1305 only on supporting versions.
- Pass identical context bytes to context-aware signing and verification operations.
- Migrate classic crypto calls away from WebCrypto `CryptoKey` inputs where deprecated; use supported raw and JWK formats where available.
- Set `outputLength` for XOF, cSHAKE, KMAC, TurboSHAKE, and KangarooTwelve operations as documented.
- Use zstd dictionaries when applicable and set `rejectGarbageAfterEnd` when trailing compressed data must be rejected.

## Filesystem, streams, and resource management

- Use `using` and `await using` for disposable directories, workers, readline interfaces, event-loop histograms, SQLite sessions, and `AsyncLocalStorage` where supported.
- Use `FileHandle.readableWebStream({ autoClose: true })` when the stream owns the handle; expect a byte stream and a `Uint8Array` BYOB request view.
- Preserve the primary pipeline failure: later aborts no longer replace an existing pipeline error in 25.9.0+.
- Pass a reusable destination buffer to `readFile()` in 26.4.0+ when allocation control matters.
- Treat `node:vfs` as routing, never as a security boundary.

## Diagnostics and performance

- Enable CPU and heap profiling through `NODE_OPTIONS`; use `${pid}` in profile names for concurrent processes.
- Use per-worker CPU usage, CPU profiles, and heap profiles to isolate worker behavior.
- Use `--heap-snapshot-on-oom`, `--max-heap-size`, percentage old-space limits, and precise inspector coverage where appropriate.
- Subscribe to HTTP, HTTP/2, and Web Lock diagnostics channels instead of patching core calls.
- Account for event-loop delay sampling once per loop iteration and the new minor mark-sweep GC classification in 26.5.0.

## Runtime and release planning

- Use `Temporal`, `Map.getOrInsert()`, `Map.getOrInsertComputed()`, and `Iterator.concat()` on 26.0.0+.
- Use direct `Uint8Array` base64 and hex conversion on 25.0.0+.
- Feature-detect `localStorage`: it throws without a configured path in 25.2.0 but returns `undefined` in 26.0.0+.
- Plan for the annual all-LTS cycle beginning with 27.x: Alpha runs October–March, Current ships in April, and LTS begins in October.
- Add Alpha releases to library CI for compatibility testing, but do not deploy them to production.
