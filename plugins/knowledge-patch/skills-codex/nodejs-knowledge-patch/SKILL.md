---
name: nodejs-knowledge-patch
description: Node.js
version: 26.5.0
license: MIT
metadata:
  author: Nevaberry
---


# Node.js Knowledge Patch

Use this skill when implementing, reviewing, debugging, testing, building, or
upgrading JavaScript or TypeScript that depends on recent Node.js behavior.
Start with the quick references below, then open the topic file that matches the
work. Treat patch-release corrections and security-release instructions as
version-specific; do not generalize a transient behavior across a release line.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI, configuration, SEA, and releases](references/cli-config-sea-and-releases.md) | Startup flags, JSON configuration, watch mode, SEA, release cadence, trust and security releases |
| [Cryptography and compression](references/crypto-and-compression.md) | Classic crypto, WebCrypto, TLS roots, post-quantum algorithms, zlib, Zstandard |
| [Diagnostics and performance](references/diagnostics-and-performance.md) | Inspector, profiles, reports, tracing, heap and event-loop metrics, console and call sites |
| [Filesystem, buffers, and streams](references/filesystem-and-streams.md) | Filesystem APIs, Buffers, stream semantics, Web streams, VFS, Blob text |
| [Modules, TypeScript, and WebAssembly](references/modules-and-typescript.md) | ESM and CommonJS, hooks, TypeScript stripping, JSON and text imports, VM modules, WebAssembly |
| [Native addons and builds](references/native-addons-and-builds.md) | Node-API, addon ABI, source-build requirements, embedders, FFI |
| [Networking, HTTP, and TLS](references/networking-http-and-tls.md) | TCP, UDP, DNS, proxies, HTTP/1, HTTP/2, TLS, QUIC, WebSocket inspection |
| [Processes, workers, async context, and permissions](references/process-workers-and-permissions.md) | Process replacement, workers, structured clone, AsyncLocalStorage, signals, locks, Permission Model |
| [Runtime and Web Platform](references/runtime-and-web-platform.md) | Runtime removals, equality, events, URLs, Temporal, Web Storage, serialization, globals |
| [SQLite](references/sqlite.md) | Connections, statements, sessions, functions, extensions, tagged templates, VFS-related caution |
| [Testing and assertions](references/testing-and-assertions.md) | Test discovery and execution, mocks, snapshots, coverage, reporters, assertions and diffs |

## Breaking changes and required migrations

### Use public replacements for removed APIs

- Replace `process.assert()` and `zlib.bytesRead`; they were removed in
  23.0.0. Use `crypto.getFips()` and `crypto.setFips()` instead of the
  runtime-deprecated `crypto.fips`, and use `Dirent.parentPath` instead of the
  deprecated `Dirent.path`.
- In 24.0.0, use `fs.ftruncate()` for descriptors and `fs.constants` for access
  constants. `Dirent.path`, `tls.createSecurePair()`,
  `tls.Server.prototype.setOptions()`, and private outgoing-message header
  fields are removed; `url.parse()` is runtime-deprecated.
- In 25.0.0, use `fs.rm()` instead of recursive `fs.rmdir()`, close file handles
  explicitly, use `Buffer.allocUnsafeSlow()` instead of `SlowBuffer`, use the
  promise returned by `worker.terminate()`, and use the public child-process
  `channel` property. Corepack is no longer included in distributions.
- In 26.0.0, replace `response.writeHeader()` with `writeHead()` and private
  `_stream_*` imports with public `node:stream` APIs. Pass `authTagLength` for
  short GCM tags and stop passing `--experimental-transform-types`.

### Respect changed failure and comparison behavior

- Out-of-bounds `Buffer.prototype.write()` throws from 23.0.0. Zlib writes with
  out-of-bounds buffers throw in 22.23.2, and compressed-data decoders gain
  stricter trailing or truncated-input handling in 26.5.0 and 26.7.0.
