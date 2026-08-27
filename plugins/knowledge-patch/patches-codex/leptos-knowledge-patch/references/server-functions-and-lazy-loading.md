# Server Functions and Lazy Loading

## Custom server-function errors

Server functions can return any error type that implements
`FromServerFnError` (since 0.8.0), rather than being restricted to
`ServerFnError`. Migrate custom error types accordingly. The `extract()`
helper uses `ServerFnErrorErr`, and WebSocket request and response streams can
have different error types.

## WebSocket server functions

The `Websocket` protocol transports encodable `BoxedStream` values through a
normal server function (since 0.8.0). It does not integrate with Resources or
SSR, so the client must consume the returned stream explicitly.

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

## Macro declaration flexibility

Server-function macros accept repeated `#[middleware]` attributes, aliased
`Result` return types, and argument names with suffixes as of 0.8.0. These
forms no longer need rewriting just to satisfy macro parsing.

## Additional codecs

Server-function codecs support additional HTTP methods, direct `bitcode`
encoding and decoding, and a codec based on `bitcode`'s Serde integration
(since 0.8.0).

## Request body limits

Primary server-function encodings now obey Axum and Actix request-body limits
(since 0.8.0). For large non-multipart requests, including POST bodies over
2 MB, raise Axum's `DefaultBodyLimit` or Actix's `PayloadConfig` as
appropriate. Multipart uploads are unaffected.

## Lazy functions and routes

With a matching `cargo-leptos` release, `#[lazy]` converts a synchronous or
asynchronous function into a lazy-loaded async function (since 0.8.0).

```rust
#[lazy]
fn deserialize_comments(data: &str) -> Vec<Comment> {
    serde_json::from_str(data).unwrap()
}
```

Stack `#[server]` and `#[lazy]` for a lazy server function. Use
`#[lazy_route]` to divide a `LazyRoute` into data and view halves. Nested route
data and lazy views load concurrently before navigation. Lazy output supports
hashed filenames, and the later `lazy_preload` macro can preload lazy code.
