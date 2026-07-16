# Fullstack, Server Functions, Routing, and WASM-Aware Navigation

## Build targets and feature isolation

DX builds a Fullstack application twice: the client enables `web`, and the backend enables `server`. The `fullstack` feature alone is not a substitute for selecting each build side. A server-function body is server-only, but adjacent modules, constants, and native dependencies are not hidden automatically; gate them and their optional dependencies or secrets and native code may enter the browser bundle.

```toml
[dependencies]
tokio = { version = "1", optional = true }

[features]
web = ["dioxus/web"]
server = ["dioxus/server", "dep:tokio"]
```

```rust
#[cfg(feature = "server")]
mod backend {
    pub static DB_PASSWORD: &str = "...";
}
```

Server functions work from Desktop and Mobile clients as well as Web. Development native clients point to localhost; production native apps must call `server_fn::client::set_server_url(...)` with the deployed endpoint before launch. Native clients have no server render, hydration data, `FullstackContext`, HTML streaming, or SSG.

## Axum-native server composition

Since 0.7.0, Dioxus exposes `dioxus::serve` and route macros whose path and query fields map to handler arguments. Any valid Axum handler can serve as a server function, and JSON is the default codec.

```rust
#[get("/api/{name}/?age")]
async fn get_message(name: String, age: i32) -> Result<String> {
    Ok(format!("Hello {name}, you are {age} years old!"))
}
```

`dioxus::server::router(app)` assembles static-file serving, registered server functions, and the SSR fallback. Ordinary Axum routes added to that router take precedence over the fallback. Fully custom servers can use `DioxusRouterExt`, or iterate `ServerFunction::collect()` and call `register_server_fn_on_router` for selected functions.

```rust
#[cfg(feature = "server")]
dioxus::serve(|| async move {
    use dioxus::server::axum::routing::get;

    Ok(dioxus::server::router(app)
        .route("/health", get(|| async { "ok" })))
});
```

During development, the CLI reverse-proxies a custom Axum server. Bind it to `dioxus_cli_config::fullstack_address_or_localhost()` instead of a fixed address.

```rust
let address = dioxus_cli_config::fullstack_address_or_localhost();
let listener = tokio::net::TcpListener::bind(address).await?;
```

## Server state and authentication

Fullstack `Lazy<T>` initializes a static server resource through an async closure. It implements `Deref<Target = T>` and blocks the accessing thread until initialization completes; it is a concise alternative to plumbing Axum `State` or `Extension` through a custom entrypoint.

```rust
static DATABASE: Lazy<sqlx::SqlitePool> = Lazy::new(|| async move {
    dioxus::Ok(
        SqlitePoolOptions::new()
            .max_connections(5)
            .connect_with("sqlite::memory:".parse().unwrap())
            .await?,
    )
});
```

Dioxus Fullstack does not supply an authentication or session store. Resolve sessions in an Axum or Tower layer and place them in request extensions. Anonymous server functions gained server-only extractors in 0.7.3, so a session can be hoisted into macro parameters without entering the client payload.

```rust
#[post("/api/user/login", auth: auth::Session)]
pub async fn login() -> Result<()> {
    auth.login_user(2);
    Ok(())
}
```

## Forms and request bodies

### Typed forms

An endpoint can accept a Serde value in Axum `Form<T>`. `FormEvent::parsed_values()` constructs the same type from controls whose `name` values match its fields. GET forms expose their values in the URL; use POST for structured or sensitive data.

```rust
#[derive(Serialize, Deserialize)]
struct LoginForm {
    username: String,
    password: String,
}

#[post("/api/login")]
async fn login(form: Form<LoginForm>) -> Result<()> {
    Ok(())
}

onsubmit: move |event: FormEvent| async move {
    event.prevent_default();
    let values: LoginForm = event.parsed_values().unwrap();
    _ = login(Form(values)).await;
}
```

Web forms submit normally unless the handler synchronously calls `prevent_default()`. Do that before the first `.await`.

### Multipart uploads

Converting `FormEvent` into `MultipartFormData` retains file parts. The server consumes fields asynchronously through `next_field()`. Multipart data is untyped in this API, so inspect names, filenames, MIME types, and bytes manually.

```rust
#[post("/api/upload")]
async fn upload(mut form: MultipartFormData) -> Result<()> {
    while let Ok(Some(field)) = form.next_field().await {
        let name = field.name().unwrap_or("<none>").to_string();
        let bytes = field.bytes().await?;
        store(name, bytes).await?;
    }
    Ok(())
}
```

