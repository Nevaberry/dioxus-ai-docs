---
name: sqlx-knowledge-patch
description: SQLx changes since training cutoff (latest: 0.9.0-alpha.1) — SqlSafeStr, owned Arguments, sqlx.toml config, begin_with transactions, SQLite hooks, PgBindIter. Load before working with SQLx.
version: "0.9.0-alpha.1"
license: MIT
metadata:
  author: Nevaberry
---

# SQLx Knowledge Patch

Covers SQLx 0.8.3–0.9.0-alpha.1 (2025-01-03 through 2025-10-14). Claude Opus 4.6 knows SQLx through 0.7.x. It is **unaware** of the 0.8+ features and 0.9 breaking changes below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Transactions | [references/transactions.md](references/transactions.md) | `begin_with`, per-DB option types, `is_in_transaction`, type aliases |
| Type system & macros | [references/type-system.md](references/type-system.md) | `SqlSafeStr`, `Arguments` lifetime removal, smart pointer Encode/Decode, `PgBindIter`, `PgHasArrayType` auto-derive, `json(nullable)`, transparent named structs |
| SQLite | [references/sqlite.md](references/sqlite.md) | Commit/rollback/preupdate hooks, feature flags (`sqlite-deserialize`, `sqlite-load-extension`, `sqlite-unlock-notify`), `sqlite-unbundled`, `no_tx` migrations |
| Postgres & MySQL | [references/postgres-and-mysql.md](references/postgres-and-mysql.md) | Geometry types, `ipnet` support, `PgConnectOptions` auto-escaping, MySQL collation inference, `PgListener` improvements |
| Configuration & runtime | [references/configuration.md](references/configuration.md) | `sqlx.toml`, MSRV 1.86, runtime feature changes, `Migrator::with_migrations`, `RawSql` type parameter |

---

## 0.8 → 0.9 Migration — Breaking Changes

**Note:** 0.9.0-alpha.1 is the current alpha. Many breaking changes from 0.8.x.

| What changed | Before (0.8) | After (0.9) |
|---|---|---|
| Query string safety | `query("...")` accepts `&str` | Accepts `impl SqlSafeStr` — only `&'static str` or `AssertSqlSafe` |
| `Arguments` lifetime | `Arguments<'q>`, `SqliteArguments<'q>` | `Arguments` (no lifetime) — values are owned |
| Runtime features | `runtime-tokio-native-tls` combos | Separate `runtime-tokio` + `native-tls`; combos removed |
| MSRV | 1.75 | 1.86 |
| `RawSql` | No type parameter | `RawSql` methods require `DB` type parameter |
| `RawSql::fetch_optional` | Returns `Result<DB::Row>` | Returns `Result<Option<DB::Row>>` |
| `Cow` decoding | Could be `Cow::Borrowed` | Always `Cow::Owned` |
| SQLite extension loading | `extension()` safe method | `unsafe`; requires `sqlite-load-extension` feature |
| `SqliteValue` | `Sync` | `!Sync`; `SqliteValueRef` is `!Send` |
| MySQL text columns | Inferred as `Vec<u8>` | Inferred as `String` |
| `PgConnectOptions::options()` | Manual escaping needed | Auto-escaped — remove manual escaping |
| `#[derive(sqlx::Type)]` newtype | No auto `PgHasArrayType` | Auto-generates `PgHasArrayType`; add `#[sqlx(no_pg_array)]` if manual impl exists |

**Also note:** 0.8.4 was **yanked** — use 0.8.5+ instead. All 0.8.4 features are available in 0.8.5.

## `SqlSafeStr` — Query String Safety (0.9)

The most impactful breaking change. All `query*()` functions now take `impl SqlSafeStr` instead of `&str`. Only `&'static str` and `AssertSqlSafe` implement it.

```rust
use sqlx::AssertSqlSafe;

// Static strings work as before
sqlx::query("SELECT * FROM users WHERE id = $1")
    .bind(user_id)
    .fetch_one(&pool).await?;

// Dynamic queries must be wrapped
let table = "users";
let q = format!("SELECT * FROM {table}");
sqlx::query(AssertSqlSafe(q)).fetch_all(&pool).await?;
```

This also enables returning owned queries as `Query<'static, DB>`.

## `begin_with` — Transaction Options (0.8.4+)

Start transactions with database-specific options:

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

Each database has its own options type: `PgTransactionOptions`, `MySqlTransactionOptions`, `SqliteTransactionOptions`.

See [references/transactions.md](references/transactions.md) for `is_in_transaction` and type aliases.

## `Arguments` Lifetime Removal (0.9)

`Arguments<'q>` is now just `Arguments` (no lifetime). `SqliteArguments` and `AnyArguments` similarly lost their lifetime parameter. Bound values are now owned.

```rust
// Before (0.8)
fn build_query<'q>(args: &mut PgArguments<'q>) { ... }

// After (0.9)
fn build_query(args: &mut PgArguments) { ... }
```

## Smart Pointer `Encode`/`Decode`/`Type` (0.9)

`Box<T>`, `Arc<T>`, `Rc<T>`, and `Cow<'_, T>` now implement `Encode`, `Decode`, and `Type` when `T` does. **Breaking:** `Cow` always decodes as `Cow::Owned`.

## `PgBindIter` — Bind Iterators as Arrays (0.9)

Bind iterators directly as Postgres arrays without collecting to `Vec`:

```rust
use sqlx::postgres::PgBindIter;

let ids = [1i32, 2, 3];
sqlx::query("SELECT * FROM users WHERE id = ANY($1)")
    .bind(PgBindIter(ids.iter()))
    .fetch_all(&pool).await?;
```

