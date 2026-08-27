---
name: rails-knowledge-patch
description: Ruby on Rails
version: "8.1"
license: MIT
metadata:
  author: Nevaberry
---


# Ruby on Rails Knowledge Patch

Use this skill when changing or upgrading a Rails application. Start with the
quick references below, then load the topic file for the subsystem being
changed; the references hold the detailed behavior, defaults, and edge cases.

## Reference index

| Reference | Topics |
|---|---|
| [Active Job and Solid Queue](references/active-job-and-solid-queue.md) | Transactional enqueueing, continuations, queue setup, workers, concurrency, failures, and recurring work |
| [Active Record and databases](references/active-record-and-databases.md) | Transactions, removed call forms, migrations, queries, adapters, pools, sharding, serialization, and tests |
| [Operations, observability, and deployment](references/operations-observability-and-deployment.md) | Development containers, Puma, backtraces, events, local CI, credentials, Docker, and Kamal |
| [Upgrading and compatibility](references/upgrading-and-compatibility.md) | Removed APIs, changed defaults, request compatibility, browser guards, cache stores, and replacements |
| [Web, assets, and storage](references/web-assets-and-storage.md) | Request parsing, Markdown, live streaming, Propshaft, Turbo refreshes, and Active Storage |

## Upgrade-critical changes

### Do not use transaction block exits as rollback signals

`return`, `break`, and `throw` no longer implicitly roll an Active Record
transaction back. Raise an exception or explicitly arrange the required
rollback behavior instead.

Register post-transaction work on the yielded transaction:

```ruby
Article.transaction do |transaction|
  article.update!(published: true)
  transaction.after_commit { PublishNotificationJob.perform_later(article) }
end
```

Use `ActiveRecord.after_all_transactions_commit` when code can run inside or
outside a transaction and must wait for every open transaction to commit.

### Audit removed Active Record forms

Replace these forms before upgrading:

- Define `enum` with a positional name and mapping, not the removed
  keyword-style definition.
- Pass `coder:` and `type:` to `serialize`; positional coder and class
  arguments are removed.
- Do not point `alias_attribute` at a missing attribute or address a singular
  association by a plural name.
- Do not depend on `read_attribute(:id)` resolving a custom primary key.
- Remove `deferrable: true` from `add_foreign_key` and the `rewhere` option
  from `Relation#merge`.
- Remove `ConnectionPool#connection` and the removed `Base.clear_*_connections!`
  and `flush_idle_connections!` calls.

`establish_connection` no longer makes `connection.active?` immediately true.
Call `ActiveRecord::Base.connection.verify!` when eager verification matters.

### Update controller and framework compatibility

- Do not compare `ActionController::Parameters` with a `Hash`.
- Use a supported symbolic `config.action_dispatch.show_exceptions` value,
  not a boolean.
- Do not pass content to void-element builders such as `tag.br`.
- Remove `form_with(model: nil)` and declare one route path at a time.
- Treat a leading `[` in a root query key literally and do not split query
  pairs on semicolons.
- Remove `Rails::ConsoleMethods`, `ActiveSupport::ProxyObject`, `bin/rake stats`,
  `STATS_DIRECTORIES`, `@`-prefixed `attr_internal_naming_format`, and array
  arguments to `ActiveSupport::Deprecation#warn`.

Plan replacements for deprecated `Benchmark.ms`, `String#mb_chars`,
`ActiveSupport::Multibyte::Chars`, `ActiveSupport::Configurable`, the Azure
Active Storage service, and arithmetic between `Time` and
`ActiveSupport::TimeWithZone`. `to_time` now preserves the receiver timezone.

### Update Active Job configuration and arguments

Jobs enqueued inside a database transaction wait for commit and are dropped on
rollback when the adapter supports transactional deferral. Current job-level
configuration is boolean:

```ruby
class AuditJob < ApplicationJob
  self.enqueue_after_transaction_commit = true
end
```

Do not use removed symbolic `:never`, `:always`, or `:default` values or the
removed application-wide setting. `perform_all_later` honors the job-level
setting. Also remove primitive `BigDecimal` serialization, numeric
`scheduled_at`, and `retry_on wait: :exponentially_longer`. Use the queue
adapter supplied by Sidekiq or `sucker_punch` instead of the deprecated built-in
adapters.

### Recheck database and pool assumptions

