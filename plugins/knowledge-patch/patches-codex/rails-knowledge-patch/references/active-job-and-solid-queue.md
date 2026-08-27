# Active Job and Solid Queue

## Transaction-aware enqueueing

Rails 7.2 (`7.2`) defers jobs enqueued in an Active Record transaction until commit and drops them on rollback. This depends on adapter support, and adapters may disable it. At that release an individual job could opt out with the symbolic value `:never`.

Rails 8.0 (`8.0`) deprecated `enqueue_after_transaction_commit`. Rails 8.1 (`8.1`) then removed its symbolic `:never`, `:always`, and `:default` values and removed `config.active_job.enqueue_after_transaction_commit`, while retaining boolean job-level configuration. `perform_all_later` honors that boolean:

```ruby
class AuditJob < ApplicationJob
  self.enqueue_after_transaction_commit = true
end
```

Treat this as a versioned migration: old 7.2 code may show `:never`, but current code must use a boolean rather than preserving the old symbol.

## Argument, scheduling, retry, and adapter compatibility

Rails 7.2 (`7.2`) removes primitive `BigDecimal` serialization, numeric `scheduled_at`, and `retry_on wait: :exponentially_longer`; it deprecates `config.active_job.use_big_decimal_serializer`. Replace each removed form during the upgrade.

Rails 8.0 (`8.0`) deprecates the internal SuckerPunch adapter; use the adapter supplied by the `sucker_punch` gem. Rails 8.1 (`8.1`) requires custom serializers to expose a public `klass` and deprecates the built-in Sidekiq adapter in favor of Sidekiq's adapter.

## Continuable jobs

Active Job continuations (`8.1-guide`) make long work resumable. Include `ActiveJob::Continuable`, divide `perform` into named steps, and use `step.advance!` to persist a cursor only after successfully completing a unit of work. Completed steps are not repeated after an interruption.

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

## Solid Queue installation and databases

The Solid Queue installer (`8.0-guide`) creates:

- `config/queue.yml`
- `config/recurring.yml`
- `db/queue_schema.rb`
- `bin/jobs`

Production normally writes through a separate `queue` database:

```ruby
config.active_job.queue_adapter = :solid_queue
config.solid_queue.connects_to = { database: { writing: :queue } }
```

For every additional environment, configure its adapter and database connection, run `db:prepare`, and run a supervisor. To use the primary database instead, move `db/queue_schema.rb` into a normal migration, delete the schema file, and remove `config.solid_queue.connects_to`.

## Worker topology and ordering

With no explicit actor configuration, Solid Queue starts one dispatcher and one worker. Configuring only one actor section runs only that actor kind. Keep each worker's thread count at or below its queue database pool size minus two.

```yaml
production:
  workers:
    - queues: [real_time, background]
      threads: 5
      processes: 3
```

Workers exhaust listed queues in order, so queue order takes precedence over job priority. Within one queue, smaller numeric priorities run first and `0` is the default.

## Process modes and Puma

`bin/jobs` and the Puma plugin use forked processes by default. Use `bin/jobs --mode async` or `SOLID_QUEUE_SUPERVISOR_MODE=async` to keep actors in supervisor threads; async mode ignores worker `processes`.

```ruby
plugin :solid_queue
solid_queue_mode :async
```

The Puma plugin requires preloading and does not support phased restarts.

## Lifecycle hooks

Supervisor, worker, dispatcher, and scheduler start/stop hooks receive the actor instance. Register any number of hooks, but register them before Solid Queue starts.

```ruby
SolidQueue.on_worker_start do |worker|
  Rails.logger.info(worker.queues.join(","))
end
```

## Enqueue and process failures

Active Record failures during enqueue raise `SolidQueue::Job::EnqueueError`, not `ActiveJob::EnqueueError`. Failed executions stay present until retried or discarded:

```ruby
failure = SolidQueue::FailedExecution.find(id)
failure.error
failure.retry # or failure.discard
```

An immediate orderly shutdown returns in-flight work to its queue. A pruned or unexpectedly killed process leaves inspectable `SolidQueue::Processes::ProcessPrunedError` or `SolidQueue::Processes::ProcessExitError` failures.

## Concurrency limits

For `limits_concurrency`, only `key` is required. Defaults are `to: 1`, `duration: 3.minutes`, the job class as `group`, and `on_conflict: :block`. `:discard` rejects the conflicting enqueue.

```ruby
limits_concurrency to: 2,
  key: ->(contact) { contact.account },
  duration: 5.minutes,
  group: "AccountDelivery",
  on_conflict: :discard
```

`duration` is a semaphore-expiry failsafe, not a maximum runtime. Delayed jobs claim concurrency when due. Controlled jobs enqueue individually instead of in bulk, and blocked jobs are released by priority without considering queue order.

## Recurring schedules

The scheduler reads `config/recurring.yml`. Each task provides a Fugit-compatible `schedule` and either a job `class` or an evaluated `command`; `args`, `queue`, and `priority` are optional.

```yaml
production:
  report:
    class: ReportJob
    args: [42, { format: "csv" }]
    schedule: "0 7 * * *"
```

Multiple schedulers may share one schedule. Duplicate prevention lasts only while finished jobs are preserved and does not apply when the recurring job uses another queue adapter.

## Dynamic recurring tasks

Database-backed recurring tasks require `dynamic_tasks_enabled: true`, persist across restarts, and can be managed at runtime. Only dynamically created tasks can be unscheduled through this API.

```yaml
production:
  scheduler:
    dynamic_tasks_enabled: true
```

```ruby
SolidQueue.schedule_recurring_task(
  "refresh", class: "RefreshJob", args: [1, 2], schedule: "every 10 minutes"
)
SolidQueue.unschedule_recurring_task("refresh")
```