## `#[derive(sqlx::Type)]` Auto-Generates `PgHasArrayType` (0.9)

Newtype structs deriving `sqlx::Type` now automatically get a `PgHasArrayType` impl. Add `#[sqlx(no_pg_array)]` to opt out:

```rust
#[derive(sqlx::Type)]
#[sqlx(no_pg_array)] // needed if you had a manual PgHasArrayType impl
struct MyId(i32);
```

## `json(nullable)` and Transparent Named Structs

Handle nullable JSON columns in `FromRow` derives (0.8.4+):

```rust
#[derive(sqlx::FromRow)]
struct MyRow {
    #[sqlx(json(nullable))]
    metadata: Option<MyJsonType>,
}
```

Single-field named structs can now use `#[sqlx(transparent)]` (0.9):

```rust
#[derive(sqlx::Type)]
#[sqlx(transparent)]
struct UserId {
    id: i32, // single named field — now supported
}
```

## Runtime Feature Migration (0.9)

Deprecated combination features removed. Use separate features:

```toml
# Before (0.8)
sqlx = { version = "0.8", features = ["runtime-tokio-native-tls"] }

# After (0.9)
sqlx = { version = "0.9", features = ["runtime-tokio", "native-tls"] }
```

New runtime options: `runtime-smol` and `runtime-async-global-executor` (replacing deprecated `async-std`).

## `sqlx.toml` Configuration (0.9)

Per-crate configuration (requires `sqlx-toml` feature). Supports renaming `DATABASE_URL`, global type overrides for macros, renaming the `_sqlx_migrations` table, and SQLite extension loading in macros/CLI.

Guide: `sqlx::_config` module docs. See [references/configuration.md](references/configuration.md) for details.

## SQLite Feature Flag Changes (0.9)

New **non-default** features for conditional SQLite APIs:

| Feature | Enables |
|---|---|
| `sqlite-deserialize` | `SqliteConnection::serialize()` / `deserialize()` |
| `sqlite-load-extension` | `SqliteConnectOptions::extension()` (now `unsafe`) |
| `sqlite-unlock-notify` | Internal `sqlite3_unlock_notify()` usage |
| `sqlite-preupdate-hook` | `conn.on_preupdate()` callback (added in 0.8.4) |

See [references/sqlite.md](references/sqlite.md) for commit/rollback hooks and `no_tx` migrations.

## New APIs Summary

| API | Version | Description |
|---|---|---|
| `conn.on_commit()` / `on_rollback()` | 0.8.3 | SQLite commit/rollback hook callbacks |
| `PgListener: Acquire` + `next_buffered()` | 0.8.3 | Use PgListener as connection; batch notifications |
| `PgPoint`, `PgLine` | 0.8.3 | Postgres geometry types |
| Transaction type aliases | 0.8.3 | `PgTransaction<'c>`, `MySqlTransaction<'c>`, `SqliteTransaction<'c>` |
| `sqlite-unbundled` feature | 0.8.3 | Dynamically link system `libsqlite3.so` |
| `AnyQueryResult` for SQLite/MySQL | 0.8.3 | Previously Postgres-only |
| `begin_with` + per-DB options | 0.8.4 | Custom transaction isolation, read-only, etc. |
| `Connection::is_in_transaction` | 0.8.4 | Check if inside a transaction |
| `conn.on_preupdate()` | 0.8.4 | SQLite preupdate hook (requires feature) |
| `#[sqlx(json(nullable))]` | 0.8.4 | Handle nullable JSON columns in FromRow |
| `PgLineSegment`, `PgBox`, `PgPath`, `PgPolygon`, `PgCircle` | 0.8.4 | Additional Postgres geometry types |
| `ipnet::IpNet` mapping | 0.8.4 | Maps to Postgres INET/CIDR (requires `ipnet` feature) |
| `SqlSafeStr` / `AssertSqlSafe` | 0.9 | Query string safety wrapper |
| `PgBindIter` | 0.9 | Bind iterators as Postgres arrays |
| `Encode`/`Decode` for `Box<T>`, `Arc<T>`, `Rc<T>`, `Cow<T>` | 0.9 | Smart pointer support |
| `#[sqlx(no_pg_array)]` | 0.9 | Opt out of auto `PgHasArrayType` |
| `#[sqlx(transparent)]` on named structs | 0.9 | Single-field named structs (not just tuple structs) |
| `no_tx` SQLite migrations | 0.9 | Opt out of transaction wrapping |
| `Migrator::with_migrations()` | 0.9 | Build Migrator from collection programmatically |
| `sqlx.toml` configuration | 0.9 | Per-crate config (requires `sqlx-toml` feature) |

## Reference Files

| File | Contents |
|---|---|
| [transactions.md](references/transactions.md) | `begin_with` options, isolation levels, `is_in_transaction`, type aliases |
| [type-system.md](references/type-system.md) | `SqlSafeStr`, `Arguments` lifetime, smart pointers, `PgBindIter`, `PgHasArrayType`, `json(nullable)`, transparent structs |
| [sqlite.md](references/sqlite.md) | Commit/rollback/preupdate hooks, feature flags, `sqlite-unbundled`, `no_tx` migrations |
| [postgres-and-mysql.md](references/postgres-and-mysql.md) | Geometry types, `ipnet`, `PgConnectOptions` escaping, MySQL collation, `PgListener` |
| [configuration.md](references/configuration.md) | `sqlx.toml`, MSRV/runtime changes, `Migrator::with_migrations`, `RawSql` type parameter |
