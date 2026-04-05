# Breaking Changes, Deprecations & Platform Support

## Major Breaking Changes by Version

### v23

- `require(esm)` enabled by default (may surface `ERR_REQUIRE_ASYNC_MODULE` in existing code)
- 32-bit Windows support removed
- Windows < 10 experimental support dropped
- `zlib.bytesRead` removed
- `process.assert` removed
- `--trace-atomics-wait` flag removed (EOL)
- `--no-experimental-global-customevent`, `--no-experimental-fetch`, `--no-experimental-global-webcrypto` flags removed
- All `util.isXxx()` legacy functions moved to EOL
- Piping to closed/destroyed stream in `pipeline()` now throws
- Negative or NaN delay in `setTimeout`/`setInterval` emits a warning
- Writing beyond buffer now throws (was silent)
- GCC minimum version bumped to 12.2

### v24

- `dirent.path` property removed (use `dirent.parentPath`)
- `tls.createSecurePair` removed
- `http.OutgoingMessage._headers` and `._headersList` private properties removed
- `fs.F_OK`, `fs.R_OK`, `fs.W_OK`, `fs.X_OK` removed from `fs` top-level (use `fs.constants`)
- `fs.truncate()` with file descriptor removed (use `fs.ftruncate`)
- Test runner: `test()` and `t.test()` no longer return promises (subtests auto-awaited)
- `AsyncLocalStorage` defaults to `AsyncContextFrame` (behavioral change)
- `url.parse()` runtime-deprecated (use WHATWG `URL`)
- `--experimental-permission` renamed to `--permission`
- `NODE_MODULE_VERSION` bumped to 137
- macOS minimum version bumped to 13.5
- Xcode minimum bumped to 16.1
- Python 3.8 build support dropped
- PowerPC 32-bit support removed
- s390 32-bit support removed
- armv7 downgraded to experimental
- MSVC removed; ClangCL required on Windows
- npm 11 bundled (major version bump)

### v25

- Corepack removed from Node.js distribution entirely
- Web Storage (`localStorage`/`sessionStorage`) enabled by default
- `NODE_MODULE_VERSION` bumped to 141
- Minimum Clang version bumped to 19
- Xcode minimum bumped to 16.4
- `--allow-net` and `--allow-inspector` permission flags added
- `ErrorEvent` exposed as global

## Deprecation Timeline

### File System

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `fs.Stats` constructor | v22 (runtime) | -- |
| `dirent.path` | v23 (runtime) | v24 (removed) |
| `fs.existsSync` invalid args | v24 (runtime) | -- |
| `fs.F_OK/R_OK/W_OK/X_OK` on `fs` | v24 (deprecated) | v25 (removed) |
| `fs.FileHandle` close-on-GC | -- | v25 (EOL) |
| `fs.rmdir` recursive option | -- | v25 (EOL) |
| `fs.ReadStream/WriteStream.open()` | -- | v25 (EOL) |
| `fs.truncate()` with fd | -- | v24 (removed) |

### Crypto & TLS

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `crypto.createCipher/Decipher` | -- | v22 (EOL) |
| `crypto.Hash/Hmac` constructors | v22 (runtime) | -- |
| `crypto.fips` | v23 (runtime) | -- |
| `tls.createSecurePair` | -- | v24 (removed) |
| `tls.Server.setOptions()` | -- | v24 (EOL) |
| `ECDH.setPublicKey()` | v25 (runtime) | -- |
| `hash`/`mgf1Hash` options | -- | v25 (EOL) |
| `shake128/256` default length | v25 (runtime) | -- |
| TLS IP-address servername | -- | v25 (EOL) |

### URL & HTTP

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `url.parse()` | v24 (runtime) | -- |
| Legacy URL bad port | -- | v25 (EOL) |
| `http.OutgoingMessage._headers` | -- | v24 (removed) |
| `http.writeHeader` | v24 (deprecated) | -- |
| `net._setSimultaneousAccepts()` | -- | v24 (EOL) |

