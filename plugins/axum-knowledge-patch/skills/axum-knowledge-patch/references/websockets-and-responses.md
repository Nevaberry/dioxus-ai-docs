# WebSockets and Responses

## WebSocket Breaking Changes (0.8.0)

### Message Type Changes

`ws::Message` variants use `Bytes` instead of `Vec<u8>` and new `Utf8Bytes` instead of `String`:

```rust
// Before (0.7)
Message::Text(String)
Message::Binary(Vec<u8>)

// After (0.8)
Message::Text(Utf8Bytes)
Message::Binary(Bytes)
```

### `WebSocket::close` Removed

Send close messages explicitly instead of calling `.close()`:

```rust
socket.send(Message::Close(None)).await.ok();
```

### HTTP/2 WebSocket Support

HTTP/2 WebSockets are now supported. Change `get(ws_handler)` to `any(ws_handler)` to allow WebSocket upgrades over both HTTP/1.1 and HTTP/2:

```rust
Router::new().route("/ws", any(ws_handler));
```

## `WebSocketUpgrade::selected_protocol` (0.8.4)

Returns the subprotocol selected during the WebSocket handshake, if any:

```rust
async fn ws_handler(ws: WebSocketUpgrade) -> impl IntoResponse {
    let proto = ws.selected_protocol().map(|p| p.to_string());
    ws.on_upgrade(move |socket| handle_socket(socket, proto))
}
```

## `NoContent` Response (0.8.0)

Shortcut for `StatusCode::NO_CONTENT`:

```rust
use axum::response::NoContent;

async fn delete_item() -> NoContent {
    // ... delete logic
    NoContent
}
```

## Binary Data in Server-Sent Events (0.8.5)

SSE events can carry arbitrary binary data via `Event::bytes()`:

```rust
use axum::response::sse::{Event, Sse};

let event = Event::default().bytes(my_bytes);
```

## `middleware::ResponseAxumBodyLayer` (0.8.5)

Maps a response with any `http_body::Body` into one using `axum::body::Body`. Useful when composing tower services that return a different body type:

```rust
use axum::middleware::ResponseAxumBodyLayer;

let app = Router::new()
    .route("/", get(handler))
    .layer(ResponseAxumBodyLayer::new());
```
