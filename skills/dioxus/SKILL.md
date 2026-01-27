---
name: Dioxus
description: This skill should be used when asking about "Dioxus", "dioxus framework", "Rust UI framework", "RSX macro", "dioxus components", "dioxus signals", "hot reload in Dioxus", "WASM splitting", "wasm_split macro", "Manganis assets", "asset! macro", "dioxus Stores", "nested reactivity", "dioxus renderers", "WriteMutations", or when working on a Rust web/UI project using Dioxus.
version: 0.7.3
---

# Dioxus 0.7.3 Knowledge Patch

Claude's baseline knowledge covers Dioxus through 0.6.3. This skill provides 0.7.3 features.

## Quick Reference

### New in 0.7.3

| Feature | Description |
|---------|-------------|
| Subsecond Hot-Patching | Full Rust code hot-reload via jump table |
| WASM Splitting | Lazy-load chunks for faster initial load |
| Manganis Assets | `asset!()` macro with optimization & cache-busting |
| Stores | Nested reactivity with path-based subscriptions |

### Subsecond Hot-Patching

Full Rust hot-reload without restart. Functions called through jump table that gets patched.

```rust
// Standard Dioxus - automatic
fn main() {
    dioxus::launch(app);
}

// Non-Dioxus apps
fn main() {
    dioxus_devtools::connect_subsecond();
    loop {
        dioxus_devtools::subsecond::call(|| handle_request());
    }
}
```

**Limitations:** No struct changes (size/alignment), thread-locals reset, only tip crate patches.

See `references/subsecond-hotpatch.md`.

### WASM Code Splitting

Split large WASM binaries into lazy-loaded chunks.

```rust
#[wasm_split(admin_panel)]
async fn load_admin_panel() -> AdminPanel {
    AdminPanel::new()  // In separate module_admin_panel.wasm
}

async fn handle_route(route: Route) {
    if let Route::Admin = route {
        let panel = load_admin_panel().await;
        panel.render();
    }
}
```

**Key points:** Split points must be async, memory shared, requires `--emit-relocs`.

See `references/wasm-split.md`.

### Manganis Assets

Compile-time asset management with optimization.

```rust
let img = asset!("/assets/image.png");
let css = asset!("/assets/style.css", AssetOptions::css().minified());

rsx! {
    img { src: "{img}" }
    link { rel: "stylesheet", href: "{css}" }
}
```

**CSS Modules:**
```rust
css_module!(Styles = "/my.module.css", AssetOptions::css_module());
rsx! { div { class: Styles::header } }
```

See `references/manganis-assets.md`.

### Stores (Nested Reactivity)

Granular path-based subscriptions for nested data.

| Scenario | Use |
|----------|-----|
| Scalar state | Signal |
| Nested structures with granular updates | Store |

```rust
#[derive(Store, Clone)]
struct TodoItem {
    checked: bool,
    contents: String,
}

let store = Store::new(TodoItem { checked: false, contents: "Buy milk".into() });

// Subscribe only to `checked` field
let checked = store.checked();
rsx! { input { checked: checked.read() } }

// Changing `contents` won't re-render above
store.contents().set("Buy eggs".into());
```

See `references/stores-signals.md`.

### Renderers

| Renderer | Package | Use Case |
|----------|---------|----------|
| Web | dioxus-web | WASM/browser via Sledgehammer JS |
| Desktop | dioxus-desktop | Wry/Tao webview |
| Native | dioxus-native | Blitz/Vello GPU (not a browser) |
| LiveView | dioxus-liveview | WebSocket streaming |
| SSR | dioxus-ssr | Server-side HTML rendering |

All implement `WriteMutations` trait.

See `references/renderers.md`.

## Workspace Structure

```
packages/
├── dioxus/           # Main re-export crate
├── core/             # VirtualDOM, components, diffing
├── rsx/              # RSX macro parsing
├── signals/          # Reactive state (Signal, Memo, Store)
├── hooks/            # Built-in hooks
├── router/           # Type-safe routing
├── fullstack/        # SSR, hydration, #[server]
├── cli/              # `dx` build tool
├── web/              # WASM renderer
├── desktop/          # Wry/Tao webview
├── native/           # Blitz/Vello GPU renderer
├── liveview/         # WebSocket streaming
├── manganis/         # asset!() macro
├── subsecond/        # Hot-patching system
└── wasm-split/       # WASM code splitting
```

## Patterns (Unchanged from 0.5-0.6)

**Components:**
```rust
#[component]
fn MyComponent(name: String) -> Element {
    let mut count = use_signal(|| 0);
    rsx! { button { onclick: move |_| count += 1, "{name}: {count}" } }
}
```

**Server Functions:**
```rust
#[server]
async fn get_data(id: i32) -> Result<Data, ServerFnError> {
    // Runs on server, auto-RPC from client
}
```

**Routing:**
```rust
#[derive(Routable, Clone)]
enum Route {
    #[route("/")]
    Home {},
    #[route("/blog/:id")]
    Blog { id: usize },
}
```

## Architecture

- **WriteMutations**: Trait all renderers implement for DOM changes
- **Generational-box**: Provides `Copy` semantics for signals
- **ReactiveContext**: Tracks signal reads for subscription
- **Template-based**: RSX compiles to static templates, only dynamic parts diffed

## Reference Files

| File | Contents |
|------|----------|
| `references/subsecond-hotpatch.md` | Hot-patching architecture, ASLR, limitations |
| `references/wasm-split.md` | WASM splitting pipeline, runtime loader |
| `references/manganis-assets.md` | Asset processing, binary patching, CSS modules |
| `references/stores-signals.md` | Store derive, subscription tree, memory model |
| `references/renderers.md` | WriteMutations trait, renderer differences |
