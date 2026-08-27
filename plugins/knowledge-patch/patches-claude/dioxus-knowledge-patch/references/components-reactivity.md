# Components, Reactivity, Events, and Hooks

## Component props and attribute forwarding

Props are memoized and derive `Clone + PartialEq`. Prefer `ReadSignal<T>` for a
value a component should read reactively: callers may pass a `Signal`, `Memo`,
store lens, literal, or inline expression, and Dioxus performs the conversion.
A plain scalar prop remains untracked, so an effect reading it will not rerun.
`WriteSignal<T>` is the writable form and is equivalent to `Signal<T>`.

```rust
#[component]
fn Validator(is_valid: ReadSignal<bool>) -> Element {
    use_effect(move || tracing::info!("validity: {is_valid}"));
    rsx! { if !is_valid() { "Invalid value" } }
}
```

At a component boundary, a readable store lens decays to `ReadSignal<T>` or
`ReadStore<T>`, keeping the public props type simple.

To forward an element's accepted attributes, collect them in a
`Vec<Attribute>` with `#[props(extends = element)]` (or global attributes) and
spread with `..`. This pattern dates to `0.5.0` and lets a wrapper accept all
attributes of its inner element.

```rust
#[derive(Props, PartialEq, Clone)]
struct ImgProps {
    #[props(extends = img)]
    attributes: Vec<Attribute>,
}

fn ImgPlus(props: ImgProps) -> Element {
    rsx! { img { ..props.attributes } }
}
```

Component props also spread with Rust struct syntax:
`Card { title: "Chapter 1", ..props }`; explicit fields override the spread.
Outside RSX, use `CardProps::builder()`. An `Option<T>` prop is optional by
default; `#[props(!optional)]` makes it required.

## Errors and boundaries

Current `Element` propagates an ordinary error with `?` into the nearest
`ErrorBoundary`. Dioxus's stack uses `anyhow::Error`, so `context`, `anyhow!`,
`bail!`, and typed downcasting work in callbacks, actions, loaders, and server
functions.

`RenderError` is either a captured error or suspended future. `CapturedError`
wraps an `Arc<anyhow::Error>` so it is cloneable; use `dioxus::Result<T>` and
`dioxus::Ok(value)` when a resource needs that concrete error type.

Inside `handle_error: |ctx: ErrorContext|`, `ctx.error()` retrieves the caught
error. Returning `Err(error.into())` rethrows it to an outer boundary. On SSR,
also preserve the HTTP status as described in
[fullstack-routing.md](fullstack-routing.md).

## Stores and lenses

### Nested reactive state

Introduced in `0.7.0`, `#[derive(Store)]` gives each field a lens accessor. A
container lens dirties only the touched entry, so changing one `Vec` or map
element does not rerender its siblings.

```rust
#[derive(Store)]
struct DirectoryState {
    children: Vec<DirectoryState>,
}

let directory = use_store(|| DirectoryState { children: vec![] });
for child in directory.children().iter() {
    // child is a per-entry reactive lens
}
```

The lens's second `Store` generic is generated and effectively unnamed. Make
helpers generic over its capability:

```rust
fn read_title(
    state: Store<HeaderState, impl Readable<Target = HeaderState>>,
) -> String {
    state.title().cloned()
}

fn clear_title(
    state: Store<HeaderState, impl Writable<Target = HeaderState>>,
) {
    state.title().take();
}
```

A store can lens through a nested type only if that type also derives `Store`.
Foreign types stop the chain. `Option`/`Result` lenses provide `unwrap()` and
`transpose()`; `transpose()` preserves the lens, while `.read().as_ref()` ends
reactive zooming. This is especially useful for collections: signal iteration
produces non-`'static` guards, while store iteration produces per-entry lenses
safe to pass as props.

Store derives also support enums, generating `is_<variant>()` predicates,
`<variant>() -> Option<Store<...>>` accessors, and `transpose()`.

### Store extension methods

Annotate an `impl` with `#[store]` to generate an extension trait over all
lenses. The receiver selects the capability bound per method: `&self` requires
`Readable`, `&mut self` requires `Writable`, and a by-value receiver needs no
lens capability.

```rust
#[store]
impl<Lens> Store<User, Lens> {
    fn email(&self) -> String { self.email_field().cloned() }
    fn clear_name(&mut self) { self.name().take(); }
}
```

### Thread-safe stores

