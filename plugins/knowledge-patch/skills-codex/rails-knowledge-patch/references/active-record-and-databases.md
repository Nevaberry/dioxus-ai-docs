# Active Record and Databases

## Transaction control and callbacks

Rails 7.2 (`7.2`) removes the old behavior in which leaving a transaction block through `return`, `break`, or `throw` caused an implicit rollback. Do not use those exits as rollback signals.

`ActiveRecord::Base.transaction` yields an `ActiveRecord::Transaction`. Register `after_commit` or `after_rollback` work on that object, or obtain it through `current_transaction`:

```ruby
Article.transaction do |transaction|
  article.update!(published: true)
  transaction.after_commit do
    PublishNotificationMailer.with(article: article).deliver_later
  end
end
```

Use `ActiveRecord.after_all_transactions_commit` when code may run inside or outside a transaction and must wait until all open transactions commit.

Transactional fixtures no longer disable asynchronous queries (`8.0`). Async work uses the connection pinned by the fixture transaction, making tests closer to production behavior.

## Isolation levels

In Rails 8.1 (`8.1`), `connection.current_transaction.isolation` reports an explicitly selected isolation level and nested transactions inherit it. `ActiveRecord.with_transaction_isolation_level` applies a level to explicit and implicit transactions opened by every pool used inside its block:

```ruby
ActiveRecord.with_transaction_isolation_level(:read_committed) do
  User.transaction do
    User.connection.current_transaction.isolation # => :read_committed
  end
end
```

## Removed and stricter call forms

Rails 7.2 (`7.2`) enforces these changes:

- `alias_attribute` cannot target a nonexistent attribute.
- A singular association cannot be addressed by its plural name.
- `read_attribute(:id)` no longer substitutes a custom primary-key attribute.
- `serialize` no longer accepts positional coder or class arguments; use `coder:` and `type:`.
- `add_foreign_key` no longer accepts `deferrable: true`.
- `Relation#merge` no longer accepts the `rewhere` option.

Rails 8.0 (`8.0`) adds these removals:

- Database adapters must be registered.
- Define `enum` with a positional name and mapping, not the removed keyword-style form.
- Remove `ConnectionPool#connection`.
- Do not pass a database name to `cache_dump_filename`.
- Stop using `ENV["SCHEMA_CACHE"]`, `warn_on_records_fetched_greater_than`, and `sqlite3_deprecated_warning`.

## Connections, pools, and diagnostics

`ActiveRecord::Base.establish_connection` no longer makes `connection.active?` immediately true (`7.2`). Call `ActiveRecord::Base.connection.verify!` when eager verification is required.

The old `ActiveRecord::Base.clear_*_connections!` and `flush_idle_connections!` methods are removed. Connection-pool list, status, and cleanup operations no longer silently use the current role when `role` is omitted; pass the intended role explicitly.

Rails 8.1 names the pool maximum `max_connections` and adds `min_connections`, `keepalive`, and `max_age`; defaults are unchanged. Requests for an undefined connection raise `ActiveRecord::ConnectionNotDefined`, whose `connection_name`, `shard`, and `role` accessors identify the failed request.

Map adapters to alternate command-line clients with `database_cli` (`8.0`):

```ruby
config.active_record.database_cli = { postgresql: "pgcli" }
```

## Adapter requirements

- Rails 8.0 drops MySQL 5.5; use MySQL 5.6.4 or newer. Replace deprecated `unsigned_float` and `unsigned_decimal` shortcuts with check constraints.
- Rails 8.1 requires SQLite 3.23.0 or newer.
- Rails 8.1.3 requires PostgreSQL 9.5 or newer.
- For SQLite, replace the deprecated adapter `retries` option with `timeout`.

## SQLite behavior and extensions

SQLite transactions use `IMMEDIATE` mode when possible, and `SQLite3::BusyException` is translated to `ActiveRecord::StatementTimeout` (`8.0`). `create_virtual_table` supports virtual tables such as full-text search without breaking `schema.rb`.

