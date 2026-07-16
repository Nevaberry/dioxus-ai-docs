# Upgrading and Compatibility

Topic details draw from batches `7.2`, `8.0`, and `8.1`.

## Contents

- [Controllers, routes, and views](#controllers-routes-and-views)
- [Active Support and framework APIs](#active-support-and-framework-apis)
- [Active Record compatibility](#active-record-compatibility)
- [Cache stores](#cache-stores)
- [Active Job compatibility](#active-job-compatibility)
- [Database adapters](#database-adapters)
- [Upgrade checklist](#upgrade-checklist)

## Controllers, routes, and views

### Parameters and exception rendering

`ActionController::Parameters` can no longer be compared with a `Hash` (`7.2`). The compatibility setting `config.action_controller.allow_deprecated_parameters_hash_equality` is deprecated.

`config.action_dispatch.show_exceptions` no longer accepts boolean `true` or `false` (`7.2`). Migrate to a supported symbolic value rather than carrying the boolean through a configuration-default update.

### Forms, routes, and tags

`form_with(model: nil)` is removed (`8.0`).

Declaring multiple paths in one route is deprecated (`8.0`). Split the declaration into explicit routes.

Passing content to a void element through a tag builder such as `tag.br` is deprecated (`7.2`). Emit a void tag without content.

### Query parsing configuration

Request parsing no longer strips a leading bracket from a root parameter name and no longer treats semicolons as query-pair separators (`8.1`). The old `config.action_dispatch.ignore_leading_brackets` setting is deprecated. See the web reference for concrete parse results.

## Active Support and framework APIs

Remove these APIs and call forms (`8.0` unless otherwise noted):

- Console extension through `Rails::ConsoleMethods`.
- `ActiveSupport::ProxyObject`.
- `@`-prefixed `attr_internal_naming_format`.
- Array arguments to `ActiveSupport::Deprecation#warn`.
- `bin/rake stats` and `STATS_DIRECTORIES` (`8.1`).

Plan replacements for these deprecations:

- `Benchmark.ms` (`8.0`).
- Addition or `since` between `Time` and `ActiveSupport::TimeWithZone` (`8.0`).
- `String#mb_chars` and `ActiveSupport::Multibyte::Chars` (`8.1`).
- `ActiveSupport::Configurable` (`8.1`).
- `config.active_support.to_time_preserves_timezone` (`8.1`).

`to_time` now always preserves the receiver's timezone (`8.1`). Remove branches that assume configuration can restore the earlier conversion behavior.

Rails sets global `Regexp.timeout` to one second by default (`8.0`). Confirm that deliberately expensive expressions still have an acceptable timeout strategy.

## Active Record compatibility

### Removed model and relation forms

The following are removed in `7.2`:

- `alias_attribute` with a nonexistent target.
- Referring to a singular association by its plural name.
- `read_attribute(:id)` substitution of a custom primary-key attribute.
- Positional coder/class arguments to `serialize`.
- `deferrable: true` for `add_foreign_key`.
- The `rewhere` option to `Relation#merge`.
- Implicit transaction rollback caused by leaving the block with `return`, `break`, or `throw`.

The following are removed in `8.0`:

- Unregistered database adapters.
- Keyword-style `enum` definitions.
- `ConnectionPool#connection`.
- The database-name argument to `cache_dump_filename`.
- `ENV["SCHEMA_CACHE"]`.
- `warn_on_records_fetched_greater_than`.
- `sqlite3_deprecated_warning`.

Also stop relying on `establish_connection` to make `connection.active?` immediately true. Verify the connection explicitly. Removed connection cleanup methods and role-selection behavior are detailed in the Active Record reference.

### Finder, association, and bulk-write checks

The `8.1` framework default can raise `ActiveRecord::MissingRequiredOrderError` when `first` or `last` has no relation or model order. Define deterministic ordering before enabling the default.

Remove `class_name:` from polymorphic `belongs_to` declarations. It is ineffective and no longer accepted (`8.1`).

Bulk inserts on associations with unpersisted members are deprecated. So are `update_all` relations containing `WITH`, `WITH RECURSIVE`, or `DISTINCT` (`8.1`).

### Signed IDs

`signed_id_verifier_secret` is deprecated (`8.1`). Migrate to `Rails.application.message_verifiers["active_record/signed_id"]` or a model-specific `signed_id_verifier`. Use `config.active_record.use_legacy_signed_id_verifier = :verify` when new tokens should use the registry while old tokens remain verifiable.

## Cache stores

Cache stores no longer accept `:pool_size` or `:pool_timeout` (`7.2`). Cache format version 6.1 is unsupported. `MemCacheStore` no longer accepts an already-created `Dalli::Client`.

## Active Job compatibility

Remove these `7.2` forms:

- Primitive `BigDecimal` serialization.
- Numeric `scheduled_at` values.
- `retry_on wait: :exponentially_longer`.

`config.active_job.use_big_decimal_serializer` is deprecated.

The `enqueue_after_transaction_commit` surface changed in stages. It was deprecated in `8.0`; in `8.1`, the symbolic `:never`, `:always`, and `:default` values and application-wide `config.active_job.enqueue_after_transaction_commit` are removed, while supported job-level boolean configuration remains. `perform_all_later` honors the boolean.

Custom serializers must make `klass` public (`8.1`).

The internal `SuckerPunch` adapter is deprecated (`8.0`); use the adapter from the `sucker_punch` gem. The built-in Sidekiq adapter is deprecated (`8.1`); use Sidekiq's adapter.

## Database adapters

- MySQL 5.5 support is removed; require at least MySQL 5.6.4 (`8.0`).
- `unsigned_float` and `unsigned_decimal` shortcuts are deprecated; use check constraints (`8.0`).
- SQLite adapter `retries` is deprecated; use `timeout` (`8.0`).
- Ensure SQLite is at least 3.23.0 (`8.1`).
- Ensure PostgreSQL is at least 9.5 when using Rails `8.1.3`.

The Active Storage Azure backend is deprecated (`8.0`). Plan a service migration before its removal.

## Upgrade checklist

1. Search the application and dependencies for every removed constant, configuration key, and call form above.
2. Convert deprecated forms before changing framework defaults so failures remain attributable.
3. Verify database server and adapter requirements, then regenerate and inspect schema output.
4. Exercise transactions that use nonlocal control flow and jobs enqueued inside transactions.
5. Load representative query strings containing leading brackets or semicolons.
6. Recalculate Puma and database-pool concurrency if generated defaults were used.
7. Run deprecation reporting across application boot, tests, background jobs, and deployment tasks.
