# Companion crates: tokio-util and tokio-stream

## `tokio-util` compatibility and I/O

- `tokio-util` 0.7.12 raises the Rust floor to 1.70, and 0.7.17 raises it to
  Rust 1.71. Version 0.7.18 requires Tokio 1.44.0 or newer.
- Version 0.7.18 adds `tokio_util::io::simplex` for one-direction asynchronous
  I/O.
- Version 0.7.14 adds `tokio_util::io::read_exact_arc` for exact reads backed by
  an `Arc`.
- From 0.7.14, `Either` delegates `AsyncWrite` to its active branch.
- Version 0.7.13 fixes `LinesCodec::decode_eof` handling of invalid UTF-8 at the
  end of input; require it when malformed terminal bytes must be handled
  correctly.

## `tokio-util` task and cancellation tools

- `CancellationToken::run_until_cancelled` arrives in 0.7.12, its owned form in
  0.7.14, and `FutureExt` cancellation adapters in 0.7.16. From 0.7.16,
  cancellation wins when it and the wrapped future become ready together.
- `DropGuardRef` arrives in 0.7.16 for cancelling a borrowed token when its
  guard drops.
- `AbortOnDropHandle` arrives in 0.7.12 and aborts its task on drop; `detach`
  arrives in 0.7.16 to let the task continue independently.
- `JoinMap` is stable from 0.7.16, and `tokio_util::task::JoinQueue` arrives in
  0.7.17.

## `tokio-util` framing and queues

- From 0.7.16, `Framed::with_capacity` applies the capacity to its read buffer
  as well as its write buffer. Version 0.7.17 removes unnecessary trait bounds
  from every `Framed` constructor.
- From 0.7.12, removing the last `DelayQueue` entry wakes a waiting consumer so
  it can observe the queue becoming empty.

## `tokio-stream` compatibility and features

- `tokio-stream` 0.1.13 raises the Rust floor to 1.56, 0.1.15 raises it to
  1.63, and 0.1.16 raises it to 1.70. Version 0.1.14 raises the minimum Tokio
  dependency to 1.15 so `timeout_repeating` compiles.
- Version 0.1.13 adds the aggregate `full` feature.

```toml
tokio-stream = { version = "0.1.13", features = ["full"] }
```

## Watch, timeout, and closure adapters

- `WatchStream::from_changes` is available from 0.1.12 when the stream should
  wait for a later watch value instead of yielding the current value first.
- `StreamExt::timeout_repeating` arrives in 0.1.13 for timeout behavior driven
  by a repeating timer.
- `StreamNotifyClose` arrives in 0.1.13 to emit an explicit closure notification
  before the wrapper terminates.
- `StreamExt::chunks_timeout` can be constructed outside a Tokio runtime from
  0.1.11, allowing synchronous pipeline assembly.
- `ChunksTimeout::into_remainder` arrives in 0.1.18 for recovering an incomplete
  buffered chunk while dismantling the adapter.

## Stream maps and concrete adapters

- `StreamMap::next_many` and `poll_next_many` arrive in 0.1.16 for collecting
  multiple ready keyed items at once.
- Stream adapter concrete types become public in 0.1.16, so signatures and
  stored state can name them.
- `ReceiverStream` and `UnboundedReceiverStream` expose meaningful
  `Stream::size_hint` bounds from 0.1.18.
