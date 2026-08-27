# Active Record and Databases

## Transaction boundaries

### Transaction callbacks

Since `7.2`, `ActiveRecord::Base.transaction` yields an
`ActiveRecord::Transaction`. Register commit and rollback callbacks on that
object; `current_transaction` exposes it when the block argument is not
available.

```ruby
Article.transaction do |transaction|
  article.update!(published: true)
  transaction.after_commit do
    PublishNotificationMailer.with(article: article).deliver_later
  end
end
```

Use `ActiveRecord.after_all_transactions_commit` for work that may be invoked
inside or outside a transaction and must run only after all open transactions
have committed.

### Block exits do not roll back

Exiting a transaction block with `return`, `break`, or `throw` no longer
triggers the deprecated implicit rollback behavior. Do not use control-flow
exits as rollback signals.

### Isolation inspection and scoping

In `8.1`, `connection.current_transaction.isolation` reports an explicitly
chosen isolation level and inherits it through nested transactions.
`ActiveRecord.with_transaction_isolation_level` applies an isolation level to
explicit and implicit transactions opened by every pool used in its block.

```ruby
ActiveRecord.with_transaction_isolation_level(:read_committed) do
  User.transaction do
    User.connection.current_transaction.isolation # => :read_committed
  end
end
```

## Upgrade-sensitive APIs

### Removed call forms

Active Record no longer permits:

- `alias_attribute` targeting a nonexistent attribute;
- referencing a singular association by its plural name;
- `read_attribute(:id)` as an alias for a custom primary-key attribute;
- positional coder or class arguments to `serialize`;
- `deferrable: true` on `add_foreign_key`;
- the `rewhere` option to `Relation#merge`;
- keyword-style `enum` definitions;
- unregistered database adapters; or
- `ConnectionPool#connection`.

Also remove the database-name argument to `cache_dump_filename`,
`ENV["SCHEMA_CACHE"]`, `warn_on_records_fetched_greater_than`, and
`sqlite3_deprecated_warning`.

`ActiveRecord::Base.establish_connection` no longer makes
`connection.active?` true. Call `ActiveRecord::Base.connection.verify!` for
immediate verification. Removed connection cleanup calls include
`ActiveRecord::Base.clear_*_connections!` and `flush_idle_connections!`.
Pool list, status, and cleanup calls no longer silently target the current role
when `role` is omitted, so pass the role deliberately.

### Finder-order and association checks

The `8.1` framework default can raise
`ActiveRecord::MissingRequiredOrderError` when `first` or `last` has neither a
relation order nor a model order:

```ruby
config.active_record.raise_on_missing_required_finder_order_columns = true
self.implicit_order_column = [:created_at, nil]
```

The trailing `nil` disables the automatic primary-key tie-breaker.

Polymorphic `belongs_to` declarations may no longer specify the ineffective
`class_name:` option. Bulk inserts on associations containing unpersisted
members are deprecated. So are `update_all` relations that use `WITH`,
`WITH RECURSIVE`, or `DISTINCT`.

### Deprecated associations

The `8.1-guide` adds `deprecated: true` to association definitions. Direct
reads and writes, preloading, nested attributes, and other indirect use are
reported. Reporting modes are `:warn`, `:raise`, and `:notify`; the default
warns without backtraces but always includes the usage location.

```ruby
has_many :posts, deprecated: true
```

## Database configuration

### Adapter floors and pool controls

MySQL 5.5 is no longer supported; use MySQL 5.6.4 or newer. Rails `8.1`
requires SQLite 3.23.0 or newer, and Rails 8.1.3 raises the PostgreSQL minimum
to 9.5.

Use `max_connections` as the pool-size setting. `min_connections`, `keepalive`,
and `max_age` add pool controls without changing the existing defaults.

For SQLite, replace the deprecated `retries` adapter option with `timeout`.
The `unsigned_float` and `unsigned_decimal` MySQL column shortcuts are
deprecated; express the requirement with check constraints.

