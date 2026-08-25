# Queues, Concurrency, Scheduling, and Processes

## `JobAttempted` exception data (13.0-upgrade)

`JobAttempted::$exception` now contains the thrown exception or `null`, replacing the boolean `$exceptionOccurred` property.

## `QueueBusy` connection name (13.0-upgrade)

`QueueBusy::$connection` has been renamed to `$connectionName`; queue event listeners must use the new property.

## Adding multiple jobs to a chain (2025-05)

`appendToChain()` and `prependToChain()` accept multiple jobs at once, such as `$this->appendToChain([new PublishReport, new NotifyOwner])`.

## Always-deferred flexible cache refreshes (2025-05)

`Cache::flexible()` accepts `alwaysDefer: true` to defer regeneration even when the current execution context would otherwise refresh immediately.

## Background queue execution (2025-11)

Queue jobs can be processed in the background through `Concurrently::defer()`, providing a background execution path distinct from the deferred queue option.

## Batch and worker lifecycle hooks (2026-04)

The new `BatchStarted` event exposes batch startup. Jobs can react to worker signals, `WorkerInterrupted` reports interruptions, and `WorkerStopReason` includes lost connections; pausing is disabled for managed queue workers.

## Batch cancellation events (2026-02)

Cancelling a job batch now dispatches `BatchCancelled`, allowing listeners to react explicitly to cancellation.

## Batchable job generation (2025-06)

`make:job` accepts `--batchable` to scaffold a job with batch support.

```shell
php artisan make:job ImportChunk --batchable
```

## Batched-job failure callbacks (2025-09)

Jobs executed inside a batch now support job failure callbacks, allowing batch members to perform their own failure-specific cleanup or reporting.

## Beanstalkd client compatibility (13.0.0)

The Beanstalkd queue integration supports `pda/pheanstalk` 8.x and no longer supports 5.x.

## Callback-scoped queue fakes (2025-07)

`Queue::fakeFor()` and `Queue::fakeExceptFor()` temporarily scope queue faking to a callback, including a variant that lets selected jobs continue to use the real queue.

## Carbon intervals for process timeouts (13.0.0)

Pending process timeouts accept `CarbonInterval` values in addition to numeric durations.

```php
Process::timeout(CarbonInterval::seconds(30))->run('php artisan report:build');
```

## Central class-based queue routing (13.0.0)

`Queue::route()` defines the default connection and queue for a job class in one central location.

```php
Queue::route(ProcessPodcast::class, connection: 'redis', queue: 'podcasts');
```

## Clearing multiple queues (2026-07)

The `queue:clear` command can clear multiple queues in one invocation.

## Conditional job lists (2026-01)

`Bus::batch()` and `Bus::chain()` filter falsy members from their job lists, so callers may include jobs conditionally without pre-filtering the array.

## Custom queued-notification jobs (2025-06)

Queued notification dispatch can override the default `SendQueuedNotifications` job class when job-level behavior needs customization.

## Day-of-month schedules (2025-11)

Scheduled events can target specific calendar days with `daysOfMonth()`.

```php
Schedule::command('reports:close')->daysOfMonth([1, 15]);
```

## Debounceable queued jobs (2026-04)

Queued jobs can be debounced, and `DebounceFor` declarations are inherited by subclasses.

## Deferred callbacks on sync queues (2026-02)

Deferred callbacks registered while using the sync queue are now retained instead of being discarded.

## Deferred HTTP batches (2025-10)

HTTP client batches provide `defer()`, allowing a batch to be scheduled for deferred execution instead of being sent immediately.

## Deferred queue execution (2025-10)

Laravel includes a deferred queue option for sending queued work through deferred execution rather than requiring an external worker.

## Deferred schedule registration (13.0-upgrade)

Schedules passed to `ApplicationBuilder::withScheduling()` are now registered only when `Schedule` is resolved; bootstrap code must not rely on immediate registration.

## Delay attributes in batches and bulk dispatch (2026-07)

The `Delay` attribute is honored by `Bus::batch()` and bulk dispatch.

## Disabling queue memory verification (12.0.0)

A zero memory limit now disables the worker's memory-exceeded check instead of acting as an immediately exceeded limit.

```shell
php artisan queue:work --memory=0
```

## Disk-backed SQS overflow payloads (2026-05)

SQS queues may offload large payloads to optional disk storage. `queue:clear` can optionally flush that overflow store as well.

## Dynamic missing-model handling for queued listeners (13.0.0)

Queued listeners may now decide dynamically whether their job should be deleted when a serialized model is missing, rather than relying only on a fixed setting.

## Dynamic queued-listener retry counts (2025-09)

Queueable listeners may define a `tries()` method to calculate their retry count dynamically instead of relying only on a fixed property.

## Enum scheduler cache stores (2025-10)

`Schedule::useCache()` accepts enum cache-store selectors in addition to strings.

