# Routing and Handlers

## Path Parameter Syntax (0.8.0)

`/:param` → `/{param}`, `/*wildcard` → `/{*wildcard}`. Old colon/star syntax **panics at runtime**.

```rust
// Before (0.7)
Router::new().route("/users/:id/files/*path", get(handler));
// After (0.8)
Router::new().route("/users/{id}/files/{*path}", get(handler));
```

Escape literal braces with `{{` / `}}`.

## `Router::method_not_allowed_fallback` (0.8.0)

Custom handler when a path matches but the HTTP method doesn't:

```rust
let app = Router::new()
    .route("/items", get(list_items))
    .method_not_allowed_fallback(|| async { "Method not supported" });
```

## `Router::reset_fallback` (0.8.4)

Removes a previously set fallback handler, reverting to the default 404. Useful when nesting a router that has its own fallback into a parent that should use a different one:

```rust
let api = Router::new()
    .route("/items", get(list_items))
    .fallback(api_fallback);

// Nest but discard the nested fallback so the parent's fallback applies
let app = Router::new()
    .nest("/api", api.reset_fallback())
    .fallback(global_fallback);
```

## CONNECT Method Support (0.8.0)

```rust
use axum::routing::connect;

let app = Router::new().route("/proxy", connect(connect_handler));
```

Also available via `MethodFilter::CONNECT`.

## All Handlers Must Be `Sync` (0.8.0)

All handlers and services on `Router` / `MethodRouter` must implement `Sync` (in addition to `Send`). This was already the case in practice for most handlers.

## `serve` Is Generic Over Listener/IO Types (0.8.0)

`serve` is now generic over listener and IO types. `Serve::tcp_nodelay` was removed — use `serve::ListenerExt` instead:

```rust
use axum::serve::ListenerExt;

let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
    .await?
    .tap(|l| l.set_nodelay(true));
```