Rails 8.0.4 prevents a table alteration's internal SQLite table recreation from firing `ON DELETE CASCADE` and silently deleting rows in referencing child tables.

With sqlite3 2.4 or newer, Rails 8.1 can load SQLite extensions from module names, filesystem paths, or ERB-derived paths in `database.yml`:

```yaml
development:
  adapter: sqlite3
  extensions:
    - SQLean::UUID
    - .sqlpkg/nalgeon/crypto/crypto.so
```

## PostgreSQL and MySQL schema controls

On PostgreSQL 18 and newer, generated columns are virtual rather than stored by default. Pass `stored: true` when persistence is required:

```ruby
create_table :users do |t|
  t.string :name
  t.virtual :lower_name, type: :string, as: "LOWER(name)"
  t.virtual :name_length, type: :integer, as: "LENGTH(name)", stored: true
end
```

MySQL 8 and MariaDB 10.6 indexes accept `enabled:` and can be changed through the index helpers:

```ruby
add_index :users, :email, enabled: false
enable_index :users, :email
```

Check-constraint failures raise `ActiveRecord::CheckViolation`; PostgreSQL exclusion-constraint failures raise `ActiveRecord::ExclusionViolation`, rather than both appearing only as `StatementInvalid` (`8.1`).

## Database creation, preparation, and schemas

On a fresh database, Rails 8.0 (`8.0`) makes `db:migrate` load the schema before pending migrations. Use `db:migrate:reset` to drop the database and replay every migration; Rails 8.1 extends that reset task to multiple databases.

`db:prepare` seeds only the primary database by default. Override this per database:

```yaml
primary:
  seeds: true
analytics:
  seeds: false
```

Each database may also choose its own `schema_format`:

```yaml
primary:
  schema_format: ruby
```

Rails 8.1 sorts `schema.rb` table columns alphabetically instead of by creation order.

## Migration and schema helpers

Rails 8.0 adds or expands these helpers:

- `drop_table` accepts multiple table names.
- PostgreSQL `add_enum_value` accepts `if_not_exists:`.
- `rename_enum` accepts separate old and new names.
- `NULLS NOT DISTINCT` is supported for unique constraints as well as unique indexes.
- `create_schema` and `drop_schema` are reversible.
- PostgreSQL schema dumps preserve schema-qualified extensions, table inheritance, and native partition definitions.
- `disable_extension` accepts a schema-qualified name.

```ruby
ActiveRecord::Base.lease_connection.drop_table(:users, :posts)
add_enum_value :article_status, "archived", if_not_exists: true
```

## Query construction and ordering

`pluck` accepts symbol- or string-keyed hashes for qualified selections, avoiding raw SQL strings for joined columns. Common table expressions accept bound SQL literals (`8.0`).

```ruby
Post.joins(:comments).pluck(:id, comments: :id)
Post.joins(:comments).pluck("id", "comments" => "id")
```

Batch iteration accepts custom or compound cursor columns:

```ruby
Product.in_batches(cursor: [:shop_id, :id]) do |relation|
  # process relation
end
```

Pass `filter: false` to `in_order_of` to prioritize listed values without excluding unlisted rows:

```ruby
Conversation.in_order_of(:status, %w[open pending], filter: false)
```

The Rails 8.1 framework default can raise `ActiveRecord::MissingRequiredOrderError` when `first` or `last` has neither relation order nor model order:

```ruby
config.active_record.raise_on_missing_required_finder_order_columns = true
self.implicit_order_column = [:created_at, nil]
```

A trailing `nil` suppresses automatic primary-key tie-breaking.

## Bulk writes and write results

PostgreSQL and SQLite may reference joined tables in `update_all` assignments when the relation has no `LIMIT`, `ORDER`, or `GROUP BY` (`8.1`):

```ruby
Comment.joins(:post).update_all("title = posts.title")
```

Nil primary keys in `insert_all` and `upsert_all` use the adapter's insert default. Relation-scoped bulk inserts reset the relation afterward so it does not retain stale loaded data.

