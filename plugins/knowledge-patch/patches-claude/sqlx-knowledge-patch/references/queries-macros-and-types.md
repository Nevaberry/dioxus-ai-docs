# Queries, Macros, and Types

## Static and dynamic query strings

All SQLx 0.9 `query*()` functions accept `impl SqlSafeStr`. Static strings can be passed directly:

```rust
let query = sqlx::query("SELECT id FROM users WHERE active = $1");
```

A non-static or dynamically constructed string must be wrapped explicitly:

```rust
let query = sqlx::query(sqlx::AssertSqlSafe(dynamic_sql));
```

The wrapper asserts that the SQL string itself is safe. Continue to bind application values as query parameters instead of interpolating them into the asserted string.

Because the wrapper can own its string, the API can return an owned `Query<'static, DB>`.

## Query and argument signatures

The `0.9.0-changelog` batch changes several generic signatures:

- `RawSql` methods have a `DB` type parameter.
- `Arguments` no longer has its old lifetime parameter.
- `SqliteArguments` no longer has its old lifetime parameter.
- `AnyArguments` no longer has its old lifetime parameter.
- `PgAdvisoryLockGuard` no longer has a lifetime parameter.

Remove obsolete lifetime arguments from explicit types, aliases, trait bounds, and return signatures. Supply the database type where a `RawSql` method now requires it.

## Macro nullability inference

For PostgreSQL, `query!()` now forces the database to use a generic plan while inferring nullability. Some queries can consequently produce different generated output types than before.

After upgrading, compile-check macro queries and review output nullability rather than assuming the earlier inferred shape remains stable.

## Offline macro data

If `SQLX_OFFLINE_DIR` is explicitly set, it takes precedence when query macros locate offline metadata. Check the environment first when a build appears to use an unexpected offline-data directory.

## PostgreSQL newtypes and arrays

For a newtype struct, `#[derive(sqlx::Type)]` now also generates `PgHasArrayType`:

```rust
#[derive(sqlx::Type)]
#[sqlx(transparent)]
struct AccountId(i64);
```

An existing manual `PgHasArrayType` implementation may now conflict with the generated one. Remove the manual implementation when generated behavior is appropriate. Otherwise, opt out:

```rust
#[derive(sqlx::Type)]
#[sqlx(no_pg_array)]
struct AccountId(i64);
```

## Encoded wrapper types

`Encode`, `Decode`, and `Type` now cover these wrappers:

- `Box`
- `Arc`
- `Rc`
- `Cow`

Decoding a `Cow` always produces `Cow::Owned`; do not rely on receiving a borrowed variant.

## Domains and transparent derives

PostgreSQL nested domains are supported. Transparent type derives also support a single-field named struct, not only tuple-style newtypes.

Use the support directly instead of introducing conversions solely because the value is wrapped by nested domains or a named one-field transparent struct.
