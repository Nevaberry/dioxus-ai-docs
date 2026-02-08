---
name: dioxus-knowledge-patch
description: This skill should be used when writing Dioxus code, building Rust web/desktop/mobile apps with Dioxus, using RSX macro, signals, server functions, or any Dioxus features from 0.5+ (2024-2026).
license: MIT
metadata:
  author: Nevaberry
  version: "0.7.3"
---

# Dioxus 0.5+ Knowledge Patch

Claude's baseline knowledge covers Dioxus through 0.4.x. This skill provides features from 0.5 (2024) onwards.

## Quick Reference

### Component Syntax (0.5+)

| Old (0.4) | New (0.5+) |
|-----------|------------|
| `fn App(cx: Scope) -> Element` | `fn App() -> Element` |
| `cx.use_hook()` | `use_signal()`, `use_memo()` |
| `use_state`, `use_ref` | `Signal<T>` (always Copy) |
| Per-platform launchers | `dioxus::launch(App)` |

### Signals

| Operation | Syntax |
|-----------|--------|
| Create | `let count = use_signal(\|\| 0);` |
| Read (subscribes) | `count.read()` or `count()` |
| Read (no subscribe) | `count.peek()` |
| Write | `count.write()`, `count.set(5)`, `count += 1` |
| Global | `static THEME: GlobalSignal<T> = GlobalSignal::new(\|\| ...)` |
| Mapped | `user.map(\|u\| &u.name)` |

See `references/signals-hooks.md` for hooks, effects, resources, coroutines.

### RSX Syntax

| Pattern | Example |
|---------|---------|
| Conditional | `if show { Header {} }` |
| Conditional attr | `class: if active { "active" }` |
| List with key | `for item in items { li { key: "{item.id}", ... } }` |
| Children prop | `fn Card(children: Element) -> Element` |
| Optional prop | `#[props(default)] disabled: bool` |
| Prop into | `#[props(into)] id: String` |

See `references/rsx-patterns.md` for attributes, events, prop spreading.

### Assets (0.6+)

```rust
const LOGO: Asset = asset!("/assets/logo.png");
const HERO: Asset = asset!("/hero.png", ImageAssetOptions::new()
    .format(ImageFormat::Avif).preload(true));
const STYLES: Asset = asset!("/app.css", CssAssetOptions::new().minify(true));
```

### Server Functions (0.7+)

| Feature | Syntax |
|---------|--------|
| Basic | `#[server] async fn get_data() -> Result<T>` |
| Route params | `#[get("/api/users/{id}")] async fn get_user(id: u32)` |
| Query params | `#[get("/search?query")] async fn search(query: String)` |
| Middleware | `#[server] #[middleware(AuthLayer)]` |
| Extractors | `async fn auth(headers: HeaderMap, cookies: Cookies)` |

See `references/fullstack.md` for WebSocket, SSR, streaming, server config.

### Router

```rust
#[derive(Routable, Clone, PartialEq)]
enum Route {
    #[route("/")]
    Home {},
    #[route("/user/:id")]
    User { id: u32 },
    #[route("/files/:..path")]     // Catch-all
    Files { path: Vec<String> },
}
```

See `references/router.md` for layouts, navigation, nested routes.

### CLI Commands

| Command | Purpose |
|---------|---------|
| `dx serve` | Dev server with hot-reload |
| `dx serve --platform ios` | iOS simulator |
| `dx build --release` | Production build |
| `dx bundle` | Package for distribution |
| `dx serve --wasm-split` | Route-based code splitting |

See `references/cli-desktop.md` for desktop config, platform args.

## Reference Files

| File | Contents |
|------|----------|
| `signals-hooks.md` | Signals, use_memo, use_effect, use_resource, context |
| `rsx-patterns.md` | RSX syntax, props, events, conditionals, lists |
| `fullstack.md` | Server functions, SSR, WebSocket, extractors |
| `router.md` | Routes, layouts, navigation, parameters |
| `cli-desktop.md` | CLI commands, desktop config, platforms |

## Critical Knowledge

### Element is Result (0.6+)

Use `?` anywhere - propagates to ErrorBoundary:

```rust
#[component]
fn Profile(id: u32) -> Element {
    let user = get_user(id)?;  // Early return on error
    rsx! { "{user.name}" }
}
```

### Suspense for Async

```rust
rsx! {
    SuspenseBoundary {
        fallback: |_| rsx! { "Loading..." },
        AsyncChild {}
    }
}

fn AsyncChild() -> Element {
    let data = use_resource(fetch_data).suspend()?;
    rsx! { "{data}" }
}
```

### Document Head

```rust
use dioxus::document::{Title, Link, Meta};

rsx! {
    Title { "My Page" }
    Meta { name: "description", content: "..." }
    Link { rel: "stylesheet", href: asset!("/style.css") }
}
```

### Stores for Nested State (0.7+)

```rust
#[derive(Store)]
struct AppState {
    users: BTreeMap<String, User>,
}

#[component]
fn UserList(state: Store<AppState>) -> Element {
    let users = state.users();
    rsx! {
        for (id, user) in users.iter() {
            UserRow { key: "{id}", user }  // Only changed items re-render
        }
    }
}
```

### CSS Modules (0.7.3+)

```rust
css_module!(Styles = "/styles.module.css", AssetOptions::css_module());

rsx! {
    div { class: Styles::container,  // Typed, compile-checked
        p { class: Styles::title, "Hello" }
    }
}
```

### Fullstack Server Setup

```rust
use axum::Router;
use dioxus::prelude::*;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .serve_static_assets("dist")
        .serve_dioxus_application(ServeConfig::new(), App);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

### Reactivity Gotchas

**Memos in attributes don't subscribe properly:**
```rust
// BAD: Won't update
let style = use_memo(move || format!("color: {}", color()));
rsx! { div { style: style } }

// GOOD: Direct signal read
rsx! { div { style: format!("color: {}", color()) } }
```

**Use individual CSS properties:**
```rust
// GOOD: Proper reactivity
rsx! {
    p {
        font_weight: if bold() { "bold" } else { "normal" },
        text_align: "{align}",
    }
}
```

### Hot-Reload Boundaries

**Instant reload:** Literal values, text, formatted segments, attribute order, template structure

**Requires rebuild:** Rust logic, component structure, control flow conditions, struct field changes
