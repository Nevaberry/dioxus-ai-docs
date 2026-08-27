# WebSockets and streaming

## Byte-backed WebSocket messages

Axum 0.8.0 changes WebSocket message payloads:

- binary variants use `Bytes` instead of `Vec<u8>`;
- text variants use `Utf8Bytes` instead of `String`.

Convert owned strings and vectors at construction sites where required:

```rust
socket.send(Message::Text("hello".into())).await?;
```

## Explicit close messages

`WebSocket::close` has been removed. Send a close frame through the normal message sink:

```rust
socket.send(Message::Close(None)).await?;
```

Supply close-frame data instead of `None` when the protocol requires a close code or reason.

## HTTP/2 WebSocket routing

WebSockets over HTTP/2 are supported, but an endpoint registered only with `get` does not accept the HTTP/2 connection method. Register the endpoint with method-agnostic routing:

```rust
Router::new().route("/ws", any(ws_endpoint))
```

## Dynamic subprotocol selection

Use the upgrade object's protocol APIs when selection depends on the client's offers:

1. Read offered protocols with `WebSocketUpgrade::requested_protocols`.
2. Choose one with `set_selected_protocol`.
3. Inspect the negotiated result with `selected_protocol`.

## Fused stream support

`WebSocket` implements `FusedStream`. Stream consumers can query whether it has terminated and pass it to combinators or utilities that require fused-stream semantics.

## Server-sent events

SSE events accept arbitrary binary payload data rather than only text-like values.

The `sse` module and `Sse` type no longer require axum's `tokio` feature. A `default-features = false` build can use SSE without enabling `tokio` solely for that module.

