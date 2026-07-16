# Server Functions and Lazy Loading

## Custom server-function errors

A server function can use any error type that implements
`FromServerFnError` (since 0.8.0); it is not restricted to `ServerFnError`.
Migrate custom errors to satisfy that conversion. The `extract()` helper uses
`ServerFnErrorErr`, and WebSocket request and response streams may use
different error types.

## WebSocket server functions

The `Websocket` protocol transports encoded `BoxedStream` values through an
ordinary server function. It does not integrate with Resources or SSR, so the
client must explicitly consume the returned stream.

```rust
use futures::{channel::mpsc, SinkExt, StreamExt};
use server_fn::{codec::JsonEncoding, BoxedStream, ServerFnError, Websocket};

#[server(protocol = Websocket<JsonEncoding, JsonEncoding>)]
async fn uppercase(
    input: BoxedStream<String, ServerFnError>,
) -> Result<BoxedStream<String, ServerFnError>, ServerFnError> {
    let mut input = input;
    let (mut tx, rx) = mpsc::channel(1);
    tokio::spawn(async move {
        while let Some(message) = input.next().await {
            let _ = tx.send(message.map(|text| text.to_ascii_uppercase())).await;
        }
    });
    Ok(rx.into())
}
```

## Macro declarations and codecs

Server-function macros accept multiple `#[middleware]` attributes, aliased
`Result` return types, and argument names with suffixes (since 0.8.0). These
forms do not need to be rewritten merely to satisfy macro parsing.

Supported codecs include additional HTTP methods, direct `bitcode` encoding
and decoding, and a codec that uses `bitcode`'s Serde integration.

## Request body limits

Primary server-function encodings honor Axum and Actix request-body limits
(since 0.8.0). A large non-multipart request, such as a POST body over 2 MB,
may require a larger Axum `DefaultBodyLimit` or Actix `PayloadConfig`.
Multipart uploads are unaffected by this change.

## Lazy functions

With a matching `cargo-leptos` release, `#[lazy]` changes a synchronous or
asynchronous function into a lazy-loaded async function:

```rust
#[lazy]
fn deserialize_comments(data: &str) -> Vec<Comment> {
    serde_json::from_str(data).unwrap()
}
```

Stack `#[server]` and `#[lazy]` to make a server function lazy. Lazy-loaded
output supports file hashing. `lazy_preload` can preload lazy code.

## Lazy routes

`#[lazy_route]` splits a `LazyRoute` into data and view halves (since 0.8.0).
Nested route data and lazy views load concurrently before navigation, avoiding
a serial data-then-view waterfall while preserving the route boundary.
