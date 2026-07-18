---
name: sqlx-knowledge-patch
description: SQLx
license: MIT
version: "0.9.0"
metadata:
  author: Nevaberry
---

# SQLx Knowledge Patch

Baseline: SQLx through 0.7.x. Covered range: `0.8.0` through the `0.9.0-changelog` batch.

Use this skill before changing SQLx dependencies, features, queries, macros, migrations, connection options, or encoded types. Check the detailed references when a task touches backend-specific behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [installation-and-configuration.md](references/installation-and-configuration.md) | Rust and CLI requirements, runtime/TLS features, `sqlx.toml`, offline builds, SQLite linking and opt-in APIs |
| [queries-macros-and-types.md](references/queries-macros-and-types.md) | `SqlSafeStr`, dynamic queries, macro inference, argument/API signature changes, derives, encoded types |
| [database-specific-behavior.md](references/database-specific-behavior.md) | PostgreSQL `ipnet` and connection escaping, MySQL RSA/text/collations, SQLite value and extension safety |
| [migrations-and-observability.md](references/migrations-and-observability.md) | Migration capabilities and API changes, tracing field correction |

## Breaking changes and removals

### Toolchain and CLI installation

SQLx 0.9 requires Rust 1.94.0. The repository no longer tracks `Cargo.lock`, so this old installation form no longer works:

```console
cargo install --locked sqlx-cli
```

Install without `--locked`, or maintain a lockfile yourself when reproducibility is required.

### Runtime and TLS features

The combined runtime-and-TLS features were soft-deprecated in 0.8 and removed in 0.9. Select a runtime and TLS implementation independently.

```toml
[dependencies]
sqlx = { version = "0.9", features = [
  "runtime-tokio",
  "postgres",
  "tls-rustls-ring-native-roots",
] }
```

Do not carry forward features such as:

```toml
features = ["runtime-tokio-native-tls"]
```

The Rustls choices include:

- `tls-rustls-ring-native-roots`
- `tls-rustls-ring-webpki`
- `tls-rustls-aws-lc-rs`

For runtimes, `runtime-smol` and `runtime-async-global-executor` replace deprecated async-std usage.

### Dynamic query strings require an assertion

All `query*()` functions accept `impl SqlSafeStr`. String literals and other static strings work directly. Wrap non-static or dynamically assembled SQL explicitly in `AssertSqlSafe`:

```rust
let query = sqlx::query(sqlx::AssertSqlSafe(dynamic_sql));
```

This API also permits an owned query to be returned as `Query<'static, DB>`.

Treat the wrapper as an explicit trust boundary: parameterize values and assert only the SQL structure.

### Public type signatures changed

Update annotations, bounds, and manual trait implementations for these changes:

- `RawSql` methods now have a `DB` type parameter.
- `Arguments`, `SqliteArguments`, and `AnyArguments` no longer have their former lifetime parameters.
- `PgAdvisoryLockGuard` no longer has a lifetime parameter.
- The `Migrate` trait changed significantly.
- `resolve_blocking()` is hidden and SemVer-exempt; do not depend on it.

### SQLite values have tighter thread boundaries

`SqliteValue` is now `!Sync`, and `SqliteValueRef` is now `!Send`. Before crossing the respective thread boundary, clone the value, convert it to an owned representation, or put owned state behind appropriate synchronization.

After decoding one SQLite value as borrowed `&[u8]` or `&str`, decoding that same value as another type now returns an error.

### PostgreSQL newtype array derivation

`#[derive(sqlx::Type)]` now generates `PgHasArrayType` for newtype structs. Remove a conflicting manual implementation or disable generation:

```rust
#[derive(sqlx::Type)]
#[sqlx(no_pg_array)]
struct UserId(i64);
```

### Escaping and telemetry corrections

`PgConnectOptions::options()` escapes option values itself. Remove caller-side manual escaping to prevent double escaping.

Backslash escapes in `.pgpass` passwords are decoded, which can change the password sent compared with earlier behavior.

Rename tracing consumers that expect `aquired_after_secs`; the corrected field is `acquired_after_secs`.

## Configuration quick reference

