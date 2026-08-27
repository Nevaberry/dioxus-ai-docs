---
name: tokio-knowledge-patch
description: Tokio
version: "1.52.0"
license: MIT
metadata:
  author: Nevaberry
---


# Tokio Knowledge Patch

Use this patch when upgrading Tokio, selecting a safe patch release, or writing
version-sensitive runtime, synchronization, I/O, networking, process, signal,
`tokio-util`, or `tokio-stream` code. Check the detailed topic reference before
depending on unstable APIs or patch-level fixes.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility.md](references/compatibility.md) | Rust and dependency floors, safe patch releases, build configuration, target support |
| [runtime-and-tasks.md](references/runtime-and-tasks.md) | Runtime construction, local execution, task APIs, scheduling, hooks, metrics, tracing |
| [synchronization.md](references/synchronization.md) | `watch`, `broadcast`, `mpsc`, `oneshot`, `Notify`, semaphores, permits, and single-assignment state |
| [io-and-filesystem.md](references/io-and-filesystem.md) | Async I/O types, files, pipes, AIO, io_uring filesystem support, and standard output |
| [networking-process-signals.md](references/networking-process-signals.md) | Sockets, networking targets, child processes, and signals |
| [tokio-util-and-stream.md](references/tokio-util-and-stream.md) | Companion-crate dependency floors, task utilities, codecs, cancellation, and stream adapters |

## Breaking changes and upgrade gates

### Select safe patch releases

- Use at least 1.42.1 when a `broadcast` channel can carry a `Send` but `!Sync`
  value; 1.42.0 clones such values without synchronization.
- On the 1.43 line, use at least 1.43.2 for pidfd-backed child waiting, 1.43.3
  for receiverless `broadcast::Sender` state, and 1.43.4 for closed-and-drained
  `mpsc::Receiver::try_recv` behavior.
- Use at least 1.45.1 on `wasm32-unknown-unknown`; 1.45.0 can panic when
  time-based metrics call `Instant::now()`.
- Use at least 1.46.1 when task hooks inspect `TaskMeta::spawned_at` for tasks
  created with `tokio::spawn`.
- On the 1.47 line, use 1.47.2 for `join!`/`try_join!` macro hygiene, 1.47.4
  for closed-channel `recv_many`, and 1.47.5 for corrected mpsc length, permit
  wakeups, outstanding-permit state, and nonzero `RwLock` reader limits.
- Use at least 1.51.1 when semaphore closure after forgotten permits, Linux UDP
  pending errors, or cancelled io_uring opens matter.
- Do not remain on 1.52.0 when using `spawn_blocking`; use at least 1.52.1 to
  avoid the sharded blocking-queue hang.
- Use 1.51.4 or 1.52.4 when a `before_park` callback can schedule work, so the
  runtime does not skip the driver.
- Use 1.53.1 for Tokio signal support on Windows with the Rust 1.71 toolchain;
  1.53.0 accidentally used a newer standard-library API.

See [compatibility.md](references/compatibility.md) for the complete upgrade
and target matrix.

### Enforce compiler and dependency floors

| Package floor | Requirement |
| --- | --- |
| Tokio 1.39.0 | Rust 1.70 or newer |
| Tokio 1.48.0 | Rust 1.71 or newer |
| `tokio-util` 0.7.12 | Rust 1.70 or newer |
| `tokio-util` 0.7.17 | Rust 1.71 or newer |
| `tokio-util` 0.7.18 | Tokio 1.44.0 or newer |
| `tokio-stream` 0.1.13 | Rust 1.56 or newer |
| `tokio-stream` 0.1.15 | Rust 1.63 or newer |
| `tokio-stream` 0.1.16 | Rust 1.70 or newer |
| `tokio-stream` 0.1.14 | Tokio 1.15 or newer |

### Adjust rejected or changed code

- Put standard-library sockets into nonblocking mode before any Tokio
  `from_std` conversion. Since 1.44.0, passing a blocking socket panics.

```rust
let listener = std::net::TcpListener::bind("127.0.0.1:0")?;
listener.set_nonblocking(true)?;
let listener = tokio::net::TcpListener::from_std(listener)?;
```

- Keep `runtime::Builder::event_interval` nonzero; passing `0` panics as of
  1.50.0.
- Keep in-place blocking operations out of futures and destructors driven by a
  `LocalSet` as of 1.46.0. Move blocking work to `spawn_blocking`.
- Replace deprecated `TcpStream::set_linger` and `TcpSocket::set_linger` calls.
  Use `TcpStream::set_zero_linger()` from 1.50.0 for abortive close behavior.
- Await, retain, or explicitly discard `JoinHandle::abort_handle()` and
  `Notify::notified()` results; their types are `#[must_use]` as of 1.40.0 and
  1.41.0 respectively.
- Do not interpret signal-stream `None` as shutdown. Signal listeners remain
  open as of 1.50.0; arrange explicit cancellation.
- Expect task-owned state to be dropped before its `JoinHandle` completes as of
  1.50.0.
- Expect a panicked task's formatted `JoinError` to include the panic message
  as of 1.40.0.
- Reuse or synchronize one Tokio standard-output handle when write ordering
  matters; multiple handles can reorder writes.

### Update unstable configuration

- Select `taskdump` and `io_uring` with Cargo features as of 1.48.0, replacing
  their former custom `--cfg` switches.
- Pass `LocalOptions` by value to `runtime::Builder::build_local` as of 1.46.0.
- Migrate away from the removed unstable alternate multi-threaded runtime as of
  1.45.0.
