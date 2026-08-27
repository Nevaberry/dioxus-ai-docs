# Runtime, tasks, and scheduling

## Runtime construction and identity

### Local runtimes

Tokio 1.41.0 introduces an unstable `LocalRuntime` for local task execution.
Tokio 1.48.0 adds an unstable `local` flavor to runtime macros:

```rust
#[tokio::main(flavor = "local")]
async fn main() {
    // Local task work.
}
```

`tokio::runtime::LocalRuntime` becomes stable in 1.51.0, removing the unstable
API requirement for direct local-runtime use.

When using unstable construction APIs, note that
`runtime::Builder::build_local` takes `LocalOptions` by value as of 1.46.0.

### Runtime and local-set identifiers

- Task `Id` APIs become stable in 1.41.0.
- `task::Id` implements `Ord` as of 1.48.0, allowing direct sorting and use in
  ordered collections.
- `runtime::id::Id` becomes stable in 1.49.0.
- `LocalSet::id()` becomes stable in 1.49.0.

### Runtime names and workers

Tokio 1.51.0 lets a runtime carry a name and adds
`tokio::runtime::worker_index()` for finding the current worker index. Use
these values in diagnostics and per-worker context.

The default runtime thread name changes in 1.50.0 to fit Linux's thread-name
limit. Set an explicit name when tests, filters, or logs depend on a stable
value.

### Construction and shutdown errors

- Tokio 1.50.0 adds `is_rt_shutdown_err` to distinguish errors caused by
  runtime shutdown.
- `runtime::Builder::event_interval(0)` panics as of 1.50.0; validate
  configuration before passing it to the builder.
- Tokio 1.53.0 fixes a stack overflow that could occur during runtime
  construction.

## Awaitables and task collections

### `IntoFuture` inputs (1.39.0)

`time::timeout`, `join!`, and `select!` accept `IntoFuture` values. Custom
awaitable types can be passed without first converting them into futures.

### Join sets (1.49.0)

`JoinSet<T>` implements `Extend`, so an iterator of tasks can be added with
standard collection machinery.

### Fallible task-local access (1.48.0)

`LocalKey::try_get()` reads task-local state without panicking when the key is
not set in the current task.

### Must-use abort handles (1.40.0)

`JoinHandle::abort_handle()` is `#[must_use]`. Retain the handle or explicitly
discard it to avoid an unused-result warning.

### Join completion and destruction (1.50.0)

A spawned task is dropped before its `JoinHandle` completes. When awaiting the
handle returns, destructors for task-owned state have already run.

## Cooperative scheduling

### Cooperative channels (1.41.0)

`watch` receives and `broadcast::Receiver` participate in Tokio's cooperative
scheduling. Loops over immediately ready channel values can no longer
indefinitely monopolize an executor thread.

### Immediate blocking-region yields (1.42.0)

`yield_now` is no longer deferred inside `block_in_place`; the yield takes
effect immediately.

### Custom cooperative resources (1.44.0 and 1.47.0)

Tokio 1.44.0 adds `task::coop`, exposing cooperative scheduling utilities for
custom asynchronous resources. Tokio 1.47.0 adds:

- `cooperative`, which wraps a future so it consumes cooperative budget;
- `poll_proceed`, which lets custom polling code check the task budget.

### Budget-aware selection (1.44.0)

`select!` participates in cooperative budgeting. A loop repeatedly selecting
ready branches yields after its task budget is exhausted.

### Blocking restrictions in local sets (1.46.0)

Tokio disallows its in-place blocking operation while a `LocalSet` is being
polled or dropped. Keep blocking work out of futures and destructors driven by
the local set, or move it to `spawn_blocking`.

### Blocking-pool patch floor (1.52.0)

The sharded blocking queue introduced by 1.52.0 can make `spawn_blocking`
hang. Use at least 1.52.1 on this line; it reverts the problematic queue.

### Work created by `before_park` (1.53.1)

Tokio 1.51.4 and 1.52.4 fix runtimes skipping the driver when a
`before_park` callback schedules work. Select the appropriate patched line
when the callback can make work ready.

## Runtime metrics

### Unstable metrics (1.39.0)

The unstable metrics API adds:

- `spawned_tasks_count`;
- `worker_park_unpark_count`;
- access to worker thread IDs.

### Stable global queue depth (1.41.0)

`RuntimeMetrics::global_queue_depth` is stable and does not require unstable
API configuration.

### H2 histograms (1.41.0)

Unstable runtime-metrics configuration adds an H2 histogram option for finer
granularity and renames existing histogram APIs. Update unstable configuration
code that used the former names.

### Stable per-worker metrics (1.45.0)

These `RuntimeMetrics` methods become stable:

- `worker_total_busy_duration`;
- `worker_park_count`;
- `worker_unpark_count`.

### Alive-task sampling (1.49.0)

`num_alive_tasks` is not strongly consistent. Concurrent task changes make a
sample unsuitable as an exact invariant or synchronization condition.

### Task schedule latency (1.53.1)

The runtime metrics API adds a task schedule-latency metric in 1.53.0. It lets
instrumentation measure how long scheduled tasks wait before execution.

## Hooks, tracing, and task dumps

### Task lifecycle hooks (1.40.0)

The unstable runtime builder adds `on_task_spawn` and `on_task_terminate`
callbacks for observing task lifecycle events.

### Task-poll callbacks and tracing (1.44.0)

The unstable runtime API adds callbacks immediately before and after every
task poll. The task-tracing API is also publicly available as unstable for
integrations that consume task-level tracing data.

### Spawn locations (1.46.0)

Unstable runtime metadata records where tasks are spawned. In 1.46.0,
`TaskMeta::spawned_at` is wrong for tasks created with `tokio::spawn`; tasks
created with `Runtime::spawn` and tracing event locations are unaffected. Use
at least 1.46.1 when hooks consume this field.

### Task-dump configuration and output

- Select the unstable `taskdump` subsystem with a Cargo feature as of 1.48.0,
  replacing its former custom `--cfg` switch.
- Tokio 1.52.0 adds `trace_with` for customized unstable task dumps. Its
  callback is `FnMut()`, so it may carry mutable state.
- Tokio 1.52.4 removes crate disambiguators from unstable task-dump output.
  Update output parsers and snapshots that expected them.
- Tokio 1.53.0 supports unstable task dumps on s390x.

### Eager driver handoff (1.52.0)

With unstable APIs, `runtime::Builder::enable_eager_driver_handoff` hands off
the I/O and time drivers eagerly before tasks are polled.

## Diagnostics and trait bounds

### Panic messages in join errors (1.40.0)

Formatting a panicked task's `JoinError` includes the panic message. Logs and
tests that inspect diagnostic text must account for it.

### Unwind-safe runtime handles (1.45.0)

`runtime::Handle` is unwind-safe and can satisfy unwind-safety bounds around
panic-catching boundaries.

### Caller-aware timeouts (1.53.1)

`time::timeout_at` is `#[track_caller]` as of 1.53.0. Panic diagnostics point
to the caller rather than an internal Tokio location.

## Unstable timer correctness (1.53.1)

For the unstable alternate timer:

- Tokio 1.53.0 keeps a timer associated with its original runtime after
  `Sleep::reset`;
- Tokio 1.53.1 fixes a race between timer cancellation and insertion.
