# Companion crates: `tokio-util` and `tokio-stream`

## `tokio-util`

### Toolchain and Tokio floors

- `tokio-util` 0.7.12 requires Rust 1.70 or newer.
- `tokio-util` 0.7.17 requires Rust 1.71 or newer.
- `tokio-util` 0.7.18 requires Tokio 1.44.0 or newer.

### Simplex I/O

Version 0.7.18 adds `tokio_util::io::simplex`, a one-direction asynchronous I/O
primitive available directly from `tokio-util`.

### Join collections

- `JoinMap` is stable as of 0.7.16.
- `tokio_util::task::JoinQueue` is available from 0.7.17 as another task
  collection primitive.

### Framed construction and capacity

Starting in 0.7.16, the capacity passed to `Framed::with_capacity` applies to
the read buffer as well. Recheck code that assumed the value only affected
another buffer.

Version 0.7.17 removes unnecessary trait bounds from all `Framed`
constructors, allowing a broader set of transport and codec types to be
constructed directly.

### Cancellation composition

- Version 0.7.12 adds `CancellationToken::run_until_cancelled`.
- Version 0.7.14 adds its owned form.
- Version 0.7.16 adds `FutureExt` cancellation adapters.
- From 0.7.16, cancellation wins when the token and wrapped future become ready
  simultaneously.

### Borrowed cancellation guards

Version 0.7.16 adds `DropGuardRef`. It borrows a `CancellationToken` and
cancels the token when the guard is dropped.

### Abort-on-drop task handles

Version 0.7.12 adds `AbortOnDropHandle`, which aborts its task when the wrapper
is dropped. Version 0.7.16 adds `detach`, allowing the task to continue
independently.

### Arc-backed exact reads

Version 0.7.14 adds `tokio_util::io::read_exact_arc` for exact reads backed by
an `Arc`.

### Asynchronous writing through `Either`

From 0.7.14, `Either` delegates `AsyncWrite` to its selected branch. It can
satisfy asynchronous-write bounds without manual enum dispatch.

### Terminal invalid UTF-8

Version 0.7.13 fixes `LinesCodec::decode_eof` when invalid UTF-8 appears at the
end of input. Require at least this version when malformed terminal bytes must
be handled correctly.

### Emptying a delay queue

From 0.7.12, removing the final `DelayQueue` item wakes a waiting consumer, so
the consumer can observe the transition to an empty queue without another
event.

## `tokio-stream`

### Toolchain and Tokio floors

- `tokio-stream` 0.1.13 requires Rust 1.56 or newer.
- `tokio-stream` 0.1.15 requires Rust 1.63 or newer.
- `tokio-stream` 0.1.16 requires Rust 1.70 or newer.
- `tokio-stream` 0.1.14 requires Tokio 1.15 or newer so
  `timeout_repeating` compiles.

### Aggregate feature flag

Version 0.1.13 adds `full` for opting into the complete crate feature set.

```toml
tokio-stream = { version = "0.1.13", features = ["full"] }
```

### Watch streams that begin with changes

`WatchStream::from_changes` is available from 0.1.12. Use it when a stream
should wait for later watch-channel changes rather than first yielding the
currently stored value.

### Repeating stream timeouts

Version 0.1.13 adds `StreamExt::timeout_repeating`, allowing timeout behavior
to be driven by a repeating timer.

### Explicit close notifications

Version 0.1.13 adds `StreamNotifyClose`, which exposes the inner stream's
closure as a notification before the wrapper itself terminates.

### Timed chunks outside a runtime

Starting in 0.1.11, `StreamExt::chunks_timeout` can be constructed outside a
Tokio runtime. Pipelines using it can be assembled during synchronous setup.

### Batched `StreamMap` polling

Version 0.1.16 adds `StreamMap::next_many` and `StreamMap::poll_next_many` for
collecting multiple ready keyed items in one operation.

### Public stream adapter types

Version 0.1.16 makes stream adapter types public, allowing concrete adapter
types to appear in signatures and stored state.

### Recovering a timed chunk

Version 0.1.18 adds `ChunksTimeout::into_remainder`, which recovers an
incomplete buffered chunk when dismantling the adapter.

### Receiver-stream size hints

From 0.1.18, `ReceiverStream` and `UnboundedReceiverStream` provide meaningful
`Stream::size_hint` bounds instead of the trait default.
