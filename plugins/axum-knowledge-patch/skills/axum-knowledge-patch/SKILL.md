---
name: axum-knowledge-patch
description: "Axum changes since training cutoff (latest: 0.8.5) — {param} path syntax, no async_trait, OptionalFromRequestParts, Utf8Bytes WS, HTTP/2 WebSockets, NoContent. Load before working with Axum."
version: "0.8.5"
license: MIT
metadata:
  author: Nevaberry
---

# Axum Knowledge Patch

Covers Axum 0.8.0–0.8.5 (2025-01-01 through 2025-09-28). Claude Opus 4.6 knows Axum through 0.7.x. It is **unaware** of the 0.8 breaking changes and features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Routing & handlers | [references/routing-and-handlers.md](references/routing-and-handlers.md) | Path syntax `/{param}`, `reset_fallback`, `method_not_allowed_fallback`, CONNECT, Sync requirement |
| Extractors | [references/extractors.md](references/extractors.md) | No `#[async_trait]`, `OptionalFromRequestParts`, `Option<Json<T>>`, `Option<Multipart>` |
| WebSockets & responses | [references/websockets-and-responses.md](references/websockets-and-responses.md) | `Utf8Bytes`/`Bytes` messages, HTTP/2 WS, `NoContent`, SSE binary, `ResponseAxumBodyLayer` |

---

## 0.7 → 0.8 Migration — Breaking Changes

| What changed | Before (0.7) | After (0.8) |
|---|---|---|
| Path params | `/:id`, `/*path` | `/{id}`, `/{*path}` (old syntax panics) |
| Extractor traits | `#[async_trait] impl FromRequestParts` | Native async fn (remove `#[async_trait]`) |
| `Option<T>` extraction | Swallows all errors as `None` | Requires `OptionalFromRequestParts`; invalid → rejection |
| WS message types | `String` / `Vec<u8>` | `Utf8Bytes` / `Bytes` |
| `WebSocket::close` | Method on socket | Removed — send `Message::Close` explicitly |
| HTTP/2 WebSockets | Not supported | Use `any(ws_handler)` instead of `get(ws_handler)` |
| Handler trait bounds | `Send` | `Send + Sync` |
| `Host` extractor | `axum::extract::Host` | Moved to `axum-extra` |
| `Serve::tcp_nodelay` | Method on `Serve` | Removed — use `serve::ListenerExt` |

## Path Parameter Syntax (0.8.0)

The most common migration issue. Old colon/star syntax **panics at runtime**.

```rust
// Before (0.7)
Router::new().route("/users/:id/files/*path", get(handler));

// After (0.8)
Router::new().route("/users/{id}/files/{*path}", get(handler));
```

Escape literal braces with `{{` / `}}`.

See [references/routing-and-handlers.md](references/routing-and-handlers.md) for details.

## Extractor Trait Migration (0.8.0)

Remove `#[async_trait]` from custom `FromRequestParts` / `FromRequest` impls — Axum 0.8 uses native async fn in traits (RPITIT):

```rust
// Before (0.7)
#[async_trait]
impl<S> FromRequestParts<S> for MyExtractor where S: Send + Sync {
    type Rejection = StatusCode;
    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        todo!()
    }
}

// After (0.8) — remove #[async_trait], signature unchanged
impl<S> FromRequestParts<S> for MyExtractor where S: Send + Sync {
    type Rejection = StatusCode;
    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        todo!()
    }
}
```

See [references/extractors.md](references/extractors.md) for `OptionalFromRequestParts` and optional extractors.

## Optional Extractors (0.8.0–0.8.5)

`Option<T>` extraction changed: `T` must implement `OptionalFromRequestParts` (or `OptionalFromRequest`). Missing value → `None`, invalid value → rejection error.

Built-in support added incrementally:

| Extractor | `Option<T>` support | Version |
|---|---|---|
| `Json<T>` | `OptionalFromRequest` | 0.8.3 |
| `Extension<T>` | `OptionalFromRequestParts` | 0.8.3 |
| `Multipart` | `OptionalFromRequest` | 0.8.5 |

```rust
async fn handler(body: Option<Json<MyPayload>>) -> impl IntoResponse {
    match body {
        Some(Json(payload)) => { /* process payload */ }
        None => { /* no body sent */ }
    }
}
```

## WebSocket Changes (0.8.0)

Message types changed from `String`/`Vec<u8>` to `Utf8Bytes`/`Bytes`:

```rust
// Before (0.7)
Message::Text(String)
Message::Binary(Vec<u8>)

// After (0.8)
Message::Text(Utf8Bytes)
Message::Binary(Bytes)
```

`WebSocket::close` removed — send close messages explicitly:

```rust
socket.send(Message::Close(None)).await.ok();
```

For HTTP/2 WebSocket support, use `any()` instead of `get()`:

```rust
Router::new().route("/ws", any(ws_handler));
```

See [references/websockets-and-responses.md](references/websockets-and-responses.md) for `selected_protocol` and more.

## New APIs

| API | Version | Description |
|---|---|---|
| `Router::method_not_allowed_fallback` | 0.8.0 | Custom handler when path matches but method doesn't |
| `NoContent` | 0.8.0 | Shortcut response for `StatusCode::NO_CONTENT` |
| `routing::connect` | 0.8.0 | CONNECT method support |
| `Router::reset_fallback` | 0.8.4 | Remove a fallback, reverting to default 404 |
| `WebSocketUpgrade::selected_protocol` | 0.8.4 | Get the subprotocol selected during WS handshake |
| `Event::bytes()` | 0.8.5 | Binary data in SSE events |
| `ResponseAxumBodyLayer` | 0.8.5 | Map any body type to `axum::body::Body` |

### Quick Examples

```rust
use axum::response::NoContent;

// NoContent response
async fn delete_item() -> NoContent {
    NoContent
}

// Router with method_not_allowed_fallback and reset_fallback
let api = Router::new()
    .route("/items", get(list_items).post(create_item))
    .fallback(api_fallback);

let app = Router::new()
    .nest("/api", api.reset_fallback())
    .method_not_allowed_fallback(|| async { "Method not supported" })
    .fallback(global_fallback);

// SSE with binary data (0.8.5)
use axum::response::sse::{Event, Sse};
let event = Event::default().bytes(my_bytes);

// ResponseAxumBodyLayer — normalize body types from tower services (0.8.5)
use axum::middleware::ResponseAxumBodyLayer;
let app = Router::new()
    .route("/", get(handler))
    .layer(ResponseAxumBodyLayer::new());
```

## Reference Files

| File | Contents |
|---|---|
| [routing-and-handlers.md](references/routing-and-handlers.md) | Path syntax, router methods, CONNECT, Sync requirement, serve changes |
| [extractors.md](references/extractors.md) | async_trait removal, OptionalFromRequestParts, optional extractor support |
| [websockets-and-responses.md](references/websockets-and-responses.md) | WS message types, HTTP/2 WS, NoContent, SSE binary, ResponseAxumBodyLayer |
