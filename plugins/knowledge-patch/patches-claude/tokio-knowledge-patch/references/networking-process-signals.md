# Networking, processes, and signals

## Socket conversion and address APIs

- Tokio Unix `SocketAddr` gains standard address conversions in 1.41.0, and
  abstract socket-path behavior is restored in that release after a regression.
- Tokio `from_std` socket conversions reject blocking sockets from 1.44.0 and
  panic if one is passed. Set nonblocking mode before conversion.

```rust
let socket = std::net::TcpListener::bind(addr)?;
socket.set_nonblocking(true)?;
let socket = tokio::net::TcpListener::from_std(socket)?;
```

- `Unix SocketAddr::as_abstract_name()` arrives in 1.48.0 for retrieving an
  abstract address's name bytes.
- Tokio 1.53.0 adds more Unix `SocketAddr` inspection methods; require that
  release when code depends on the expanded surface.

## TCP, UDP, and target capabilities

- Networking support arrives for Haiku in 1.43.0 and Cygwin in 1.46.0.
- `TcpStream::shutdown` succeeds reliably on macOS from 1.46.0 instead of
  returning a spurious error.
- `TcpStream::quickack()` and `set_quickack()` arrive in 1.48.0 where the target
  exposes TCP quick acknowledgements.
- IPv6 `TCLASS` socket-option support arrives in 1.49.0.
- `TcpStream::set_linger` and `TcpSocket::set_linger` are deprecated from
  1.49.0. For abortive close, use `TcpStream::set_zero_linger()` from 1.50.0.
- Networking supports `wasm32-wasip2`, and Hurd gains `get_peer_cred`, from
  1.51.0. On Linux, UDP receive operations surface pending `SO_ERROR` errors
  from 1.51.1.
- Tokio 1.53.0 adds NuttX networking, FreeBSD `UCred::pid`, and QNX peer
  credentials through `getpeereid`.

## Child processes

- Stable Unix `Command::process_group` arrives in 1.40.0 for configuring the
  process group before spawn.

```rust
let mut command = tokio::process::Command::new("worker");
command.process_group(0);
let child = command.spawn()?;
```

- Tokio 1.43.2 fixes a process panic caused by spurious pidfd wakeups.
- `Child::start_kill()` treats an already-exited child as a successful cleanup
  race from 1.44.0.
- `Command::spawn_with` arrives in 1.45.0 and accepts an `FnOnce` callback from
  1.48.0, allowing the callback to consume captures.

## Signals

- On illumos, `SignalKind::info()` and realtime signals are supported from
  1.43.0.
- Windows console close, logoff, and shutdown events are handled from 1.44.0.
- Signal listeners never return `None` from 1.50.0. Use explicit cancellation
  rather than end-of-stream as the shutdown condition.
- Tokio 1.53.0 accidentally breaks Windows signal builds at the Rust 1.71
  minimum; use 1.53.1 for the restored implementation.