### Alternative command-line clients

Map adapters to the database CLI Rails should invoke:

```ruby
config.active_record.database_cli = { postgresql: "pgcli" }
```

## Database preparation and schemas

### Fresh and multiple databases

In `8.0`, `db:migrate` on a fresh database loads the schema before applying
pending migrations. Use `db:migrate:reset` to drop the database and replay all
migrations. The command supports multiple databases in `8.1`.

`db:prepare` seeds only the primary database by default. Override that per
database:

```yaml
primary:
  seeds: true
analytics:
  seeds: false
```

Set `schema_format` independently for each database:

```yaml
primary:
  schema_format: ruby
```

`schema.rb` now sorts table columns alphabetically instead of preserving
creation order.

### Migration and PostgreSQL schema helpers

Migration support includes:

- `drop_table` with multiple table names;
- PostgreSQL `add_enum_value ... if_not_exists:`;
- `rename_enum` with separate old and new names;
- `NULLS NOT DISTINCT` on unique constraints as well as unique indexes;
- reversible `create_schema` and `drop_schema`; and
- schema-qualified names for `disable_extension`.

```ruby
ActiveRecord::Base.lease_connection.drop_table(:users, :posts)
add_enum_value :article_status, "archived", if_not_exists: true
```

PostgreSQL schema dumps preserve schema-qualified extensions, table
inheritance, and native partition definitions.

### PostgreSQL generated columns

On PostgreSQL 18 and newer, generated columns are virtual by default. Request
persistence explicitly:

```ruby
create_table :users do |t|
  t.string :name
  t.virtual :lower_name, type: :string, as: "LOWER(name)"
  t.virtual :name_length, type: :integer,
    as: "LENGTH(name)", stored: true
end
```

### Adapter-specific controls

For MySQL 8 and MariaDB 10.6, indexes can be created enabled or disabled and
later toggled with index helpers:

```ruby
add_index :users, :email, enabled: false
enable_index :users, :email
```

With sqlite3 2.4 or newer, SQLite extensions in `database.yml` can be module
names, filesystem paths, or paths produced by ERB:

```yaml
development:
  adapter: sqlite3
  extensions:
    - SQLean::UUID
    - .sqlpkg/nalgeon/crypto/crypto.so
```

## SQLite behavior

### Virtual tables and busy transactions

`create_virtual_table` creates SQLite virtual tables, including full-text
search tables, without breaking `schema.rb`. Transactions use `IMMEDIATE` mode
when possible, and `SQLite3::BusyException` is translated into
`ActiveRecord::StatementTimeout`.

Rails 8.0.4 fixes table alteration so temporary table recreation cannot fire
`ON DELETE CASCADE` and silently remove rows from referencing child tables.

## Queries and bulk writes

### Qualified plucks and CTE bindings

The `8.0` query API lets `pluck` accept symbol- or string-keyed hashes for
qualified selections, avoiding raw SQL strings for joined columns. Common
table expressions also accept bound SQL literals.

```ruby
Post.joins(:comments).pluck(:id, comments: :id)
Post.joins(:comments).pluck("id", "comments" => "id")
```

### Batch cursors and ordering

Batch iteration accepts custom or compound cursor columns:

```ruby
Product.in_batches(cursor: [:shop_id, :id]) do |relation|
  # process relation
end
```

Use `filter: false` with `in_order_of` to prioritize listed values while
retaining rows whose values are not listed:

```ruby
Conversation.in_order_of(:status, %w[open pending], filter: false)
```

### Joined updates and bulk inserts

PostgreSQL and SQLite can reference joined tables in `update_all` assignments
when the relation has no `LIMIT`, `ORDER`, or `GROUP BY`:

```ruby
Comment.joins(:post).update_all("title = posts.title")
```

Nil primary keys in `insert_all` and `upsert_all` now use the adapter's insert
default. Relation-scoped bulk inserts reset the relation afterward so already
loaded data cannot remain stale.

### Low-level write results and constraint errors

