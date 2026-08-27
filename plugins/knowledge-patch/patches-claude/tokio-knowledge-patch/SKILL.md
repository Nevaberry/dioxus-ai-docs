---
name: tokio-knowledge-patch
description: Tokio
version: "1.52.0"
license: MIT
metadata:
  author: Nevaberry
---


# Tokio Knowledge Patch

Use this skill for version-sensitive Tokio work: dependency selection, runtime
construction, task behavior, channels, asynchronous I/O, networking, processes,
signals, and the companion `tokio-util` and `tokio-stream` crates. Check the
project manifest first and apply only guidance relevant to its pinned versions.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility.md](references/compatibility.md) | Toolchain floors, safe patch releases, target support, and unstable configuration |
| [runtime-and-tasks.md](references/runtime-and-tasks.md) | Runtime construction, scheduling, task APIs, metrics, hooks, and diagnostics |
| [synchronization.md](references/synchronization.md) | `watch`, `broadcast`, `mpsc`, `oneshot`, `Notify`, semaphores, and `RwLock` |
| [io-and-filesystem.md](references/io-and-filesystem.md) | Async I/O types, files, pipes, AIO, io_uring, and standard output |
| [networking-process-signals.md](references/networking-process-signals.md) | Sockets, target-specific networking, child processes, and signals |
| [tokio-util-and-stream.md](references/tokio-util-and-stream.md) | Compatibility and APIs in `tokio-util` and `tokio-stream` |

## Upgrade gates

### Select safe patch releases

- Use at least 1.42.1 when a `broadcast` channel may carry `Send` but `!Sync`
  values; 1.42.0 has an unsynchronized-clone soundness bug.
- On the 1.43 line, use 1.43.4 to include the pidfd, receiverless-broadcast,
  and closed-and-drained `mpsc::try_recv` corrections.
- Use at least 1.45.1 on `wasm32-unknown-unknown`; time-based metrics in 1.45.0
  can make valid `Instant::now()` calls panic.
- Use at least 1.46.1 when task hooks inspect `TaskMeta::spawned_at` for tasks
  created with `tokio::spawn`.
- On the 1.47 line, use 1.47.5 for channel length, permit wakeup, outstanding
  permit, and `RwLock` limit behavior; 1.47.4 also fixes `recv_many` on a closed
  channel, and 1.47.2 fixes `join!`/`try_join!` hygiene.
- Use at least 1.51.1 when semaphore closure, Linux UDP pending errors, or
  cancellable io_uring opens matter.
- Do not remain on 1.52.0 when using `spawn_blocking`; require 1.52.1 to avoid a
  sharded blocking-queue hang.
- Use 1.53.1 for Windows signal support at the Rust 1.71 minimum and for the
  unstable alternate-timer cancellation race fix.

See [compatibility.md](references/compatibility.md) for exact patch-line floors
and older-line backports.

### Enforce compiler and dependency floors

| Package | Minimum toolchain or dependency |
| --- | --- |
| Tokio from 1.39.0 | Rust 1.70 |
| Tokio from 1.48.0 | Rust 1.71 |
| `tokio-util` 0.7.12 | Rust 1.70 |
| `tokio-util` 0.7.17 | Rust 1.71 |
| `tokio-util` 0.7.18 | Tokio 1.44.0 |
| `tokio-stream` 0.1.16 | Rust 1.70 |

### Adjust rejected or changed code

- Put every standard-library socket into nonblocking mode before a Tokio
  `from_std` conversion; blocking sockets panic from 1.44.0 onward.

```rust
let listener = std::net::TcpListener::bind(addr)?;
listener.set_nonblocking(true)?;
let listener = tokio::net::TcpListener::from_std(listener)?;
```

- Keep `runtime::Builder::event_interval` nonzero; `event_interval(0)` panics
  from 1.50.0 onward.
- Keep blocking work out of futures and destructors polled or dropped by a
  `LocalSet` from 1.46.0 onward. Use `spawn_blocking` or move it outside.
- Replace deprecated `TcpStream::set_linger` and `TcpSocket::set_linger` calls.
  Use `TcpStream::set_zero_linger()` for abortive close from 1.50.0.
- Await, retain, or explicitly discard `JoinHandle::abort_handle()` and
  `Notify::notified()` results; their types are `#[must_use]`.
- Do not interpret a signal receive result of `None` as shutdown; signal
  listeners remain open from 1.50.0 onward.
- Expect task-owned state to be dropped before its `JoinHandle` completes from
  1.50.0 onward.
- Reuse or synchronize one Tokio standard-output handle when write ordering
  matters; independent handles may reorder writes.

### Update unstable builds

- Select `taskdump` and `io_uring` with Cargo features from 1.48.0; replace the
  former custom `--cfg` switches.
- Pass `LocalOptions` by value to unstable `Builder::build_local` from 1.46.0.
- Migrate off the removed unstable alternate multi-threaded runtime before
  using 1.45.0 or newer.
