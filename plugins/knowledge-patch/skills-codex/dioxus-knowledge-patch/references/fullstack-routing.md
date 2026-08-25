# Fullstack, Server Functions, Routing, and Navigation

Use this reference for Fullstack feature isolation, Axum composition, endpoint
types, authentication, forms, errors, SSR and hydration, streams, file
transfers, WebSockets, routing, history, SSG, and native clients.

## Fullstack target isolation

DX builds a Fullstack app twice: the client enables `web`, while the backend
enables `server`. A server-function body runs only on the server, but adjacent
constants, modules, secrets, and native dependencies are not hidden
automatically. Gate both code and optional dependencies.

```toml
[dependencies]
tokio = { version = "1", optional = true }

[features]
web = ["dioxus/web"]
server = ["dioxus/server", "dep:tokio"]
```

Server functions have worked from Desktop and Mobile clients since 0.6.0.
Development points native clients at localhost; production must set the
deployed server URL before launch.

## Axum server composition

Since 0.7.0, `dioxus::serve` and the method route macros map path and query
parameters into handler arguments. Any valid Axum handler can serve as a
server function, and JSON is the default codec.

```rust
#[get("/api/{name}/?age")]
async fn get_message(name: String, age: i32) -> Result<String> {
    Ok(format!("Hello {name}, you are {age} years old!"))
}
```

`dioxus::server::router(app)` assembles static files, collected server
functions, and the SSR fallback. Ordinary Axum routes added to it take
precedence over the fallback.

```rust
#[cfg(feature = "server")]
dioxus::serve(|| async move {
    use dioxus::server::axum::routing::get;
    Ok(dioxus::server::router(app)
        .route("/health", get(|| async { "ok" })))
});
```

For a fully custom setup, use `DioxusRouterExt`, or iterate
`ServerFunction::collect()` and call `register_server_fn_on_router` for only the
desired endpoints.

During development, the CLI reverse-proxies a custom server. Bind it to
`dioxus_cli_config::fullstack_address_or_localhost()` rather than a fixed
address. The former `dioxus/axum` feature is now `dioxus/server`.

### Async server globals

Fullstack `Lazy<T>` initializes a static through an async closure, implements
`Deref<Target = T>`, and blocks an accessing thread until initialization
finishes. Use it as a concise alternative to threading Axum `Extension` or
`State<T>` through a custom entrypoint.

## Authentication and server-only extractors

Dioxus does not supply authentication or a session store. Use an Axum or Tower
layer to resolve the session and insert it into request extensions. Anonymous
server functions have accepted server-only extractors since 0.7.3, so an
extension can be hoisted into the macro arguments without entering the client
payload.

```rust
#[post("/api/user/login", auth: auth::Session)]
pub async fn login() -> Result<()> {
    auth.login_user(2);
    Ok(())
}
```

## Forms and multipart uploads

### Typed forms

An endpoint accepts a Serde payload through Axum `Form<T>`.
`FormEvent::parsed_values()` constructs the same type from controls whose
`name` attributes match fields. Prefer POST for structured data because GET
puts form values in the URL.

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
```

Web form submission is allowed by default in the current stable behavior. Call
`event.prevent_default()` synchronously in `onsubmit` before awaiting a server
function. Desktop blocks page navigation separately.

### Multipart forms

Convert a `FormEvent` into `MultipartFormData` to retain files. Multipart
payloads are untyped: consume `next_field()` asynchronously and inspect each
field's name, filename, content type, and bytes.

```rust
#[post("/api/upload")]
async fn upload(mut form: MultipartFormData) -> Result<()> {
    while let Ok(Some(field)) = form.next_field().await {
        let name = field.name().unwrap_or("<none>").to_string();
        let bytes = field.bytes().await?;
        // Store `bytes` under `name`.
    }
    Ok(())
}
```

## Errors and HTTP semantics

The prelude `Result<T>` is `anyhow::Result<T>`. Its concrete server error is
erased at the client into Dioxus `ServerFnError`; an error without a recognized
HTTP representation defaults to status 500.

- Use `ServerFnError` to distinguish transport from server failures.
- Use `OrHttpError` to attach a status inline.
- For a stable domain contract, use a Serde error implementing `AsStatusCode`
  and `From<ServerFnError>`.
- Since 0.7.5, errors from `#[get]` functions remain errors rather than being
  converted into redirects.

```rust
#[post("/api/private")]
async fn private_data() -> Result<()> {
    authorize()
        .or_http_error(StatusCode::UNAUTHORIZED, "Log in first!")?;
    Ok(())
}
```

An uncaught render error automatically contributes its status to SSR. If an
`ErrorBoundary` catches it, the fallback must call
`FullstackContext::commit_error_status` to recommit that status.

### Preview response-body failures

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

Failures while reading a response body propagate to the caller. Consumers must
handle those errors instead of assuming successful body materialization.

## Custom endpoint transports

Inputs may be a group of Serde values or one body implementing Axum
`FromRequest` plus Dioxus `IntoRequest`. Outputs may be Serde values or types
implementing Axum `IntoResponse` plus Dioxus `FromResponse`. If a third-party
Axum result lacks the client trait, convert it and return an erased
`axum::response::Response`.

```rust
#[get("/api/video", range: RangeHeader)]
async fn video_endpoint() -> Result<axum::response::Response> {
    Ok(get_chunk_from_range(range).into_response())
}
```

Fullstack endpoints have supported redirects, middleware, custom transports,
headers, status capture, and typed status-bearing errors since 0.7.0.

## Hydration, suspense, streaming, and SSG

### Deterministic hydration