## Environment data in schedule listings (2025-11)

The JSON output from `schedule:list` now includes environment information for scheduled events.

## Exact queue dispatch assertions (2026-01)

`QueueFake::assertPushedTimes()` is now public, allowing tests to assert an exact job dispatch count.

```php
Queue::assertPushedTimes(SendReport::class, 2);
```

## Expanded worker lifecycle control (2026-05)

Laravel 13 adds `WorkerIdle`; the `WorkerPausing`, `WorkerResuming`, `WorkerInterrupted`, and `Looping` events now carry `WorkerOptions`. Worker timeout exit codes can be overridden, and workers can opt out of restarting when a connection is lost.

## Failing throttled jobs conditionally (2025-07)

`ThrottlesExceptions::failWhen()` lets queue middleware fail a job when a thrown exception matches a callback instead of continuing its normal throttled retry handling.

```php
(new ThrottlesExceptions(10, 300))
    ->failWhen(fn (Throwable $e) => $e instanceof InvalidArgumentException);
```

## Failover queues (2025-10)

Laravel includes failover queue support for trying alternative queue connections when the primary connection fails. The `QueueFailedOver` event receives the originating exception so listeners can inspect the failure.

## Filtering schedule listings by environment (2026-05)

`schedule:list` can filter scheduled events by environment, so deployment tooling can inspect only events active for a target environment.

## First-party image processing (2026-07)

Laravel 13 adds first-party image processing, and `ImageManager::fromStorage()` accepts enum disk selectors.

## Foreground scheduled-task failures (2025-06)

A failed foreground scheduled task now dispatches `ScheduledTaskFailed`, so scheduler failure listeners observe foreground and background failures consistently.

## HTTP pool and batch concurrency (2025-10)

`Http::pool()` and `Http::batch()` support concurrency control, allowing callers to bound the number of simultaneous outgoing requests.

## HTTP pool default concurrency (13.0.0)

Pools created from `PendingRequest` now default to a concurrency of two; specify concurrency explicitly when a different limit is required.

## HTTP request batches (2025-09)

`Http::batch()` provides first-class batching for multiple outgoing HTTP requests, avoiding manual coordination when a set of client calls should be managed together.

## Keyed concurrency results (12.0-upgrade)

`Concurrency::run()` preserves keys when given an associative array, so callers now receive a keyed result instead of a numerically indexed one.

```php
$result = Concurrency::run([
    'first' => fn () => 2,
    'second' => fn () => 4,
]);
// ['first' => 2, 'second' => 4]
```

## Laravel Cloud queue integration (2026-05)

Laravel 12 and 13 add dedicated Cloud queue support, Cloud metrics that can honor `after_commit`, cached-configuration support, and scoped filesystem support. Managed queues boot before application service providers, missing queues throw `ManagedQueueNotFoundException`, and `Cloud-Request-ID` is logged for request correlation.

## Limiting Vite asset preloads (2025-05)

Laravel's Vite integration can cap the number of assets preloaded for an entry point, avoiding an unbounded set of preload links for large dependency graphs.

## Machine-readable failed-job listings (2026-05)

`queue:failed` supports JSON output, and its normal listing reports the actual job class name.

## Macroable invoked processes (2026-06)

`InvokedProcess` is now macroable, allowing applications to add project-specific helpers to invoked process instances.

## Missing models in queued notifications (13.0-upgrade)

Queued notifications now honor the notification class's `#[DeleteWhenMissingModels]` attribute and `$deleteWhenMissingModels` property, deleting the job instead of failing when a serialized model is missing.

## Named SQS credential providers (2026-04)

Laravel 12 and 13 SQS queue connections support named credential providers instead of requiring only inline credentials.

## Oldest pending queue metrics (2026-02)

`queue:monitor` now displays `oldest_pending`, exposing the oldest waiting job in its monitoring output.

## Pausing scheduled execution (13.0.0)

The scheduler provides dedicated pause and resume commands and emits corresponding lifecycle events.

```shell
php artisan schedule:pause
php artisan schedule:resume
```

## Pheanstalk 7 support (2025-04)

The Beanstalkd queue integration now supports `pda/pheanstalk` 7.

## Preparing jobs for dispatch (2026-05)

Jobs may implement `PreparesForDispatch` to participate in a preparation step before dispatch.

## Queue attribute refinements (2026-06)

Time-based queue attributes and `DebounceFor` support explicit units. Queue attributes may be declared on traits, while a child job's queue properties take precedence over inherited attributes.

## Queue contract metrics (13.0-upgrade)

Custom queue drivers must implement the contract methods `pendingSize`, `delayedSize`, `reservedSize`, and `creationTimeOfOldestPendingJob`, which were previously present only in docblocks.

## Queue delay attributes and runtime precedence (2026-04)

