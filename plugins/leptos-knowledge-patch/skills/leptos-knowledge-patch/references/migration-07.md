# 0.6.x → 0.7 Migration Guide

Leptos 0.7 is a near-complete rewrite of internals. This covers all breaking changes.

## Import Paths

```rust
// 0.6.x
use leptos::*;

// 0.7+
use leptos::prelude::*;
```

Router items moved to `leptos_router::components` and `leptos_router::hooks` (no longer flat namespace).

## Signal Constructors

The `create_` prefix is replaced with idiomatic Rust constructors:

```rust
// 0.6.x
let (count, set_count) = create_signal(0);
let rw = create_rw_signal(0);
let memo = create_memo(|_| count.get() * 2);

// 0.7+
let (count, set_count) = signal(0);
let rw = RwSignal::new(0);
```

Old `create_*` functions are deprecated but some remain for compatibility.

## Send + Sync Requirement

Signals require `Send + Sync` data by default (for SSR thread safety). Use `_local()` variants for non-Send types:

```rust
let (foo, bar) = signal("baz"); // requires Send + Sync
let (foo, bar) = signal_local(Rc::new("baz")); // Rc is not Send

let qux = RwSignal::new("baz");
let qux = RwSignal::new_local(Rc::new("baz"));
```

Signal types have a storage generic defaulting to `SyncStorage`; specify `LocalStorage` for non-Send data.

## Static Typed Views (View Enum Removed)

The `View` enum is replaced with statically-typed views. Binary size savings are significant. For branching, use `Either` or `.into_any()`:

```rust
// Either (preferred — compiler optimizes better)
if condition {
    Either::Left(view! { <p>"Foo"</p> })
} else {
    Either::Right("Bar")
}

// .into_any() — type-erased AnyView
if condition {
    view! { <p>"Foo"</p> }.into_any()
} else {
    "Bar".into_any()
}
```

**Recursive components MUST use `.into_any()`** so the compiler can compute view tree size.

### Views Cannot Be Stored in Signals

In 0.6.x, `View` was `Clone`. In 0.7, `AnyView` is not necessarily cloneable. Use a reactive channel pattern instead:

```rust
let trigger = ArcTrigger::new();
let (tx, rx) = std::sync::mpsc::channel();
let on_click = {
    let trigger = trigger.clone();
    move |_| {
        tx.send(view! { <p>"Dynamic"</p> }.into_any()).unwrap();
        trigger.trigger();
    }
};
view! {
    <button on:click=on_click>"Update"</button>
    {move || { trigger.track(); rx.try_recv().unwrap_or_else(|_| view! { <p>"Initial"</p> }.into_any()) }}
}
```

## Route Definition Changes

Multiple breaking changes to routing:

1. **`fallback` is now required** on `<Routes/>` (was optional on `<Router/>`)
2. **`<FlatRoutes/>`** is new for apps without nested routing (optimization)
3. **Routes with children must use `<ParentRoute/>`** instead of `<Route/>`
4. **Route paths are now type-safe**, not strings:

```rust
// 0.6.x
path="/foo/:id"

// 0.7+
path=(StaticSegment("foo"), ParamSegment("id"))
// or via macro:
path=path!("/foo/:id")
```

## Signal<T> No Longer From<Fn() -> T>

Removed to allow `Signal<T>: From<T>`. Use `Signal::derive()` explicitly:

```rust
// 0.6.x
let s: Signal<i32> = move || some_val;

// 0.7+
let s: Signal<i32> = Signal::derive(move || some_val);
// Plain T now works:
let s: Signal<i32> = Signal::from(42);
```

Note: `From<Fn() -> T>` was restored in 0.8.14 for `Signal`, `ArcSignal`, and `Callback`.

## Custom IntoView / IntoAttribute

- Replace `IntoView` implementations with `IntoRender`
- Replace `IntoAttribute` implementations with `IntoAttributeValue`

## SSR Boilerplate Changes

- `get_configuration` is now **sync** (remove `.await`)
- `.leptos_routes()` no longer takes `LeptosOptions` as argument
- Use `leptos::mount::hydrate_body` for hydration (SSR); `mount_to_body` is CSR-only
- `experimental-islands` feature renamed to `islands`
- `batch` function removed — all updates batch automatically

## LeptosOptions Fields

`LeptosOptions` fields changed from `String` to `Arc<str>`. Use `&field` or `field.as_ref()` where `&str` is required.

## ParamsMap Multiple Values

`ParamsMap` now supports multiple values per key (matching query string semantics). The API differentiates insert-new vs replace, and get-one vs get-all.

## Await Component

`Await` now takes a plain `Future` for its `future` prop (not `Fn() -> Future`).

## A Component Attribute Spreading

`<A>` and similar components no longer have dedicated HTML attribute props (`class`, etc.). Use attribute spreading with `{..}` instead.

## Axum 0.8 (from 0.8.0)

Leptos 0.8.0 upgraded to Axum 0.8 (forced because Axum types are re-exported). If on Axum 0.7, migration is required.
