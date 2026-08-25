# Server Functions and Lazy Loading

## Use custom server-function errors

Server functions can return any error implementing `FromServerFnError` (since
0.8.0), rather than only `ServerFnError`. Custom error types may need migration
to implement that conversion. Code using `extract()` must account for
`ServerFnErrorErr`, and WebSocket request and response streams can have
different error types.

## Stream through WebSocket server functions

The `Websocket` protocol transports encodable `BoxedStream` values through an
ordinary server function (since 0.8.0). It does not integrate with Resources
or SSR; consume the returned stream explicitly on the client.

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

## Use flexible server declarations

Server-function macros accept repeated `#[middleware]` attributes, aliased
`Result` return types, and argument names with suffixes (since 0.8.0). These
forms no longer need to be rewritten merely to satisfy macro parsing.

## Select newer codecs

Server-function codecs support additional HTTP methods, direct `bitcode`
encoding and decoding, and a codec using `bitcode`'s Serde integration (since
0.8.0). Select the transport and encoding that match both server and client.

## Configure request-body limits

Primary server-function encodings respect Axum and Actix request-body limits
(since 0.8.0). Large non-multipart requests, including POST bodies over 2 MB,
may require a larger Axum `DefaultBodyLimit` or Actix `PayloadConfig`.
Multipart uploads are unaffected by this change.

## Split WASM code lazily

With a matching `cargo-leptos`, `#[lazy]` turns either a synchronous or an
asynchronous function into a lazy-loaded async function (since 0.8.0).

```rust
#[lazy]
fn deserialize_comments(data: &str) -> Vec<Comment> {
    serde_json::from_str(data).unwrap()
}
```

Stack `#[server]` and `#[lazy]` to make a lazy server function. Lazy-loaded
output supports file hashing, and `lazy_preload` can preload lazy code.

## Split route data from views

`#[lazy_route]` splits a `LazyRoute` into data and view halves (since 0.8.0).
Nested route data and lazy views load concurrently before navigation. Keep the
application and `cargo-leptos` versions compatible so the generated chunks and
route loading behavior agree.