- Treat io_uring as opportunistic: Tokio may disable it after `EPERM`, and the
  operations available through the backend depend on the Tokio release.

## Runtime and task quick reference

### Choose local execution deliberately

- Use stable `tokio::runtime::LocalRuntime` from 1.51.0 for thread-local
  `!Send` tasks. Earlier forms were unstable.
- The unstable macro flavor `#[tokio::main(flavor = "local")]` is available
  from 1.48.0.
- Use stable `runtime::id::Id` and `LocalSet::id()` from 1.49.0 for diagnostic
  identity.
- From 1.51.0, assign runtime names and use `runtime::worker_index()` for
  per-worker diagnostic context.

### Preserve cooperative scheduling

- `watch` receives and `broadcast::Receiver` participate in cooperative
  scheduling from 1.41.0.
- `select!` consumes cooperative budget from 1.44.0.
- Use `task::coop` for custom asynchronous resources from 1.44.0;
  `cooperative` and `poll_proceed` arrive in 1.47.0.
- `yield_now` takes effect immediately inside `block_in_place` from 1.42.0.

### Use current task primitives

- Use `tokio::sync::SetOnce` from 1.47.0 for asynchronously observable,
  single-assignment state.
- Use `Notify::notified_owned()` and `OwnedNotified` from 1.47.0 when the
  notification future must not borrow its `Notify`.
- Extend `JoinSet<T>` from an iterator from 1.49.0.
- Sort `task::Id` values or use them as ordered keys from 1.48.0.
- Use `LocalKey::try_get()` from 1.48.0 when missing task-local state should not
  panic.

### Interpret metrics carefully

- Stable global queue depth arrives in 1.41.0; stable per-worker busy duration
  and park/unpark counts arrive in 1.45.0.
- Unstable spawned-task totals, combined park/unpark counts, and worker thread
  IDs arrive in 1.39.0.
- Unstable H2 histogram configuration and renamed histogram APIs arrive in
  1.41.0.
- Do not use `num_alive_tasks` as an exact concurrent invariant; its samples
  are not strongly consistent.

Read [runtime-and-tasks.md](references/runtime-and-tasks.md) for task hooks,
poll callbacks, task dumps, spawn locations, timers, and lifecycle ordering.

## Synchronization quick reference

- Await `broadcast::Sender::closed()` to stop producers after every receiver is
  gone, and use `broadcast::WeakSender` when an observer must not keep the
  channel open; both are available from 1.44.0.
- Use `mpsc::Receiver::blocking_recv_many` from 1.41.0 for synchronous batched
  receives.
- After `Receiver::close()`, a drained `try_recv()` reports `Disconnected` from
  1.43.4, except while outstanding permits can still send, where it reports
  `Empty` from 1.47.5.
- `watch::Sender<T>` implements `Default` when its value can be defaulted from
  1.39.0.
- Tokio mpsc types satisfy unwind-safety bounds from 1.40.0.

Read [synchronization.md](references/synchronization.md) before relying on close,
permit, wakeup, or fairness semantics.

## I/O and networking quick reference

- Use `tokio::io::util::SimplexStream` from 1.40.0 or
  `tokio_util::io::simplex` from `tokio-util` 0.7.18.
- Name chained readers with public `tokio::io::Chain` and inspect file buffer
  limits with `File::max_buf_size()` from 1.48.0.
- Use Unix pipe endpoint `try_io` and `AioSource::register_borrowed` from 1.52.0
  for immediate pipe operations and borrowed AIO registration.
- Use `TcpStream::{quickack,set_quickack}` from 1.48.0 and IPv6 `TCLASS`
  support from 1.49.0 where supported by the target.
- Configure Unix child process groups with stable `Command::process_group` from
  1.40.0. `Command::spawn_with` arrives in 1.45.0 and accepts `FnOnce` from
  1.48.0.

Consult the I/O and networking references for target support, backend details,
socket-address APIs, process races, and signal behavior.

## Companion crate quick reference

- In `tokio-util`, compose cancellation with `run_until_cancelled`, its owned
  form, or `FutureExt`; cancellation wins a simultaneous-ready tie from 0.7.16.
- Use `AbortOnDropHandle` from 0.7.12 and detach it from 0.7.16.
- Use stable `JoinMap` from 0.7.16 and `JoinQueue` from 0.7.17.
- Recheck buffer assumptions: `Framed::with_capacity` applies its capacity to
  both read and write buffers from 0.7.16.
- In `tokio-stream`, batch `StreamMap` output with `next_many` or
  `poll_next_many` from 0.1.16, recover timed-chunk remainder with
  `ChunksTimeout::into_remainder` from 0.1.18, and use meaningful receiver
  stream size hints from 0.1.18.

Read [tokio-util-and-stream.md](references/tokio-util-and-stream.md) for all
companion-crate features, fixes, and exact floors.
