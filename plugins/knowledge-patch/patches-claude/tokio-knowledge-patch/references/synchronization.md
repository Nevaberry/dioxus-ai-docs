# Synchronization and channels

## Watch, broadcast, and notification

- `watch::Sender<T>` implements `Default` from 1.39.0 when the value meets the
  required default bounds.
- `Notify::notified()` returns a `#[must_use]` `Notified` from 1.41.0; await,
  retain, or explicitly discard it.
- Watch receives and `broadcast::Receiver` are cooperative from 1.41.0.
- Tokio 1.42.0 has a soundness bug when cloning a `Send` but `!Sync` broadcast
  value. Require at least 1.42.1 for that payload shape.
- A `broadcast::Sender` created without receivers reports closed from 1.43.3.
- `broadcast::Sender::closed()` and `broadcast::WeakSender` arrive in 1.44.0.
  Await the former to stop producers; use the latter for handles that must not
  keep a channel open.
- `Notify::notified_owned()` and lifetime-free `OwnedNotified` arrive in 1.47.0
  for notification futures that must own their `Notify` relationship.

## MPSC receive, closure, and permits

- Tokio mpsc types implement `UnwindSafe` from 1.40.0.
- `mpsc::Receiver::blocking_recv_many` arrives in 1.41.0 for batched synchronous
  receives.
- From 1.43.4, a closed and drained receiver returns
  `TryRecvError::Disconnected` even while sender handles remain.
- Tokio 1.47.4 fixes `recv_many` panicking when a closed channel is called with
  a nonempty destination vector.
- Tokio 1.47.5 fixes `len()` underflow and makes `OwnedPermit::release()` wake a
  waiting receiver. In that release, a closed channel with outstanding permits
  returns `TryRecvError::Empty`, because a permit may still send, rather than
  `Disconnected`.
- Tokio 1.53.0 drops an mpsc receiver's registered waker when the receiver is
  dropped, even if senders remain. It also wakes the receiver when a queued
  `reserve` or `reserve_many` request obtains permits.

## Single assignment, semaphores, and locks

- `tokio::sync::SetOnce` arrives in 1.47.0 for single-assignment state whose
  initialization can be awaited asynchronously.
- Tokio 1.47.5 rejects an explicit `RwLock` maximum-reader count of zero.
- Tokio 1.51.1 fixes a closed semaphore reopening after permits are forgotten;
  require that patch when closure and forgotten permits can interact.
