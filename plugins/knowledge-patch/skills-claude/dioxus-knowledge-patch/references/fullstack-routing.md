# Fullstack, Server Functions, Routing, and WASM-Aware Navigation

## Fullstack feature boundary

The fullstack client and server are separate builds. Pair `dioxus/fullstack`
with `dioxus/web` for the browser and `dioxus/server` for the backend.

Native desktop and mobile clients can call server functions. Production native
builds must set a server URL because they have no browser origin.

## Building the Axum server

`dioxus::serve` accepts an async closure returning an Axum router.
`dioxus::server::router(app)` assembles static assets and `/public`, registered
server functions, and SSR as a fallback. Routes added to that router take
priority over the fallback. Import Axum through `dioxus::server::axum` so its
version matches Dioxus.

```rust
#[cfg(feature = "server")]
dioxus::serve(|| async move {
    use dioxus::server::axum::routing::post;
    Ok(dioxus::server::router(app)
        .route("/submit", post(|| async { "Form submitted" })))
});
```

For fine-grained assembly, `DioxusRouterExt` provides
`.register_server_functions()` and `.serve_static_assets()`, while
`RenderHandleState::new(config, app)` supplies SSR state. `ServerFunction::collect()`
iterates registrations and exposes each function's method and path, allowing a
router to register only a subset.

`dioxus::serve` replaced hand-started Axum servers in `0.7.0`, enabling the
router itself to hot-patch. That generation also permits a fullstack backend to
target `wasm32` hosts such as server-side-WASM platforms.

## Server-function route macros

Since `0.7.0`, `#[get]`, `#[post]`, and the other HTTP-method macros expose
stable routes with path (`{name}`) and query (`?age`) parameters. The body may
use valid Axum handler arguments and responses; server-only extractors do not
enter the client-callable function signature.

```rust
#[get("/api/{name}/?age")]
async fn greeting(name: String, age: i32) -> Result<String> {
    Ok(format!("Hello {name}, age {age}"))
}
```

The result alias here is Dioxus's `Result`, and the default encoding changed to
JSON with the Axum 0.8-based fullstack rewrite. Route queries use `serde_qs` since
`0.7.1`, so nested structs and sequences round-trip. Named and anonymous server
functions both support server-only `FromRequestParts`/`FromRequest` extractors
since `0.7.3`.

Bare `#[server]` generates an endpoint whose module/body/signature hash may
change. Use explicit HTTP macros for a native client released independently of
its backend. A custom wire format implements `Encoding` (`content_type`,
`encode`, and `decode`) and is selected with
`#[server(input = MyEncoding, output = MyEncoding)]`.

Calling a server function from backend code is supported: since `0.7.1`, absent
request context falls back to a blank `GET` request, and the caller's tracing
span propagates into the function.

Generated path/query parameters go through Axum `Path` and `Query` extraction,
so signatures may use extractor-compatible shapes such as `Option<T>`.

Annotate a single endpoint with `#[middleware]` to apply a Tower layer such as
auth or timeout only to its generated `MethodRouter`; use `.layer()` for the
whole Axum router.

## Lazy server globals

Dioxus's `Lazy<T>` is a global whose initializer is async. First dereference
blocks the current thread until it resolves, making it useful for a pool that
can be accessed synchronously without custom Axum state. The initializer
returns a result, so use `dioxus::Ok`.

```rust
static DATABASE: Lazy<sqlx::SqlitePool> = Lazy::new(|| async move {
    dioxus::Ok(
        sqlx::sqlite::SqlitePoolOptions::new()
            .connect("sqlite::memory:")
            .await?
    )
});
```

## Errors and HTTP status

`HttpError` carries a status and message. `OrHttpError` extends `Result<T>`,
`Option<T>`, and `bool`; named helpers include authorization cases and
`or_http_error(status, message)` handles arbitrary statuses. Dioxus downcasts a
bubbled error to recover an `HttpError`; an unrecognized error becomes 500.