Bulk inserts on associations with unpersisted members are deprecated. So are `update_all` relations using `WITH`, `WITH RECURSIVE`, or `DISTINCT`.

`update_column` and `update_columns` accept `touch: true`. `ActiveRecord::Result#affected_rows` and the `sql.active_record` payload expose affected-row counts:

```ruby
user.update_columns(last_ip: request.remote_ip, touch: true)
result.affected_rows
```

## Type casting, serialization, and encryption

`ActiveRecord::Point` accepts hashes with numeric `x` and `y` values, using symbol or string keys, in addition to strings and arrays (`8.0`):

```ruby
PostgresqlPoint.new(z: { x: "12.34", y: -43.21 })
```

Encrypted attributes accept a compressor with `deflate` and `inflate`, or can disable compression per attribute:

```ruby
encrypts :name, compressor: ZstdCompressor
encrypts :token, compress: false
```

Rails 8.1 serialized attributes can compare deserialized values with `comparable: true`, and `ActiveRecord::Coder::JSON` accepts JSON options. An encrypted attribute can independently read unencrypted data even when the global setting is off:

```ruby
serialize :config, type: Hash, coder: JSON, comparable: true
serialize :metadata, coder: ActiveRecord::Coder::JSON.new(symbolize_names: true)
encrypts :email, support_unencrypted_data: true
```

## Column and association migrations

`ActiveRecord::Base.only_columns` is the inverse of `ignored_columns`: only the explicit list is exposed. Use it for shared or legacy schemas and staged column changes.

```ruby
class LegacyUser < ApplicationRecord
  self.only_columns = %w[id name email]
end
```

Associations accept `deprecated: true` (`8.1-guide`). Direct access, assignment, preloading, nested attributes, and other indirect use are reported. Reporting supports `:warn`, `:raise`, and `:notify`; the default warns without backtraces and always includes the usage location.

```ruby
has_many :posts, deprecated: true
```

Polymorphic `belongs_to` declarations may no longer specify the ineffective `class_name:` option (`8.1`).

## Strict loading, events, and retries

Global or per-model `strict_loading_mode` defaults to `:all`; set `:n_plus_one_only` when only lazy loads that create N+1 queries should be rejected (`8.0`).

The structured event reporter receives `active_record.strict_loading_violation` and `active_record.sql` (`8.1`). `sql.active_record` notifications include `allow_retry` and `affected_rows`. Attributes in `filter_attributes` are also filtered through `filter_parameters`. Idempotent association and `exists?` reads can retry automatically after connection errors.

## Shards and connection switching

Models expose `shard_keys` and `sharded?`; `connected_to_all_shards` runs a block once for each configured shard and returns the collected results (`8.0`):

```ruby
ShardedModel.shard_keys
ShardedModel.sharded?
ShardedBase.connected_to_all_shards { ShardedModel.current_shard }
```

Rails 8.1 allows integer shard keys and lets `config.active_record.shard_selector[:class_name]` restrict middleware switching to a chosen abstract connection class:

```ruby
ActiveRecord::Base.connects_to(shards: {
  1 => { writing: :primary_shard_one, reading: :primary_shard_one }
})
config.active_record.shard_selector = { class_name: "AnimalsRecord" }
```

## Signed-ID verifier migration

Signed IDs can use `Rails.application.message_verifiers["active_record/signed_id"]`. `signed_id_verifier_secret` is deprecated in favor of that registry or a model's `signed_id_verifier`.

Set `config.active_record.use_legacy_signed_id_verifier = :verify` to generate with the registry while accepting legacy tokens. The default `:generate_and_verify` retains legacy generation and verification.

## Multi-database parallel and transactional tests

Rails 8.1 parallel test setup includes replicas and changes worker database suffixes from `-N` to `_N`. A test class may disable transactional tests for selected databases while retaining them elsewhere:

```ruby
class SharedDatabaseTest < ActiveSupport::TestCase
  self.use_transactional_tests = true
  skip_transactional_tests_for_database :shared
end
```
