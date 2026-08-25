# Filesystem, Buffers, and Streams

Use this reference for filesystem, buffers, and streams work.

## `-1` ownership sentinels (`24.4.0`)

`fs.chown()`, `fs.lchown()`, and `fs.fchown()` now accept `-1` as the UID or GID sentinel for leaving that ownership field unchanged.

## `Buffer.allocUnsafe()` behavior in 24.11.x (`24.11.0`)

Node.js 24.11.0 has a known issue that makes `Buffer.allocUnsafe()` return zero-filled buffers. Node.js 24.11.1 restores the documented uninitialized-memory behavior, so code that requires zeroes must use `Buffer.alloc()` instead of relying on the 24.11.0 regression.

## `SlowBuffer` remains runtime-deprecated (`24.0.0`)

Node.js 24.0.1 reverses 24.0.0's move of `SlowBuffer` to end-of-life status. It remains available on the 24.x line but emits a runtime deprecation.

## Buffer methods on `Uint8Array` (`24.13.0`)

Buffer methods can now operate on `Uint8Array` instances in 24.13.1, avoiding a conversion when byte-processing code receives a plain typed array.

## Buffer-valued file URL paths (`24.3.0`)

`fileURLToPathBuffer()` converts a file URL to a `Buffer` path, preserving path bytes that cannot be represented as valid UTF-8.

```js
import { fileURLToPathBuffer } from 'node:url';

const path = fileURLToPathBuffer(new URL('file:///tmp/%FF'));
console.log(Buffer.isBuffer(path)); // true
```

## Buffered UTF-8 file output (`24.6.0`)

`node:fs` now exports `Utf8Stream`, a buffered stream specialized for writing UTF-8 text to a file.

```js
import { Utf8Stream } from 'node:fs';

const log = new Utf8Stream('./app.log');
log.write('started\n');
log.end();
```

## Buffers track resizable ArrayBuffers (`23.1.0`)

A `Buffer` created with `Buffer.from(resizableArrayBuffer)` now changes length when its underlying `ArrayBuffer` is resized.

```js
const ab = new ArrayBuffer(10, { maxByteLength: 20 });
const buffer = Buffer.from(ab);
ab.resize(15);
console.log(buffer.byteLength); // 15
```

## Built-in `Uint8Array` encodings (`25.0.0`)

V8 14.1 makes the standard base64 and hexadecimal conversion helpers available on `Uint8Array`, including `fromBase64()`, `fromHex()`, `toBase64()`, and `toHex()`.

```js
const bytes = Uint8Array.fromHex('4869');
console.log(bytes.toBase64()); // SGk=
```

## Byte streams from `Readable.toWeb()` (`25.4.0`)

`Readable.toWeb()` now supports Web readable byte streams when converting byte-oriented Node streams, enabling byte-stream consumers such as BYOB readers.

```js
import { Readable } from 'node:stream';

const source = Readable.from([Buffer.from('data')], { objectMode: false });
const reader = Readable.toWeb(source).getReader({ mode: 'byob' });
```

## Byte streams from file handles (`23.8.0`)

`FileHandle.readableWebStream()` now always creates a Web Streams byte stream.

## Byte-oriented stream consumption (`24.14.0`)

`node:stream/consumers` now exports `bytes()` for consuming a readable source as bytes.

```js
import { Readable } from 'node:stream';
import { bytes } from 'node:stream/consumers';

const payload = await bytes(Readable.from([Buffer.from('data')]));
```

## Caller-supplied `readFile()` buffers (`26.4.0`)

`readFile()` now accepts a caller-supplied buffer, allowing applications to control allocation and reuse storage for whole-file reads.

## Destroyed-stream pause and resume behavior (`24.18.0`)

The change that made `pause()` and `resume()` no-ops on destroyed streams is reverted. Check `stream.destroyed` explicitly when callers require those operations to do nothing after destruction.

## Direct composed-stream output (`24.14.0`)

`readable.compose()` no longer passes its output through `Readable.from()`. Code that depended on that wrapper's conversion behavior must handle the composed output directly.

## Directory-read failures are asynchronous (`24.1.0`)

Operational failures from `fs.Dir.read()` are no longer thrown synchronously; they arrive through the callback or as a rejected promise.

## Disposable filesystem directories (`24.1.0`)

`fs.Dir` now supports explicit resource management, so an `await using` binding closes the directory when its scope exits.

```js
import { opendir } from 'node:fs/promises';

async function firstEntry(path) {
  await using dir = await opendir(path);
  return (await dir.read())?.name;
}
```

## Disposable synchronous temporary directories (`24.4.0`)

`fs.mkdtempDisposableSync()` creates a temporary directory as an explicit-resource-management object. Its `path` is available inside the scope, and leaving a `using` scope removes the directory.

```js
import { mkdtempDisposableSync } from 'node:fs';

using temporary = mkdtempDisposableSync('./job-');
console.log(temporary.path);
```

## Enumerable filesystem stat dates (`24.18.0`)

The `Date` properties on `fs.Stats` objects are now enumerable, so properties such as `atime`, `mtime`, `ctime`, and `birthtime` appear in `Object.keys()` and object spreads.

## Experimental stream iterator implementation (`25.9.0`)

Node.js now includes an experimental stream/iterator implementation. Treat it as an unstable surface and feature-detect it rather than assuming compatibility across release lines.

