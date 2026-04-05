---
name: leptos-knowledge-patch
description: "Leptos 0.7-0.8 changes since training cutoff (latest: 0.8.17) — 0.7 rewrite (signals, views, routing), reactive stores, WASM code splitting, WebSocket server fns, lazy routes, custom shell. Load before writing Leptos code."
version: "0.8.17"
license: MIT
metadata:
  author: Nevaberry
  version: "1.0.0"
---

# Leptos Knowledge Patch

Covers Leptos 0.7.0 through 0.8.17. Claude's training includes Leptos through 0.6.x. The 0.7 release was a near-complete rewrite of internals with many breaking changes. 0.8.x added WASM code splitting, WebSocket server functions, and reactive store improvements.

## Reference Index

| Topic | Reference | Key features |
|---|---|---|
| 0.6→0.7 Migration | [references/migration-07.md](references/migration-07.md) | Imports, signal constructors, typed views, route syntax, Send+Sync |
| Reactive Primitives | [references/reactive-primitives.md](references/reactive-primitives.md) | Stores, Arc signals, read/write guards, context APIs |
| Routing | [references/routing.md](references/routing.md) | Type-safe paths, FlatRoutes, view transitions, islands router, lazy routes |
| Server Functions | [references/server-functions.md](references/server-functions.md) | WebSocket protocol, custom errors, bitcode encoding, lazy server fns |
| Code Splitting | [references/code-splitting.md](references/code-splitting.md) | `#[lazy]`, `#[lazy_route]`, `LazyRoute` trait, lazy server fns |
| Components & Views | [references/components-views.md](references/components-views.md) | Static typed views, Either, ShowLet, bind:, attribute spreading |
| SSR & Hydration | [references/ssr-hydration.md](references/ssr-hydration.md) | Custom HTML shell, erase_components, subsecond, streaming fixes |

## Quick Migration: 0.6.x → 0.7+

| Area | 0.6.x | 0.7+ |
|---|---|---|
| Import | `use leptos::*` | `use leptos::prelude::*` |
| Signal | `create_signal(0)` | `signal(0)` |
| RwSignal | `create_rw_signal(0)` | `RwSignal::new(0)` |
| Mount | `mount_to_body(App)` | `leptos::mount::mount_to_body(App)` |
| Hydrate | `leptos_dom::HydrationCtx` | `leptos::mount::hydrate_body` |
| View branch | `View` enum | `Either::Left(a)` / `Either::Right(b)` or `.into_any()` |
| Route path | `path="/foo/:id"` | `path=path!("/foo/:id")` |
| Nested route | `<Route/>` with children | `<ParentRoute/>` with children |
| Fallback | Optional on `<Router/>` | **Required** on `<Routes/>` |
| Config | `get_configuration().await` | `get_configuration()` (sync) |
| Batch | `batch(\|\| { ... })` | Removed — always batches automatically |
| Closure→Signal | `let s: Signal<T> = \|\| val` | `Signal::derive(\|\| val)` |
| Plain T→Signal | Not supported | `Signal::from(42)` |
| IntoView impl | `impl IntoView` | `impl IntoRender` |
| IntoAttribute | `impl IntoAttribute` | `impl IntoAttributeValue` |
| LeptosOptions | `String` fields | `Arc<str>` fields — use `&field` for `&str` |

## Essential New Patterns

### Signals require Send + Sync (0.7+)

```rust
let (count, set_count) = signal(0); // T: Send + Sync
let (local, set_local) = signal_local(Rc::new(0)); // non-Send OK
let rw = RwSignal::new(0);
let rw_local = RwSignal::new_local(Rc::new(0));
```

### Read/write guards — no-clone signal access (0.7+)

```rust
let data = RwSignal::new(vec![1, 2, 3]);
let len = move || data.read().len(); // no clone, returns guard
data.write().push(4); // mutable guard
```

### Static typed views — Either and .into_any() (0.7+)

```rust
// Preferred: Either (compiler optimizes better)
if condition {
    Either::Left(view! { <p>"A"</p> })
} else {
    Either::Right(view! { <span>"B"</span> })
}

// Type-erased: .into_any() (required for recursive components)
view! { <p>"A"</p> }.into_any()
```

### Two-way binding (0.7+)

```rust
let checked = RwSignal::new(false);
let text = RwSignal::new(String::new());
let (val, set_val) = signal("hello".to_string());

view! {
    <input type="checkbox" bind:checked=checked />
    <input type="text" bind:value=(val, set_val) />
    <input type="radio" value="a" bind:group=text />
}
```

### Reactive stores (0.7+)

```rust
#[derive(Store)]
struct AppState {
    user: String,
    count: i32,
}
// Each field independently reactive — updating count doesn't trigger user watchers
```

### Resource .await with Suspend (0.7+)

```rust
let user = Resource::new(|| (), |_| fetch_user());
view! {
    <Suspense fallback=|| "Loading...">
        {move || Suspend::new(async move {
            let u = user.await;
            view! { <p>{u.name}</p> }
        })}
    </Suspense>
}
```

### Custom HTML shell (0.7+)

```rust
pub fn shell(options: LeptosOptions) -> impl IntoView {
    view! {
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <AutoReload options=options.clone() />
                <HydrationScripts options/>
                <MetaTags/>
            </head>
            <body>
                <App/>
            </body>
        </html>
    }
}
```

### WebSocket server functions (0.8+)

```rust
use server_fn::{BoxedStream, ServerFnError, Websocket, codec::JsonEncoding};

#[server(protocol = Websocket<JsonEncoding, JsonEncoding>)]
async fn echo(
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

### WASM code splitting (0.8.5+)

```rust
#[lazy]
fn heavy_computation(data: &str) -> Vec<Item> {
    serde_json::from_str(data).unwrap()
}

#[lazy_route]
impl LazyRoute for MyView {
    fn data() -> Self { Self { data: Resource::new(|| (), |_| load()) } }
    fn view(this: Self) -> AnyView {
        view! { <Suspense>/* use this.data */</Suspense> }.into_any()
    }
}
```

### ShowLet for Option values (0.8.8+)

```rust
<ShowLet when=move || optional_value() let:value>
    <p>{value}</p>
</ShowLet>

// Show now accepts signals directly (not just closures)
<Show when=my_bool_signal>
    <p>"Visible"</p>
</Show>
```

See individual reference files for complete details on each topic area.
