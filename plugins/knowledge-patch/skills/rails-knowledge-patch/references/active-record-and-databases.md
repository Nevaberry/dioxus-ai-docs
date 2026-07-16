# Active Record and Databases

Topic details draw from batches `7.2`, `8.0`, `8.1-guide`, and `8.1`.

## Contents

- [Transactions and connection handling](#transactions-and-connection-handling)
- [Compatibility-sensitive model APIs](#compatibility-sensitive-model-apis)
- [Database preparation, migrations, and schemas](#database-preparation-migrations-and-schemas)
- [Adapter requirements and adapter-specific behavior](#adapter-requirements-and-adapter-specific-behavior)
- [Queries, ordering, and bulk writes](#queries-ordering-and-bulk-writes)
- [Shards and isolation](#shards-and-isolation)
- [Serialization, encryption, and signed IDs](#serialization-encryption-and-signed-ids)
- [Testing, events, and retries](#testing-events-and-retries)

## Transactions and connection handling

### Transaction callbacks

`ActiveRecord::Base.transaction` yields an `ActiveRecord::Transaction` that accepts commit and rollback callbacks (`7.2`):

```ruby
Article.transaction do |transaction|
  article.update!(published: true)
  transaction.after_commit do
    PublishNotificationMailer.with(article: article).deliver_later
  end
end
```

Use `current_transaction` when the transaction object is needed outside the block argument. Use `ActiveRecord.after_all_transactions_commit` when code can run either inside or outside transactions and must wait until all state changes have committed.

Do not use `return`, `break`, or `throw` as an implicit rollback signal. The deprecated rollback-on-block-exit behavior is removed (`7.2`).

### Establishment, verification, and pools

`ActiveRecord::Base.establish_connection` no longer makes `connection.active?` immediately true (`7.2`). Call this when eager verification matters:

```ruby
ActiveRecord::Base.connection.verify!
```

The deprecated `ActiveRecord::Base.clear_*_connections!` and `flush_idle_connections!` methods are removed. Pool list, status, and cleanup operations no longer default to the current role when `role` is omitted; pass the intended role explicitly.

`ConnectionPool#connection` is removed (`8.0`).

An undefined connection raises `ActiveRecord::ConnectionNotDefined`; inspect `connection_name`, `shard`, and `role` for structured diagnostics (`8.0`).

## Compatibility-sensitive model APIs

Remove or replace these call forms:

- `alias_attribute` targeting an attribute that does not exist (`7.2`).
- Referring to a singular association by its plural name (`7.2`).
- Expecting `read_attribute(:id)` to substitute the custom primary-key attribute (`7.2`).
- Positional coder or class arguments to `serialize`; use keywords (`7.2`).
- `deferrable: true` on `add_foreign_key` (`7.2`).
- The `rewhere` option to `Relation#merge` (`7.2`).
- Unregistered database adapters and keyword-style `enum` definitions (`8.0`).
- The database-name argument to `cache_dump_filename` and `ENV["SCHEMA_CACHE"]` (`8.0`).
- The removed `warn_on_records_fetched_greater_than` and `sqlite3_deprecated_warning` settings (`8.0`).

### Deprecated associations

Mark an association as deprecated to locate callers during a staged migration (`8.1-guide`):

```ruby
has_many :posts, deprecated: true
```

Direct reads, assignment, preloading, nested attributes, and other indirect use are reported. Configure reporting as `:warn`, `:raise`, or `:notify`. The default warns without backtraces but always includes the usage location.

Polymorphic `belongs_to` declarations may no longer include the ineffective `class_name:` option (`8.1`).

## Database preparation, migrations, and schemas

### Preparing databases

On a fresh database, `db:migrate` loads the schema before applying pending migrations (`8.0`). Use `db:migrate:reset` when the intent is to drop the database and replay every migration; in `8.1` it supports multiple databases.

`db:prepare` seeds only the primary database by default. Configure each database independently:

```yaml
primary:
  seeds: true
analytics:
  seeds: false
```

Multi-database configurations can also choose `schema_format` independently:

```yaml
primary:
  schema_format: ruby
```

### Migration helpers and PostgreSQL dumps

The following schema operations are available in `8.0`:

```ruby
ActiveRecord::Base.lease_connection.drop_table(:users, :posts)
add_enum_value :article_status, "archived", if_not_exists: true
```

- `drop_table` accepts multiple table names.
- PostgreSQL `add_enum_value` accepts `if_not_exists:`.
- `rename_enum` accepts separate old and new names.
- `NULLS NOT DISTINCT` applies to unique constraints as well as unique indexes.
- `create_schema` and `drop_schema` are reversible.
- PostgreSQL schema dumps preserve schema-qualified extensions, table inheritance, and native partition definitions.
- `disable_extension` accepts a schema-qualified extension name.

In `8.1`, `schema.rb` sorts table columns alphabetically rather than by creation order. Expect schema-only diffs after regeneration.

## Adapter requirements and adapter-specific behavior

### Requirements and pool controls

- MySQL 5.5 is unsupported; use MySQL 5.6.4 or newer (`8.0`).
- SQLite must be 3.23.0 or newer for `8.1`.
- Rails `8.1.3` raises the PostgreSQL minimum to 9.5.
- MySQL `unsigned_float` and `unsigned_decimal` shortcuts are deprecated; model the rule with check constraints (`8.0`).
- SQLite's `retries` adapter option is deprecated; use `timeout` (`8.0`).

Database pool configuration adds `keepalive`, `max_age`, and `min_connections`; `max_connections` is the new name for the maximum pool-size setting (`8.1`). Defaults do not change.

### SQLite virtual tables, locking, and alteration safety

Create SQLite virtual tables, including full-text-search tables, with `create_virtual_table`; they remain representable in `schema.rb` (`8.0`). SQLite transactions use `IMMEDIATE` mode when possible, and `SQLite3::BusyException` is translated to `ActiveRecord::StatementTimeout`.

Rails `8.0.4` prevents SQLite table recreation during an alteration from firing `ON DELETE CASCADE` and silently deleting rows in referencing child tables.

With sqlite3 `2.4` or newer, load extensions from module names, direct paths, or ERB-derived paths in `database.yml` (`8.1`):

```yaml
development:
  adapter: sqlite3
  extensions:
    - SQLean::UUID
    - .sqlpkg/nalgeon/crypto/crypto.so
```

### PostgreSQL generated columns

On PostgreSQL 18 or newer, generated columns are virtual rather than stored by default (`8.1`). Request persistence explicitly:

```ruby
create_table :users do |t|
  t.string :name
  t.virtual :lower_name, type: :string, as: "LOWER(name)"
  t.virtual :name_length,
    type: :integer,
    as: "LENGTH(name)",
    stored: true
end
```

### MySQL and MariaDB index state

MySQL 8 and MariaDB 10.6 indexes support `enabled:` at creation and dedicated enable/disable helpers (`8.1`):

```ruby
add_index :users, :email, enabled: false
enable_index :users, :email
```

### Database command-line clients

Map an adapter to the client Rails should launch (`8.0`):

```ruby
config.active_record.database_cli = { postgresql: "pgcli" }
```

## Queries, ordering, and bulk writes

### Qualified plucks and CTEs

`pluck` accepts symbol- or string-keyed hashes for qualified joined selections (`8.0`):

```ruby
Post.joins(:comments).pluck(:id, comments: :id)
Post.joins(:comments).pluck("id", "comments" => "id")
```

Common table expressions also accept bound SQL literals.

### Batch cursors and explicit ordering

Use custom or compound batch cursors (`8.0`):

```ruby
Product.in_batches(cursor: [:shop_id, :id]) do |relation|
  # process relation
end
```

Use `filter: false` with `in_order_of` to prioritize listed values without dropping all other values:

```ruby
Conversation.in_order_of(:status, %w[open pending], filter: false)
```

Global or per-model `strict_loading_mode` defaults to `:all`. Set `:n_plus_one_only` when only lazy loads that would produce N+1 queries should fail (`8.0`).

### Column allowlists and finder ordering

`only_columns` is the inverse of `ignored_columns`: only explicitly listed database columns are exposed (`8.1`). This is useful with legacy/shared schemas and staged column changes.

```ruby
class LegacyUser < ApplicationRecord
  self.only_columns = %w[id name email]
end
```

The `8.1` framework default can raise `ActiveRecord::MissingRequiredOrderError` for `first` or `last` when neither the relation nor model supplies an order:

```ruby
config.active_record.raise_on_missing_required_finder_order_columns = true
self.implicit_order_column = [:created_at, nil]
```

A trailing `nil` in compound `implicit_order_column` suppresses automatic primary-key tie-breaking.

### Low-level writes and result metadata

`update_column` and `update_columns` accept `touch: true` (`8.1`):

```ruby
user.update_columns(last_ip: request.remote_ip, touch: true)
```

`ActiveRecord::Result#affected_rows` exposes the affected count, and `sql.active_record` includes the same `affected_rows` value. Check-constraint and PostgreSQL exclusion-constraint failures raise `ActiveRecord::CheckViolation` and `ActiveRecord::ExclusionViolation`, respectively, instead of only `StatementInvalid`.

### Bulk-write behavior

PostgreSQL and SQLite `update_all` assignments may reference joined tables when the relation has no `LIMIT`, `ORDER`, or `GROUP BY` (`8.1`):

```ruby
Comment.joins(:post).update_all("title = posts.title")
```

Nil primary keys in `insert_all` and `upsert_all` use the adapter's insert default. Relation-scoped bulk inserts reset the relation afterward so a previously loaded relation does not retain stale data.

The following uses are deprecated (`8.1`):

- Bulk inserts on associations that contain unpersisted members.
- `update_all` on relations using `WITH`, `WITH RECURSIVE`, or `DISTINCT`.

## Shards and isolation

Models expose `shard_keys` and `sharded?`; `connected_to_all_shards` runs a block for every configured shard and returns all results (`8.0`):

```ruby
ShardedModel.shard_keys
ShardedModel.sharded?
ShardedBase.connected_to_all_shards { ShardedModel.current_shard }
```

Shard keys may be integers (`8.1`):

```ruby
ActiveRecord::Base.connects_to(shards: {
  1 => { writing: :primary_shard_one, reading: :primary_shard_one }
})
```

Limit shard-selector middleware switching to a chosen abstract connection class rather than `ActiveRecord::Base`:

```ruby
config.active_record.shard_selector = { class_name: "AnimalsRecord" }
```

Inspect an explicitly selected isolation level through `connection.current_transaction.isolation`; nested transactions inherit it (`8.1`). Apply one level to explicit and implicit transactions opened by every pool used in a block:

```ruby
ActiveRecord.with_transaction_isolation_level(:read_committed) do
  User.transaction do
    User.connection.current_transaction.isolation # => :read_committed
  end
end
```

## Serialization, encryption, and signed IDs

### Points and encrypted compression

`ActiveRecord::Point` accepts hashes with numeric `x` and `y` values using symbol or string keys, in addition to strings and arrays (`8.0`):

```ruby
PostgresqlPoint.new(z: { x: "12.34", y: -43.21 })
```

Encrypted attributes accept a compressor that implements `deflate` and `inflate`, or can disable compression per attribute:

```ruby
encrypts :name, compressor: ZstdCompressor
encrypts :token, compress: false
```

### Comparable serialization and encryption migration

Compare deserialized values for change tracking with `comparable: true`; `ActiveRecord::Coder::JSON` accepts JSON options (`8.1`):

```ruby
serialize :config, type: Hash, coder: JSON, comparable: true
serialize :metadata,
  coder: ActiveRecord::Coder::JSON.new(symbolize_names: true)
```

An encrypted attribute can independently read unencrypted data even if the global setting is disabled:

```ruby
encrypts :email, support_unencrypted_data: true
```

### Signed-ID verifier migration

Signed IDs can use `Rails.application.message_verifiers["active_record/signed_id"]` (`8.1`). `signed_id_verifier_secret` is deprecated; use the registry or a model's `signed_id_verifier`.

Set `config.active_record.use_legacy_signed_id_verifier = :verify` to generate with the registry while still verifying legacy tokens. The default `:generate_and_verify` continues legacy generation and verification.

## Testing, events, and retries

Transactional fixtures no longer disable asynchronous queries (`8.0`). Async work uses the connection pinned by the fixture transaction, making test behavior closer to production.

Parallel multi-database test setup in `8.1`:

- Includes replicas.
- Uses `_N`, not `-N`, for worker database suffixes.
- Allows a test class to disable transactional tests for selected databases while retaining them for others.

```ruby
class SharedDatabaseTest < ActiveSupport::TestCase
  self.use_transactional_tests = true
  skip_transactional_tests_for_database :shared
end
```

The structured event reporter receives `active_record.strict_loading_violation` and `active_record.sql` (`8.1`). `sql.active_record` notifications include `allow_retry` and `affected_rows`. Attributes listed in `filter_attributes` are also covered by `filter_parameters`.

Idempotent association reads and `exists?` reads can automatically retry after connection errors.