### Per-crate `sqlx.toml`

SQLx 0.9 adds per-crate `sqlx.toml` configuration. It can:

- rename the crate's `DATABASE_URL` variable;
- define global macro type overrides;
- rename or relocate `_sqlx_migrations`;
- exclude selected characters, including whitespace, from migration hashes.

`sqlx-cli` enables this support by default. Library users must enable it:

```toml
[dependencies]
sqlx = { version = "0.9", features = ["sqlx-toml"] }
```

An explicitly set `SQLX_OFFLINE_DIR` environment variable takes precedence when macros search for offline data.

The `offline` feature is optional, allowing configurations that do not need it to build without `serde`.

### SQLite linking choice

Since 0.8, `sqlite` bundles and statically links SQLite. Select `sqlite-unbundled` when linking a system or custom library:

```toml
[dependencies]
sqlx = { version = "0.9", features = ["runtime-tokio", "sqlite-unbundled"] }
```

The unbundled path requires SQLite at build time, recommends SQLite 3.20.0 or newer, and may invoke bindgen and increase build time.

### SQLite opt-in features

Enable only the APIs the application needs:

| Feature | Capability / caveat |
| --- | --- |
| `sqlite-preupdate-hook` | Enables SQLite's normally disabled preupdate-hook API; with `sqlite-unbundled`, linking fails if the system library omits it. |
| `sqlite-deserialize` | Gates SQLite serialize/deserialize APIs. |
| `sqlite-load-extension` | Gates extension-loading APIs; loading is `unsafe`, including configuration through `sqlx.toml`. |
| `sqlite-unlock-notify` | Gates SQLx's internal SQLite unlock notification support. |

The compatible maximum `libsqlite3-sys` version may increase in a non-breaking SQLx release.

## Query, macro, and type quick reference

PostgreSQL `query!()` now forces a generic plan for nullability inference. Recheck generated output types when upgrading queries whose inferred nullability depends on planning.

`Encode`, `Decode`, and `Type` support `Box`, `Arc`, `Rc`, and `Cow`. Decoding a `Cow` always yields `Cow::Owned`.

PostgreSQL also supports nested domains. Transparent derives work for single-field named structs.

## Database-specific quick reference

### PostgreSQL

Enable `ipnet` to map PostgreSQL `INET` and `CIDR` to types from the `ipnet` crate, as an alternative to `ipnetwork`:

```toml
sqlx = { version = "0.9", features = ["runtime-tokio", "postgres", "ipnet"] }
```

### MySQL

Plaintext connections that need RSA password encryption fail unless `mysql-rsa` is enabled. TLS connections do not use this path.

```toml
sqlx = { version = "0.9", features = ["runtime-smol", "mysql", "mysql-rsa"] }
```

Non-binary text-like columns that previously inferred as `Vec<u8>` may infer as `String`. SQLx sends `SET NAMES utf8mb4` without forcing a collation. Calling `MySqlConnectOptions::charset()` or `.collation()` automatically enables `set_names`.

## Migration quick reference

The migration layer now supports:

- `no_tx` migrations;
- skipping migrations;
- constructing a migrator with `Migrator::with_migrations()`.

`set_ignore_missing()` and `set_locking()` now return `&mut Self`, so update code that expected ownership or a different builder return type.

## Upgrade checklist

1. Move to Rust 1.94.0 before adopting SQLx 0.9.
2. Remove `--locked` from direct `sqlx-cli` installation unless supplying your own lockfile workflow.
3. Replace combined runtime/TLS and deprecated async-std features.
4. Decide whether library crates should enable `sqlx-toml` and `offline`.
5. Wrap dynamic SQL with `AssertSqlSafe` and keep values parameterized.
6. Update removed lifetimes, the `RawSql` database parameter, and migration trait usage.
7. Audit derived PostgreSQL newtypes for duplicate `PgHasArrayType` implementations.
8. Recheck `query!()` output nullability and MySQL text inference.
9. Audit SQLite thread crossings, repeated borrowed decoding, and extension-loading safety.
10. Remove manual PostgreSQL option escaping and update the corrected tracing field name.