### Custom transports

Inputs can be multiple Serde values or one body implementing Axum `FromRequest` plus Dioxus `IntoRequest`. Outputs can be Serde values or implement Axum `IntoResponse` plus Dioxus `FromResponse`. If a third-party output lacks the client trait, convert it and return erased `axum::response::Response`.

```rust
#[get("/api/video", range: RangeHeader)]
async fn video_endpoint() -> Result<axum::response::Response> {
    Ok(get_chunk_from_range(range).into_response())
}
```

Fullstack endpoints also support middleware, redirects, request and response headers, captured status, and custom `Transport` implementations.

## Errors and HTTP semantics

The prelude `Result<T>` aliases `anyhow::Result<T>`. A concrete server error is erased at the client into Dioxus `ServerFnError`; an error without a recognized HTTP representation defaults to status 500. Use `ServerFnError` to distinguish transport from server failure, `OrHttpError` for an inline status, or a Serde error implementing `AsStatusCode` and `From<ServerFnError>` for a stable domain contract.

```rust
#[post("/api/private")]
async fn private_data() -> Result<()> {
    authorize()
        .or_http_error(StatusCode::UNAUTHORIZED, "Log in first!")?;
    Ok(())
}
```

Error responses from `#[get]` server functions are returned as failures rather than redirects as of 0.7.5.

An uncaught render error propagates its status to the SSR response. Handling it in `ErrorBoundary` stops that propagation; the fallback must call `FullstackContext::commit_error_status` if the response should retain the captured status.

```rust
ErrorBoundary {
    handle_error: move |error: ErrorContext| {
        let http_error =
            FullstackContext::commit_error_status(error.error().unwrap());
        rsx! { "Request failed: {http_error:?}" }
    },
    Outlet::<Route> {}
}
```

## Hydration, suspense, and streamed HTML

Hydration reruns every component on the client, so the tree must exactly match the server output. Put synchronous nondeterminism in `use_server_cached`, asynchronous nondeterminism in a server future or loader, and client-only reads in `use_effect`. Server-cached and server-future closures must have no side effects because the client may deserialize the result without running them.

`SuspenseBoundary` can stream server-rendered boundary chunks as futures resolve. A Fullstack suspended resource should use `use_server_future`; only the outer closure is reactive, so read dependencies there.

Out-of-order streaming is opt-in with `ServeConfig::enable_out_of_order_streaming`. Normally the router waits for suspense above it and calls `commit_initial_chunk()`. After the first commit, response headers and status cannot change. Head elements emitted in later chunks are installed only after hydration and are invisible to crawlers or no-JavaScript clients.

## Typed streams and files

### General streams

Server functions have supported bidirectional streaming since 0.5.0. `Streaming<T, E>` serializes each item through an `Encoding`; built-ins include JSON, CBOR, Postcard, and MessagePack. `TextStream` and `ByteStream` specialize strings and raw bytes. `Streaming::spawn` supplies an unbounded sender, while `Streaming::new` adapts an existing futures `Stream`.

```rust
#[get("/api/numbers")]
async fn numbers() -> Result<Streaming<u32, JsonEncoding>> {
    Ok(Streaming::spawn(|tx| async move {
        for number in 0..10 {
            if tx.unbounded_send(number).is_err() {
                break;
            }
        }
    }))
}
```

The older output-codec form remains useful context for migrations:

```rust
#[server(output = StreamingText)]
async fn updates() -> Result<TextStream, ServerFnError> {
    Ok(TextStream::new(make_stream()))
}
```

### File streams

`FileStream` is distinct from `Streaming<T, E>` and transfers native paths without buffering the full file. Create one with `FileStream::from_path(...).await` or convert browser `FileData` for upload. It carries `Content-Disposition` and `X-Content-Size`. Since 0.7.2, `FileStream::from_response` rejects unsuccessful HTTP status codes instead of treating their bodies as ordinary file bytes.

```rust
#[get("/api/download")]
async fn download() -> Result<FileStream> {
    Ok(FileStream::from_path(file!()).await?)
}
```

### Typed WebSockets

A WebSocket server function receives `WebSocketOptions` and returns `Websocket<In, Out, Encoding>`. Its `on_upgrade` future runs on a Tokio `LocalSet` and need not be `Send`. WebSocket handles implement standard stream and sink interfaces since 0.7.4.

Calling the function opens the client connection directly. `use_websocket` adds reactive connection status plus `send` and `recv`; replacing its value through `.set()` restarts a failed connection.

