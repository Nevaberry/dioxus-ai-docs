# Async I/O and filesystem

Use this reference for Tokio I/O types, file buffering, pipes, borrowed AIO registration, target availability, and unstable io_uring filesystem behavior.

## Contents

- [General async I/O](#general-async-io)
- [Files and filesystem targets](#files-and-filesystem-targets)
- [Pipes and AIO registration](#pipes-and-aio-registration)
- [Unstable io_uring filesystem backend](#unstable-io_uring-filesystem-backend)

## General async I/O

### Seekable empty readers

Tokio 1.39.0 implements `AsyncSeek` for `tokio::io::Empty`. An empty reader can now satisfy generic bounds that require both asynchronous reading and seeking.

### Simplex streams

Tokio 1.40.0 adds `util::SimplexStream` to Tokio's I/O utilities. Use the provided simplex-stream type instead of maintaining an ad hoc one.

The companion `tokio-util` 0.7.18 release separately adds the `tokio_util::io::simplex` constructor; select the API belonging to the crate already used by the component.

### Pinned I/O values

Tokio 1.45.0 removes `Unpin` requirements from some I/O trait implementations. Compatible pinned `!Unpin` I/O values can use those implementations without an extra wrapper whose only job is to satisfy `Unpin`.

### Nameable chained readers

Tokio 1.48.0 publicly exports `tokio::io::Chain`, the concrete type returned by `AsyncReadExt::chain`. Use it in fields, aliases, and function signatures that need to name a chained reader.

## Files and filesystem targets

### File buffer limits

Tokio 1.48.0 adds `File::max_buf_size()` for reading a file's configured maximum buffer size. Cloning a `File` now preserves that setting, so code no longer needs to reapply the limit to each clone.

### WASI filesystem availability

Tokio 1.41.0 enables its filesystem configuration for `wasi` targets. Filesystem-gated Tokio APIs are no longer removed solely because the target is WASI.

## Pipes and AIO registration

### Android read-write pipes

Tokio 1.46.0 supports `pipe::OpenOptions::read_write` on Android. A pipe can be opened for both reading and writing on that target.

### Nonblocking Unix pipe access

Tokio 1.52.0 adds `try_io` to `unix::pipe::Sender` and `unix::pipe::Receiver`. Use it to attempt custom nonblocking I/O against a pipe endpoint while preserving readiness handling.

### Borrowed AIO sources

Tokio 1.52.0 adds `AioSource::register_borrowed`. It provides an I/O-safety-aware path for registering a borrowed resource without transferring ownership to the AIO source.

## Unstable io_uring filesystem backend

### Enablement and fallback

Tokio 1.48.0 moves io_uring opt-in to a Cargo feature instead of a custom `--cfg` flag.

Treat the backend as opportunistic even when the feature is enabled:

- Tokio 1.49.0 disables io_uring after an `EPERM` result.
- Tokio 1.50.0 checks whether the running kernel supports an opcode before using that operation.

Keep normal filesystem behavior available as a fallback; feature enablement alone is not evidence that a particular operation will use io_uring.

### Operation coverage

- Tokio 1.48.0 allows unstable io_uring to back `fs::write`, `File::open`, and `OpenOptions`.
- Tokio 1.49.0 allows unstable io_uring to back `tokio::fs::read`.
- Tokio 1.52.0 allows the `AsyncRead` implementation for `tokio::fs::File` to use io_uring.

### Cancellation correctness

Tokio 1.51.1 fixes a file-descriptor leak when an io_uring open operation is cancelled. Require at least that patch release when cancellation can race file opening.
