# Networking, processes, and signals

Use this reference for socket conversion and options, operating-system coverage, child-process construction and cleanup, and shutdown signal handling.

## Contents

- [Socket construction and addresses](#socket-construction-and-addresses)
- [TCP and UDP behavior](#tcp-and-udp-behavior)
- [Networking target coverage](#networking-target-coverage)
- [Child processes](#child-processes)
- [Signals and shutdown](#signals-and-shutdown)

## Socket construction and addresses

### Convert only nonblocking sockets

Tokio 1.44.0 makes networking `from_std` constructors panic when the supplied standard-library socket is blocking. Set nonblocking mode before conversion:

```rust
let listener = std::net::TcpListener::bind(addr)?;
listener.set_nonblocking(true)?;
let listener = tokio::net::TcpListener::from_std(listener)?;
```

### Unix socket addresses

- Tokio 1.41.0 adds conversions between Tokio's Unix `SocketAddr` and the standard library's Unix socket address type.
- Tokio 1.46.0 implements `Clone` for `tokio::net::unix::SocketAddr`.
- Tokio 1.48.0 adds `SocketAddr::as_abstract_name()`, returning the bytes of an abstract-namespace name when present.

Tokio 1.39.3 restores Unix abstract-namespace socket-address support after the regression on the earlier 1.39 patch releases.

## TCP and UDP behavior

### TCP shutdown and linger

Tokio 1.46.0 fixes `TcpStream::shutdown` incorrectly returning an error on macOS. Require that version or newer when callers treat successful shutdown as an invariant.

Tokio 1.49.0 deprecates `TcpStream::set_linger` and `TcpSocket::set_linger`. Tokio 1.50.0 provides `TcpStream::set_zero_linger()` for the supported zero-duration case:

```rust
stream.set_zero_linger()?;
```

Use it only when an abortive close is intended; normal close remains graceful.

### Socket options

- Tokio 1.48.0 adds `TcpStream::quickack()` and `TcpStream::set_quickack()` for the TCP quick-acknowledgement option on supported targets.
- Tokio 1.49.0 adds the IPv6 `TCLASS` socket option, avoiding a lower-level socket API for traffic-class configuration.

### Linux UDP errors

Tokio 1.51.1 surfaces Linux UDP `SO_ERROR` failures from receive operations. Handle these receive errors instead of assuming they remain hidden in socket state.

## Networking target coverage

- Tokio 1.43.0 adds networking support for Haiku OS.
- Tokio 1.46.0 adds networking support for Cygwin targets.
- Tokio 1.51.0 adds networking support for `wasm32-wasip2`.
- Tokio 1.51.0 adds peer-credential lookup on GNU Hurd.

Filesystem support for WASI and Android pipe support are covered separately in [io-and-filesystem.md](io-and-filesystem.md).

## Child processes

### Process groups and spawning

Tokio 1.40.0 stabilizes `tokio::process::Command::process_group`, allowing Unix child process groups to be configured without unstable APIs.

Tokio 1.45.0 adds `tokio::process::Command::spawn_with`. Tokio 1.48.0 broadens its callback to `FnOnce`, so the callback may consume captured values.

### Cleanup races and driver fixes

Since Tokio 1.44.0, `Child::start_kill()` does not fail merely because the child exited normally before cleanup won the race.

Tokio 1.43.2 fixes process-driver panics caused by spurious pidfd wakeups. Prefer at least that patch release on the 1.43 line, and 1.43.4 for all fixes on the line.

## Signals and shutdown

### illumos

Tokio 1.43.0 makes `SignalKind::info()` available on illumos and adds realtime-signal support there.

### Windows console events

Tokio 1.44.0 correctly handles the Windows `CTRL_CLOSE`, `CTRL_LOGOFF`, and `CTRL_SHUTDOWN` console signal events. Include them in shutdown handling where the application must flush or clean up during these session events.

### Listener lifetime

Tokio 1.50.0 guarantees that signal listeners do not return `None`. Combine signal waiting with an independent cancellation condition:

```rust
tokio::select! {
    _ = signal.recv() => handle_signal(),
    _ = cancellation.cancelled() => return,
}
```

Do not use listener exhaustion as the application's shutdown mechanism.