- `stream.pipeline()` rejects an already closed or destroyed destination from
  23.0.0. From 25.9.0, a substantive pipeline failure takes precedence over a
  later abort. From 26.0.0, readable consumers must not depend on coalesced
  buffered chunks.
- Deep strict equality compares weak collections and promises by identity.
  Invalid dates compare equal but retain own-property comparison. Distinct
  missing and explicit-`undefined` error causes compare unequal.
- `Buffer.allocUnsafe()` was accidentally zero-filled in 24.11.0; 24.11.1
  restores uninitialized behavior. Use `Buffer.alloc()` whenever zero filling
  is required.

### Update module and TypeScript launch behavior

- The `--experimental-default-type` option is removed in 23.4.0. The
  `--experimental-transform-types` option is removed in 26.0.0.
- Type stripping is enabled by default in 23.6.0, stops warning in 24.3.0, and
  is stable in 25.2.0. It still covers only erasable syntax; unsupported syntax
  reports `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`.
- Synchronous `require(ESM)` is stable in 25.4.0 and can be controlled with
  `--require-module` or `--no-require-module`. Dedicated-thread
  `module.register()` becomes documentation-deprecated in 25.9.0 and emits a
  runtime warning in 26.0.0; prefer `module.registerHooks()` when synchronous
  hooks are suitable.
- Extensionless files in a package with `"type": "module"` follow ESM
  interpretation from 26.0.0. `.cts` imports use the synchronous CommonJS
  loader from 24.10.0.

### Update Permission Model launchers

- Use `--permission`; `--experimental-permission` is removed in 24.0.0.
- Entry files receive implicit read permission from 24.2.0. Parent permission
  flags propagate to spawned Node processes from 24.4.0.
- Network and inspector access require separate `--allow-net` and
  `--allow-inspector` grants from 25.0.0. Pipe connections and operations are
  also covered by network permission in 25.3.0 and 26.3.1.
- Symlink creation requires read and write grants, `futimes` and
  `FileHandle.utimes()` are disabled under the model, and report or trace-event
  destinations require write permission. Permission-audit mode in 26.7.0
  warns with unique codes instead of throwing for denied access.

### Account for platform and addon baselines

- ABI-dependent addons must match `NODE_MODULE_VERSION` 131 for 23.x, 137 for
  24.x, 141 for 25.x, and 147 for 26.x.
- Node 23 removes 32-bit Windows and pre-Windows-10 experimental support and
  builds as C++20. Node 24 changes Windows source builds to ClangCL and removes
  Python 3.8 support. Node 25 requires Clang 19 and Xcode 16.4 on macOS builds.
- Node 26 requires GCC 13.2, drops Python 3.9, Power8, and IBM z13, and requires
  Rust 1.86 by 26.7.0. Addons needing the complete Node-API surface must include
  `node_api.h` explicitly.

## High-value runtime and platform features

### Modules, configuration, and executables

- Use `module.registerHooks()` for synchronous in-thread `resolve` and `load`
  hooks across `require()`, `import`, and `createRequire()`. Registrations are
  disposable in 26.7.0.
- JSON configuration begins behind experimental config-file flags in 23.10.0,
  gains namespaces, watch, permission, and test settings over later releases,
  and accepts an empty selected configuration in 24.19.0. Configuration files
  are trusted input; Node does not sanitize or validate their contents.
- Build a single executable directly with `node --build-sea` from 25.5.0.
  SEA configuration supports baked-in `execArgv`, controlled runtime argument
  extension, and ESM code caches; inspector flags work in packaged executables.
- `import.meta.main` reports direct execution, `findPackageJSON()` locates a
  relevant manifest, and deferred imports use `import defer` in 26.4.0.

### Networking and security

- Enable environment proxies for core HTTP clients with
  `NODE_USE_ENV_PROXY=1`, `--use-env-proxy`, a custom agent's `proxyEnv`, or
  `http.setGlobalProxyFromEnv()`.
