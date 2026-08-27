# Runtime, tasks, and scheduling

## Runtime construction and identity

- `runtime::Handle` satisfies unwind-safety bounds from 1.45.0.
- An unstable `LocalRuntime` first appears in 1.41.0 for local task execution;
  it remains behind the unstable API configuration in that release.
- Blocking while a `LocalSet` is polled or dropped is rejected from 1.46.0.
  Move blocking futures and destructor work to `spawn_blocking` or outside the
  local set.
- The unstable `Builder::build_local` accepts `LocalOptions` by value from
  1.46.0. The unstable `#[tokio::main(flavor = "local")]` and matching test
  macro flavor arrive in 1.48.0.
- Stable `runtime::id::Id` and `LocalSet::id()` arrive in 1.49.0.
- `Builder::event_interval(0)` panics from 1.50.0; validate configuration before
  construction. The default runtime thread name also becomes shorter, so set a
  name explicitly when diagnostics or tests depend on it.
- Tokio 1.51.0 stabilizes `runtime::LocalRuntime`, allows runtimes to carry a
  name, and adds `runtime::worker_index()` for per-worker context.
- Tokio 1.53.0 fixes a stack overflow that could occur during runtime
  construction.

## Awaitables and cooperative scheduling

- `time::timeout`, `join!`, and `select!` accept `IntoFuture` values from
  1.39.0, so custom awaitables need not be converted manually.
- `watch` receive operations and `broadcast::Receiver` consume cooperative task
  budget from 1.41.0.
- `yield_now` takes effect immediately inside `block_in_place` from 1.42.0.
- `task::coop` is public from 1.44.0 for custom resources; `select!` also becomes
  budget-aware in that release.
- `task::coop::cooperative` and `poll_proceed` arrive in 1.47.0 for wrapping
  futures and checking budget in custom polling code.
- When `before_park` can schedule work, use 1.51.4 on the 1.51 line or 1.52.4
  on the 1.52 line so the runtime does not skip the driver.

## Task APIs and lifecycle

- Task `Id` APIs are stable from 1.41.0, and `Id` implements `Ord` from 1.48.0.
- `JoinHandle::abort_handle()` is `#[must_use]` from 1.40.0; retain or explicitly
  discard the returned handle.
- Formatting a panicked task's `JoinError` includes the panic message from
  1.40.0, changing log and snapshot text.
- `LocalKey::try_get()` provides non-panicking access to absent task-local state
  from 1.48.0.
- `JoinSet<T>` implements `Extend` from 1.49.0.
- A task future and its retained state are dropped before the `JoinHandle`
  completes from 1.50.0, so destructors have run when `await` returns.

## Metrics

- Unstable `spawned_tasks_count`, combined `worker_park_unpark_count`, and
  worker thread IDs arrive in 1.39.0.
- `RuntimeMetrics::global_queue_depth` is stable from 1.41.0. That release also
  adds unstable H2 histograms and renames existing histogram configuration.
- Per-worker total busy duration and park/unpark counts are stable from 1.45.0.
- `num_alive_tasks` is not strongly consistent as of 1.49.0; never use one
  sample as a concurrency invariant.
- Tokio 1.53.0 adds task schedule-latency metrics for time spent ready but not
  yet executing.

## Hooks, tracing, timers, and diagnostics

- Unstable runtime builders gain `on_task_spawn` and `on_task_terminate` in
  1.40.0, and before/after task-poll callbacks plus public task tracing in
  1.44.0.
- Unstable task metadata records spawn locations from 1.46.0. Require 1.46.1
  when hooks inspect `TaskMeta::spawned_at` for tasks created by `tokio::spawn`;
  tracing event locations are not affected by the 1.46.0 bug.
- Unstable `Builder::enable_eager_driver_handoff` arrives in 1.52.0 and hands
  off I/O and time drivers before polling tasks.
- Task dumps gain `trace_with` in 1.52.0; its callback is `FnMut()`. Tokio
  1.52.4 removes crate disambiguators from dump output, which can change
  parsers and snapshots, while 1.53.0 adds s390x dump support.
- With the unstable alternate timer, Tokio 1.53.0 keeps a timer on its original
  runtime after `Sleep::reset`, and 1.53.1 fixes a cancellation/insertion race.
- `time::timeout_at` is `#[track_caller]` from 1.53.0, so panic diagnostics point
  to the caller rather than an internal location.
- Use `is_rt_shutdown_err` from 1.50.0 to distinguish runtime-shutdown errors.
