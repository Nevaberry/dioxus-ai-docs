# Compatibility and upgrade floors

## Rust and dependency floors

- Tokio 1.39.0 raises the minimum supported Rust version to 1.70.
- Tokio 1.48.0 raises it to Rust 1.71.
- Tokio 1.53.0 still targets Rust 1.71, but its Windows signal implementation
  accidentally used a newer `OnceLock::wait`. Use 1.53.1 when building signal
  support on Windows with the minimum toolchain.
- `tokio-util` and `tokio-stream` have independent floors; see
  [tokio-util-and-stream.md](tokio-util-and-stream.md).

## Patch-release selection

- Tokio 1.42.0 unsafely clones `Send` but `!Sync` broadcast values without
  synchronization. Require at least 1.42.1 for channels carrying such values.
- Tokio 1.43.2 fixes a process panic after a spurious pidfd wakeup. Version
  1.43.3 makes a `broadcast::Sender` constructed without receivers report
  closed, and 1.43.4 corrects drained `mpsc::Receiver::try_recv` behavior after
  explicit closure.
- Tokio 1.45.1 disables time-based metrics on `wasm32-unknown-unknown`, fixing a
  1.45.0 regression that could make valid `Instant::now()` calls panic.
- Require Tokio 1.46.1 if hooks read `TaskMeta::spawned_at` for tasks made with
  `tokio::spawn`; 1.46.0 records the wrong location for that path.
- Tokio 1.47.2 fixes `join!` and `try_join!` macro hygiene. Version 1.47.4 fixes
  `recv_many` panicking with a nonempty destination on a closed channel.
  Version 1.47.5 fixes mpsc length underflow, receiver wakeups after permit
  release, closed-channel results with outstanding permits, and zero-reader
  `RwLock` limits.
- Tokio 1.51.1 fixes semaphore reopening after forgotten permits, surfaces
  Linux UDP pending errors, and closes a descriptor leak when a cancellable
  io_uring open is cancelled.
- Tokio 1.52.0 can hang `spawn_blocking` through its sharded blocking queue.
  Require at least 1.52.1, which reverts that queue.
- Tokio 1.53.1 restores minimum-toolchain Windows signal builds and fixes a
  cancellation-versus-insertion race in the unstable alternate timer.
- When a `before_park` callback can schedule work, use at least 1.51.4 on the
  1.51 line or 1.52.4 on the 1.52 line so the runtime does not skip the driver.

## Target support

- Filesystem configuration is enabled for WASI from 1.41.0.
- Networking supports Haiku from 1.43.0 and Cygwin from 1.46.0. Android pipe
  options gain `read_write` in 1.46.0.
- Networking supports `wasm32-wasip2`, and Hurd gains `get_peer_cred`, from
  1.51.0.
- Tokio 1.53.0 adds NuttX networking, FreeBSD `UCred::pid`, QNX peer
  credentials through `getpeereid`, and unstable task dumps on s390x.

## Unstable configuration and compatibility

- The unstable H2 metrics-histogram option and histogram API renames in 1.41.0
  require affected configuration code to be updated.
- The experimental alternate multi-threaded runtime is removed in 1.45.0.
- `runtime::Builder::build_local` takes `LocalOptions` by value from 1.46.0.
- From 1.48.0, select `taskdump` and `io_uring` with Cargo features instead of
  the former custom `--cfg` flags.
- io_uring is opportunistic: from 1.49.0 Tokio disables the backend after
  `EPERM`, and each filesystem operation still needs support in the pinned
  Tokio release.
