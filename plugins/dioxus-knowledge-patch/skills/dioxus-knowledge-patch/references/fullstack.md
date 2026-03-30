# Fullstack & Server Functions

## Server Functions (0.7+)

### Axum-Style Routing

New syntax with typed path/query params:

```rust
#[get("/api/users/{id}?include_posts")]
async fn get_user(id: u32, include_posts: bool) -> Result<User> {
    // Path param: {id}, Query param: ?include_posts
    Ok(fetch_user(id, include_posts).await?)
}
```

### Basic Server Function

```rust
#[server]
async fn get_data() -> Result<Vec<Item>, ServerFnError> {
    // Runs on server, auto-RPC from client
    Ok(db::get_items().await?)
}
```

### WebSocket Support

Built-in WebSocket with typed messages:

```rust
#[get("/ws/chat")]
async fn chat_ws(opts: WebSocketOptions) -> Result<Websocket<ClientMsg, ServerMsg>> {
    Ok(opts.on_upgrade(|mut socket| async move {
        while let Ok(msg) = socket.recv().await {
            socket.send(ServerMsg::Echo(msg)).await;
        }
    }))
}

// Client side
fn Chat() -> Element {
    let socket = use_websocket(|| chat_ws(WebSocketOptions::new()));
    use_future(move || async move {
        while let Ok(msg) = socket.recv().await { /* handle */ }
    });
    rsx! { button { onclick: move |_| socket.send(ClientMsg::Hello), "Send" } }
}
```

### WebSocket Stream/Sink Split (0.7.4+)

`TypedWebsocket` implements `Stream + Sink`, enabling concurrent read/write via `.split()`:

```rust
#[get("/api/ws")]
async fn handle_ws(opts: WebSocketOptions) -> Result<Websocket<Msg, Msg>> {
    Ok(opts.on_upgrade(|mut socket| async move {
        let (mut sender, mut receiver) = socket.split();
        tokio::spawn(async move {
            while let Some(Ok(msg)) = receiver.next().await { /* read */ }
        });
        sender.send(Msg::Hello).await;
    }))
}
```

### Other Fullstack Types

- `ServerEvents<T>` - Server-sent events
- `Streaming<T>` - Arbitrary data streams
- `Form<T>`, `MultipartFormData` - Form handling
- `FileStream` - Upload/download streaming

### Server Extractors

Access request data in server functions:

```rust
use axum::http::HeaderMap;
use dioxus::fullstack::prelude::*;

#[server]
async fn auth_check(headers: HeaderMap, cookies: Cookies) -> Result<User> {
    let token = headers.get("Authorization").ok_or(ServerFnError::new("No auth"))?;
    let session = cookies.get("session_id");
    // validate...
}
```

### Middleware on Server Functions

Apply Tower middleware layers:

```rust
#[server]
#[middleware(AuthLayer::new())]
async fn protected_endpoint() -> Result<String> {
    Ok("authenticated".into())
}
```

## SSR and Hydration

### use_server_future for SSR

Data fetched on server, cached for hydration on client:

```rust
fn UserProfile(id: u32) -> Element {
    let user = use_server_future(move || async move {
        get_user(id).await // runs on server during SSR, cached for client
    })?;
    rsx! { "{user.name}" }
}
```

### Response Customization

Set headers/status from server functions:

```rust
#[server]
async fn custom_response() -> Result<String> {
    let ctx = FullstackContext::current()?;
    ctx.response_headers().insert("X-Custom", "value".parse()?);
    ctx.set_status_code(StatusCode::CREATED);
    Ok("created".into())
}
```

## Server Setup

### Axum Integration

Set up fullstack server with `DioxusRouterExt`:

```rust
use axum::Router;
use dioxus::prelude::*;

#[tokio::main]
async fn main() {
    let app = Router::new()
// Serve static assets from /public
.serve_static_assets("dist")
// Full SSR + hydration + server functions
.serve_dioxus_application(ServeConfig::new(), App)
// Or just server functions (API only)
// .register_server_functions()
;

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

### ServeConfig Options

```rust
ServeConfig::new()
    .index_html(custom_html) // Custom index.html template
    .streaming_mode(StreamingMode::OutOfOrder) // Streaming SSR
    .incremental(IncrementalConfig::default()) // ISR caching
```

## Launch Patterns

### Conditional Compilation for Server/Client

```rust
fn main() {
    #[cfg(feature = "server")]
    dioxus::LaunchBuilder::server().launch(App);

    #[cfg(feature = "web")]
    dioxus::LaunchBuilder::web().launch(App);
}
```

### Platform-Specific Launchers

```rust
// Simple (auto-detects platform)
dioxus::launch(App);

// Explicit platform
dioxus::LaunchBuilder::desktop().launch(App);
dioxus::LaunchBuilder::web().launch(App);
dioxus::LaunchBuilder::server().launch(App);
```

## Static Site Generation (0.6+)

Generate static HTML at build time:

```rust
#[server]
async fn static_routes() -> Vec<String> {
    vec!["/", "/about", "/blog/post-1"]
}
```

```bash
dx build --ssg
```

## WASM Bundle Splitting (0.7+)

Route-based lazy loading for smaller initial bundles:

```bash
dx serve --wasm-split
```

Define split points with `#[wasm_split]` (must be async):

```rust
use dioxus::prelude::*;

// This code loads separately when called
#[wasm_split(admin)]
async fn load_admin_panel() -> Element {
    rsx! { AdminDashboard {} }
}

// Use in routes - panel code not in initial bundle
fn App() -> Element {
    let route = use_route();
    match route {
        Route::Admin => {
            let panel = load_admin_panel().await;
            panel
        }
        _ => rsx! { Home {} },
    }
}
```

Split points must be async functions. The macro generates lazy loaders that fetch the WASM chunk on first call.
