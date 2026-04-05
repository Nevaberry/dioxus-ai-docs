# Server Functions

WebSocket support, custom error types, encoding options, and server function enhancements.

## WebSocket Server Functions (0.8.0+)

Server functions can accept and return `BoxedStream` with `Websocket` protocol:

```rust
use server_fn::{BoxedStream, ServerFnError, Websocket, codec::JsonEncoding};

#[server(protocol = Websocket<JsonEncoding, JsonEncoding>)]
async fn echo_websocket(
    input: BoxedStream<String, ServerFnError>,
) -> Result<BoxedStream<String, ServerFnError>, ServerFnError> {
    use futures::{SinkExt, StreamExt, channel::mpsc};
    let (mut tx, rx) = mpsc::channel(1);
    tokio::spawn(async move {
        while let Some(msg) = input.next().await {
            tx.send(msg.map(|s| s.to_ascii_uppercase())).await;
        }
    });
    Ok(rx.into())
}
```

Client-side usage:

```rust
if cfg!(feature = "hydrate") {
    spawn_local(async move {
        match echo_websocket(rx.into()).await {
            Ok(mut messages) => {
                while let Some(msg) = messages.next().await {
                    latest.set(Some(msg));
                }
            }
            Err(e) => leptos::logging::warn!("{e}"),
        }
    });
}
```

Different error types for input and output streams are supported. WebSocket protocol respects custom server URL as of 0.8.16.

## Custom Error Types (0.8.0+)

Server functions now use `FromServerFnError` trait instead of being constrained to `ServerFnError`. Implement `FromServerFnError` for custom error types. The `extract()` helper uses `ServerFnErrorErr`.

## Aliased Result Types (0.8.0+)

```rust
type MyResult<T> = Result<T, MyError>;

#[server]
async fn my_fn() -> MyResult<String> { ... }
```

## Bitcode Encoding (0.8.11+)

Binary encoding for server function I/O using `bitcode`:

| Version | Variant |
|---|---|
| 0.8.11 | Raw `bitcode` encoding/decoding |
| 0.8.17 | `bitcode` serde integration codec (uses serde layer) |

## Lazy Server Functions (0.8.6+)

`#[server]` and `#[lazy]` can be combined:

```rust
#[server]
#[lazy]
async fn heavy_server_fn() -> Result<String, ServerFnError> {
    // This function's client-side code is lazy-loaded
    Ok("result".into())
}
```

## Route Generation Options (0.8.0+)

More options for generating server function routes.

## Additional HTTP Methods (0.8.0+)

Beyond GET/POST, additional HTTP methods are now supported in server function codecs.

## Actix Multipart Support (0.7.1+)

Multipart form handling implemented for Actix integration, enabling file upload server functions.

## Server Function Error Fixes

| Version | Fix |
|---|---|
| 0.8.8 | Error responses now set correct `Content-Type` header |
| 0.8.11 | `server_fn` feature flags propagate correctly |
| 0.8.16 | `#[expect]` lint attribute in server fn macro works |
| 0.8.17 | Lint attributes applied to both original and generated function |

## Multiple Middleware (0.8.3+)

Multiple `#[middleware]` macros on the same route handler now work correctly.
