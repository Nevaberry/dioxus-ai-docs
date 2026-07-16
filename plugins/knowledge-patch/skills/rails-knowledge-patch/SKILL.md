---
name: rails-knowledge-patch
description: Ruby on Rails 8.1 compatibility. Use for Ruby on Rails work.
license: MIT
version: "8.1"
metadata:
  author: Nevaberry
---

# Ruby on Rails Knowledge Patch

Use the quick references for upgrade-sensitive defaults and common implementation paths. Load the topic file before changing the corresponding subsystem; the reference files contain the complete behavioral details and edge cases.

## Reference index

| Reference | Topics |
|---|---|
| [Active Job and Solid Queue](references/active-job-and-solid-queue.md) | Transactional enqueueing, queue setup, workers, concurrency, recurring work, continuations |
| [Active Record and databases](references/active-record-and-databases.md) | Transactions, connections, migrations, queries, adapters, sharding, serialization, tests |
| [Operations, observability, and deployment](references/operations-observability-and-deployment.md) | Development containers, Puma, backtraces, events, CI, credentials, Kamal |
| [Upgrading and compatibility](references/upgrading-and-compatibility.md) | Removed APIs, changed defaults, deprecated call forms, replacement paths |
| [Web, assets, and storage](references/web-assets-and-storage.md) | Controllers, request parsing, rendering, Propshaft, Turbo, live streaming, Active Storage |

## Upgrade-critical quick reference

### Do not rely on transaction block exits

`return`, `break`, and `throw` no longer implicitly roll back an Active Record transaction. Do not use those control-flow exits as rollback signals.

Register post-transaction work on the transaction object:

```ruby
Article.transaction do |transaction|
  article.update!(published: true)
  transaction.after_commit { PublishNotificationJob.perform_later(article) }
end
```

Use `ActiveRecord.after_all_transactions_commit` for code that may run inside or outside a transaction but must wait for every open transaction to commit.

### Audit removed Active Record call forms

Replace these forms before an upgrade:

- Define `enum` with a positional name and mapping; keyword-style definitions are removed.
- Pass `coder:` and `type:` to `serialize`; positional coder or class arguments are removed.
- Do not point `alias_attribute` at a missing attribute or refer to a singular association by a plural name.
- Do not depend on `read_attribute(:id)` resolving a custom primary-key attribute.
- Remove `deferrable: true` from `add_foreign_key` and the `rewhere` option from `Relation#merge`.
- Remove calls to `ConnectionPool#connection` and the removed `ActiveRecord::Base.clear_*_connections!` or `flush_idle_connections!` methods.

`establish_connection` does not eagerly make `connection.active?` true. Call `ActiveRecord::Base.connection.verify!` when immediate verification is required.

### Update controller and view compatibility

- Do not compare `ActionController::Parameters` with a `Hash`.
- Replace boolean `config.action_dispatch.show_exceptions` values with a supported symbolic value.
- Do not pass content to void-element builders such as `tag.br`.
- Do not call `form_with(model: nil)`.
- Declare one route path at a time; multiple-path declarations are deprecated.

Query parsing treats a leading `[` in a root key literally and no longer splits pairs on semicolons. Remove reliance on `config.action_dispatch.ignore_leading_brackets`.

### Update framework compatibility surfaces

Remove uses of `Rails::ConsoleMethods`, `ActiveSupport::ProxyObject`, `@`-prefixed `attr_internal_naming_format`, array arguments to `ActiveSupport::Deprecation#warn`, `bin/rake stats`, and `STATS_DIRECTORIES`.

Plan replacements for deprecated `Benchmark.ms`, `String#mb_chars`, `ActiveSupport::Multibyte::Chars`, `ActiveSupport::Configurable`, the Active Storage Azure backend, and arithmetic between `Time` and `ActiveSupport::TimeWithZone`. `to_time` now always preserves the receiver timezone.

## Active Job quick reference

### Enqueueing and transactions

Jobs enqueued inside an Active Record transaction wait for commit and are dropped on rollback when the adapter supports this behavior. Current job-level configuration is boolean:

```ruby
class AuditJob < ApplicationJob
  self.enqueue_after_transaction_commit = true
end
```

Do not use the removed symbolic `:never`, `:always`, or `:default` values or the removed application-wide setting. `perform_all_later` honors the job-level setting.

Also remove primitive `BigDecimal` serialization, numeric `scheduled_at`, and `retry_on wait: :exponentially_longer`. Use the adapter supplied by Sidekiq or `sucker_punch` rather than the deprecated built-in adapters.

