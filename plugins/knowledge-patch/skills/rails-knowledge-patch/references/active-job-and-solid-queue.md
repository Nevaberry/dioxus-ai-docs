# Active Job and Solid Queue

Topic details draw from batches `7.2`, `8.0-guide`, `8.0`, `8.1-guide`, and `8.1`.

## Contents

- [Transactional enqueueing and compatibility](#transactional-enqueueing-and-compatibility)
- [Solid Queue installation and database layout](#solid-queue-installation-and-database-layout)
- [Supervisor, worker, and dispatcher operation](#supervisor-worker-and-dispatcher-operation)
- [Failures and lifecycle hooks](#failures-and-lifecycle-hooks)
- [Concurrency controls](#concurrency-controls)
- [Recurring tasks](#recurring-tasks)
- [Continuable jobs](#continuable-jobs)

## Transactional enqueueing and compatibility

### Enqueue after commit

Jobs scheduled inside an Active Record transaction are deferred until commit and dropped on rollback (`7.2`). A queue adapter can disable this behavior. In the earlier API, one job could opt out explicitly:

```ruby
class NewTopicNotificationJob < ApplicationJob
  self.enqueue_after_transaction_commit = :never
end
```

Treat this as migration syntax only. The symbolic `:never`, `:always`, and `:default` values and `config.active_job.enqueue_after_transaction_commit` are removed in `8.1`; supported job-level configuration is boolean, and `perform_all_later` honors it:

```ruby
class AuditJob < ApplicationJob
  self.enqueue_after_transaction_commit = true
end
```

The control itself was deprecated during `8.0`; when targeting the current API, do not infer that this deprecation removed the remaining boolean job-level setting.

### Argument, scheduling, retry, and adapter changes

Remove the following old forms (`7.2`):

- Active Job's primitive `BigDecimal` serializer.
- Numeric `scheduled_at` values.
- `retry_on wait: :exponentially_longer`.
- Reliance on `config.active_job.use_big_decimal_serializer`, which is deprecated.

The internal `SuckerPunch` adapter is deprecated in `8.0`; use the adapter from the `sucker_punch` gem. The built-in Sidekiq adapter is deprecated in `8.1`; use the adapter supplied by Sidekiq.

Custom serializers must expose a public `klass` method (`8.1`).

## Solid Queue installation and database layout

The installer described in `8.0-guide` creates:

- `config/queue.yml`
- `config/recurring.yml`
- `db/queue_schema.rb`
- `bin/jobs`

Production is configured to use the Solid Queue adapter and a separate writing connection named `queue`:

```ruby
config.active_job.queue_adapter = :solid_queue
config.solid_queue.connects_to = { database: { writing: :queue } }
```

To run Solid Queue in another environment, configure its adapter and database connection there, run `db:prepare`, and start the supervisor. Do not assume production's database stanza applies to other environments.

To keep jobs in the main application database instead:

1. Convert `db/queue_schema.rb` into a normal migration.
2. Delete `db/queue_schema.rb` after moving its definitions.
3. Remove `config.solid_queue.connects_to`.

## Supervisor, worker, and dispatcher operation

### Default topology and queue ordering

With no actor configuration, Solid Queue starts one dispatcher and one worker (`8.0-guide`). If configuration contains only one actor section, it runs only that actor kind.

Keep the thread count of each worker no greater than its queue database pool size minus two. A worker exhausts queue names in their configured order, so queue order takes precedence over job priority. Within one queue, smaller numeric priorities run first; the default priority is `0`.

```yaml
production:
  workers:
    - queues: [real_time, background]
      threads: 5
      processes: 3
```

### Process and async modes

`bin/jobs` and the Puma plugin fork actor processes by default. Run `bin/jobs --mode async` or set `SOLID_QUEUE_SUPERVISOR_MODE=async` to keep actors in supervisor threads. Async mode ignores the worker `processes` setting.

The equivalent Puma configuration is:

```ruby
plugin :solid_queue
solid_queue_mode :async
```

The Puma plugin requires application preloading and does not support phased restarts (`8.0-guide`).

## Failures and lifecycle hooks

### Hook registration

Start and stop hooks exist for supervisors, workers, dispatchers, and schedulers (`8.0-guide`). Each hook receives the actor instance, and the same hook kind can be registered more than once. Register hooks before Solid Queue starts.

```ruby
SolidQueue.on_worker_start do |worker|
  Rails.logger.info(worker.queues.join(","))
end
```

### Enqueue and execution failures

An Active Record failure during Solid Queue enqueueing raises `SolidQueue::Job::EnqueueError`, not an absorbed `ActiveJob::EnqueueError` (`8.0-guide`). Account for the different exception in callers that need to retry or report an enqueue failure.

Failed executions remain in storage until retried or discarded:

```ruby
failure = SolidQueue::FailedExecution.find(id)
failure.error
failure.retry
# or
failure.discard
```

An immediate orderly shutdown returns in-flight work to its queue. A pruned process leaves an inspectable `SolidQueue::Processes::ProcessPrunedError`; an unexpectedly killed process leaves `SolidQueue::Processes::ProcessExitError`.

## Concurrency controls

For `limits_concurrency`, only `key` is required (`8.0-guide`). Defaults are:

- `to: 1`
- `duration: 3.minutes`
- `group:` the job class
- `on_conflict: :block`

Use `on_conflict: :discard` to prevent the conflicting job from being enqueued:

```ruby
limits_concurrency to: 2,
  key: ->(contact) { contact.account },
  duration: 5.minutes,
  group: "AccountDelivery",
  on_conflict: :discard
```

`duration` is a semaphore-expiry failsafe, not a maximum execution time. Delayed jobs claim concurrency only when they become due. Controlled jobs are enqueued individually rather than in bulk. Blocked jobs are released by priority without considering queue ordering.

## Recurring tasks

### File-backed schedules

The scheduler reads `config/recurring.yml` (`8.0-guide`). Each task needs a Fugit-compatible `schedule` and either a job `class` or an evaluated `command`; it may also provide `args`, `queue`, and `priority`.

```yaml
production:
  report:
    class: ReportJob
    args: [42, { format: "csv" }]
    schedule: "0 7 * * *"
```

Multiple schedulers can safely share one schedule. Duplicate prevention lasts only while finished jobs remain preserved, and it does not apply when the recurring job uses a different queue adapter.

### Dynamic schedules

Enable database-backed schedules under the scheduler configuration:

```yaml
production:
  scheduler:
    dynamic_tasks_enabled: true
```

Dynamic tasks persist across restarts and can be changed at runtime:

```ruby
SolidQueue.schedule_recurring_task(
  "refresh",
  class: "RefreshJob",
  args: [1, 2],
  schedule: "every 10 minutes"
)
SolidQueue.unschedule_recurring_task("refresh")
```

Only dynamically created tasks can be unscheduled through this API (`8.0-guide`).

## Continuable jobs

Include `ActiveJob::Continuable` to define durable steps that resume after interruption without repeating completed steps (`8.1-guide`). A step may persist a cursor with `advance!` so iteration resumes inside the step:

```ruby
class ProcessImportJob < ApplicationJob
  include ActiveJob::Continuable

  def perform(import_id)
    @import = Import.find(import_id)

    step(:initialize) { @import.initialize }
    step :process do |step|
      @import.records.find_each(start: step.cursor) do |record|
        record.process
        step.advance! from: record.id
      end
    end
    step :finalize
  end

  private

  def finalize = @import.finalize
end
```
