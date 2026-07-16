# Filesystem, Buffers, and Streams

Filesystem behavior, paths and directories, buffers, Node streams, and Web streams.

## Contents

- [Paths, directories, and metadata](#paths-directories-and-metadata)
- [Watching and globbing](#watching-and-globbing)
- [File handles and lifecycle](#file-handles-and-lifecycle)
- [Node and Web streams](#node-and-web-streams)
- [Buffers and serialization](#buffers-and-serialization)
- [Filesystem APIs](#filesystem-apis)

## Paths, directories, and metadata

### Asynchronous directory-read failures (since 24.1.0)

Operational failures from `fs.Dir.read()` are now reported through its asynchronous result instead of being thrown synchronously; handle the promise rejection or callback error.

### Byte-preserving file URL conversion (since 24.3.0)

`node:url` now exports `fileURLToPathBuffer()`, which converts a file URL to platform path bytes in a `Buffer`; for example, `fileURLToPathBuffer(new URL('file:///tmp/data.bin'))`. Unlike the string-returning conversion, this can represent non-UTF-8 filesystem paths.

### Deterministic directory cleanup (since 24.9.0)

Relying on garbage collection to close an `fs.Dir` is now deprecated. Call `dir.close()` or use the explicit-resource-management support available on directory handles.

### Enumerable filesystem timestamps (since 24.18.0)

The `atime`, `mtime`, `ctime`, and `birthtime` `Date` properties on `fs.Stats` are now enumerable, so they appear in `Object.keys()`, object spreads, and other enumeration-based processing.

### Filesystem API migrations (since 24.0.0)

`fs.truncate()` no longer accepts a file descriptor; use `fs.ftruncate()` or `fs.ftruncateSync()` for descriptors. `Dirent.path` has been removed in favor of `Dirent.parentPath`, and the top-level `fs.F_OK`, `fs.R_OK`, `fs.W_OK`, and `fs.X_OK` aliases are runtime-deprecated in favor of `fs.constants`.

### Invalid `existsSync()` argument types (since 23.4.0)

Passing unsupported argument types to `fs.existsSync()` is now deprecated; normalize values to a supported path type before calling it.

### Missing `statSync()` paths below files (since 23.9.0)

`statSync(path, { throwIfNoEntry: false })` now treats `ENOTDIR` as a missing entry and returns `undefined`, including when an intermediate path component is a regular file.

### Ownership fields left unchanged with `-1` (since 24.4.0)

`fs.chown()`, `fs.lchown()`, and `fs.fchown()` now accept `-1` as the UID or GID sentinel for leaving that ownership field unchanged; for example, `chown(path, -1, newGid, callback)` changes only the group.

### Stable path glob matching (since 24.8.0)

`path.matchesGlob(path, pattern)` is now stable and can be used without relying on an experimental API.

```js
import { matchesGlob } from 'node:path';

console.log(matchesGlob('/srv/app/index.js', '/srv/**/*.js')); // true
```

### Symlinks in recursive directory reads (since 23.4.0)

`fs.readdir()` with both `recursive: true` and `withFileTypes: true` now includes symbolic-link entries instead of omitting them from the result.

### Writable `Dirent.path` (since 23.2.0)

The `fs.Dirent.path` property can now be assigned to, so code that adjusts a directory entry's path can use `dirent.path = '/replacement/path'` directly.


## Watching and globbing

### Burst-safe asynchronous filesystem watches (since 24.3.0)

The async iterator returned by `watch()` from `node:fs/promises` now handles bursts of filesystem events correctly instead of mishandling rapid events while the consumer is between iterations.

### Filesystem watch exclusions (since 25.5.0)

`fs.watch()` now accepts an `ignore` option, allowing a watcher to omit unwanted paths instead of filtering every resulting event itself.

### Glob-pattern exclusions (since 23.7.0)

The `exclude` option of `fs.glob()` and `fs.globSync()` now accepts glob patterns, so exclusions no longer require a predicate callback.

```js
import { globSync } from 'node:fs';

const files = globSync('**/*.js', {
  exclude: ['node_modules/**', 'dist/**'],
});
```

### URL working directories for filesystem globs (since 24.1.0)

The `cwd` option of `fs.glob()` now accepts a `URL`, allowing module-relative searches such as `glob('**/*.js', { cwd: new URL('./src/', import.meta.url) }, callback)`.


## File handles and lifecycle

### Auto-closing file-handle web streams (since 24.2.0)

`FileHandle.readableWebStream()` accepts an `autoClose` option; use `handle.readableWebStream({ autoClose: true })` when the stream should own cleanup of its file handle.

### Disposable synchronous temporary directories (since 24.4.0)

`node:fs` now exports `mkdtempDisposableSync()`. A resource declared with `using temp = mkdtempDisposableSync(prefix)` exposes its path as `temp.path` and removes the temporary directory when its scope exits.

### Explicit file-handle and stream lifecycle (since 25.0.0)

Garbage collection no longer closes an unclosed `FileHandle`, so every handle needs an explicit `close()` path. The deprecated `open()` methods on filesystem read and write streams have also been removed; create a new stream and observe its `open` event instead of calling the method.

### File-handle web streams are always byte streams (since 23.8.0)

`FileHandle.readableWebStream()` now always creates a WHATWG byte stream, even when called without a type option, so consumers can consistently use BYOB readers.


## Node and Web streams

### Byte views for BYOB requests (since 24.18.0)

An active `ReadableStreamBYOBRequest.view` is now specifically a `Uint8Array` rather than an arbitrary `ArrayBufferView`.

### Closed destinations in `stream.pipeline()` (since 23.0.0)

Piping to a stream that is already closed or destroyed is no longer allowed. Callback-based `pipeline()` reports an error and `stream/promises.pipeline()` rejects instead of attempting the pipe.

### Core UTF-8 output streams (since 24.6.0)

`node:fs` now provides `Utf8Stream`, a core port of the SonicBoom UTF-8 stream implementation.

### Destination stream write errors (since 24.0.0)

Errors thrown by a destination's `write()` operation are now caught and forwarded through stream error handling rather than escaping the piping operation directly.

### Direct readable-stream teeing (since 26.5.0)

The streams API now exposes `ReadableStreamTee`, making the tee primitive directly available for splitting one readable source into branches.

### Experimental stream iterator implementation (since 25.9.0)

Node now includes an experimental `stream/iter` implementation. Treat this surface as unstable until it advances beyond experimental status.

### Per-stream console inspection options (since 24.10.0)

The `Console` constructor's `inspectOptions` can now be a `Map` keyed by its output streams, allowing standard output and standard error to format inspected values differently.

```js
import { Console } from 'node:console';

const logger = new Console({
  stdout: process.stdout, stderr: process.stderr,
  inspectOptions: new Map([[process.stdout, { depth: 4 }], [process.stderr, { depth: 1 }]]),
});
```

### Readable chunk boundaries (since 26.0.0)

Readable streams now read one buffered chunk at a time rather than combining multiple buffers in one read. Consumers and tests must not rely on the previous coalesced chunk boundaries.

### Stream abort reasons (since 23.1.0)

Stream cancellation now propagates the associated `AbortSignal` reason instead of discarding it.

### Stream composition and byte-stream conversion (since 25.4.0)

`readable.compose()` no longer passes its composed output through `Readable.from()`, removing that extra wrapper's conversion behavior. Stream `.toWeb()` conversion paths now also support readable byte streams.

### Stream pipeline error precedence (since 25.9.0)

When a pipeline operation has already failed, that error is now preserved instead of being replaced by a later `AbortError`.


## Buffers and serialization

### `Buffer.allocUnsafe()` behavior in 24.11.x (since 24.11.0)

Node.js 24.11.0 has a known issue that makes `Buffer.allocUnsafe()` return zero-filled buffers. Node.js 24.11.1 restores the documented uninitialized-memory behavior; code that requires zeroes must use `Buffer.alloc()` rather than depending on the 24.11.0 regression.

### Caller-supplied `readFile()` buffers (since 26.4.0)

`readFile()` now accepts a caller-provided buffer, allowing applications to control or reuse the storage used for file contents.

```js
import { readFile } from 'node:fs/promises';

const storage = Buffer.alloc(64 * 1024);
const data = await readFile('payload.bin', { buffer: storage });
```

### Larger default buffer pool (since 24.18.0)

`Buffer.poolSize` now defaults to 64 KiB, so small pooled buffer allocations draw from a larger shared slab unless an application overrides the property.

### Out-of-bounds `Buffer` writes (since 23.0.0)

Buffer write operations now throw when a requested write starts beyond the buffer instead of silently accepting a zero-byte write. Validate offsets before calling `Buffer.prototype.write()`.

### Removed `SlowBuffer` (since 25.0.0)

The runtime-deprecated `SlowBuffer` constructor has now been removed.

### Resizable `ArrayBuffer`-backed buffers (since 23.1.0)

A `Buffer` created from a resizable `ArrayBuffer` now tracks changes to its byte length: after `const ab = new ArrayBuffer(10, { maxByteLength: 20 }); const buffer = Buffer.from(ab); ab.resize(15)`, `buffer.byteLength` is `15`.


## Filesystem APIs

### Async-disposable filesystem directories (since 24.1.0)

`fs.Dir` now participates in explicit resource management, so a handle returned by `opendir()` can be declared with `await using` and is closed automatically when its scope exits.

```js
import { opendir } from 'node:fs/promises';

await using dir = await opendir('./data');
console.log((await dir.read())?.name);
```

### Removed filesystem shortcuts (since 25.0.0)

The recursive option of `fs.rmdir()` and `fs.rmdirSync()` has been removed; use `fs.rm()` or `fs.rmSync()` for recursive deletion. The top-level `fs.F_OK`, `fs.R_OK`, `fs.W_OK`, and `fs.X_OK` aliases are also gone, leaving their `fs.constants` forms.

```js
import { rm } from 'node:fs/promises';

await rm('./output', { recursive: true, force: true });
```

### Virtual filesystem support (since 26.4.0)

The new minimal `node:vfs` subsystem supports mounted virtual filesystem instances, and `node:fs/promises` operations are dispatched to the applicable mount.

### Virtual filesystems are not sandboxes (since 26.5.0)

`node:vfs` changes filesystem routing but is not a security sandbox; mounts must not be treated as permission boundaries.
