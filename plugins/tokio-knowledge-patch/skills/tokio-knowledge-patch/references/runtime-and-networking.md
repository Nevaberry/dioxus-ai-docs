# Runtime & Networking

## Cooperative scheduling APIs (Tokio 1.47)

Stabilized functions for cooperative scheduling in custom `Future` and `Stream` implementations. These prevent a single task from monopolizing the runtime by yielding when the task's budget is exhausted.

### `coop::poll_proceed` — for `poll`-based code

Use in manual `Future::poll` or `Stream::poll_next` implementations:

```rust
use tokio::task::coop;

impl Stream for MyStream {
    type Item = Data;

    fn poll_next(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        // Yields Poll::Pending if this task has consumed its coop budget
        let coop = ready!(coop::poll_proceed(cx));

        let item = self.get_mut().produce_item();
        coop.made_progress(); // report that useful work was done
        Poll::Ready(Some(item))
    }
}
```

The `coop::poll_proceed` call checks the task's cooperation budget. If budget is exhausted, it returns `Poll::Pending` and schedules the task to be woken, giving other tasks a chance to run. The returned `RestoreOnPending` guard has a `made_progress()` method to signal that the poll produced a result.

### `coop::cooperative` — for async code

Wrap an entire async block to opt into cooperative scheduling:

```rust
use tokio::task::coop;

// This async block will yield cooperatively, even if it
// doesn't use any Tokio I/O or sync primitives internally
let result = coop::cooperative(async {
    // CPU-intensive or custom work
    heavy_computation()
})
.await;
```

Use `cooperative()` when your async code does significant work between `.await` points and you want to be a good citizen in the runtime.

## `is_rt_shutdown_err` (Tokio 1.50)

Check whether an error was caused by the Tokio runtime shutting down. Works with any error type that implements `std::error::Error`. Useful for graceful shutdown handlers where you want to distinguish "runtime is going away" from real errors.

```rust
use tokio::runtime::is_rt_shutdown_err;

match sender.send(msg).await {
    Err(e) if is_rt_shutdown_err(&e) => {
        // Runtime is shutting down — this is expected, exit gracefully
        tracing::debug!("send failed due to runtime shutdown");
    }
    Err(e) => return Err(e.into()),
    Ok(()) => {}
}
```

This function walks the error's source chain looking for Tokio's internal shutdown error. It's the canonical way to detect shutdown — don't pattern-match on error messages.

## `set_linger` deprecated → `set_zero_linger` (Tokio 1.49/1.50)

`TcpStream::set_linger` and `TcpSocket::set_linger` are deprecated. The only valid use case for linger was `set_linger(Some(Duration::ZERO))` to force a TCP RST on close. The new API makes intent explicit:

```rust
// Old (deprecated):
// stream.set_linger(Some(Duration::from_secs(0)))?;

// New:
stream.set_zero_linger(true)?; // RST on close
stream.set_zero_linger(false)?; // Normal close (OS default)
```

If you were calling `set_linger(None)` — just remove the call entirely, as the OS default is already no linger.

Migration:
- `set_linger(Some(Duration::ZERO))` → `set_zero_linger(true)`
- `set_linger(Some(Duration::from_secs(0)))` → `set_zero_linger(true)`
- `set_linger(None)` → remove the call
