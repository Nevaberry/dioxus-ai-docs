# Compatibility and upgrade floors

## Compiler and dependency requirements

| Package version | Minimum requirement | Upgrade effect |
| --- | --- | --- |
| Tokio 1.39.0 | Rust 1.70 | Update older Rust toolchains before upgrading Tokio. |
| Tokio 1.48.0 | Rust 1.71 | Update toolchains older than Rust 1.71. |
| `tokio-util` 0.7.12 | Rust 1.70 | Establishes the Rust 1.70 floor. |
| `tokio-util` 0.7.17 | Rust 1.71 | Raises the earlier floor again. |
| `tokio-util` 0.7.18 | Tokio 1.44.0 | Raises the minimum Tokio dependency. |
| `tokio-stream` 0.1.13 | Rust 1.56 | Raises the crate's Rust floor. |
| `tokio-stream` 0.1.15 | Rust 1.63 | Raises the floor again. |
| `tokio-stream` 0.1.16 | Rust 1.70 | Raises the floor to Rust 1.70. |
| `tokio-stream` 0.1.14 | Tokio 1.15 | Required so `timeout_repeating` compiles. |

Tokio 1.53.0 accidentally exceeded its declared Rust 1.71 minimum on Windows
because its signal handler used `OnceLock::wait`. Use 1.53.1 when Windows
signal support must build on that minimum toolchain.

## Patch-release safety

### Sound broadcast cloning (1.42.0)

Tokio 1.42.0 clones `Send` but `!Sync` broadcast values without
synchronization. This is a soundness issue. Require at least 1.42.1 whenever a
broadcast channel may carry such a value; that release synchronizes cloning.

### Process and channel fixes (1.43.0)

- Use at least 1.43.2 when pidfd-backed child waiting is active; it fixes a
  panic caused by a spurious pidfd wakeup.
- Starting in 1.43.3, a `broadcast::Sender` created with `Sender::new()` is
  closed while it has no receivers.
- Starting in 1.43.4, a closed and drained `mpsc::Receiver::try_recv()` returns
  `TryRecvError::Disconnected` even while sender handles still exist.

### WASM metrics regression (1.45.0)

Tokio 1.45.0 can make previously valid `Instant::now()` calls panic on
`wasm32-unknown-unknown` because of time-based metrics. Version 1.45.1 disables
those metrics on that target; require at least that patch release.

### Spawn-location metadata (1.46.0)

Unstable `TaskMeta::spawned_at` reports incorrect locations in 1.46.0 for tasks
created by `tokio::spawn`, although `Runtime::spawn` locations and tracing
event locations are unaffected. Require at least 1.46.1 when hooks consume
this metadata.

### Macro, channel, and lock fixes (1.47.0)

- Require at least 1.47.2 if `join!` or `try_join!` can collide with
  macro-internal identifiers.
- Require at least 1.47.4 when `recv_many` can receive into a non-empty vector
  after a channel closes; earlier patch releases can panic.
- Require at least 1.47.5 when mpsc `len()` accuracy matters; it fixes a length
  underflow.
- Starting in 1.47.5, releasing an `mpsc::OwnedPermit` wakes waiting receivers.
- Starting in 1.47.5, `try_recv()` returns `TryRecvError::Empty`, not
  `Disconnected`, when a closed mpsc channel still has outstanding permits
  that can send values.
- Version 1.47.5 rejects a zero maximum-reader limit for `RwLock`; keep the
  explicitly configured limit nonzero.

### Semaphore, UDP, and io_uring fixes (1.51.0)

Use at least 1.51.1 when any of these behaviors matter:

- a closed semaphore must remain closed after permits are forgotten;
- Linux UDP receives must surface pending errors reported through `SO_ERROR`;
- cancelling an unstable io_uring file-open operation must not leak its file
  descriptor.

### Blocking-pool regression (1.52.0)

The new sharded blocking queue in 1.52.0 can make `spawn_blocking` hang.
Version 1.52.1 reverts that queue. Require at least 1.52.1 on this release line
when using the blocking pool.

### Later patch-line fixes (1.53.1)

- Tokio 1.53.1 restores Windows signal support on the Rust 1.71 minimum after
  the 1.53.0 regression described above.
- Tokio 1.51.4 and 1.52.4 fix runtimes skipping the driver when a
  `before_park` callback schedules work. Use the applicable patch release when
  such a hook can make work ready.

## Changed inputs and diagnostics

### Reject blocking standard sockets (1.44.0)

Tokio's socket `from_std` conversions panic when passed a blocking socket. Set
nonblocking mode before transferring the socket.

```rust
let listener = std::net::TcpListener::bind("127.0.0.1:0")?;
listener.set_nonblocking(true)?;
let listener = tokio::net::TcpListener::from_std(listener)?;
```

### Reject zero event intervals (1.50.0)

`runtime::Builder::event_interval(0)` panics. Validate configuration-derived
values before constructing the runtime.

### Default thread-name change (1.50.0)

The default runtime thread name is short enough to fit Linux's thread-name
limit. Tests, filters, and diagnostics that match the old default should set an
explicit runtime thread name or accept the new value.

### Caller-aware timeout diagnostics (1.53.1)

`time::timeout_at` is `#[track_caller]` as of 1.53.0. Panics now report the
caller's location instead of an internal Tokio location.

## Unstable build configuration and removals

### Alternate runtime removal (1.45.0)

The unstable alternate multi-threaded runtime was removed. Migrate code using
that experimental runtime to a supported runtime flavor before upgrading.

### Local builder signature (1.46.0)

Unstable `runtime::Builder::build_local` takes `LocalOptions` by value. Pass
`options`, not `&options`.

### Feature selection (1.48.0)

Select the unstable `taskdump` and `io_uring` subsystems with Cargo features,
replacing their former custom `--cfg` switches.

## Platform availability

- Tokio 1.41.0 enables filesystem configuration for WASI targets.
- Tokio 1.43.0 adds networking support for Haiku OS.
- Tokio 1.43.0 supports `SignalKind::info()` and realtime signals on illumos.
- Tokio 1.44.0 handles Windows `CTRL_CLOSE`, `CTRL_LOGOFF`, and
  `CTRL_SHUTDOWN` console events.
- Tokio 1.46.0 adds networking support for Cygwin and supports Android
  `pipe::OpenOptions::read_write`.
- Tokio 1.51.0 supports `get_peer_cred` on Hurd and networking on
  `wasm32-wasip2`.
- Tokio 1.53.0 adds NuttX networking, exposes `UCred::pid` on FreeBSD, obtains
  QNX peer credentials through `getpeereid`, and supports unstable task dumps
  on s390x.
