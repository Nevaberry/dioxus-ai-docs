---
name: nodejs-knowledge-patch
description: Node.js
version: 26.5.0
license: MIT
metadata:
  author: Nevaberry
---


# Node.js Knowledge Patch

Use this skill when upgrading, reviewing, debugging, or writing modern Node.js
applications, tooling, tests, native integrations, or build configurations.

## How to use this skill

1. Determine the exact Node.js version used by the project or deployment.
2. Read the quick references below for high-impact migrations.
3. Open only the topic references relevant to the task.
4. Respect exact batch attribution: later patch and minor releases sometimes
   restore, revert, or tighten earlier behavior.
5. Feature-detect where a reference says support can be omitted from custom
   builds or differs by crypto backend.

## Reference index

| Reference | Read for |
| --- | --- |
| [CLI, Configuration, SEA, and Releases](references/cli-config-sea-and-releases.md) | Startup flags, JSON and environment configuration, watch mode, single executables, and release cadence |
| [Cryptography and Compression](references/crypto-and-compression.md) | WebCrypto, classic crypto, post-quantum algorithms, OpenSSL, Zstandard, Brotli, and zlib |
| [Diagnostics and Performance](references/diagnostics-and-performance.md) | Inspector, diagnostic channels and reports, profiling, heap statistics, and performance monitoring |
| [Filesystem, Buffers, and Streams](references/filesystem-and-streams.md) | Filesystem APIs, buffers, globs, file URLs, Node streams, and Web streams |
| [Modules, TypeScript, and WebAssembly](references/modules-and-typescript.md) | ESM, CommonJS, loader hooks, built-in TypeScript, WebAssembly, and compile caches |
| [Native Addons, Embedding, and Builds](references/native-addons-and-builds.md) | Node-API, addon ABI changes, embedders, FFI, source builds, and platform baselines |
| [Networking, HTTP, and TLS](references/networking-http-and-tls.md) | TCP, UDP, DNS, proxies, HTTP, HTTP/2, TLS, QUIC, certificates, and block lists |
| [Processes, Workers, Async Context, and Permissions](references/process-workers-and-permissions.md) | Permission Model, processes, signals, workers, async context, cloning, and Web Locks |
| [Runtime and Web Platform](references/runtime-and-web-platform.md) | Runtime semantics, deprecations, globals, events, URLs, readline, and general Web APIs |
| [SQLite](references/sqlite.md) | `node:sqlite` connections, statements, sessions, functions, extensions, and query helpers |
| [Testing and Assertions](references/testing-and-assertions.md) | `node:test`, mocking, snapshots, coverage, reporters, reruns, and deep comparison |

## Breaking changes and migrations

### Node.js 26 application migrations

- Replace `response.writeHeader()` with `response.writeHead()` and replace
  private `_stream_*` imports with public `node:stream` APIs.
- Stop passing `--experimental-transform-types`. Extensionless files inside a
  package with `"type": "module"` now follow ESM interpretation.
- Do not assume a readable combines buffered chunks: reads now return one
  buffered chunk at a time.
- Pass `authTagLength` when creating a decipher for a short GCM tag.
- Prefer `module.registerHooks()` when synchronous hooks fit; dedicated-thread
  `module.register()` now emits a runtime deprecation warning.
- Add `node_api.h` explicitly when an addon uses the full Node-API surface;
  `node.h` now includes only `node_api_types.h`.

### Node.js 25 application and toolchain migrations

- Install Corepack separately when a project depends on it; distributions no
  longer include it.
- Replace top-level filesystem access-mode aliases with `fs.constants`, use
  `fs.rm()` instead of recursive `fs.rmdir()`, and close file handles explicitly.
- Replace `SlowBuffer` with `Buffer.allocUnsafeSlow()`, avoid
  `assert.CallTracker`, use the single-message `assert.fail()` form, and await
  the promise returned by `worker.terminate()`.
- Use the public child-process `channel` property instead of `_channel`.
- Replace RSA-PSS `hash` and `mgf1Hash` options with `hashAlgorithm` and
  `mgf1HashAlgorithm`; specify XOF `outputLength` explicitly.
- Replace `response.writeHeader()` with `writeHead()` and use valid, explicit
  hostnames, TLS server names, and ports.

### Node.js 24 application migrations

- Start the Permission Model with `--permission`; the removed
  `--experimental-permission` spelling no longer works.
- Use `fs.ftruncate()` for file descriptors. Use `fs.constants` for access
  modes, and replace removed `Dirent.path` reads with `parentPath`.
- Replace `url.parse()` and the deprecated string form of `url.format()` with
  the WHATWG `URL` API.
- Do not pass an empty child-process `shell`; omit it or supply a valid shell.
- Call `node:http` classes with `new` or use their documented factories.
- Stop depending on HTTP/2 priority signaling or `options.selectPadding`.

### Node.js 23 behavior changes

