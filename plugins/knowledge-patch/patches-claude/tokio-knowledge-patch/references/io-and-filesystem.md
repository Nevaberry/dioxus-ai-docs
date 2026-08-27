# Async I/O and filesystem

## Core I/O types

- `tokio::io::Empty` implements `AsyncSeek` from 1.39.0, so a seekable generic
  reader can use the empty source directly.
- `io::util::SimplexStream` arrives in 1.40.0 for one-direction asynchronous
  I/O. `tokio-util` later adds its own `io::simplex` in 0.7.18.
- `AsyncFd::try_io` and `try_io_mut` arrive in 1.42.0 for immediate attempts
  through shared or mutable access to a registered source.
- From 1.45.0, affected I/O implementations no longer impose unnecessary
  `Unpin` bounds and can work with pinned `!Unpin` values.
- `tokio::io::Chain`, the concrete type returned by `AsyncReadExt::chain`, is
  public from 1.48.0.
- Tokio 1.53.0 fixes `Chain` treating a zero-length read request as end of file;
  an empty destination no longer advances prematurely to the second reader.

## Files and owned resources

- Filesystem configuration is available on WASI from 1.41.0.
- `File::max_buf_size()` exposes the configured buffer limit from 1.48.0, and a
  cloned `File` preserves that limit.
- `AioSource::register_borrowed` arrives in 1.52.0 for registering a borrowed
  resource without transferring ownership.
- Tokio 1.53.0 implements `From<OwnedFd>` and `From<OwnedHandle>` for
  `tokio::fs::File`, allowing direct transfer of Unix descriptors and Windows
  handles.

```rust
let file: tokio::fs::File = owned_fd.into();
```

## Pipes and standard output

- Android `pipe::OpenOptions::read_write` is supported from 1.46.0.
- Unix `pipe::Sender::try_io` and `pipe::Receiver::try_io` arrive in 1.52.0 for
  immediate custom I/O on pipe endpoints.
- Writes through distinct Tokio standard-output handles may be reordered.
  Reuse one handle or synchronize access when ordering is significant.

## Unstable io_uring filesystem backend

- From 1.48.0, enable the backend with the `io_uring` Cargo feature. That
  release supports `fs::write`, `File::open`, and `OpenOptions` opens.
- Tokio 1.49.0 adds `tokio::fs::read` and disables io_uring after `EPERM`, so
  configuration does not guarantee that the backend stays active.
- Tokio 1.51.1 closes a file-descriptor leak when an io_uring open is cancelled.
- Tokio 1.52.0 supports `File`'s `AsyncRead` operations through io_uring.
- Tokio 1.53.0 adds `tokio::fs::try_exists` and file renaming. Treat every
  operation as version-gated and allow the runtime to fall back when needed.
