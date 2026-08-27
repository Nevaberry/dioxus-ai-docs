# Queues, Jobs, and Scheduling

Queue drivers, jobs and batches, workers, deferred execution, and scheduler behavior.

## `JobAttempted` exception data (13.0-upgrade)

`JobAttempted::$exception` now contains the thrown exception or `null`, replacing the boolean `$exceptionOccurred` property.

## `QueueBusy` connection name (13.0-upgrade)

`QueueBusy::$connection` has been renamed to `$connectionName`; queue event listeners must use the new property.

## Adding multiple jobs to a chain (2025-05)

`appendToChain()` and `prependToChain()` accept multiple jobs at once, such as `$this->appendToChain([new PublishReport, new NotifyOwner])`.

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

## Central class-based queue routing (13.0.0)

`Queue::route()` defines the default connection and queue for a job class in one central location.

```php
Queue::route(ProcessPodcast::class, connection: 'redis', queue: 'podcasts');
```

## Clearing multiple queues (2026-07)

The `queue:clear` command can clear multiple queues in one invocation.

## Conditional job lists (2026-01)

`Bus::batch()` and `Bus::chain()` filter falsy members from their job lists, so callers may include jobs conditionally without pre-filtering the array.

## Day-of-month schedules (2025-11)

Scheduled events can target specific calendar days with `daysOfMonth()`.

```php
Schedule::command('reports:close')->daysOfMonth([1, 15]);
```

## Debounceable queued jobs (2026-04)

Queued jobs can be debounced, and `DebounceFor` declarations are inherited by subclasses.

## Deferred callbacks on sync queues (2026-02)

Deferred callbacks registered while using the sync queue are now retained instead of being discarded.

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

## Foreground scheduled-task failures (2025-06)

A failed foreground scheduled task now dispatches `ScheduledTaskFailed`, so scheduler failure listeners observe foreground and background failures consistently.

## Laravel Cloud queue integration (2026-05)

Laravel 12 and 13 add dedicated Cloud queue support, Cloud metrics that can honor `after_commit`, cached-configuration support, and scoped filesystem support. Managed queues boot before application service providers, missing queues throw `ManagedQueueNotFoundException`, and `Cloud-Request-ID` is logged for request correlation.

## Machine-readable failed-job listings (2026-05)

`queue:failed` supports JSON output, and its normal listing reports the actual job class name.

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

## Redis Cluster queues and concurrency (2026-04)

Queues and `ConcurrencyLimiter` now have first-class Redis Cluster support.

## Redis command failure listeners (2026-01)

Redis connections expose `listenForFailures()` and dispatch `CommandFailed`, allowing applications to observe failed Redis commands explicitly.

## Redis connections for queue middleware (2026-02)

Redis-based queue middleware can select an explicit Redis connection instead of always using the default connection.

## Released-job exception data (2026-07)

`JobReleasedAfterException` now exposes the exception that caused the job to be released.

## Richer inspected jobs (2026-06)

`InspectedJob` now includes payload and queue information, extending the queue inspection APIs with the data needed to identify and examine a queued job.

## Schedule-group callbacks (2026-05)

`Schedule::group()` now accepts lifecycle and output callbacks. Scheduled callbacks can receive the scheduled `Event`, with parameters resolved by type rather than parameter name.

## Schedule-group termination handling (2026-04)

`releaseOnTerminationSignals()` configured on a schedule group now propagates to its grouped events.

## Scheduled context propagation (2025-11)

Scheduled tasks now receive Laravel context from the scheduling process, preserving contextual values across scheduled execution.

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

## Unique job locks after rollback (2025-04)

When an `afterCommit()` job implementing `ShouldBeUnique` is discarded by a transaction rollback, its unique lock is now released instead of remaining stuck.

## Unique queued listeners (2026-02)

Queued event listeners can now participate in Laravel's uniqueness mechanism, preventing duplicate listener jobs from being enqueued together.

## Wider queue attempt counters (2026-04)

The queue job `attempts` column now uses a small integer instead of a tiny integer; custom job-table migrations should use the wider type when matching the framework schema.

## Worker stop memory usage (2026-07)

`WorkerStopping` now also exposes memory usage for worker shutdown telemetry.

## Worker stop telemetry (2026-06)

`WorkerStopping` exposes the processed-job count and the last-job timestamp; the timestamp is `null` when the worker processed no jobs.