### Util & Process

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `util.isXxx()` functions (16+) | v22 (runtime) | v23 (EOL) |
| `util.log` | v22 (runtime) | v23 (EOL) |
| `process.assert` | -- | v23 (removed) |
| `process.multipleResolves` | -- | v25 (EOL) |

### Async & Workers

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `asyncResource` on bound fn | -- | v25 (EOL) |
| `worker.terminate()` callback | -- | v25 (EOL) |

### Assert

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `assert.fail()` multi-args | -- | v25 (EOL) |
| `assert.CallTracker` | -- | v25 (EOL) |

### Buffer & Streams

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `SlowBuffer` | v24 (runtime) | v25 (EOL) |
| `_stream_*` internal modules | v25 (deprecated) | -- |
| `_tls_common`/`_tls_wrap` | v25 (deprecated) | -- |

### Other

| Item | Deprecated | EOL/Removed |
|------|-----------|-------------|
| `Module._debug` | -- | v25 (EOL) |
| REPL without `new` | v24 (runtime) | v25 (EOL) |
| Zlib without `new` | v24 (deprecated) | -- |
| `child_process` `_channel` | -- | v25 (EOL) |
| `child_process` spawn `args` positional | v24 (deprecated) | -- |
| `dgram` deprecated APIs | -- | v25 (EOL) |
| `dns.lookup` falsy hostname | -- | v25 (EOL) |
| `perf_hooks` deprecated accessors | -- | v25 (EOL) |
| Corepack bundled | -- | v25 (removed) |

## Platform Support Changes

| Version | Change |
|---------|--------|
| v23 | 32-bit Windows removed, Windows < 10 dropped, GCC min 12.2, AIX uses GCC 12 |
| v24 | macOS min 13.5, Xcode min 16.1, Python 3.8 dropped, PPC32 removed, s390-32 removed, armv7 experimental, MSVC removed (ClangCL required), NODE_MODULE_VERSION=137 |
| v25 | Clang min 19, Xcode min 16.4, NODE_MODULE_VERSION=141 |

## npm Versions

| Node.js | npm |
|---------|-----|
| v22 | 10.5.1 |
| v24 | 11.x |
| v24.5 | 11.5.1 |
| v25 | 11.6.2+ |

## V8 Versions

| Node.js | V8 |
|---------|-----|
| v22 | 12.4 |
| v23 | 12.9 |
| v24 | 13.6 |
| v25 | 14.1 |

## assert Behavioral Changes (v25)

- Promise comparison now fails deep equal checks (promises compared by identity, not content)
- Invalid dates treated as equal to each other in deep comparison
- `Float16Array` supported in loose deep equality checks (v24+)

## node:sqlite (v23.3+)

While still experimental, notable additions:

- Session Extension support (v23.3)
- Conflict resolution handler receives conflict type argument (v23.6)
- `setReturnArrays` method documented (v24.5)
- Updated to SQLite 3.50.3 (v24.5)

## Miscellaneous

- `node --run` stable (v23+) -- runs package.json scripts directly
- `process.ref()` / `process.unref()` added (v23.6)
- `path.matchGlob()` added (v23)
- `v8.queryObjects()` added (v22) for memory leak testing
- `v8.cpuProfile()` added (v25) for programmatic CPU profiling
- `worker.markAsUncloneable()` added (v23) -- mark objects as non-transferable
- `worker.getHeapStatistics()` added (v24)
- `--watch` marked stable (v22)
- `--cpu-prof-name` supports `${pid}` placeholder (v24.5)
- `util.deprecate()` gains `code` and `since` options (v25.2)
- `util.styleText` respects nested formats (v25.2)
- `HeapStatistics` gains `total_allocated_bytes` (v25.2)
- Node-API version 10 defined (v23.6)
- REPL multiline history support (v24)
- `console` regex colorization improvements (v25)
