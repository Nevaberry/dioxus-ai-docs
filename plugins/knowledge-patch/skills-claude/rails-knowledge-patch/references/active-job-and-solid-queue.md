# Active Job and Solid Queue

## Transactional enqueueing

### Commit-aware jobs

Starting with `7.2`, jobs enqueued inside an Active Record transaction are
deferred until commit and dropped on rollback. An adapter can disable this
behavior. At that point an individual job could opt out with a symbolic value:

```ruby
class NewTopicNotificationJob < ApplicationJob
  self.enqueue_after_transaction_commit = :never
end
```

The configuration changed later. In `8.0`,
`enqueue_after_transaction_commit` was deprecated. In `8.1`, symbolic
`:never`, `:always`, and `:default` values and the application-wide
`config.active_job.enqueue_after_transaction_commit` setting are removed, but
job-level boolean configuration remains:

```ruby
class AuditJob < ApplicationJob
  self.enqueue_after_transaction_commit = true
end
```

`perform_all_later` honors that job-level setting. Audit version-sensitive code
rather than carrying the old symbolic override into current applications.

### Removed argument and scheduling forms

Active Job no longer supports its primitive `BigDecimal` serializer, numeric
`scheduled_at` values, or `:exponentially_longer` as a `retry_on wait:` value.
The `config.active_job.use_big_decimal_serializer` compatibility switch is
deprecated.

Custom serializers in `8.1` must expose a public `klass` method.

### Adapter ownership

The internal SuckerPunch adapter was deprecated in `8.0`; use the adapter
provided by the `sucker_punch` gem. The built-in Sidekiq adapter is deprecated
in `8.1`; use the adapter supplied by Sidekiq.

## Resumable work

### Continuations

The `8.1-guide` introduces `ActiveJob::Continuable` for long-running jobs that
must resume after an interruption without repeating completed work. Declare
discrete steps. A named step can be a method or a block, and a block receives a
step object that can persist a cursor with `advance!`.

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

Advance the cursor only after the record's work completes so resumption does
not skip unfinished work.

## Installing Solid Queue

### Default files and database topology

The `8.0-guide` installer creates:

- `config/queue.yml`
- `config/recurring.yml`
- `db/queue_schema.rb`
- `bin/jobs`

Production is configured to use a separate `queue` database:

```ruby
config.active_job.queue_adapter = :solid_queue
config.solid_queue.connects_to = { database: { writing: :queue } }
```

Each additional environment needs its own adapter selection, database
connection, `db:prepare`, and running supervisor.

To keep Solid Queue in the primary database, move `db/queue_schema.rb` into a
normal migration, delete the queue schema file, and remove
`config.solid_queue.connects_to`.

## Workers and processes

### Actor topology

With no actor configuration, Solid Queue starts one dispatcher and one worker.
If configuration contains only one actor section, it starts only that actor
kind.

Keep a worker's thread count at or below its queue database pool size minus two:

```yaml
production:
  workers:
    - queues: [real_time, background]
      threads: 5
      processes: 3
```

Workers exhaust listed queues in order, so queue order outranks job priority.
Inside one queue, smaller numeric priority values run first and `0` is the
default.

### Forked and async supervisor modes

`bin/jobs` and the Puma plugin use forked processes by default. Use
`bin/jobs --mode async` or `SOLID_QUEUE_SUPERVISOR_MODE=async` to run actors in
supervisor threads; async mode ignores the workers' `processes` setting.

For Puma:

```ruby
plugin :solid_queue
solid_queue_mode :async
```

The Puma plugin requires preloading and does not support phased restarts.

### Lifecycle hooks

Supervisor, worker, dispatcher, and scheduler start and stop hooks receive the
actor instance. Hooks may be registered more than once, but registration must
happen before Solid Queue starts.

```ruby
SolidQueue.on_worker_start do |worker|
  Rails.logger.info(worker.queues.join(","))
end
```

## Failures and shutdown

Active Record failures during enqueue raise `SolidQueue::Job::EnqueueError`
rather than being absorbed as `ActiveJob::EnqueueError`.

Failed executions remain stored until retried or discarded:

```ruby
failure = SolidQueue::FailedExecution.find(id)
failure.error
failure.retry # or failure.discard
```

An immediate orderly shutdown returns in-flight work to its queue. A pruned
process or an unexpectedly killed process instead leaves an inspectable failure
with `SolidQueue::Processes::ProcessPrunedError` or
`SolidQueue::Processes::ProcessExitError`.

## Concurrency controls

For `limits_concurrency`, only `key` is required. Defaults are:

- `to: 1`
- `duration: 3.minutes`
- `group`: the job class
- `on_conflict: :block`

`on_conflict: :discard` prevents a conflicting job from being enqueued.
`duration` is semaphore expiry, not a maximum job runtime. Delayed jobs claim
concurrency when they become due. Controlled jobs are enqueued individually,
not in bulk, and blocked jobs are released by priority without considering
queue order.

```ruby
limits_concurrency to: 2,
  key: ->(contact) { contact.account },
  duration: 5.minutes,
  group: "AccountDelivery",
  on_conflict: :discard
```

## Recurring work

### Static schedules

The scheduler reads `config/recurring.yml`. Every task supplies a
Fugit-compatible `schedule` and either a job `class` or an evaluated `command`;
`args`, `queue`, and `priority` are optional.

```yaml
production:
  report:
    class: ReportJob
    args: [42, { format: "csv" }]
    schedule: "0 7 * * *"
```

Multiple schedulers may safely share one schedule. Duplicate prevention lasts
only while finished jobs are preserved and does not apply when the recurring
job uses a different queue adapter.

### Dynamic schedules

Database-backed recurring tasks require `dynamic_tasks_enabled: true` and
persist across restarts:

```yaml
production:
  scheduler:
    dynamic_tasks_enabled: true
```

```ruby
SolidQueue.schedule_recurring_task(
  "refresh",
  class: "RefreshJob",
  args: [1, 2],
  schedule: "every 10 minutes"
)
SolidQueue.unschedule_recurring_task("refresh")
```

Only tasks created dynamically can be unscheduled through this API.