- Distinct `WeakMap` and `WeakSet` instances no longer compare deeply equal.
- An out-of-bounds `Buffer.prototype.write()` offset now throws.
- Negative or `NaN` timer delays warn, and `stream.pipeline()` rejects a
  closed or destroyed destination.
- Replace `crypto.fips` with `crypto.getFips()` and `crypto.setFips()`; replace
  `fs.Dirent.path` with `parentPath`.
- Remove startup reliance on retired global-experiment opt-outs,
  `--trace-atomics-wait`, and `--experimental-default-type`.

## High-value version transitions

### Test completion and TypeScript discovery

Node.js 24.0 made `test()` and `t.test()` stop returning completion promises,
but 24.3 restored those promises and reverted automatic subtest waiting. Await
subtests when sequencing their completion.

The TypeScript discovery glob changed in 23.10 and was rolled back in 24.1.
Projects adapted to the intervening behavior should verify which tests run.

### Built-in TypeScript

- `stripTypeScriptTypes()` provides programmatic stripping.
- Supported `.ts` execution became enabled by default while still experimental,
  then type stripping became stable.
- Unsupported syntax has the dedicated
  `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` error.
- `.cts` imports use the synchronous CommonJS loader.

### Module hooks and ESM

- `module.registerHooks()` installs synchronous `resolve` and `load` hooks in
  the current thread and covers `require()`, `import`, and `createRequire()`.
- Synchronous `require(ESM)` is stable, with `--require-module` and
  `--no-require-module` controls.
- `import.meta.main` identifies a directly run ES module.
- `import defer` postpones static-module evaluation until its namespace is used.
- Native-addon ESM imports are enabled by default.

### Permission Model

- An entry point receives implicit read permission.
- Active permission flags propagate to spawned Node.js processes.
- Network and inspector grants use separate `--allow-net` and
  `--allow-inspector` controls.
- Pipe connections, pipe opening, and pipe mode changes are checked against the
  network scope.
- Symlink operations require both filesystem-read and filesystem-write grants;
  `futimes` and later `FileHandle.utimes()` are disabled under permissions.
- Audit mode reports denied access without throwing and uses distinct warning
  codes.

### Core HTTP proxies and connection lifetime

- Core `http`, `https`, and fetch clients can use proxy environment variables;
  custom agents accept `proxyEnv`.
- `http.setGlobalProxyFromEnv()` enables environment proxy handling at runtime.
- `server.keepAliveTimeoutBuffer` extends the server socket timeout, while
  `agentKeepAliveTimeoutBuffer` shortens the client reuse window.
- `shouldUpgradeCallback()` filters incoming HTTP upgrades before the
  `'upgrade'` handler.
- `ServerResponse.writeInformation()` sends arbitrary informational responses.

### SQLite defaults and query APIs

- Foreign keys are enabled by default, and double-quoted string compatibility
  is disabled; use single quotes for SQL string literals.
- SQLite defensive mode later became the default. Change it explicitly when an
  application needs the earlier policy.
- Connections support read-only mode, busy timeouts, connection-wide bigint
  reads, online backups, custom scalar and aggregate functions, and loadable
  extensions.
- Sessions are public and disposable; tagged-template stores bind interpolated
  values and cache prepared statements.
- `SQLTagStore.size` is a property, not a method.
- Custom Node.js builds may omit SQLite, so code targeting those builds must
  feature-detect `node:sqlite`.

### Files, buffers, and streams

- A `Buffer` backed by a resizable `ArrayBuffer` follows the buffer's resized
  length, and the default `Buffer.poolSize` is now 64 KiB.
- `FileHandle.readableWebStream()` always creates a byte stream and can close
  its handle with `autoClose: true`.
- `Readable.toWeb()` can create readable byte streams for BYOB consumers.
- `stream.compose()` is stable, and half-open duplex streams remain half-open
  during async iteration.
- `node:vfs` routes mounted filesystem operations but is not a security
  boundary.

### Crypto and compression

- Use `SubtleCrypto.supports()` before selecting newer algorithms on
  nonstandard builds.
- Key encapsulation, Argon2, and modern WebCrypto algorithms are available;
  later releases promote Argon2 and encapsulation/decapsulation to stable.
- Post-quantum PKCS#8 imports require seed-bearing private-key encodings, and
  later ML-KEM and ML-DSA exports default to seed-only encodings.
- Zstandard supports dictionaries; later decompression rejects truncated input
  and accepts `ArrayBuffer` dictionaries.
- `rejectGarbageAfterEnd` rejects trailing compressed data, and Web
  decompression streams reject trailing gzip members.

### Diagnostics, profiling, and tests

- CPU and heap profiling can be enabled through supported startup options, and
  workers expose per-worker CPU usage plus CPU and heap profile handles.
- Inspector network tooling progressively covers HTTP, Undici, WebSocket, and
  HTTP/2 traffic and bodies.
- Test runs support global setup, per-test timeouts, object-property mocking,
  file snapshots, failure reruns, expected failures, tags, ambient contexts,
  and test-authored log events.
- Suite-level failures set a non-zero process exit code, and failed-test reruns
  preserve retry failures.
