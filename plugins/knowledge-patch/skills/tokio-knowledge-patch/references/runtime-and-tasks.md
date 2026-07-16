# Runtime, tasks, and scheduling

Use this reference for runtime construction, local task execution, cooperative scheduling, task management, metrics, hooks, and task dumps.

## Contents

- [Runtime construction and identity](#runtime-construction-and-identity)
- [Cooperative scheduling and polling](#cooperative-scheduling-and-polling)
- [Task and future APIs](#task-and-future-apis)
- [Runtime metrics](#runtime-metrics)
- [Unstable hooks, tracing, and dumps](#unstable-hooks-tracing-and-dumps)

## Runtime construction and identity

### Local runtimes

Tokio 1.41.0 introduces the unstable `runtime::LocalRuntime` for thread-local tasks that do not implement `Send`. Tokio 1.51.0 stabilizes `LocalRuntime`, so current code can run `!Send` tasks without an unstable API opt-in.

For unstable macro-based entry points, Tokio 1.48.0 adds the `local` runtime flavor to Tokio's attribute macros:

```rust
#[tokio::main(flavor = "local")]
async fn main() {
    // Run thread-local work.
}
```

Tokio 1.46.0 changes unstable `runtime::Builder::build_local` to accept `LocalOptions` by value rather than by reference.

Tokio 1.46.0 also forbids Tokio's in-place blocking operation while `LocalSet::poll` is running and during the `LocalSet` drop path. Put blocking work in `spawn_blocking` or outside the local set.

### Runtime configuration

- Tokio 1.50.0 makes `runtime::Builder::event_interval(0)` panic. Supply a nonzero event interval.
- Tokio 1.50.0 shortens the default runtime thread name to fit the Linux thread-name limit. Set `Builder::thread_name` explicitly when log, profiler, or monitoring integration depends on the label.
- Tokio 1.52.0 adds unstable `Builder::enable_eager_driver_handoff`, which hands off I/O and time drivers eagerly before task polling.
- Tokio 1.45.0 removes the unstable alternate multi-threaded runtime. Use a supported runtime implementation.

### Runtime and worker identity

- Tokio 1.49.0 stabilizes `runtime::id::Id`.
- Tokio 1.49.0 stabilizes `LocalSet::id()`.
- Tokio 1.51.0 adds runtime names and `tokio::runtime::worker_index()`, allowing diagnostics to identify the current runtime and worker without custom thread tracking.

## Cooperative scheduling and polling

### Cooperative resources

Tokio 1.41.0 makes `watch` operations and `broadcast::Receiver` participate in cooperative scheduling. A loop consuming continuously ready channel values can exhaust its budget and yield rather than starve unrelated tasks.

Tokio 1.44.0 exposes `tokio::task::coop`, allowing custom futures and resources to use Tokio's cooperative budget. Tokio 1.47.0 adds two important entry points:

- `cooperative` wraps work so it participates in cooperative scheduling.
- `poll_proceed` lets manual polling code consume and check the task budget.

### Macro polling

Tokio 1.44.0 makes `select!` budget-aware. A loop whose branches remain ready can yield after exhausting its cooperative budget.

Tokio 1.46.0 adds `biased;` to `join!` and `try_join!`. The default rotates the first-polled future; biased mode always polls in declaration order:

```rust
let (a, b) = tokio::try_join!(biased; first(), second())?;
```

Use biased mode only when the ordering is intentional; an always-ready earlier future can receive preferential polling.

### Yielding inside blocking regions

Since Tokio 1.42.0, `yield_now` is no longer deferred when driven inside `block_in_place`. The yield takes effect before `block_in_place` returns.

## Task and future APIs

### `IntoFuture` inputs

Since Tokio 1.39.0, `tokio::time::timeout`, `join!`, and `select!` accept values implementing `IntoFuture`, including values that do not implement `Future` directly.

### Task handles and sets

- Tokio 1.40.0 marks `JoinHandle::abort_handle()` as `#[must_use]`.
- Tokio 1.40.0 includes a panicked task's panic message when formatting its `JoinError`.
- Tokio 1.49.0 implements `Extend` for `JoinSet<T>`, so iterator and collection machinery can add work to an existing set.
- Tokio 1.50.0 guarantees that a spawned task is dropped before its `JoinHandle` completes. Destructors for data retained by the task future have run by the time awaiting the handle returns.

### Identifiers and task-local values

- Tokio 1.48.0 implements `Ord` for `task::Id`, enabling sorting and direct use in ordered maps and sets.
- Tokio 1.48.0 adds `LocalKey::try_get()`, which retrieves task-local state without taking the panicking path when no value is available.

### Unwind safety

Tokio 1.45.0 makes `runtime::Handle` unwind-safe, allowing it to cross a boundary such as `catch_unwind` without an assertion wrapper solely for the handle.

## Runtime metrics

### Stable metrics

Tokio 1.45.0 stabilizes these per-worker metrics:

- `worker_total_busy_duration`
- `worker_park_count`
- `worker_unpark_count`

Tokio 1.49.0 documents `num_alive_tasks` as not strongly consistent. Concurrent task creation and completion can affect a sample, so never use it as an exact synchronization condition or invariant.

### Unstable metrics

Tokio 1.39.0 adds unstable metrics for:

- Total spawned-task count.
- Each worker's combined park/unpark count.
- Each worker's thread ID.

Tokio 1.41.0 adds an unstable H2 histogram configuration option for finer-grained buckets and renames the unstable histogram APIs. Revisit names and configuration when upgrading instrumentation code across that release.

## Unstable hooks, tracing, and dumps

### Lifecycle and poll hooks

- Tokio 1.40.0 adds `runtime::Builder::on_task_spawn` and `on_task_terminate` callbacks.
- Tokio 1.44.0 adds runtime callbacks that run immediately before and after every task poll.
- Tokio 1.46.0 adds `TaskMeta::spawned_at`. In 1.46.0, runtime hook locations are wrong for `tokio::spawn` tasks; use 1.46.1 for the correction. Task-tracing event locations are not affected.

Keep hook work bounded and avoid introducing blocking or reentrant runtime behavior.

### Task tracing and dumps

- Tokio 1.43.0 adds accessors to unstable task-dump backtraces for programmatic inspection.
- Tokio 1.44.0 makes the unstable task-tracing API public to external instrumentation code.
- Tokio 1.48.0 moves unstable task-dump enablement to the `taskdump` Cargo feature.
- Tokio 1.52.0 adds customizable task dumps through `trace_with()`. Its callback accepts `FnMut`, rather than only a function pointer, so a stateful closure can collect or transform dump data.