Hydration reruns the component tree in the client, so its rendered tree must
match the server exactly. Put synchronous nondeterminism in
`use_server_cached`, async nondeterminism in a server future or loader, and
browser-only reads in `use_effect`. Server-cached and server-future closures
must be side-effect-free because hydration may deserialize their result without
executing them.

### Streaming commit boundary

Out-of-order HTML streaming is opt-in with
`ServeConfig::enable_out_of_order_streaming`. The router normally waits for
suspense above it and calls `commit_initial_chunk()`. After the first chunk,
response headers and status are frozen. Head elements discovered in later
chunks are installed only after hydration and are invisible to crawlers and
no-JavaScript clients.

Suspense boundaries and streamed boundary chunks have existed since 0.6.0.
Fullstack control added in 0.7.0 makes the router and enclosing suspense
boundary part of the initial commit decision.

### Static and incremental generation

The 0.6.0 SSG path exposes a JSON `static_routes` server function and builds
with:

```sh
dx build --platform web --ssg
```

It is built on the experimental incremental renderer. Configure
`IncrementalRendererConfig`; uncached ISG routes render on demand and are
stored on disk. Use `Routable::SITE_MAP.flatten()` for route tooling, but
expand only fully static entries into SSG routes.

### Preview HTTPS SSG behavior

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

SSG preserves HTTPS while processing static routes instead of treating their
URLs as HTTP.

## Typed streams, files, and WebSockets

### Typed streams

The original 0.5.0 streaming server function selected `StreamingText` and
returned a `TextStream`. The current `Streaming<T, E>` encodes each item;
built-ins include JSON, CBOR, Postcard, and MessagePack, with `TextStream` and
`ByteStream` specializations. `Streaming::spawn` supplies an unbounded sender,
and `Streaming::new` adapts an existing futures `Stream`.

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

### File streams

`FileStream` uses native paths rather than buffering a whole file. Construct it
with `FileStream::from_path(...).await` or convert browser `FileData` for an
upload; it carries `Content-Disposition` and `X-Content-Size`. Since 0.7.2,
`FileStream::from_response` checks the HTTP status and rejects unsuccessful
responses.

### Typed WebSockets

A WebSocket function takes `WebSocketOptions` and returns
`Websocket<In, Out, Encoding>`. Its upgrade future runs on a Tokio `LocalSet`
and need not be `Send`. Calling it creates the client connection;
`use_websocket` adds reactive status, `send`, and `recv`, and `.set()` restarts
a failed connection. WebSocket handles also implement stream and sink traits
since 0.7.4.

```rust
#[get("/api/echo")]
async fn echo(options: WebSocketOptions) -> Result<Websocket> {
    Ok(options.on_upgrade(|mut socket| async move {
        while let Ok(message) = socket.recv().await {
            _ = socket.send(message).await;
        }
    }))
}
```

## Native-client compatibility

Native clients support server functions, files, streams, and WebSockets but
not server rendering, hydration payloads, `FullstackContext`, HTML streaming,
or SSG. Anonymous `#[server]` functions receive generated, code-dependent
URLs, so durable native clients should use explicit method routes and evolve
them with optional arguments or versioned paths.

```rust
#[post("/api/v1/do_it")]
async fn do_it(name: Option<String>) -> Result<()> {
    Ok(())
}
```

### Preview repeated endpoint configuration

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The Fullstack server URL may be set more than once; a later configuration can
replace or repeat an earlier endpoint assignment.

## Typed routing

### Routable enums

`#[derive(Routable)]` parses and formats URLs and dispatches each `#[route]`
variant to an in-scope component of the same name; a second route argument can
select another component. Mount `Router::<Route> {}` and navigate with typed
variants.

```rust
#[derive(Clone, PartialEq, Routable)]
enum Route {
    #[route("/")]
    Home,
    #[route("/post/:id")]
    Post { id: u64 },
}
```

### Segment grammar and precedence

- `:id` uses `FromStr + Display` and falls through if parsing fails.
- Final `:..parts` catch-alls use `Vec<String>` or route-segment traits.
- `?:page&:sort` and `?:..query` capture query data; `#:section` captures a
  hash.
- Missing or malformed typed query/hash values default rather than reject the
  route.
- Path precedence is static, dynamic, then catch-all; enum order breaks ties.

Web base-path resolution has trimmed surrounding slashes since 0.7.2.

### Nests, layouts, and redirects

`#[nest("/prefix")]` prefixes variants through `#[end_nest]`. A nest cannot
contain catch-all or query segments. Dynamic nest fields are passed to every
child route and layout. Layouts render `Outlet::<Route> {}` and can receive
those fields or call `use_route`. `#[redirect]` maps a path and parsed
parameters to a `NavigationTarget`.

### Preview child URL preservation

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

Child routes preserve query and hash segments instead of dropping those URL
fragments.

## Navigation and history

`Link` and `Navigator::{push, replace}` accept `NavigationTarget`, which may be
a typed route or external URL. The navigator also moves backward and forward.
Histories exist for memory, LiveView, browser paths, and browser hashes.
Hash-history support arrived in 0.7.0 for static hosts that cannot provide path
fallbacks.

Configure the history provider explicitly when URL behavior matters; the
nominal default is `MemoryHistory`, and feature selection does not guarantee
browser history. LiveView routing does not synchronize route state with browser
history.

`RouterConfig::on_update` runs after router state changes but before dependent
components update. Returning a target replaces the location without invoking
the callback again; failures bypass it. Native apps can render `GoBackButton`
and `GoForwardButton`, but `WebHistory` cannot reliably disable them at history
boundaries and can leave the app's history.

### Preview external-navigation interception

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

Applications can opt into a handler for external URLs and intercept or
customize navigation that leaves the app.