Use `max_connections` for maximum pool size. Optional `min_connections`,
`keepalive`, and `max_age` controls do not otherwise change defaults. Ensure
SQLite is at least 3.23.0 and PostgreSQL is at least 9.5 where the applicable
point release requires it; MySQL must be 5.6.4 or newer.

For SQLite, replace adapter `retries` with `timeout`. Transactions use
`IMMEDIATE` mode where possible and busy exceptions surface as
`ActiveRecord::StatementTimeout`.

The framework default can reject `first` or `last` without a relation or model
order:

```ruby
config.active_record.raise_on_missing_required_finder_order_columns = true
self.implicit_order_column = [:created_at, nil]
```

The trailing `nil` suppresses automatic primary-key tie-breaking.

### Harden Active Storage image processing

Security releases call `Vips.block_untrusted(true)` at boot. With ruby-vips
installed, require libvips 8.13 or newer and ruby-vips 2.2.1 or newer. Affected
untrusted loaders, savers, and delegated output formats now fail rather than
being transformed; review variable content types before deployment.

Active Storage also accepts one byte range per request, with a 100 MB default
cap. Disk keys with dot segments, invalid paths, or paths outside the service
root raise `InvalidKeyError`; prefix deletion treats glob metacharacters
literally.

## Common implementation paths

### Install and size Solid Queue deliberately

The standard production layout uses a separate `queue` database,
`db/queue_schema.rb`, `config/queue.yml`, `config/recurring.yml`, and `bin/jobs`.
Configure, prepare, and supervise the queue database in every additional
environment.

Keep each worker's thread count at or below its queue database pool size minus
two. Workers exhaust queue names in listed order; within a queue, smaller
numeric priorities run first and `0` is the default.

Use async supervisor mode only when process isolation is unnecessary:

```ruby
plugin :solid_queue
solid_queue_mode :async
```

The Puma plugin requires preloading, cannot use phased restarts, and ignores
worker `processes` in async mode.

For `limits_concurrency`, `duration` is semaphore expiry, not a runtime limit.
Defaults are `to: 1`, three minutes, the job class as `group`, and
`on_conflict: :block`; `:discard` rejects a conflicting enqueue.

### Build resumable jobs with continuations

Use `ActiveJob::Continuable` to split long work into durable steps. Save a
cursor after each completed record:

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

### Prepare and migrate databases predictably

On a fresh database, `db:migrate` loads the schema before pending migrations.
Use `db:migrate:reset` to drop and replay all migrations; it supports multiple
databases. `db:prepare` seeds only the primary database by default, but each
database can set `seeds`. Set `schema_format` per database when stores need
different Ruby or SQL dumps.

### Configure Propshaft explicitly

Propshaft precompiles every file under `config.assets.paths`. Exclude
compiler-only inputs by full path, and name files that already contain their
final digest with `-[digest].digested.<extension>`.

Configure an SRI algorithm and opt helpers in individually:

```ruby
config.assets.integrity_hash_algorithm = "sha384"
```

```erb
<%= stylesheet_link_tag "application", integrity: true %>
```

Production helpers omit integrity hashes over plain HTTP. The stylesheet helper
accepts `:all` for all stylesheets and `:app` for those under `app/assets`.

### Use morph refreshes for page-level updates

```html
<meta name="turbo-refresh-method" content="morph">
<meta name="turbo-refresh-scroll" content="preserve">
```

Add `refresh="morph"` to a `src`-backed Turbo Frame to reload and morph it
during a page refresh. A `refresh` stream can override the method and scrolling;
consecutive broadcast refreshes are debounced. In Rails, pair
`broadcasts_refreshes` with `turbo_stream_from`.

### Emit structured events

Use `Rails.event` for structured payloads, tags, and shared context:

```ruby
Rails.event.set_context(request_id: request.request_id)
Rails.event.tagged("checkout") do
  Rails.event.notify("order.paid", order_id: order.id)
end
```

Subscribers implement `emit(event)` and control serialization and output.

### Plan Kamal migration as a staged operation

For an in-place Kamal 2 migration, deploy successfully with Kamal 1.9.x first.
Then move secrets to `.kamal/secrets`, validate every destination with
`kamal config`, and account for `kamal-proxy`, the `kamal` Docker network, and
the default application port changing from 3000 to 80.
