# Type System & Macros

## `SqlSafeStr` — Query String Safety (0.9)

All `query*()` functions now take `impl SqlSafeStr` instead of `&str`. Only `&'static str` and `AssertSqlSafe` implement it. This prevents accidental SQL injection from dynamic strings.

```rust
use sqlx::AssertSqlSafe;

// Static strings work as before — no changes needed
sqlx::query("SELECT * FROM users WHERE id = $1")
    .bind(user_id)
    .fetch_one(&pool).await?;

// Dynamic queries must be wrapped in AssertSqlSafe
let table = "users";
let q = format!("SELECT * FROM {table}");
sqlx::query(AssertSqlSafe(q)).fetch_all(&pool).await?;
```

This also enables returning owned queries as `Query<'static, DB>`.

## `Arguments` Trait — Lifetime Parameter Removed (0.9)

`Arguments<'q>` is now just `Arguments` (no lifetime). `SqliteArguments` and `AnyArguments` similarly lost their lifetime parameter. Bound values are now owned.

```rust
// Before (0.8)
fn build_query<'q>(args: &mut PgArguments<'q>) { ... }

// After (0.9)
fn build_query(args: &mut PgArguments) { ... }
```

## `Encode`/`Decode`/`Type` for Smart Pointers (0.9)

`Box<T>`, `Arc<T>`, `Rc<T>`, and `Cow<'_, T>` now implement `Encode`, `Decode`, and `Type` when `T` does.

**Breaking:** `Cow` always decodes as `Cow::Owned`.

## `PgBindIter` — Bind Iterators as Postgres Arrays (0.9)

Bind iterators directly as Postgres arrays without collecting to `Vec`:

```rust
use sqlx::postgres::PgBindIter;

let ids = [1i32, 2, 3];
sqlx::query("SELECT * FROM users WHERE id = ANY($1)")
    .bind(PgBindIter(ids.iter()))
    .fetch_all(&pool).await?;
```

Works with any iterator whose items implement `Encode` + `Type` for Postgres.

## `#[derive(sqlx::Type)]` Auto-Generates `PgHasArrayType` (0.9)

Newtype structs deriving `sqlx::Type` now automatically get a `PgHasArrayType` impl. If a manual `PgHasArrayType` impl exists, add `#[sqlx(no_pg_array)]` to avoid conflicts:

```rust
#[derive(sqlx::Type)]
#[sqlx(no_pg_array)] // needed if you had a manual PgHasArrayType impl
struct MyId(i32);
```

## `#[sqlx(json(nullable))]` — Nullable JSON Columns (0.8.4+)

Handle nullable JSON columns in `FromRow` derives:

```rust
#[derive(sqlx::FromRow)]
struct MyRow {
    #[sqlx(json(nullable))]
    metadata: Option<MyJsonType>,
}
```

## `#[sqlx(transparent)]` on Named Structs (0.9)

Single-field named structs (not just tuple structs) can now use `#[sqlx(transparent)]`:

```rust
#[derive(sqlx::Type)]
#[sqlx(transparent)]
struct UserId {
    id: i32, // single named field — now supported
}
```
