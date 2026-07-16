# Companion crates: tokio-util and tokio-stream

Use this reference when selecting or implementing APIs from the included `tokio-util` and `tokio-stream` updates.

## Contents

- [Dependency floors](#dependency-floors)
- [I/O, framing, and codecs](#io-framing-and-codecs)
- [Cancellation and task ownership](#cancellation-and-task-ownership)
- [Task collections and delay queues](#task-collections-and-delay-queues)
- [Stream adapters and batching](#stream-adapters-and-batching)

## Dependency floors

### `tokio-util`

- Version 0.7.12 raises the minimum supported Rust version to 1.70.
- Version 0.7.17 raises it again to Rust 1.71.
- Version 0.7.18 raises the Tokio dependency floor to 1.44.0.

An upgrade to 0.7.18 must satisfy both the Rust 1.71 floor inherited from 0.7.17 and the Tokio 1.44.0 floor.

### `tokio-stream`

Version 0.1.16 raises the minimum supported Rust version to 1.70.

## I/O, framing, and codecs

### Simplex I/O

`tokio-util` 0.7.18 adds `tokio_util::io::simplex`, providing simplex I/O directly without a project-local implementation.

Tokio itself also has `util::SimplexStream` from Tokio 1.40.0. Choose the API from the crate whose dependency and type surface the component already owns.

### Exact reads and asynchronous writes

- `tokio-util` 0.7.14 adds `tokio_util::io::read_exact_arc` for an exact-read operation backed by an `Arc`.
- From `tokio-util` 0.7.14, `Either` delegates `AsyncWrite` to its selected underlying branch. It can satisfy an `AsyncWrite` bound without manual enum dispatch.

### Framed construction and buffers

- Starting with `tokio-util` 0.7.16, the capacity supplied to `Framed::with_capacity` applies to the read buffer as well. Recheck code that assumed it controlled only another side of the framed transport.
- `tokio-util` 0.7.16 adds `FramedWrite::with_capacity` for explicit write-buffer sizing.
- `tokio-util` 0.7.17 removes unnecessary trait bounds from every `Framed` constructor, allowing more codec and transport types to be constructed directly.

### End-of-stream decoding

`tokio-util` 0.7.13 fixes `LinesCodec::decode_eof` handling of invalid UTF-8 at the end of input. Require at least that version when malformed terminal bytes must be reported or processed correctly.

## Cancellation and task ownership

### Cancellation composition

`CancellationToken` gains several ways to compose cancellation with a future:

- `tokio-util` 0.7.12 adds `CancellationToken::run_until_cancelled`.
- Version 0.7.14 adds the owned form, allowing composition without a borrowed token lifetime.
- Version 0.7.16 adds `CancellationToken` adapters to `FutureExt`.
- From 0.7.16, `run_until_cancelled` is biased toward cancellation when the token and wrapped future become ready simultaneously.

Account for that tie-breaking rule when the wrapped future has side effects at completion.

### Borrowed cancellation guards

`tokio-util` 0.7.16 adds `DropGuardRef`, a reference-based guard that cancels a `CancellationToken` on drop without requiring ownership of the token.

### Abort-on-drop handles

- `tokio-util` 0.7.12 adds `AbortOnDropHandle`, which aborts its task when the wrapper is dropped.
- Version 0.7.16 adds `AbortOnDropHandle::detach`, allowing the task to continue independently.
- Version 0.7.18 removes unnecessary trait bounds from `AbortOnDropHandle`'s `Debug` implementation.

Choose at least 0.7.16 when ownership may deliberately detach, and avoid accidental early drops when abortion is not desired.

## Task collections and delay queues

### Join collections

- `tokio-util` 0.7.16 stabilizes `JoinMap`.
- Version 0.7.17 adds `tokio_util::task::JoinQueue`.
- Version 0.7.18 removes unnecessary trait bounds from `JoinQueue`'s `Debug` implementation.

### Removing the final delayed item

`tokio-util` 0.7.12 makes `DelayQueue` wake a waiter when its final item is removed. Waiters can now observe the transition to an empty queue without an unrelated wakeup.

## Stream adapters and batching

### Batch `StreamMap` retrieval

`tokio-stream` 0.1.16 adds:

- `StreamMap::next_many` for asynchronously collecting multiple mapped items per operation.
- `StreamMap::poll_next_many` for manual poll-based batched retrieval.

### Nameable adapter types

`tokio-stream` 0.1.16 makes stream adapter types public. The concrete types returned by stream combinators can be named in structure fields, aliases, and function signatures.

### Recover partial timed chunks

`tokio-stream` 0.1.18 adds `ChunksTimeout::into_remainder`. Consuming an adapter can return the items in its current incomplete chunk instead of discarding them.

### Receiver stream bounds

In `tokio-stream` 0.1.18, `ReceiverStream` and `UnboundedReceiverStream` return meaningful `Stream::size_hint` values. Consumers can use their lower and upper item-count bounds for allocation or planning.
