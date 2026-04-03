# Task Management

## `biased` option for `join!` and `try_join!` (Tokio 1.46)

Like `select!`, `join!` and `try_join!` now support a `biased;` option that polls branches in declaration order instead of random order. Useful when poll order matters for correctness or performance (e.g., prioritizing a database write over a cache update).

```rust
tokio::join!(biased; fut_a, fut_b, fut_c);
tokio::try_join!(biased; fut_a, fut_b, fut_c);
```

Without `biased;`, the macros randomize poll order each time (same as `select!` without `biased;`).

## `JoinSet` implements `Extend` (Tokio 1.49)

Collect futures directly into a `JoinSet` using the `Extend` trait:

```rust
let mut set = JoinSet::new();
set.extend((0..10).map(|i| async move { i * 2 }));

// Process results as they complete
while let Some(result) = set.join_next().await {
    println!("{}", result?);
}
```

This is more ergonomic than looping with `set.spawn()` for each future.

## `JoinMap<K, V>` stabilized (tokio-util 0.7.16)

`JoinMap` is a keyed version of `JoinSet` — each spawned task is associated with a key. When a task completes, you get both the key and result. Useful for tracking which task produced which result.

```rust
use tokio_util::task::JoinMap;

let mut map = JoinMap::new();
map.spawn("task-a", async { 1 });
map.spawn("task-b", async { 2 });

while let Some((key, result)) = map.join_next().await {
    println!("{key}: {result:?}");
}
```

Key features:
- Keys must implement `Hash + Eq + Clone`
- `map.spawn(key, future)` — spawn with a key
- `map.join_next().await` — returns `Some((K, Result<V, JoinError>))`
- `map.abort(&key)` — abort a specific task by key
- `map.contains_key(&key)` — check if a key has a running task
- Spawning with a duplicate key aborts the previous task for that key

## `JoinQueue` (tokio-util 0.7.17)

Like `JoinSet` but returns results in spawn order (FIFO) instead of completion order. Use when you need results processed in the order tasks were submitted, regardless of which finishes first.

```rust
use tokio_util::task::JoinQueue;

let mut queue = JoinQueue::new();
queue.spawn(async { expensive_step_1().await });
queue.spawn(async { expensive_step_2().await });
queue.spawn(async { expensive_step_3().await });

// Always returns in spawn order: step_1, step_2, step_3
// Even if step_3 finishes before step_1
while let Some(result) = queue.join_next().await {
    process_in_order(result?);
}
```

API mirrors `JoinSet`:
- `queue.spawn(future)` / `queue.spawn_on(future, handle)`
- `queue.join_next().await` — returns in FIFO order
- `queue.len()` / `queue.is_empty()`
- `queue.abort_all()`