- Treat io_uring as opportunistic: Tokio disables it on `EPERM`, and later
  filesystem operations remain explicitly unstable.

## Runtime and task quick reference

### Choose local execution deliberately

- Use stable `tokio::runtime::LocalRuntime` from 1.51.0 for local task
  execution. It first appeared as unstable in 1.41.0.
- With unstable APIs on 1.48.0, use `#[tokio::main(flavor = "local")]` for a
  macro-created local runtime.
- Use stable `runtime::id::Id` and `LocalSet::id()` from 1.49.0 to identify
  runtimes and local sets.
- From 1.51.0, assign runtime names and call
  `tokio::runtime::worker_index()` for per-worker diagnostic context.

### Preserve cooperative scheduling

- `watch` receives and `broadcast::Receiver` participate in cooperative
  scheduling as of 1.41.0.
- `select!` consumes cooperative task budget as of 1.44.0.
- Use `task::coop` for custom resources from 1.44.0; `cooperative` and
  `poll_proceed` are available from 1.47.0.
- `yield_now` takes effect immediately inside `block_in_place` as of 1.42.0.

### Use task and runtime instrumentation

- Stable `RuntimeMetrics::global_queue_depth` and task `Id` APIs arrive in
  1.41.0.
- Stable per-worker busy duration and park/unpark counts arrive in 1.45.0.
- Unstable spawned-task totals, combined worker park/unpark counts, and worker
  thread IDs arrive in 1.39.0.
- The runtime metrics API adds task schedule latency in 1.53.0.
- Do not use `num_alive_tasks` as an exact concurrent invariant; samples are
  not strongly consistent as of 1.49.0.

Read [runtime-and-tasks.md](references/runtime-and-tasks.md) for lifecycle and
poll hooks, tracing, task dumps, caller-aware timeouts, and driver handoff.

## Synchronization quick reference

- Use `tokio::sync::SetOnce` from 1.47.0 for asynchronously observable
  single-assignment state.
- Use `Notify::notified_owned()` and `OwnedNotified` from 1.47.0 when a
  notification future must not borrow its `Notify`.
- Await `broadcast::Sender::closed()` from 1.44.0 to stop a producer after all
  receivers disappear; use `broadcast::WeakSender` when an observer must not
  keep the channel open.
- Use `mpsc::Receiver::blocking_recv_many` from 1.41.0 for blocking batched
  receives.
- Derive `Default` for state containing `watch::Sender<T>` as of 1.39.0 when
  `T` satisfies the implementation's bounds.
- Use Tokio mpsc values across unwind-safety bounds as of 1.40.0.

Read [synchronization.md](references/synchronization.md) before depending on
close, permit, wakeup, or fairness semantics.

## I/O, networking, process, and signal quick reference

### I/O and files

- Use `io::util::SimplexStream` from 1.40.0, or
  `tokio_util::io::simplex` from `tokio-util` 0.7.18.
- Use public `tokio::io::Chain` from 1.48.0 when a chained reader's concrete
  type must be named. From 1.53.0, a zero-length read no longer advances it.
- Inspect a file's buffer limit with `File::max_buf_size()` from 1.48.0; file
  clones preserve that limit.
- Convert `OwnedFd` or `OwnedHandle` directly into `tokio::fs::File` from
  1.53.0.
- Use Unix pipe `try_io` and `AioSource::register_borrowed` from 1.52.0 for
  immediate pipe operations and borrowed AIO registration.

### Networking, processes, and signals

- Use Unix `SocketAddr` conversions from 1.41.0 and
  `as_abstract_name()` from 1.48.0; 1.53.0 expands its inspection methods.
- Use `TcpStream::{quickack,set_quickack}` from 1.48.0 where TCP quick
  acknowledgements are exposed, and configure IPv6 `TCLASS` from 1.49.0.
- Require 1.46.0 when successful macOS `TcpStream::shutdown` matters.
- Configure Unix child process groups with stable `Command::process_group`
  from 1.40.0.
- Use `Command::spawn_with` from 1.45.0; its callback may consume captured
  values through `FnOnce` as of 1.48.0.
- Treat `Child::start_kill()` after normal exit as a successful cleanup race as
  of 1.44.0.

Read [io-and-filesystem.md](references/io-and-filesystem.md) and
[networking-process-signals.md](references/networking-process-signals.md) for
backend behavior and target-specific support.

## Companion-crate quick reference

### `tokio-util`

- Compose cancellation with `run_until_cancelled`, its owned form, or
  `FutureExt` adapters; cancellation wins a simultaneous-ready tie from
  0.7.16.
- Use `AbortOnDropHandle` from 0.7.12 and detach it from 0.7.16.
- Use stable `JoinMap` from 0.7.16 and `JoinQueue` from 0.7.17.
- Recheck capacity assumptions: from 0.7.16, `Framed::with_capacity` applies
  its capacity to the read buffer too.

### `tokio-stream`

- Use `WatchStream::from_changes` from 0.1.12 to skip the current value and
  wait for later watch-channel changes.
- Batch `StreamMap` results with `next_many` or `poll_next_many` from 0.1.16.
- Recover an incomplete timed chunk with `ChunksTimeout::into_remainder` from
  0.1.18.
- Use meaningful receiver-stream `size_hint` bounds from 0.1.18.

Read [tokio-util-and-stream.md](references/tokio-util-and-stream.md) for all
companion-crate behavior and release floors.
