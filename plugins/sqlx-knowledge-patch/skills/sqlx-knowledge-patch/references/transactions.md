# Transactions

## `begin_with` — Database-Specific Transaction Options (0.8.4+)

Start transactions with custom options (isolation level, read-only, etc.) using `begin_with`:

```rust
use sqlx::postgres::{PgIsolationLevel, PgTransactionOptions};

let tx = conn
    .begin_with(
        PgTransactionOptions::new()
            .isolation_level(PgIsolationLevel::Serializable)
            .read_only(true),
    )
    .await?;
```

Each database has its own options type:

### `PgTransactionOptions`

```rust
PgTransactionOptions::new()
    .isolation_level(PgIsolationLevel::Serializable) // or ReadCommitted, RepeatableRead
    .read_only(true)
```

### `MySqlTransactionOptions`

```rust
MySqlTransactionOptions::new()
    .isolation_level(MySqlIsolationLevel::Serializable)
    .read_only(true)
```

### `SqliteTransactionOptions`

```rust
SqliteTransactionOptions::new()
// SQLite-specific transaction options
```

## `Connection::is_in_transaction` (0.8.4+)

Check if a connection is currently inside a transaction:

```rust
assert!(!conn.is_in_transaction());
let tx = conn.begin().await?;
assert!(tx.is_in_transaction());
```

## Transaction Type Aliases (0.8.3+)

Convenience aliases to avoid verbose generic syntax:

| Alias | Expands to |
|---|---|
| `PgTransaction<'c>` | `Transaction<'c, Postgres>` |
| `MySqlTransaction<'c>` | `Transaction<'c, MySql>` |
| `SqliteTransaction<'c>` | `Transaction<'c, Sqlite>` |
