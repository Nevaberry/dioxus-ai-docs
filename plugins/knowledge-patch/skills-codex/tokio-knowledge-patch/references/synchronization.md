# Synchronization and channels

## Watch channels

### Default senders (1.39.0)

`watch::Sender` implements `Default`, so it can participate in containers that
derive `Default` when the stored value type satisfies the implementation's
bounds.

### Cooperative receives (1.41.0)

Watch receives consume Tokio's cooperative task budget. A loop over
immediately ready changes cannot indefinitely monopolize an executor thread.

## Broadcast channels

### Cooperative receivers (1.41.0)

`broadcast::Receiver` participates in cooperative scheduling and yields after
the task budget is exhausted.

### Synchronize cloning (1.42.0)

Tokio 1.42.0 clones `Send` but `!Sync` broadcast values without
synchronization. Require at least 1.42.1 when such values can be broadcast;
that release synchronizes the clone operation.

### Receiverless construction (1.43.0)

Starting in 1.43.3, a `broadcast::Sender` created with `Sender::new()` is
closed while it has no receivers. Its state therefore reflects receiverless
construction.

### Sender liveness (1.44.0)

- Await `broadcast::Sender::closed()` to detect when every receiver has gone
  away.
- Use `broadcast::WeakSender` for an observer or auxiliary handle that must not
  keep the channel open.

## MPSC channels

### Unwind safety (1.40.0)

Tokio mpsc types implement `UnwindSafe`, allowing them to satisfy bounds around
panic-catching boundaries.

### Blocking batched receives (1.41.0)

`mpsc::Receiver::blocking_recv_many` receives multiple queued messages into a
collection from blocking code.

### Closed receivers (1.43.0)

Starting in 1.43.4, after `Receiver::close()` and exhaustion of buffered
messages, `try_recv()` returns `TryRecvError::Disconnected` even if sender
handles remain.

```rust
let (_tx, mut rx) = tokio::sync::mpsc::channel::<u8>(1);
rx.close();
assert!(matches!(
    rx.try_recv(),
    Err(tokio::sync::mpsc::error::TryRecvError::Disconnected)
));
```

### `recv_many` on a closed channel (1.47.0)

Tokio 1.47.4 fixes a panic when `recv_many` receives into a non-empty
destination vector after the channel closes. Require at least that patch when
using this pattern.

### Length observations (1.47.0)

Tokio 1.47.5 fixes an mpsc `len()` underflow. Require at least that patch when
channel-length observations affect behavior or diagnostics.

### Outstanding permits (1.47.0)

Starting in 1.47.5:

- `mpsc::OwnedPermit::release()` wakes waiting receivers;
- a closed channel with outstanding permits reports `TryRecvError::Empty`, not
  `Disconnected`, because those permits can still send values.

### Receiver lifetime and reserve wakeups (1.53.1)

In 1.53.0:

- dropping an `mpsc::Receiver` or `UnboundedReceiver` also drops its registered
  waker even while senders remain;
- a receiver is woken when a queued `reserve` or `reserve_many` operation
  returns permits, avoiding a missed wakeup.

## Notifications

### Must-use notification futures (1.41.0)

`Notified` is `#[must_use]`. Await, retain, or explicitly discard the future
returned by `Notify::notified()`.

### Owned notification futures (1.47.0)

`Notify::notified_owned()` returns `OwnedNotified` without a lifetime
parameter. Store or move it without borrowing its `Notify`.

```rust
let notify = std::sync::Arc::new(tokio::sync::Notify::new());
let notified = notify.clone().notified_owned();
notify.notify_one();
notified.await;
```

## Single-assignment state (1.47.0)

`tokio::sync::SetOnce` provides single-assignment state similar to
`std::sync::OnceLock`, including asynchronous waiting for the value to be set.

## Locks and semaphores

### Nonzero `RwLock` reader limit (1.47.0)

Tokio 1.47.5 requires an explicitly configured `RwLock` maximum-reader limit
to be nonzero. Do not pass zero to such a constructor.

### Closed semaphores and forgotten permits (1.51.0)

Tokio 1.51.1 fixes a semaphore reopening after permits are forgotten. Require
at least that patch when code combines semaphore closure with permit
forgetting.