```rust
#[post("/api/login")]
async fn login() -> Result<()> {
    authenticate().or_unauthorized("Login required")?;
    authorize().or_http_error(StatusCode::FORBIDDEN, "Forbidden")?;
    Ok(())
}
```

At the SSR root, an uncaught error sets the response status. Catching it in an
`ErrorBoundary` suppresses that automatic behavior; recommit it and render by
status:

```rust
handle_error: |ctx: ErrorContext| {
    let http = FullstackContext::commit_error_status(ctx.error().unwrap());
    match http.status {
        StatusCode::NOT_FOUND => rsx! { "404" },
        _ => rsx! { "Request failed" },
    }
}
```

Since `0.7.5`, an error from a `#[get]` endpoint passes through as the error
response instead of becoming a redirect.

## Error types across the wire

A server-side concrete `anyhow` error cannot retain its Rust type on the client.
An endpoint returning plain `Result<T>` arrives as `ServerFnError`, so client
downcasts to the original type fail. Return `ServerFnResult` or
`Result<T, ServerFnError>` when callers need to distinguish transport and server
failures. Important variants include `ServerError { message, code, details }`
and `Request(RequestError)`.

A custom error that crosses the wire must implement `Serialize`, `Deserialize`,
and `AsStatusCode`; it also needs `From<ServerFnError>` so request failures have
a representation.

## Forms and multipart uploads

Cancel the browser submission synchronously. `FormEvent::parsed_values::<T>()`
deserializes inputs by `name`; hand the result to an endpoint taking Axum's
`Form<T>`. Converting the event with `.into()` produces `MultipartFormData`,
whose server side is read field-by-field. Typed multipart is not available.

```rust
form {
    onsubmit: move |event: FormEvent| async move {
        event.prevent_default();
        let values: LoginForm = event.parsed_values().unwrap();
        login(Form(values)).await?;
        Ok(())
    },
    input { name: "username" }
}

#[post("/api/upload")]
async fn upload(mut form: MultipartFormData) -> Result<()> {
    while let Ok(Some(field)) = form.next_field().await {
        let bytes = field.bytes().await?;
        // persist bytes
    }
    Ok(())
}
```

## Streams and files

In the `0.5.0` API, streaming server functions selected an output codec in
`#[server(output = StreamingText)]` and returned `TextStream`. The current
family is the generic `Streaming<T, E>` with `TextStream` and `ByteStream`
aliases. Built-in encodings include JSON, CBOR, Postcard, and MessagePack.

`Streaming::spawn` supplies an `UnboundedSender`; stop when
`unbounded_send(item)` fails because the client disconnected.
`Streaming::new(stream)` wraps an existing stream, and consumers use ordinary
`StreamExt` combinators.

```rust
#[get("/api/dogs")]
async fn dogs() -> Result<Streaming<Dog, JsonEncoding>> {
    Ok(Streaming::spawn(|tx| async move {
        for age in 0..10 {
            if tx.unbounded_send(Dog { age }).is_err() { break; }
        }
    }))
}
```

`FileStream` is separate and streams through platform-native file support rather
than buffering. Construct one on the server with
`FileStream::from_path(path).await?`, or convert client `FileData` from an input
or drop event. It sets `Content-Disposition` and `X-Content-Size` headers.

## Custom request and response types

A custom server argument combines Axum `FromRequest` with Dioxus `IntoRequest`;
a custom return combines Axum `IntoResponse` with Dioxus `FromResponse`. The
Dioxus traits define how calling the function as Rust code on the client makes
the request and reconstructs the result.

Their carrier generic defaults to `ClientResponse` but can transfer request-time
state to the response conversion, as WebSocket upgrades do. For a third-party
Axum response without `FromResponse`, return `axum::response::Response` and call
`.into_response()` explicitly.

## WebSockets and server events

A server function may return
`Websocket<ClientMessage, ServerMessage, Encoding>`. On the client,
`use_websocket` starts the call; `.recv()` waits for connection establishment.
The server builds the upgrade from `WebSocketOptions::on_upgrade`.

