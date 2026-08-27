# Filesystem, Buffers, and Streams

## Buffer and byte behavior

- In 23.0.0, `Buffer.prototype.write()` throws when the offset is beyond the
  buffer instead of tolerating the invalid write.
- In 23.1.0, a `Buffer` created with `Buffer.from(resizableArrayBuffer)` tracks
  the underlying resizable `ArrayBuffer` and changes length when it is resized.
- In 24.13.0, the 24.13.1 release lets Buffer methods operate directly on
  `Uint8Array` values.
- In 24.18.0, `Buffer.poolSize` defaults to 64 KiB. Allocation tuning and pooled
  memory estimates must not assume the earlier default.
- Node.js 24.11.0 accidentally returns zero-filled memory from
  `Buffer.allocUnsafe()`; 24.11.1 restores documented uninitialized memory.
  Use `Buffer.alloc()` whenever zero filling is required.

## Paths, URLs, and globbing

- In 23.7.0, filesystem glob APIs accept glob patterns in `exclude`, allowing
  declarative exclusions rather than only a filter callback.
- In 24.1.0, a filesystem glob's `cwd` accepts a `URL`.
- In 24.3.0, `fileURLToPathBuffer()` converts a file URL to a `Buffer` path and
  preserves bytes that are not valid UTF-8.
- In 24.8.0, `path.matchesGlob(path, pattern)` is stable.
- In 24.13.0, the 24.13.1 release fixes globstar traversal so it detects
  dotfiles without raising `ENOTDIR` when a traversed path is a file.

## File and directory lifecycle

- In 23.9.0, `fs.statSync(path, { throwIfNoEntry: false })` treats `ENOTDIR` as
  a missing entry and returns `undefined` when an intermediate component is not
  a directory.
- In 24.0.0, `fs.truncate()` no longer accepts a file descriptor; use
  `fs.ftruncate()`. Top-level `fs.F_OK`, `fs.R_OK`, `fs.W_OK`, and `fs.X_OK`
  are runtime-deprecated in favor of `fs.constants`. Invalid argument types to
  `fs.existsSync()` are deprecated, and `Dirent.path` is removed.
- In 24.1.0, `fs.Dir` supports async explicit resource management, so
  `await using` closes the directory. Operational failures from `fs.Dir.read()`
  arrive through the callback or rejected promise rather than throwing
  synchronously.
- In 24.4.0, `fs.mkdtempDisposableSync()` returns a temporary-directory object
  whose `path` is usable until a `using` scope removes it. `fs.chown()`,
  `lchown()`, and `fchown()` accept `-1` for a UID or GID that should remain
  unchanged.
- In 24.9.0, relying on garbage collection to close `fs.Dir` is deprecated;
  call `close()` or use `await using`.
- In 25.0.0, the top-level access-constant aliases and recursive `fs.rmdir()`
  are removed; use `fs.constants` and `fs.rm()`. File handles require explicit
  closure, and file-stream implementations can no longer rely on the legacy
  `open()` hook.
- In 24.13.0, 24.13.1 makes `fs.cp()` honor `errorOnExist` for directories and
  makes `fs.rmSync()` handle non-ASCII paths and remove broken symlinks.
- In 25.5.0, `fs.watch()` accepts `ignore` to exclude paths rather than
  filtering delivered events.
- In 24.18.0, `fs.Stats` date properties are enumerable.
- In 26.4.0, `readFile()` accepts a caller-supplied buffer for controlled
  allocation and storage reuse.

## Reading and writing streams

- In 23.0.0, `stream.pipeline()` rejects an already closed or destroyed
  destination. Replace or reopen the destination instead of reusing it.
- In 23.1.0, streams preserve an `AbortSignal`'s caller-supplied abort reason.
- In 24.0.0, `stream.finished()` preserves the current `AsyncLocalStorage`
  context, and stream plumbing catches and forwards synchronous errors thrown
  by a destination's `write()`.
- In 24.3.0, the async iterator from `fs.promises.watch()` correctly handles
  event bursts even when events arrive faster than a `for await` consumer.
- In 24.6.0, `node:fs` exports `Utf8Stream`, a buffered stream for UTF-8 file
  output.
- In 25.9.0, an experimental stream/iterator implementation is present. Treat
  it as unstable and feature-detect it across release lines. If a pipeline has
  a substantive failure and is later aborted, it preserves the original error
  rather than replacing it with `AbortError`.
- In 26.0.0, readable streams return one buffered chunk at a time instead of
  combining multiple chunks. Consumers and tests must not depend on coalesced
  boundaries.
- In 24.18.0, the change making `pause()` and `resume()` no-ops on destroyed
  streams is reverted. Check `stream.destroyed` when no-op behavior is needed.
- In 24.19.0, `stream.compose()` is stable. Async iteration preserves a
  half-open duplex: completion of the readable side no longer closes a writable
  side configured to remain open.

## Web streams and consumption

- In 23.8.0, `FileHandle.readableWebStream()` always creates a Web byte stream.
- In 24.2.0, `FileHandle.readableWebStream({ autoClose: true })` makes the
  stream close its file handle when the stream closes.
- In 24.13.0, 24.13.1 corrects `stream.isErrored()` and `stream.isWritable()` for
  Web `WritableStream` objects.
- In 25.4.0, `Readable.toWeb()` can create a Web readable byte stream from a
  byte-oriented Node stream, enabling BYOB readers.
- In 24.14.0, `node:stream/consumers` exports `bytes()` for consuming a readable
  source as bytes. `readable.compose()` no longer runs output through
  `Readable.from()`; handle composed output directly rather than depending on
  that wrapper's conversion.
- In 26.5.0, the streams API exposes `ReadableStreamTee` for splitting a
  readable source into branches.
- In 24.19.0, `Blob.prototype.textStream()` streams text incrementally rather
  than requiring whole-value `text()` conversion.

## Virtual filesystems

- In 26.4.0, `node:vfs` provides mountable filesystem routing and
  `node:fs/promises` operations dispatch through mounted VFS instances.
- In 26.5.0, treat VFS as routing, not a sandbox or permission boundary.