```rust
#[get("/api/echo")]
async fn echo(options: WebSocketOptions) -> Result<Websocket> {
    Ok(options.on_upgrade(|mut socket| async move {
        while let Ok(message) = socket.recv().await {
            _ = socket.send(message).await;
        }
    }))
}

let mut socket = use_websocket(|| echo(WebSocketOptions::new()));
```

## Static and incremental generation

A Fullstack app can expose a JSON `static_routes` server function and run `dx build --platform web --ssg`. SSG uses the experimental incremental-generation path, so the server must build `ServeConfig` with `.incremental(IncrementalRendererConfig::new())`. ISG renders uncached routes on demand and stores them on disk.

```rust
#[server(endpoint = "static_routes", output = server_fn::codec::Json)]
async fn static_routes() -> Result<Vec<String>, ServerFnError> {
    Ok(Route::static_routes()
        .into_iter()
        .map(|route| route.to_string())
        .collect())
}
```

```sh
dx build --platform web --ssg
```

Static generation should expand only fully static entries from `Routable::SITE_MAP`. SSG preserves HTTPS while processing static routes in 0.8.0-alpha.0.

## Typed routing

### Routable enums

`#[derive(Routable)]` parses and formats URLs and dispatches a route variant to an in-scope component of the same name. A second `#[route]` argument can select a different component. Mount `Router::<Route> {}` and navigate with typed variants instead of unchecked strings.

```rust
#[derive(Clone, PartialEq, Routable)]
enum Route {
    #[route("/")]
    Home,
    #[route("/post/:id")]
    Post { id: u64 },
}

fn App() -> Element {
    rsx! { Router::<Route> {} }
}
```

### Segment grammar and precedence

- `:id` dynamic path fields use `FromStr + Display` and fall through on parse failure.
- A final `:..parts` catch-all uses `Vec<String>` or the route-segment traits.
- `?:page&:sort` captures named query values; `?:..query` captures the remainder.
- `#:section` captures a hash value.
- Missing or malformed typed query/hash values default rather than reject the route.
- Static paths outrank dynamic paths, which outrank catch-alls; enum order breaks ties.

### Nests, layouts, and redirects

`#[nest("/prefix")]` prefixes routes until `#[end_nest]`. Nests cannot contain query or catch-all segments. A dynamic nest field is passed to every child route and layout. Layouts render children at `Outlet::<Route> {}` and may receive route fields or call `use_route`. `#[redirect]` parses a source path and returns a `NavigationTarget`.

```rust
#[derive(Clone, PartialEq, Routable)]
enum Route {
    #[nest("/settings")]
        #[route("/")]
        Settings,
        #[route("/privacy")]
        Privacy,
    #[end_nest]
}
```

### Navigation and history

`Link` and `Navigator::{push, replace}` accept `NavigationTarget`, either a typed internal route or external URL. The navigator also moves backward and forward. Histories exist for memory, LiveView, and browser URLs; Dioxus Web also supports hash history. Configure the provider explicitly when URL behavior matters because the nominal default is `MemoryHistory` and platform feature selection is not guaranteed.

`RouterConfig::on_update` runs after router state changes but before dependent hooks/components update. Returning a target replaces the location without recursively calling the callback; navigation failures bypass it. Native UIs can render `GoBackButton` and `GoForwardButton`. `WebHistory` cannot reliably disable them at history boundaries and can leave the app's history entries.

LiveView can render a router, but its history is not synchronized to browser history like `WebHistory`.

### Sitemap enumeration and split routes

`Routable::SITE_MAP` exposes the static/dynamic route tree; `.flatten()` produces a tooling-friendly list. Static generation must expand only all-static paths.

Web routes can use `#[wasm_split]` so a variant is emitted into its own chunk. The router fetches it on first navigation and displays a loading state. Split files have content-hashed names as of 0.7.6, so changed code receives a new cache key.

```rust
#[derive(Routable, Clone, PartialEq)]
enum Route {
    #[route("/")]
    Home,
    #[wasm_split("/dashboard")]
    Dashboard,
}
```

## Durable native endpoints

Anonymous `#[server]` functions use generated, code-dependent URLs. Desktop and Mobile clients can outlive a particular server build, so expose explicit method routes and evolve them through optional arguments or versioned paths.

```rust
#[post("/api/v1/do_it")]
async fn do_it(name: Option<String>) -> Result<()> {
    Ok(())
}
```