The upgrade future runs on a Tokio `LocalSet`, so it need not be `Send`.
`send_raw` bypasses typed encoding for raw frames. Since `0.7.4`, the handle also
implements `futures::Stream` and `Sink`, enabling `next`, `split`, `forward`, and
`send_all`; earlier concurrent-borrow panics were replaced with errors.

Related server-function types include `ServerEvents<T>` for SSE,
`Streaming<T>` for arbitrary sequences, typed `Form<T>`,
`MultipartFormData`, and `FileStream`.

## SSR streaming and hydration

Out-of-order HTML streaming is off by default. Enable it with
`ServeConfig::enable_out_of_order_streaming()`. After
`commit_initial_chunk()`, response headers and status are frozen. The router
commits when the root suspense boundary resolves, so an error inside a later
nested boundary may render a 404 view but still return 200. Late `Title`, `Meta`,
or `Link` entries become client-only and are invisible to crawlers.

Use `use_server_cached` for synchronous nondeterminism such as timestamps and
`use_server_future` for async values. These closures must have no side effects
because the client skips them when hydration already contains the value.

## Server URL for native clients

The setter lives at `dioxus::fullstack::set_server_url`; the older
`server_fn::client::set_server_url` path moved. Call it before launch for a
desktop or mobile release.

### Repointing at runtime

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The server URL may be set more than once, allowing a native client to switch
backends at runtime instead of being permanently fixed at startup.

## Static and incremental generation

Since `0.6.0`, fullstack supports SSG. A server function named `static_routes`
returns the URLs and `dx build --web --ssg` emits them. SSG sits on incremental
static generation; on-demand filesystem caching must be enabled explicitly with
`IncrementalRendererConfig` in the serve configuration.

`Routable::SITE_MAP` exposes the route tree; `.flatten()` enumerates it and is a
useful source for fully static routes.

## Typed routing and matching

Derive `Routable`, render `Router::<Route> {}`, and use typed variants for
navigation. A variant normally renders the same-named component, but
`#[route("/about", AboutPage)]` selects another component.

Path matching uses specificity rather than enum order: query-bearing routes are
considered, then static path segments outrank dynamic segments, which outrank
catch-alls; ties use variant order. Dynamic fields require `FromStr + Display`.
Catch-alls use route-segment conversion traits. A failed path parse rejects that
variant and tries the next route.

Query (`?:field`) and hash (`#:field`) values differ: a missing or invalid value
defaults through `FromQueryArgument`/`FromHashFragment` instead of rejecting the
route. Query, hash, and catch-all segments cannot occur inside `#[nest]`.

Capture the entire query with `?:..field`; its type implements `From<&str>`
(`FromQuery`) and `Display`:

```rust
#[route("/search?:..query")]
Search { query: MyQuery },
```

Layouts render their child with `Outlet::<Route> {}`. `#[redirect]` accepts both
the path and a closure over that path's parameters, allowing a parameter rewrite
rather than only a fixed target.

## History and route updates

The router defaults to `MemoryHistory` on every platform. Select `WebHistory`,
hash history, or `LiveviewHistory` explicitly through `RouterConfig`. Browser
history does not reveal whether back/forward entries exist, so corresponding
buttons cannot reliably disable under `WebHistory` and may leave the app.

`RouterConfig::on_update` runs after routing state changes but before dependent
components update. Returning a `NavigationTarget` replaces the current location
without invoking the callback again. Navigation failures do not run it.

LiveView routing does not integrate with browser history. Because controlled
input events round-trip to the server, use a raw browser listener for latency-
sensitive input behavior.

## Router-driven split points

Since `0.7.0`, web route variants may use `#[wasm_split("/path")]` in place of
`#[route]`. Their code is downloaded on navigation and the router displays a
loading state. The underlying async-function splitting model and toolchain
constraints are covered in
[renderers-testing-internals.md](renderers-testing-internals.md).