The `Illuminate\Queue\Attributes\Delay` attribute is honored by bus dispatch, queued notifications, and queued mailables. A runtime `onQueue()` selection takes precedence over class-level queue attributes.

## Queue job inspection (2026-04)

Laravel 13 adds queue methods for inspecting jobs instead of requiring direct access to a queue backend.

## Queue lifecycle events (2026-01)

Queue pause and resume operations now emit events, and sync jobs also dispatch `JobAttempted`. `JobPopping` includes the queue, `JobReleasedAfterException` includes the backoff, and the new `BatchFinished` event signals batch completion.

## Queue memory-limit exit codes (2025-09)

The queue worker's exit code after exceeding its memory limit is configurable, allowing process supervisors to distinguish or handle that shutdown condition as needed.

## Queue pausing (2025-11)

Queues can now be paused and resumed, and a pause may be limited to a specified number of seconds.

## Queue worker startup events (2025-06)

The `WorkerStarting` event is dispatched when a queue worker daemon starts, providing a hook for once-per-worker initialization or observation.

## Queue-fake inspection and push hooks (2026-07)

`QueueFake` can inspect delayed and reserved jobs, exposes `beforePushing()` and `afterPushing()` hooks, and implements `creationTimeOfOldestPendingJob()` for backend-free queue tests.

## Redis Cluster queues and concurrency (2026-04)

Queues and `ConcurrencyLimiter` now have first-class Redis Cluster support.

## Redis connections for queue middleware (2026-02)

Redis-based queue middleware can select an explicit Redis connection instead of always using the default connection.

## Released-job exception data (2026-07)

`JobReleasedAfterException` now exposes the exception that caused the job to be released.

## Reloadable service lifecycle (2025-12)

Laravel now provides a reload command and lets services register for reloading. Queue workers may also opt out of the `queuePaused` and `queueShouldRestart` cache checks when those controls are not needed.

## Richer inspected jobs (2026-06)

`InspectedJob` now includes payload and queue information, extending the queue inspection APIs with the data needed to identify and examine a queued job.

## Schedule-group callbacks (2026-05)

`Schedule::group()` now accepts lifecycle and output callbacks. Scheduled callbacks can receive the scheduled `Event`, with parameters resolved by type rather than parameter name.

## Schedule-group termination handling (2026-04)

`releaseOnTerminationSignals()` configured on a schedule group now propagates to its grouped events.

## Scheduled context propagation (2025-11)

Scheduled tasks now receive Laravel context from the scheduling process, preserving contextual values across scheduled execution.

## Scheduled output email default (12.0.0)

Scheduled command `emailOutput()` now sends mail only when output exists by default.

## Scheduled-event macros in groups (2026-02)

Macros registered on scheduled command events can be applied to schedule groups.

## Scheduler cache-check opt-outs (2026-06)

The scheduler can opt out of pause and interrupt cache checks when those shared-cache controls are not wanted.

## Scheduler output modes (2025-09)

`schedule:work` accepts `--whisper`, while `schedule:list --json` emits a machine-readable schedule listing for automation.

```shell
php artisan schedule:work --whisper
php artisan schedule:list --json
```

## Scheduler-aware reloads (2026-02)

The reload workflow now includes schedule interruption, so active scheduled execution participates in service reloads.

## Single-string queue routes (2026-04)

A string supplied to `Queue::route()` is treated as the queue name, not the connection name.

## SQS fair queues (2025-09)

SQS jobs now support fair-queue message groups alongside FIFO queues. The final framework property is `messageGroup` rather than the initially introduced `group`, and later changes in this batch fixed and extended both FIFO and fair-queue handling.

## Standardized queue sizing and metrics (2025-06)

Queue `size()` behavior is standardized and extended queue metrics are supported, giving monitoring code more consistent values across queue integrations.

## Timeouts for concurrent runs (2026-05)

`Concurrency::run()` supports runtime timeouts, allowing a group of concurrent tasks to be bounded.

## Unique job locks after rollback (2025-04)

When an `afterCommit()` job implementing `ShouldBeUnique` is discarded by a transaction rollback, its unique lock is now released instead of remaining stuck.

## Unique queued listeners (2026-02)

Queued event listeners can now participate in Laravel's uniqueness mechanism, preventing duplicate listener jobs from being enqueued together.

## Waiting on fake processes (2025-10)

`FakeInvokedProcess` now provides `waitUntil()`, allowing process-fake tests to cover code that waits for a condition using the same API as an invoked process.

## Wider queue attempt counters (2026-04)

The queue job `attempts` column now uses a small integer instead of a tiny integer; custom job-table migrations should use the wider type when matching the framework schema.

## Worker stop memory usage (2026-07)

`WorkerStopping` now also exposes memory usage for worker shutdown telemetry.

## Worker stop telemetry (2026-06)

`WorkerStopping` exposes the processed-job count and the last-job timestamp; the timestamp is `null` when the worker processed no jobs.
