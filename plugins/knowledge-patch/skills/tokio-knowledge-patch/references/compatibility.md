# Compatibility and upgrade floors

Use this reference when selecting dependency versions, raising a compiler floor, or reviewing an upgrade for behavior that can break builds or production assumptions.

## Contents

- [Compiler and dependency floors](#compiler-and-dependency-floors)
- [Safe Tokio patch releases](#safe-tokio-patch-releases)
- [Source and behavior migrations](#source-and-behavior-migrations)
- [Unstable build configuration](#unstable-build-configuration)

## Compiler and dependency floors

### Tokio

- Tokio 1.39.0 raises the minimum supported Rust version (MSRV) to 1.70.
- Tokio 1.48.0 raises the MSRV again to 1.71.

Check the workspace compiler, CI matrix, container images, and downstream library policy before raising either dependency floor.

### Companion crates

- `tokio-util` 0.7.12 requires Rust 1.70 or newer.
- `tokio-util` 0.7.17 requires Rust 1.71 or newer.
- `tokio-util` 0.7.18 raises its Tokio dependency floor to 1.44.0. Satisfy both its Rust and Tokio floors.
- `tokio-stream` 0.1.16 requires Rust 1.70 or newer.

These changes belong to the included `tokio-util` and `tokio-stream` batches.

## Safe Tokio patch releases

### 1.39 line

Tokio 1.39.0 is yanked because of a buggy timer-wheel change. Tokio 1.39.1 reverts that change, 1.39.2 restores `select!` expressions that rely on temporary lifetime extension, and 1.39.3 restores Unix abstract-namespace socket addresses. Prefer 1.39.3 when constrained to this line.

### 1.42 line

Tokio 1.42.1 fixes unsynchronized cloning in `broadcast` channels carrying values that implement `Send` but not `Sync`. Do not remain on 1.42.0 when such values can traverse a broadcast channel.

### 1.43 line

Prefer Tokio 1.43.4 when constrained to this line:

- 1.43.2 fixes process-driver panics caused by spurious pidfd wakeups.
- 1.43.3 marks the receiverless channel made by `broadcast::Sender::new()` as closed.
- 1.43.4 makes a drained, explicitly closed `mpsc::Receiver::try_recv()` return `TryRecvError::Disconnected` instead of `TryRecvError::Empty`.

### 1.45 line

Tokio 1.45.0 can panic on `wasm32-unknown-unknown` because time-based metrics call `Instant::now()`. Tokio 1.45.1 disables those metrics on that target; require at least that patch release.

### 1.46 line

Unstable `TaskMeta::spawned_at` reports the wrong source location to runtime task hooks for work launched with `tokio::spawn` in 1.46.0. Tokio 1.46.1 corrects hook locations; task-tracing event locations were already correct.

### 1.51 line

Prefer Tokio 1.51.3 when constrained to this line. The line's synchronization fixes include:

- Prevent `mpsc::Receiver::len()` underflow.
- Wake receivers when an `OwnedPermit` is released.
- Return `TryRecvError::Empty` while a closed channel still has outstanding permits.
- Reject an `RwLock` maximum-reader count of zero.
- Correct `Notify::notify_waiters` priority.
- Avoid a `recv_many` panic when a closed channel is read into a non-empty destination vector.
- Prevent semaphores from reopening after permits have been forgotten.

Tokio 1.51.1 also surfaces Linux UDP `SO_ERROR` failures from receive operations. With unstable io_uring enabled, it avoids leaking a file descriptor when an open operation is cancelled.

### 1.52 line

Tokio 1.52.0's sharded `spawn_blocking` queue can cause blocking jobs to hang. Tokio 1.52.1 reverts that queue; require at least 1.52.1.

## Source and behavior migrations

### Results that must be used

- Since 1.40.0, `JoinHandle::abort_handle()` is `#[must_use]`. Bind, use, or explicitly discard its returned handle when warnings are denied.
- Since 1.41.0, `Notified` is `#[must_use]`. Await, store, or explicitly discard the future returned by `Notify::notified()`.

### Runtime and socket preconditions

- Since 1.44.0, Tokio networking `from_std` constructors panic for blocking sockets. Call the standard socket's `set_nonblocking(true)` before conversion.
- Since 1.46.0, `LocalSet::poll` and the `LocalSet` drop path reject Tokio's in-place blocking operation. Use `spawn_blocking` or perform the blocking work outside the local set.
- Since 1.50.0, `runtime::Builder::event_interval(0)` panics. Validate dynamically derived values and require a nonzero interval.

### Deprecated and changed APIs

- Tokio 1.49.0 deprecates `TcpStream::set_linger` and `TcpSocket::set_linger`. Migrate code or handle the warning explicitly.
- Tokio 1.50.0 adds `TcpStream::set_zero_linger()` as the supported way to request a zero-duration linger and an abortive close.
- Tokio 1.46.0 changes unstable `runtime::Builder::build_local` to take `LocalOptions` by value: use `build_local(options)`, not `build_local(&options)`.
- Tokio 1.45.0 removes the unstable alternate multi-threaded runtime. Move experimental users to a supported runtime implementation.

### Observable behavior

- Since 1.40.0, displaying a `JoinError` for a panicked task includes the panic message. Update exact diagnostic assertions and log-processing assumptions.
- Since 1.50.0, Tokio's default runtime thread name is short enough for Linux's thread-name limit. Configure `Builder::thread_name` when external tooling depends on a fixed label.
- Since 1.50.0, a spawned task is destroyed before its `JoinHandle` completes. After `await` returns, destructors for state retained by the task future have already run.
- Since 1.50.0, signal listeners are guaranteed not to yield `None`. Use a separate cancellation branch instead of relying on stream closure to stop a listener.

## Unstable build configuration

Tokio 1.48.0 moves the unstable `taskdump` and `io_uring` modes from custom `--cfg` flags to Cargo features. Put these opt-ins in dependency feature configuration.

Enabling io_uring does not guarantee that it remains active or that every operation uses it:

- Since 1.49.0, Tokio disables the io_uring backend after `EPERM`.
- Since 1.50.0, Tokio checks kernel opcode support before choosing an operation.

Keep a working fallback path and avoid using feature presence as proof of runtime kernel support.