- Use `net.BlockList` for connection-level TCP filtering, UDP filtering, and
  persistent rule files. It reaches release-candidate stability in 26.4.0.
- HTTP servers and agents expose keep-alive timeout buffers. HTTP/2 supports
  raw alternating header arrays, graceful shutdown, extensive diagnostics
  channels, and inspector traffic and body visibility.
- Use `tls.getCACertificates()` to inspect CA sets and
  `tls.setDefaultCACertificates()` to replace the default. Include the current
  defaults explicitly when the intent is to extend rather than replace them.

### Cryptography and compression

- Modern crypto support includes ML-DSA, ML-KEM encapsulation, SLH-DSA,
  Argon2, KMAC, SHA-3/SHAKE, AES-OCB, ChaCha20-Poly1305, TurboSHAKE, and
  KangarooTwelve. Use `SubtleCrypto.supports()` where availability can vary by
  build.
- Ed448, ML-DSA, and Ed25519 signatures can carry an application context; the
  verifier must receive the same bytes. ML-KEM and ML-DSA PKCS#8 imports need a
  seed, and their 26.0.0 exports default to a seed-only representation.
- Zstandard supports dictionaries and later `ArrayBuffer` dictionaries; use
  the same dictionary for decompression. Web compression streams support
  Brotli, while Web decompression rejects trailing gzip members in 26.5.0.

### Files, streams, and databases

- Prefer explicit resource management for directories, temporary directories,
  workers, event-loop histograms, readline interfaces, `AsyncLocalStorage`,
  SQLite sessions, and synchronous module-hook registrations where supported.
- File-handle Web streams are byte streams and can own their handle with
  `autoClose`. `Readable.toWeb()` supports BYOB-compatible byte streams, and
  `node:stream/consumers` exposes `bytes()`.
- `node:vfs` routes `node:fs/promises` calls through mounted filesystems. It is
  not a sandbox or permission boundary.
- SQLite defaults include foreign keys on, double-quoted string compatibility
  off, and defensive mode on in 25.5.0. Connections support read-only mode,
  busy timeouts, connection-wide BigInt reads, authorizers, sessions, tagged
  templates, custom and aggregate functions, and online backups.

### Tests and diagnostics

- Await `test()` and `t.test()` completion promises when sequencing subtests;
  24.3.0 restores those promises after the 24.0.0 behavior change.
- Mock timers and snapshots are stable. Tests can wait for conditions, register
  custom assertions, mock object properties and modules, mark expected
  failures, tag tests, and obtain the ambient context with `getTestContext()`.
- Coverage supports custom globs, source maps, unexecuted-file inclusion, and
  TypeScript erased-line filtering. Source-mapped coverage requires
  `--enable-source-maps`.
- Profile the process through startup flags or `NODE_OPTIONS`, and profile an
  individual worker with `cpuUsage()`, `startCpuProfile()`, or
  `startHeapProfile()`. Inspector network tooling covers core HTTP, HTTP/2,
  Undici, and initial WebSocket and storage inspection.

## Release and security handling

- Do not rely on a documented temporary regression across patch releases.
  Notable corrections include 23.11.1 async-crypto error handling, 24.4.1 V8
  HashDoS and Windows path normalization, 24.13.1 Permission Model and runtime
  hardening, and 24.14.1 filesystem, HTTP, WebCrypto, and HTTP/2 hardening.
- The 24.x Krypton LTS line receives updates through April 2028.
- Beginning with 27.x, each line spends six months in Alpha, six months as
  Current, and 30 months in LTS. Alpha builds are signed, tagged, and tested but
  may contain semver-major and API changes; use them for early compatibility
  testing rather than production.
- Release-verification keyrings must include Stewart X Addison's Ed25519 key,
  fingerprint `655F3B5C1FB3FA8D1A0CA6BDE4A7D232B936D2FD`, for future releases that
  use it.
