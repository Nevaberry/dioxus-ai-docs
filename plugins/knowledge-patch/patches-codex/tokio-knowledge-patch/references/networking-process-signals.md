# Networking, processes, and signals

## Socket construction and addresses

### Unix address conversions (1.41.0)

Tokio's Unix `SocketAddr` supports direct conversions to and from corresponding
socket-address representations, reducing manual address translation.

Tokio 1.41.0 also restores Unix abstract socket-path behavior after a
regression, which matters for applications that bind or connect through
abstract addresses.

### Reject blocking standard sockets (1.44.0)

Tokio socket `from_std` conversions panic when passed a blocking socket. Put a
standard-library socket in nonblocking mode before transfer.

```rust
let listener = std::net::TcpListener::bind("127.0.0.1:0")?;
listener.set_nonblocking(true)?;
let listener = tokio::net::TcpListener::from_std(listener)?;
```

### Abstract socket names (1.48.0)

Unix `SocketAddr::as_abstract_name()` returns the name bytes of an abstract
socket address when present.

### Expanded Unix address inspection (1.53.1)

Unix socket types gain additional `SocketAddr` methods in 1.53.0. Require this
release when code depends on the expanded address-inspection surface.

## TCP and UDP behavior

### Reliable macOS shutdown (1.46.0)

`TcpStream::shutdown` no longer incorrectly returns an error on macOS. Require
1.46.0 or newer when successful asynchronous stream shutdown matters.

### TCP quick acknowledgements (1.48.0)

Use `TcpStream::quickack()` and `TcpStream::set_quickack()` to inspect or change
TCP quick-ack behavior where the platform exposes it.

### IPv6 traffic class (1.49.0)

Tokio supports the IPv6 `TCLASS` socket option, allowing traffic-class
configuration without dropping to a lower-level socket API.

### Linger APIs (1.49.0 and 1.50.0)

`TcpStream::set_linger` and `TcpSocket::set_linger` are deprecated as of
1.49.0. Migrate calls, especially when builds deny warnings. For a
zero-duration linger, use `TcpStream::set_zero_linger()` from 1.50.0.

```rust
stream.set_zero_linger()?;
```

### Linux pending UDP errors (1.51.0)

Starting in 1.51.1, Linux UDP receive operations surface pending errors from
`SO_ERROR`. Require at least that patch when callers must observe them.

## Networking targets and credentials

- Tokio 1.43.0 adds networking support for Haiku OS.
- Tokio 1.46.0 adds networking support for Cygwin.
- Tokio 1.51.0 supports `get_peer_cred` on Hurd and networking on
  `wasm32-wasip2`.
- Tokio 1.53.0 adds networking support for NuttX, exposes `UCred::pid` on
  FreeBSD, and obtains QNX peer credentials through `getpeereid`.

## Child processes

### Unix process groups (1.40.0)

`tokio::process::Command::process_group` is stable and configures a Unix child
process group before spawning.

```rust
let mut command = tokio::process::Command::new("worker");
command.process_group(0);
let child = command.spawn()?;
```

### pidfd wakeups (1.43.0)

Tokio 1.43.2 fixes a process panic caused by a spurious pidfd wakeup. Use at
least that patch when waiting for children through pidfds on the 1.43 line.

### Killing an already-exited child (1.44.0)

`Child::start_kill()` does not fail merely because the child already exited.
Shutdown code can tolerate the race between observing and terminating it.

### Spawn callbacks (1.45.0 and 1.48.0)

Tokio 1.45.0 adds `Command::spawn_with`. In 1.48.0 its callback accepts
`FnOnce`, so the callback can consume captured values.

## Signals

### illumos signals (1.43.0)

`SignalKind::info()` and realtime signals are supported on illumos.

```rust
let mut info = tokio::signal::unix::signal(
    tokio::signal::unix::SignalKind::info(),
)?;
```

### Windows console shutdown (1.44.0)

Tokio handles Windows `CTRL_CLOSE`, `CTRL_LOGOFF`, and `CTRL_SHUTDOWN` events,
allowing listeners to respond to console closure, user logoff, and system
shutdown.

### Signal listeners remain open (1.50.0)

Signal listeners are guaranteed not to return `None`. Do not use an optional
receive result as a normal end-of-stream shutdown signal; provide explicit
cancellation.

### Windows minimum-toolchain fix (1.53.1)

Tokio 1.53.0 accidentally exceeded its Rust 1.71 minimum on Windows by using
`OnceLock::wait` in the signal handler. Use 1.53.1 when signal support must
compile on that minimum toolchain.
