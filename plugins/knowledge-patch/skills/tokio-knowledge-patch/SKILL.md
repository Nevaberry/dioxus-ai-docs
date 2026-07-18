---
name: tokio-knowledge-patch
description: Tokio
license: MIT
version: "1.52.0"
metadata:
  author: Nevaberry
---

# Tokio Knowledge Patch

Baseline: Tokio through 1.39.x. Covered range: Tokio 1.39.0 through 1.52.0, plus the included `tokio-util` and `tokio-stream` updates.

Use this patch to choose safe dependency floors, account for changed behavior, and select APIs added after the baseline. Check the detailed topic reference before implementing version-sensitive code.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility.md](references/compatibility.md) | Rust and dependency floors, safe patch releases, upgrade regressions, build flags |
| [runtime-and-tasks.md](references/runtime-and-tasks.md) | Runtime construction, local execution, cooperative scheduling, task APIs, metrics, tracing |
| [synchronization.md](references/synchronization.md) | `watch`, `broadcast`, `mpsc`, `oneshot`, `Notify`, permits, and single-assignment state |
| [io-and-filesystem.md](references/io-and-filesystem.md) | Async I/O types, files, pipes, AIO, and unstable io_uring filesystem support |
| [networking-process-signals.md](references/networking-process-signals.md) | Socket behavior and options, platform targets, child processes, and signals |
| [tokio-util-and-stream.md](references/tokio-util-and-stream.md) | `tokio-util` 0.7.12–0.7.18 and `tokio-stream` 0.1.16–0.1.18 |

## Breaking changes and upgrade gates

### Select safe patch releases

- Avoid Tokio 1.39.0: it is yanked. Use 1.39.3 on the 1.39 line to include the timer-wheel rollback, temporary-lifetime `select!` restoration, and Unix abstract-address restoration.
- Use at least 1.42.1 when a `broadcast` channel may carry a `Send` but non-`Sync` value; 1.42.0 has an unsynchronized-clone soundness bug.
- Use 1.43.4 on the 1.43 line for the pidfd, receiverless `broadcast`, and closed-and-drained `mpsc::try_recv` fixes.
- Use at least 1.45.1 on `wasm32-unknown-unknown`; 1.45.0 can panic while collecting time-based metrics.
- Use at least 1.46.1 when task hooks consume `TaskMeta::spawned_at` for tasks created with `tokio::spawn`.
- Use 1.51.3 on the 1.51 line for the accumulated channel and `RwLock` fixes, and at least 1.51.1 for Linux UDP error reporting and the cancelled io_uring-open descriptor fix.
- Use at least 1.52.1; 1.52.0's sharded `spawn_blocking` queue can hang.

See [compatibility.md](references/compatibility.md) for the complete patch-level behavior list.

### Enforce compiler and dependency floors

| Package floor | Requirement |
| --- | --- |
| Tokio 1.39.0 | Rust 1.70 or newer |
| Tokio 1.48.0 | Rust 1.71 or newer |
| `tokio-util` 0.7.12 | Rust 1.70 or newer |
| `tokio-util` 0.7.17 | Rust 1.71 or newer |
| `tokio-util` 0.7.18 | Tokio 1.44.0 or newer |
| `tokio-stream` 0.1.16 | Rust 1.70 or newer |

### Adjust changed or rejected code

- Put standard-library sockets into nonblocking mode before any Tokio `from_std` conversion. Since 1.44.0, passing a blocking socket panics.

```rust
let listener = std::net::TcpListener::bind(addr)?;
listener.set_nonblocking(true)?;
let listener = tokio::net::TcpListener::from_std(listener)?;
```

- Keep `runtime::Builder::event_interval` nonzero; passing `0` panics since 1.50.0.
- Do not call Tokio's in-place blocking operation while polling or dropping a `LocalSet` as of 1.46.0. Move blocking work to `spawn_blocking` or outside the local set.
- Replace deprecated `TcpStream::set_linger` and `TcpSocket::set_linger` calls. For an abortive close, use `TcpStream::set_zero_linger()` from 1.50.0.
- Consume or explicitly discard the results of `JoinHandle::abort_handle()` and `Notify::notified()`; their types became `#[must_use]` in 1.40.0 and 1.41.0.
- Stop treating signal-stream `None` as a shutdown path. Since 1.50.0, signal listeners are guaranteed to remain open; use explicit cancellation.
- Expect a task future's retained state to be dropped before its `JoinHandle` completes as of 1.50.0.
- Account for changed diagnostics: formatting a panicked task's `JoinError` includes the panic message since 1.40.0.

### Update unstable configuration

- Enable `taskdump` and `io_uring` as Cargo features as of 1.48.0; do not use the former custom `--cfg` switches.
- Pass `LocalOptions` by value to unstable `Builder::build_local` as of 1.46.0.
- Migrate away from the removed unstable alternate multi-threaded runtime as of 1.45.0.
- Treat io_uring as opportunistic: Tokio can disable it after `EPERM` and checks kernel opcode support before dispatch.

## Runtime and task quick reference

### Choose local execution deliberately