`update_column` and `update_columns` accept `touch: true`.
`ActiveRecord::Result#affected_rows` and the `sql.active_record` payload expose
affected-row counts.

```ruby
user.update_columns(last_ip: request.remote_ip, touch: true)
result.affected_rows
```

Check-constraint failures raise `ActiveRecord::CheckViolation`; PostgreSQL
exclusion-constraint failures raise `ActiveRecord::ExclusionViolation` rather
than only `StatementInvalid`.

## Models, attributes, and sharding

### Column allowlists and strict loading

`ActiveRecord::Base.only_columns` is the inverse of `ignored_columns`: it
exposes only named database columns, which helps with shared schemas and staged
column changes.

```ruby
class LegacyUser < ApplicationRecord
  self.only_columns = %w[id name email]
end
```

Global and per-model `strict_loading_mode` defaults to `:all`. Set it to
`:n_plus_one_only` when only lazy loads that would create N+1 queries should be
rejected.

### Point casts

`ActiveRecord::Point` accepts a hash with numeric `x` and `y` values and either
symbol or string keys, in addition to existing string and array inputs:

```ruby
PostgresqlPoint.new(z: { x: "12.34", y: -43.21 })
```

### Shard introspection and selection

Models expose `shard_keys` and `sharded?`.
`connected_to_all_shards` runs a block once per configured shard and returns
the results:

```ruby
ShardedModel.shard_keys
ShardedModel.sharded?
ShardedBase.connected_to_all_shards { ShardedModel.current_shard }
```

Shard keys may be integers. Limit shard-selector middleware to an abstract
connection class with `class_name` rather than always switching from
`ActiveRecord::Base`:

```ruby
ActiveRecord::Base.connects_to(shards: {
  1 => { writing: :primary_shard_one, reading: :primary_shard_one }
})
config.active_record.shard_selector = { class_name: "AnimalsRecord" }
```

### Serialization and encryption

Encrypted attributes accept a compressor that implements `deflate` and
`inflate`, or can disable compression per attribute:

```ruby
encrypts :name, compressor: ZstdCompressor
encrypts :token, compress: false
```

Serialized attributes can compare deserialized values with `comparable: true`.
`ActiveRecord::Coder::JSON` accepts JSON options, and an encrypted attribute
can allow unencrypted reads independently of the global setting:

```ruby
serialize :config, type: Hash, coder: JSON, comparable: true
serialize :metadata,
  coder: ActiveRecord::Coder::JSON.new(symbolize_names: true)
encrypts :email, support_unencrypted_data: true
```

### Signed-ID verifier migration

Signed IDs can use
`Rails.application.message_verifiers["active_record/signed_id"]`.
`signed_id_verifier_secret` is deprecated; use that registry or a model's
`signed_id_verifier`.

Set `config.active_record.use_legacy_signed_id_verifier = :verify` to generate
with the registry while continuing to verify legacy tokens. The default
`:generate_and_verify` keeps legacy generation and verification.

## Errors, events, and tests

### Structured connection errors

An undefined connection raises `ActiveRecord::ConnectionNotDefined`. Its
`connection_name`, `shard`, and `role` readers describe the failed request.

### Notifications and retries

The structured event reporter receives `active_record.strict_loading_violation`
and `active_record.sql`. `sql.active_record` notifications include
`allow_retry` and `affected_rows`. Attributes named in `filter_attributes` are
also covered by `filter_parameters`. Idempotent association and `exists?`
reads can be retried automatically after connection errors.

### Transactional and parallel tests

Transactional fixtures no longer disable asynchronous queries. Async work uses
the connection pinned by the fixture transaction, matching production behavior
more closely.

Parallel test database setup includes replicas and uses `_N`, not `-N`, for
worker suffixes. A test class can keep transactional tests generally enabled
while opting selected databases out:

```ruby
class SharedDatabaseTest < ActiveSupport::TestCase
  self.use_transactional_tests = true
  skip_transactional_tests_for_database :shared
end
```
