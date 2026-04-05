# Database Configuration

## Connection pool configuration (8.1)

New options: `keepalive`, `max_age`, `min_connections`. `pool` renamed to `max_connections` (old name still works):

```yaml
production:
  adapter: postgresql
  max_connections: 10
  min_connections: 2
  keepalive: 300
  max_age: 600
```

## ActiveRecord.with_transaction_isolation_level (8.1)

Set transaction isolation for all pools within a block:

```ruby
ActiveRecord.with_transaction_isolation_level(:read_committed) do
  Tag.create!  # uses read_committed isolation
end
```

Also: `connection.current_transaction.isolation` returns the current level.

## SQLite extensions in database.yml (8.1)

```yaml
development:
  adapter: sqlite3
  extensions:
    - SQLean::UUID # module responding to .to_path
    - .sqlpkg/nalgeon/crypto/crypto.so # filesystem path
```

Requires `sqlite3` gem >= v2.4.0.

## Invisible indexes — MySQL 8.0+, MariaDB 10.6+ (8.1)

```ruby
add_index :users, :email, enabled: false  # invisible to query optimizer
enable_index :users, :email               # make visible again
```
