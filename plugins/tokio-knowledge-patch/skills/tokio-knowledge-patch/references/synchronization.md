# Synchronization

## `sync::SetOnce` (Tokio 1.47)

New async equivalent of `std::sync::OnceLock`. Allows one task to set a value and many others to wait for it. Thread-safe and works across tasks and threads.

```rust
use tokio::sync::SetOnce;

static GLOBAL: SetOnce<String> = SetOnce::const_new();

// First call sets the value; subsequent calls return the existing value
let val = GLOBAL.get_or_init(|| async { "hello".to_string() }).await;

// Non-blocking access after initialization
let val: Option<&String> = GLOBAL.get();
```

Key methods:
- `SetOnce::const_new()` — create in `static` context
- `SetOnce::new()` — create at runtime
- `get_or_init(f)` — initialize with async closure, or return existing value
- `get_or_try_init(f)` — like `get_or_init` but the closure returns `Result`
- `get()` — non-blocking `Option<&T>`, returns `None` if not yet set
- `set(value)` — try to set the value, returns `Err(value)` if already set

Common pattern — lazy async initialization:

```rust
static DB_POOL: SetOnce<PgPool> = SetOnce::const_new();

async fn get_pool() -> &'static PgPool {
    DB_POOL.get_or_init(|| async {
        PgPool::connect(&std::env::var("DATABASE_URL").unwrap())
            .await
            .expect("Failed to create pool")
    }).await
}
```

## `Notify::notified_owned()` (Tokio 1.47)

Returns `OwnedNotified` (no lifetime parameter) instead of `Notified<'_>`. This enables use in spawned tasks without `Arc` workarounds or lifetime issues.

```rust
use std::sync::Arc;
use tokio::sync::Notify;

let notify = Arc::new(Notify::new());

// Old: notified() returns Notified<'_> — can't move into spawn
// let fut = notify.notified(); // borrows notify
// tokio::spawn(async move { fut.await }); // ERROR: lifetime issue

// New: notified_owned() returns OwnedNotified — no lifetime
let owned = notify.notified_owned();
tokio::spawn(async move { owned.await });
```

`OwnedNotified` holds an internal `Arc` to the `Notify`, so it's `'static` and can be freely moved across task boundaries.

## `CancellationToken` `FutureExt` adapters (tokio-util 0.7.16)

Extension methods on futures to cancel them directly with a `CancellationToken`:

```rust
use tokio_util::sync::CancellationToken;
use tokio_util::either::Either;

let token = CancellationToken::new();

let result = my_future.unless_cancelled_with(&token).await;
match result {
    Either::Left(value) => {
        // Future completed successfully
    }
    Either::Right(()) => {
        // Token was cancelled
    }
}
```

This is more ergonomic than `tokio::select!` with `token.cancelled()` for simple cancellation patterns:

```rust
// Before (select! approach):
tokio::select! {
    result = my_future => handle(result),
    _ = token.cancelled() => handle_cancel(),
}

// After (adapter approach):
match my_future.unless_cancelled_with(&token).await {
    Either::Left(result) => handle(result),
    Either::Right(()) => handle_cancel(),
}
```