- Use stable `tokio::runtime::LocalRuntime` from 1.51.0 for thread-local `!Send` tasks. It first appeared as an unstable API in 1.41.0.
- With unstable APIs on 1.48.0, `#[tokio::main(flavor = "local")]` and the corresponding test macro provide a local-runtime macro entry point.
- Use stable `runtime::id::Id` and `LocalSet::id()` from 1.49.0 to identify runtimes and local sets.
- From 1.51.0, assign runtime names and call `tokio::runtime::worker_index()` for diagnostic context.

### Preserve cooperative scheduling

- `watch` receives and `broadcast::Receiver` became cooperative in 1.41.0.
- `select!` became budget-aware in 1.44.0.
- Use `tokio::task::coop` for custom resources from 1.44.0; `cooperative` and `poll_proceed` are available from 1.47.0.
- `yield_now` takes effect immediately inside `block_in_place` as of 1.42.0.
- Use `biased;` with `join!` or `try_join!` from 1.46.0 only when declaration-order polling is intentional.

```rust
let (first, second) = tokio::join!(biased; first_job(), second_job());
```

### Use newer task primitives

- Use `tokio::sync::SetOnce` from 1.47.0 for single assignment.
- Use `Notify::notified_owned()` and `OwnedNotified` from 1.47.0 when the notification future must not borrow its `Notify`.
- Extend a `JoinSet<T>` from an iterator with `Extend` as of 1.49.0.
- Sort `task::Id` values or use them as ordered keys as of 1.48.0.
- Use `LocalKey::try_get()` from 1.48.0 when absent task-local state should not panic.

### Read metrics with their guarantees

- Stable per-worker busy duration and park/unpark counts arrive in 1.45.0.
- Unstable spawned-task totals, combined worker park/unpark counts, and worker thread IDs arrive in 1.39.0.
- Unstable H2 histogram configuration and renamed histogram APIs arrive in 1.41.0.
- Do not use `num_alive_tasks` as an exact concurrent invariant; its samples are not strongly consistent as of 1.49.0.

Read [runtime-and-tasks.md](references/runtime-and-tasks.md) for lifecycle hooks, poll callbacks, task dumps, spawn locations, and eager driver handoff.

## Synchronization quick reference

- Await `broadcast::Sender::closed()` from 1.44.0 to stop producers after all receivers disappear.
- Hold a `broadcast::WeakSender` from 1.44.0 when an observer must not keep a channel open.
- Inspect `oneshot::Receiver` synchronously with `is_empty()` and `is_terminated()` from 1.44.0.
- Compare an `mpsc::OwnedPermit` with another permit or sender using `same_channel` and `same_channel_as_sender` from 1.46.0.
- Derive `Default` for structures containing `watch::Sender<T>` when `T: Default` as of 1.39.0.
- Use Tokio mpsc types across unwind-safety bounds as of 1.40.0.

Read [synchronization.md](references/synchronization.md) before depending on close, permit, wakeup, or fairness semantics.

## I/O, networking, process, and signal quick reference

### I/O and files

- Use `util::SimplexStream` from 1.40.0, or `tokio_util::io::simplex` from `tokio-util` 0.7.18.
- Name the concrete chained-reader type with public `tokio::io::Chain` from 1.48.0.
- Read a file's configured buffer limit with `File::max_buf_size()` from 1.48.0; clones now preserve that limit.
- Use `unix::pipe::{Sender, Receiver}::try_io` from 1.52.0 for custom nonblocking endpoint operations.
- Use `AioSource::register_borrowed` from 1.52.0 to register a borrowed resource without transferring ownership.

### Networking

- Use Unix `SocketAddr` standard-library conversions from 1.41.0, cloning from 1.46.0, and `as_abstract_name()` from 1.48.0.
- Use `TcpStream::{quickack,set_quickack}` from 1.48.0 where the platform exposes TCP quick acknowledgements.
- Configure IPv6 `TCLASS` through Tokio from 1.49.0.
- Require 1.46.0 when successful macOS `TcpStream::shutdown` behavior matters.

### Processes and signals

- Configure Unix child process groups with stable `Command::process_group` from 1.40.0.
- Use `Command::spawn_with` from 1.45.0; its callback may be `FnOnce` from 1.48.0.
- Treat `Child::start_kill()` after normal exit as a successful cleanup race from 1.44.0.
- Account for illumos realtime signals from 1.43.0 and Windows console close, logoff, and shutdown events from 1.44.0.

Read [io-and-filesystem.md](references/io-and-filesystem.md) and [networking-process-signals.md](references/networking-process-signals.md) for backend and target details.

## Companion crate quick reference

### `tokio-util`

- Compose cancellation with `run_until_cancelled`, its owned form, or `FutureExt` adapters; cancellation wins a simultaneous-ready tie from 0.7.16.
- Use `AbortOnDropHandle` from 0.7.12 and detach it from 0.7.16.
- Use stable `JoinMap` from 0.7.16 and `JoinQueue` from 0.7.17.
- Recheck framing capacity assumptions: from 0.7.16, `Framed::with_capacity` applies the capacity to the read buffer too.

### `tokio-stream`

- Batch `StreamMap` results with `next_many` or `poll_next_many` from 0.1.16.
- Name public stream adapter types from 0.1.16.
- Recover an incomplete timed chunk with `ChunksTimeout::into_remainder` from 0.1.18.
- Use meaningful receiver-stream `size_hint` bounds from 0.1.18.

Read [tokio-util-and-stream.md](references/tokio-util-and-stream.md) for all included companion-crate changes and exact release floors.