## Explicit `fs.Dir` closure (`24.9.0`)

Relying on garbage collection to close an unclosed `fs.Dir` is now deprecated. Call `dir.close()` or use the existing `await using` support.

## Exposed `ReadableStreamTee` (`26.5.0`)

The streams API now exposes `ReadableStreamTee`, making the tee primitive directly available for splitting a readable source into branches.

## File-handle Web streams can own their handle (`24.2.0`)

`FileHandle.readableWebStream()` now accepts `autoClose`; setting it to `true` makes the stream close its file handle when the stream closes.

```js
import { open } from 'node:fs/promises';

const handle = await open('data.bin');
const stream = handle.readableWebStream({ autoClose: true });
```

## File-URL entry points (`23.0.0`)

The main entry point passed to Node can now be a URL rather than only a filesystem path.

```sh
node file:///absolute/path/app.mjs
```

## Filesystem behavior corrections (`24.13.0`)

In 24.13.1, `fs.cp()` honors `errorOnExist` for directory copies, `fs.rmSync()` handles non-ASCII paths and removes broken symlinks, and globstar traversal detects dotfiles without raising `ENOTDIR` when a path is a file.

## Filesystem removals (`25.0.0`)

The top-level `fs.F_OK`, `fs.R_OK`, `fs.W_OK`, and `fs.X_OK` aliases are removed; use `fs.constants`. Recursive `fs.rmdir()` is removed in favor of `fs.rm()`, file handles must be closed explicitly rather than by garbage collection, and file-stream implementations can no longer rely on the legacy `open()` hook.

## Filesystem removals and deprecations (`24.0.0`)

`fs.truncate()` no longer accepts a file descriptor; descriptor-based code must use `fs.ftruncate()`. `fs.F_OK`, `fs.R_OK`, `fs.W_OK`, and `fs.X_OK` are runtime-deprecated in favor of `fs.constants`, invalid argument types to `fs.existsSync()` are deprecated, and `Dirent.path` is removed.

## Half-open duplexes survive async iteration (`24.19.0`)

Async iteration now preserves half-open duplex streams, so finishing the readable side no longer closes a writable side that is configured to remain open.

## Larger default Buffer pool (`24.18.0`)

`Buffer.poolSize` now defaults to 64 KiB, so more small `Buffer` allocations can share the internal slab. Code that tunes allocation behavior or estimates retained pooled memory should no longer assume the old default.

```js
console.log(Buffer.poolSize); // 65536
```

## Minimal virtual filesystem subsystem (`26.4.0`)

The new `node:vfs` subsystem provides mountable filesystem routing, and `node:fs/promises` operations dispatch to mounted VFS instances.

## Out-of-bounds Buffer writes now throw (`23.0.0`)

`Buffer.prototype.write()` now throws when its write offset is beyond the buffer instead of tolerating the invalid write.

```js
Buffer.alloc(1).write('x', 2); // throws
```

## Pattern-based filesystem glob exclusions (`23.7.0`)

The `exclude` option of the filesystem glob APIs now accepts glob patterns, allowing declarative exclusions instead of a filter callback.

```js
import { globSync } from 'node:fs';
const files = globSync('**/*.js', { exclude: ['**/*.test.js'] });
```

## Readable chunk boundaries (`26.0.0`)

Readable streams now return one buffered chunk at a time instead of combining multiple buffered chunks in one read, so consumers and tests must not depend on coalesced boundaries.

## Stable path glob matching (`24.8.0`)

`path.matchesGlob(path, pattern)` is now stable.

```js
import { matchesGlob } from 'node:path';

console.log(matchesGlob('/srv/app/index.js', '/srv/**/*.js')); // true
```

## Stable stream composition (`24.19.0`)

`stream.compose()` is now stable, so applications can use the composition API without treating it as an experimental surface.

## Stream abort reasons are preserved (`23.1.0`)

Streams now propagate an `AbortSignal`'s reason instead of losing the caller-supplied cancellation reason.

## Stream error and context propagation (`24.0.0`)

`stream.finished()` now preserves the current `AsyncLocalStorage` context. Stream plumbing also catches and forwards synchronous errors thrown by a destination's `write()` method.

## Stream pipeline error precedence (`25.9.0`)

If a pipeline already has a substantive failure and is then aborted, it now preserves the original error instead of replacing it with the later `AbortError`.

## Streaming Blob text (`24.19.0`)

`Blob.prototype.textStream()` streams a blob as text, avoiding a whole-value `text()` conversion when consumers can process chunks incrementally.

```js
for await (const chunk of new Blob(['hello']).textStream()) {
  process.stdout.write(chunk);
}
```

## URL working directories for filesystem globs (`24.1.0`)

The `cwd` option of the filesystem glob APIs now accepts a `URL`, avoiding a manual conversion when the working directory is relative to an ES module.

```js
import { globSync } from 'node:fs';

const files = globSync('**/*.js', {
  cwd: new URL('./src/', import.meta.url),
});
```

## VFS is not a sandbox (`26.5.0`)

`node:vfs` provides filesystem routing, not a security boundary. Do not treat its mounts as permission boundaries.

## Web-stream state probes (`24.13.0`)

`stream.isErrored()` and `stream.isWritable()` now report the state of Web `WritableStream` objects correctly in 24.13.1.
