# Async I/O and filesystem

## General I/O primitives

### Seekable empty readers (1.39.0)

`tokio::io::Empty` implements `AsyncSeek`. It can be passed directly to
generic asynchronous I/O code that requires a seekable reader.

### Simplex streams (1.40.0)

`io::util::SimplexStream` provides a one-direction asynchronous I/O primitive
for code that does not need a duplex connection. `tokio-util` 0.7.18 also
provides `tokio_util::io::simplex`.

### Immediate `AsyncFd` operations (1.42.0)

`AsyncFd::try_io` and `AsyncFd::try_io_mut` attempt I/O without waiting,
through shared and mutable access respectively, on the registered source.

### Pinned `!Unpin` values (1.45.0)

Some Tokio I/O trait implementations no longer impose `Unpin`, allowing them
to operate on appropriately pinned `!Unpin` values without an unnecessary
bound.

## Files and reader composition

### File buffer limits (1.48.0)

`File::max_buf_size()` returns a Tokio file's configured maximum buffer size.
Cloning a `File` preserves that limit rather than reverting to another value.

### Public chained-reader type (1.48.0)

`tokio::io::Chain` is the public concrete type returned by
`AsyncReadExt::chain`. APIs and stored state can name it directly.

### Zero-length chained reads (1.53.1)

As of 1.53.0, `tokio::io::Chain` does not treat a zero-length read request as
end-of-file. Reading into an empty destination no longer advances prematurely
to the second reader.

### Owned OS handles (1.53.1)

Tokio 1.53.0 adds `From<OwnedFd>` and `From<OwnedHandle>` implementations for
`tokio::fs::File`. Owned Unix descriptors and Windows handles can transfer
directly into an asynchronous file.

```rust
let file: tokio::fs::File = owned_fd.into();
```

## Pipes and AIO

### Android read-write pipes (1.46.0)

Android supports `pipe::OpenOptions::read_write`, allowing a pipe to be opened
for both reading and writing.

### Immediate Unix pipe I/O (1.52.0)

Unix pipe sender and receiver types provide `try_io`, allowing an immediate
I/O attempt through either endpoint.

### Borrowed AIO registration (1.52.0)

`AioSource::register_borrowed` registers a borrowed source without
transferring ownership and makes the ownership relationship explicit for I/O
safety.

## Unstable io_uring filesystem support

### Build configuration (1.48.0)

Select the unstable `io_uring` subsystem with a Cargo feature rather than its
former custom `--cfg` switch.

### Writes and opens (1.48.0)

The unstable io_uring filesystem backend supports:

- `tokio::fs::write`;
- `File::open`;
- files opened through `OpenOptions`.

### Whole-file reads and permission failures (1.49.0)

- `tokio::fs::read` can use the unstable io_uring backend.
- Tokio disables that backend after `EPERM`. Enabling it does not guarantee it
  remains active at runtime.

### Cancelled opens (1.51.0)

Tokio 1.51.1 fixes a file-descriptor leak when an unstable io_uring open is
cancelled. Require at least that patch for cancellable opens.

### `File` asynchronous reads (1.52.0)

With unstable io_uring filesystem support enabled, `File` can perform its
`AsyncRead` operations through that backend.

### Existence checks and renaming (1.53.1)

Tokio 1.53.0 adds unstable io_uring support for `tokio::fs::try_exists` and
file renaming.

## Standard output ordering (1.53.1)

Writes made through multiple Tokio standard-output handles can be reordered.
Reuse or synchronize one handle whenever output order matters.
