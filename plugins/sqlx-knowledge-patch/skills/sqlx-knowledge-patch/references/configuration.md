# Configuration & Runtime

## `sqlx.toml` Per-Crate Configuration (0.9)

Enable the `sqlx-toml` feature (not default). Supports:

- **Renaming `DATABASE_URL`** per crate — useful for multi-database workspaces
- **Global type overrides** for macros — prefer `chrono` over `time`, etc.
- **Renaming/relocating** the `_sqlx_migrations` table
- **Characters to ignore** when hashing migrations
- **SQLite extension loading** in macros/CLI

Guide: `sqlx::_config` module docs.

## MSRV and Runtime Feature Changes (0.9)

MSRV bumped to **1.86**.

Deprecated combination features like `runtime-tokio-native-tls` are **removed**. Use separate runtime and TLS features instead:

```toml
# Before (0.8)
sqlx = { version = "0.8", features = ["runtime-tokio-native-tls"] }

# After (0.9)
sqlx = { version = "0.9", features = ["runtime-tokio", "native-tls"] }
```

New runtime options:
- `runtime-smol`
- `runtime-async-global-executor` (replacing deprecated `async-std`)

## `Migrator::with_migrations()` (0.9)

New constructor for building a `Migrator` from a collection of migrations programmatically:

```rust
use sqlx::migrate::Migrator;

let migrator = Migrator::with_migrations(my_migrations);
```

## `RawSql` Type Parameter (0.9)

`RawSql` methods now have a `DB` type parameter. Also, `RawSql::fetch_optional()` now returns `Result<Option<DB::Row>>` instead of `Result<DB::Row>`.
