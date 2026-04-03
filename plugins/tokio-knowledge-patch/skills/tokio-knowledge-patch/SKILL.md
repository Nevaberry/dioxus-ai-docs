---
name: tokio-knowledge-patch
description: "Tokio changes since training cutoff (latest: 1.50.0 / tokio-util 0.7.18) — SetOnce, JoinMap, JoinQueue, cooperative scheduling, biased join. Load before working with Tokio."
version: "1.50.0"
license: MIT
metadata:
  author: Nevaberry
---

# Tokio Knowledge Patch

Covers Tokio 1.46–1.50 (Jul 2025 – Mar 2026) and tokio-util 0.7.16–0.7.18 (Aug 2025 – Jan 2026). Claude Opus 4.6 knows Tokio through 1.45 and tokio-util through 0.7.15.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Task management | [references/task-management.md](references/task-management.md) | `biased` join, `JoinSet::extend`, `JoinMap`, `JoinQueue` |
| Synchronization | [references/synchronization.md](references/synchronization.md) | `SetOnce`, `Notify::notified_owned`, `CancellationToken` adapters |
| Runtime & networking | [references/runtime-and-networking.md](references/runtime-and-networking.md) | Cooperative scheduling APIs, `is_rt_shutdown_err`, `set_zero_linger` |

---

## Quick Reference — New APIs by Crate

### tokio (1.46–1.50)

| API | Version | What it does |
|---|---|---|
| `join!(biased; ...)` / `try_join!(biased; ...)` | 1.46 | Poll branches in declaration order |
| `sync::SetOnce` | 1.47 | Async `OnceLock` — set once, await from many tasks |
| `Notify::notified_owned()` | 1.47 | Returns `OwnedNotified` (no lifetime) for use in spawned tasks |
| `task::coop::poll_proceed(cx)` | 1.47 | Cooperative yielding in custom `Future`/`Stream` impls |
| `task::coop::cooperative(fut)` | 1.47 | Wrap async block to opt into coop scheduling |
| `JoinSet::extend(iter)` | 1.49 | Collect futures directly into a `JoinSet` |
| `TcpStream::set_zero_linger(bool)` | 1.49 | Replaces deprecated `set_linger` |
| `runtime::is_rt_shutdown_err(&e)` | 1.50 | Check if error is caused by runtime shutdown |

### tokio-util (0.7.16–0.7.18)

| API | Version | What it does |
|---|---|---|
| `task::JoinMap<K, V>` | 0.7.16 | Keyed `JoinSet` — associate a key with each spawned task |
| `task::JoinQueue` | 0.7.17 | Like `JoinSet` but returns results in spawn (FIFO) order |
| `CancellationToken::unless_cancelled_with` | 0.7.16 | Cancel futures directly with a token |

---

## Deprecations & Migration

| Deprecated | Replacement | Version |
|---|---|---|
| `TcpStream::set_linger(Some(Duration::ZERO))` | `TcpStream::set_zero_linger(true)` | 1.49 |
| `TcpSocket::set_linger(Some(Duration::ZERO))` | `TcpSocket::set_zero_linger(true)` | 1.49 |

If you were calling `set_linger(None)` — just remove the call (OS default is no linger).

---

## Essential Patterns (inline)

### `SetOnce` — async one-time initialization

```rust
use tokio::sync::SetOnce;

static CONFIG: SetOnce<String> = SetOnce::const_new();

// First caller initializes; others wait then get the value
let val = CONFIG.get_or_init(|| async { load_config().await }).await;

// Non-blocking access after initialization
if let Some(cfg) = CONFIG.get() { /* already set */ }
```

### `JoinMap` — keyed task set

```rust
use tokio_util::task::JoinMap;

let mut map = JoinMap::new();
map.spawn("fetch-users", async { fetch_users().await });
map.spawn("fetch-orders", async { fetch_orders().await });

while let Some((key, result)) = map.join_next().await {
    println!("{key}: {result:?}");
}
```

### `JoinQueue` — ordered task results

```rust
use tokio_util::task::JoinQueue;

let mut queue = JoinQueue::new();
queue.spawn(async { step_1().await });
queue.spawn(async { step_2().await });

// Results always in spawn order, regardless of completion order
while let Some(result) = queue.join_next().await {
    process(result?);
}
```

### Biased `join!` — deterministic poll order

```rust
// Polls in declaration order (like select!(biased; ...))
tokio::join!(biased; database_write, cache_invalidation, notification);
tokio::try_join!(biased; critical_op, secondary_op);
```

### Cooperative scheduling in custom futures

```rust
use tokio::task::coop;

// In a Stream::poll_next or Future::poll implementation:
fn poll_next(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Item>> {
    let coop = ready!(coop::poll_proceed(cx)); // yields if budget exhausted
    let item = self.produce_item();
    coop.made_progress();
    Poll::Ready(Some(item))
}
```

### Runtime shutdown detection

```rust
match sender.send(msg).await {
    Err(e) if tokio::runtime::is_rt_shutdown_err(&e) => {
        // Runtime shutting down — clean exit
    }
    Err(e) => return Err(e.into()),
    Ok(()) => {}
}
```

### `CancellationToken` future adapters

```rust
use tokio_util::sync::CancellationToken;

let token = CancellationToken::new();
let result = my_future.unless_cancelled_with(&token).await;
// Either::Left(value) on completion, Either::Right(()) on cancellation
```

---

## `JoinSet` vs `JoinMap` vs `JoinQueue` — when to use which

| Type | Crate | Result order | Keyed? | Use when |
|---|---|---|---|---|
| `JoinSet` | tokio | Completion order | No | Fire-and-forget concurrent tasks |
| `JoinMap<K, V>` | tokio-util | Completion order | Yes | Need to identify which task produced a result |
| `JoinQueue` | tokio-util | Spawn (FIFO) order | No | Results must be processed in submission order |

All three support `spawn`, `spawn_on`, `join_next`, `abort_all`, `len`, and `is_empty`.

## `Notify` lifetime guide

| Method | Return type | Use when |
|---|---|---|
| `notify.notified()` | `Notified<'_>` | Awaiting in the same scope |
| `notify.notified_owned()` | `OwnedNotified` | Moving into `tokio::spawn` or storing in a struct |
