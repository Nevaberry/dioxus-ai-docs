# Synchronization and channels

Use this reference when implementing or upgrading watch, broadcast, mpsc, oneshot, notification, locking, semaphore, or single-assignment flows.

## Contents

- [Watch and broadcast](#watch-and-broadcast)
- [Mpsc channels and permits](#mpsc-channels-and-permits)
- [Oneshot and notifications](#oneshot-and-notifications)
- [Single assignment, locks, and semaphores](#single-assignment-locks-and-semaphores)

## Watch and broadcast

### Watch defaults and scheduling

Tokio 1.39.0 implements `Default` for `watch::Sender<T>` when `T: Default`. Structures containing a sender can therefore derive `Default` without constructing the channel manually.

Since Tokio 1.41.0, watch operations participate in Tokio's cooperative scheduling. Continuously ready receive loops can yield after exhausting their cooperative budget.

### Broadcast lifecycle APIs

Tokio 1.44.0 adds two sender lifecycle tools:

- Await `broadcast::Sender::closed()` until every receiver has gone away. Producers can stop generating work without polling receiver counts.
- Use `broadcast::WeakSender` for non-owning access that does not keep the channel open.

Since Tokio 1.41.0, `broadcast::Receiver` also participates in cooperative scheduling.

### Broadcast correctness floors

- Tokio 1.42.1 fixes unsynchronized cloning when a broadcast value is `Send` but not `Sync`; do not use 1.42.0 for that case.
- Tokio 1.43.3 correctly reports the receiverless channel created by `broadcast::Sender::new()` as closed.

## Mpsc channels and permits

### Unwind safety

Tokio's mpsc types implement `UnwindSafe` as of 1.40.0. They can satisfy unwind-safety bounds around operations such as `catch_unwind` without an assertion wrapper solely for the channel type.

### Channel identity

Tokio 1.46.0 adds identity checks to `mpsc::OwnedPermit`:

- `same_channel` compares owned permits.
- `same_channel_as_sender` compares a permit with a sender.

Use these checks when routing reserved capacity without consuming it by sending a value.

### Close and permit semantics

- Tokio 1.43.4 makes a drained, explicitly closed `mpsc::Receiver::try_recv()` return `TryRecvError::Disconnected` rather than `TryRecvError::Empty`.
- Tokio 1.51.3 fixes `mpsc::Receiver::len()` underflow.
- The 1.51 line wakes receivers when an `OwnedPermit` is released.
- The 1.51 line returns `TryRecvError::Empty` while a closed channel still has outstanding permits; the channel is not fully disconnected until those reservations are gone.
- The 1.51 line avoids a `recv_many` panic when the channel is closed and the destination vector is already non-empty.

Use Tokio 1.51.3 when relying on the combined corrected semantics.

## Oneshot and notifications

### Oneshot receiver inspection

Tokio 1.44.0 adds synchronous state inspection to `oneshot::Receiver`:

- `is_empty()` reports whether no value is currently available.
- `is_terminated()` reports whether the receiver can no longer produce a value.

These checks do not await or consume the receiver.

### Notification futures

Tokio 1.41.0 marks `Notified` as `#[must_use]`. Await or retain the future from `Notify::notified()`; ignoring it can become a build error when warnings are denied.

Tokio 1.47.0 adds `Notify::notified_owned()`, returning an `OwnedNotified` without a lifetime parameter. Use it when a pending notification must be stored or moved without borrowing the `Notify` value.

The 1.51 line also corrects `Notify::notify_waiters` priority. Prefer 1.51.3 for all synchronization corrections accumulated on that line.

## Single assignment, locks, and semaphores

Tokio 1.47.0 adds `tokio::sync::SetOnce`, a single-assignment cell similar in purpose to `std::sync::OnceLock`.

Tokio 1.51.3 rejects an `RwLock` maximum-reader count of zero instead of accepting an unusable configuration.

The 1.51 line prevents semaphores from reopening after permits are forgotten. Do not rely on the earlier incorrect reopening behavior.
