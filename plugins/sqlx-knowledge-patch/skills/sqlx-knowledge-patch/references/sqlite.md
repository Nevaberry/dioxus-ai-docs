# SQLite

## Commit and Rollback Hooks (0.8.3+)

Register callbacks on SQLite connections for commit/rollback events:

```rust
use sqlx::sqlite::SqliteConnection;

conn.on_commit(|| { /* called after each commit */ });
conn.on_rollback(|| { /* called after each rollback */ });
```

## Preupdate Hook (0.8.4+)

Register callbacks before row modifications (requires `sqlite-preupdate-hook` feature):

```rust
conn.on_preupdate(|preupdate| {
    // Called before INSERT, UPDATE, or DELETE
});
```

## Feature Flag Changes (0.9)

New **non-default** features for conditional SQLite APIs:

| Feature | Enables | Notes |
|---|---|---|
| `sqlite-deserialize` | `SqliteConnection::serialize()` / `deserialize()` | |
| `sqlite-load-extension` | `SqliteConnectOptions::extension()` | Now `unsafe` |
| `sqlite-unlock-notify` | Internal `sqlite3_unlock_notify()` usage | |
| `sqlite-preupdate-hook` | `conn.on_preupdate()` callback | Added in 0.8.4 |

**Breaking in 0.9:**
- Extension loading is now `unsafe`
- `SqliteValue` is now `!Sync`
- `SqliteValueRef` is `!Send`

## `sqlite-unbundled` Feature (0.8.3+)

Dynamically link to system `libsqlite3.so` instead of bundling SQLite:

```toml
[dependencies]
sqlx = { version = "0.8", features = ["sqlite-unbundled"] }
```

## `no_tx` SQLite Migrations (0.9)

SQLite migrations can opt out of transaction wrapping with `no_tx` support. Useful for migrations that include statements incompatible with transactions (e.g., `VACUUM`, `PRAGMA journal_mode`).

## `AnyQueryResult` for SQLite (0.8.3+)

`AnyQueryResult` now works with SQLite and MySQL backends (previously Postgres-only).