### Resumable jobs

Use `ActiveJob::Continuable` to split long work into durable steps. Advance the cursor after each completed record:

```ruby
class ProcessImportJob < ApplicationJob
  include ActiveJob::Continuable

  def perform(import_id)
    import = Import.find(import_id)
    step :process do |step|
      import.records.find_each(start: step.cursor) do |record|
        record.process
        step.advance! from: record.id
      end
    end
  end
end
```

## Solid Queue quick reference

Production installation normally uses a separate `queue` database, `db/queue_schema.rb`, `config/queue.yml`, `config/recurring.yml`, and `bin/jobs`. Configure and prepare the database separately in every additional environment.

Keep each worker's thread count at or below its queue database pool size minus two. Workers exhaust queue names in listed order before considering another queue; within one queue, smaller numeric priorities run first and `0` is the default.

Use async supervisor mode only when process isolation is unnecessary:

```ruby
plugin :solid_queue
solid_queue_mode :async
```

The Puma plugin requires preloading and cannot use phased restarts. Async mode ignores worker `processes`.

For `limits_concurrency`, remember that `duration` is semaphore expiry, not a runtime limit. The defaults are `to: 1`, three minutes, the job class as `group`, and `on_conflict: :block`; `:discard` rejects the conflicting enqueue.

## Database quick reference

### Migrations and preparation

On a fresh database, `db:migrate` loads the schema before pending migrations. Use `db:migrate:reset` to drop the database and replay all migrations; it supports multiple databases.

`db:prepare` seeds only the primary database by default. Override per database:

```yaml
primary:
  seeds: true
analytics:
  seeds: false
```

Set `schema_format` per database when different stores need Ruby and SQL dumps.

### Pools and adapter floors

Use `max_connections` for maximum pool size and optionally configure `min_connections`, `keepalive`, and `max_age`; defaults are unchanged. Ensure SQLite is at least 3.23.0 and PostgreSQL is at least 9.5 where the corresponding Rails point release requires it. MySQL requires 5.6.4 or newer.

For SQLite, replace adapter `retries` with `timeout`. Transactions use `IMMEDIATE` mode when possible, and busy errors are surfaced as `ActiveRecord::StatementTimeout`.

### Deterministic finders

The framework default can reject `first` or `last` without a relation or model order:

```ruby
config.active_record.raise_on_missing_required_finder_order_columns = true
self.implicit_order_column = [:created_at, nil]
```

The trailing `nil` prevents automatic primary-key tie-breaking.

## Web and asset quick reference

### Propshaft

Propshaft precompiles every file under `config.assets.paths`. Exclude compiler-only source directories by full path, and name already-digested files with `-[digest].digested.<extension>`.

Configure SRI and opt helpers in individually:

```ruby
config.assets.integrity_hash_algorithm = "sha384"
```

```erb
<%= stylesheet_link_tag "application", integrity: true %>
```

Production helpers omit integrity hashes over plain HTTP. `stylesheet_link_tag :all` selects every stylesheet; `:app` selects those below `app/assets`.

### Turbo morph refreshes

```html
<meta name="turbo-refresh-method" content="morph">
<meta name="turbo-refresh-scroll" content="preserve">
```

Use `refresh="morph"` on a `src`-backed Turbo Frame to reload and morph it during a page refresh. A `refresh` stream can override method and scrolling, and consecutive broadcast refreshes are debounced. In Rails, pair `broadcasts_refreshes` with `turbo_stream_from`.

### Storage hardening

Active Storage accepts one byte range per request and caps it at 100 MB by default. Disk service keys containing dot segments, invalid paths, or paths outside the root raise `InvalidKeyError`; prefix deletion treats glob metacharacters literally.

## Operations quick reference

Generated Puma configuration uses three threads instead of five. Recalculate process and database-pool capacity rather than assuming the old concurrency. Generated Dockerfiles use jemalloc, and `BACKTRACE` disables server backtrace cleaning.

Use `Rails.event` for structured events:

```ruby
Rails.event.set_context(request_id: request.request_id)
Rails.event.tagged("checkout") do
  Rails.event.notify("order.paid", order_id: order.id)
end
```

Subscribers implement `emit(event)` and control serialization and output.

For Kamal 2 in-place migration, first deploy successfully with Kamal 1.9.x. Then convert secrets to `.kamal/secrets`, validate every destination with `kamal config`, and account for `kamal-proxy`, the `kamal` Docker network, and the default application port changing from 3000 to 80.