Since `0.7.2`, `SyncStore<T>` and `use_store_sync` mirror thread-safe signals
for state that must move into `std::thread::spawn` or another non-Dioxus thread.

```rust
let state: SyncStore<AppState> = use_store_sync(AppState::default);
```

### Generic lens bounds

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

Constructing a `ReadStore` from a `MappedMutSignal` requires its `Lens` to be
`Readable`. Add that bound to generic store utilities that perform this
conversion.

## Signals, subscriptions, and globals

`peek()` reads without subscribing the current scope. `use_reactive` wraps
otherwise untracked dependencies in a closure that reruns when those values
change.

`GlobalMemo<T>` complements `GlobalSignal<T>`:

```rust
static COUNT: GlobalSignal<i32> = Signal::global(|| 0);
static DOUBLE: GlobalMemo<i32> = Memo::global(|| COUNT.cloned() * 2);
```

Their underlying forms are `Global<Signal<T>>` and `Global<Memo<T>>`, so custom
reactive types can be global too. Values are per application instance, not per
process; SSR requests and desktop windows get distinct instances.

`Signal::new()` may be used outside a hook, but its arena slot is not cleaned up
automatically. Call `.manually_drop()` yourself or prefer `use_signal`.

`read_unchecked()` relaxes runtime borrow overlap when a `.read()` guard blocks
a write. It is mainly relevant to Rust 2021 match scrutinees; edition 2024 fixes
that common lifetime shape.

For a hand-written reactive type, mutate through interior state and call the
free function `dioxus::core::needs_update()` to queue the current component.

## Actions, tasks, resources, and suspense

### User-triggered async work

`use_action` runs an async closure in response to input, stores the latest
`Result`, and cancels an in-flight call when fired again. Invoke `.call(arg)` and
read `.value()`, which is `Option<Result<T>>`.

```rust
let mut lookup = use_action(move |query: String| async move {
    reqwest::get(format!("/api/search?q={query}"))
        .await?
        .json::<SearchResult>()
        .await
});

button { onclick: move |_| lookup.call("rust".into()), "Search" }
```

Ordinary `spawn` work is cancelled on component unmount. `spawn_forever`
attaches to the root and survives until the app
closes, so every captured signal must live that long. Both return a `Task` with
`.cancel()`.

### Resources and loaders

Use `CapturedError`/`dioxus::Ok` when a resource result error must be cloneable.

`use_loader` is for futures returning `Result<T, E>` that should integrate with
both suspense and error propagation. It yields `Result<Loader<T>, Loading>`, so
`?` selects the nearest `SuspenseBoundary` while pending and `ErrorBoundary` on
failure. It is a strong fit for hybrid client/server fetching; ordinary
client-side fetching can remain a resource.

```rust
let breeds = use_loader(move || async move {
    reqwest::get("/api/breeds").await?.json::<Breeds>().await
})?;
```

Within a `SuspenseBoundary`, a suspended resource can override the
boundary fallback with `.with_loading_placeholder(...)`.

`SuspenseBoundary` and `.suspend()?` were introduced in `0.6.0`. Fullstack web
streams boundaries as they resolve; the same component abstraction also works
on desktop and mobile.

## Callbacks and external callers

`Callback<I, O>` is the value-returning callback type; `EventHandler<T>` is the
`O = ()` specialization. Both are `Copy`, convert automatically in props, and
retain a runtime handle, so a filesystem watcher or system-I/O callback can
invoke them from outside the active runtime without the usual panic.

## Event handling

Call `prevent_default()` synchronously, especially in `onsubmit`, before any
await. Convert a `FormEvent` to structured form or multipart data as described
in the fullstack reference.

`event.downcast::<T>()` is the generic accessor for a platform payload and
returns `Option<T>`. On web, `as_web_event()` is the renderer-specific shortcut.

`onresize` and `onvisible` have existed since `0.6.0`; Dioxus backs them with
browser observers, and resize data exposes `get_border_box_size()`. `0.7.3`
added `onauxclick` and `onscrollend`.

An `input { type: "file", directory: true }` maps folder selection to the
appropriate browser-specific attribute.

### Selection, before-input, and clipboard payloads

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The DOM event surface includes selection-event families and `beforeinput`, so
web code need not drop to `web_sys` or `eval` for those cases. Clipboard events
also carry pasted data in their payload rather than merely signaling a paste.
