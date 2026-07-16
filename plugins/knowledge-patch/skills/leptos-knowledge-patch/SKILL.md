---
name: leptos-knowledge-patch
description: Leptos 0.8.17 compatibility. Use for Leptos work.
license: MIT
version: 0.8.17
metadata:
  author: Nevaberry
---

# Leptos Knowledge Patch

Use this patch before writing, migrating, or reviewing Leptos applications.
Start with the breaking-change checklist, then open the topic reference that
matches the code being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [cargo-leptos](references/cargo-leptos.md) | Prebuilt installation, supported archives, checksums, stable hot reload |
| [Migration and configuration](references/migration-and-configuration.md) | Imports, constructors, storage, options, crate versions, CSS, feature flags |
| [Reactivity and stores](references/reactivity-and-stores.md) | Arc signals, guards, resources, automatic batching, conversions, stores |
| [Routing, SSR, and integrations](references/routing-ssr-and-integrations.md) | Typed routes, fallbacks, transitions, islands routing, document shells, Axum |
| [Server functions and lazy loading](references/server-functions-and-lazy-loading.md) | Custom errors, WebSockets, codecs, body limits, code splitting, lazy routes |
| [Views, components, and browser APIs](references/views-components-and-browser.md) | Typed views, attribute spreading, binding, rendering traits, ShowLet, platform attributes |

## Breaking-change checklist

### Update imports and constructors

- Import common APIs with `use leptos::prelude::*`.
- Import router components from `leptos_router::components` and hooks from
  `leptos_router::hooks`.
- Replace `create_signal(...)` with `signal(...)` and
  `create_rw_signal(...)` with `RwSignal::new(...)`.
- Do not add an explicit `batch(...)`: updates are automatically batched.

### Return statically typed views

The general `View` enum is gone. Keep one concrete return type, use `Either`
for a small number of branches, or erase every branch with `.into_any()`.

```rust
if ready {
    Either::Left(view! { <p>"Ready"</p> })
} else {
    Either::Right("Waiting")
}
```

Recursive components must box or erase their result so the compiler can
calculate its size. Ending the recursively used component with `.into_any()`
is sufficient. Do not assume typed views or `AnyView` implement `Clone`.

### Rewrite route definitions

Put the required `fallback` on `Routes`. Use typed path segments, normally via
`path!`; use `ParentRoute` for nesting and `FlatRoutes` when nesting is not
needed.

```rust
view! {
    <Routes fallback=|| "Not found">
        <ParentRoute path=path!("/posts") view=Posts>
            <Route path=path!(":id") view=Post/>
        </ParentRoute>
    </Routes>
}
```

`ParamsMap` is multi-valued: choose deliberately between append and replace,
and between fetching one value and all values.

### Own the complete SSR document

The application shell must return the doctype, `html`, `head`, and `body`, as
well as `AutoReload`, `HydrationScripts`, and `MetaTags`.

```rust
pub fn shell(options: LeptosOptions) -> impl IntoView {
    view! {
        <!DOCTYPE html>
        <html>
            <head>
                <AutoReload options=options.clone()/>
                <HydrationScripts options/>
                <MetaTags/>
            </head>
            <body><App/></body>
        </html>
    }
}
```

`get_configuration` is synchronous. Do not pass `LeptosOptions` to
`.leptos_routes(...)`. Hydrate with `leptos::mount::hydrate_body`; reserve
`mount_to_body` for client-side rendering.

### Construct configuration explicitly

`LeptosOptions` and `ConfFile` do not implement `Default`. Load or construct
them explicitly. Their option strings are `Arc<str>`, so borrow them or call
`.as_ref()` when an API needs `&str`. Read the configured stylesheet through
`LeptosOptions::css_file_path`.

Keep direct Axum dependencies aligned with Axum 0.8 and update route syntax.
Do not assume all Leptos workspace crates have the same patch version; resolve
compatible versions for each crate.

## Reactive primitives

Use `ArcRwSignal`, `ArcReadSignal`, and the other `Arc*` primitives for
dynamically nested state that should be released by reference counting. They
are `Clone`, not `Copy`, and can be converted to arena-backed signal handles.

Signal `.read()` and `.write()` guards avoid cloning and closure-based access:

```rust
let values = RwSignal::new(vec![1, 2, 3]);
let len = values.read().len();
values.write().push(4);
```

Drop guards promptly. Re-entering the same reactive value while a guard is
held can deadlock or panic.

Reactive primitives use thread-safe `SyncStorage` by default. Put `Rc` and
other thread-local values in `LocalStorage`, or call an API's `_local`
constructor such as `RwSignal::new_local(...)`.

## Resources and stores

Await `Resource` directly, including inside another resource. Preserve manual
dependency tracking where hydration requires it, and wrap an async Suspense
child in `Suspend::new(...)`.

```rust
let user = Resource::new(|| (), |_| async { 42 });
let posts = Resource::new(
    move || user.get(),
    move |_| async move { user.await + 1 },
);

view! {
    <Suspense>
        {move || Suspend::new(async move { posts.await.to_string() })}
    </Suspense>
}
```

Resources also expose `.write()` and related guarded mutation methods.
`#[derive(Store)]` creates deeply reactive field accessors, including variable
keyed collections, without notifying observers of untouched sibling fields.

## Components and browser behavior

Pass DOM attributes and `class:`, `style:`, `prop:`, and `on:` directives
through a component with attribute spreading. Use `attr:` for one explicit
plain attribute, or `{..}` between component props and later attributes.

```rust
view! {
    <Card some_prop=13 attr:id="card" {..} title="Details" class:active=true/>
}
```

Use `bind:checked` for checkboxes, `bind:group` for string-valued radio groups,
and `bind:value` for text controls. Each accepts an `RwSignal` or split
`(read, write)` pair.

Use `<ShowLet>` to render an `Option`; `<Show>` accepts a signal directly as
well as a closure. The `Await` component takes a `Future` directly.

## Routing behavior

`ProtectedRoute` reacts to condition changes and participates in Suspense, so
authorization may depend on asynchronous reactive state. Route fallbacks can
set a status code or redirect, not just render content.

Enable browser view transitions with `transition=true` on `Routes` or
`FlatRoutes`. Style `.routing-progress`, `.router-back`, and
`.router-outlet-{n}` on the document element. For islands applications, enable
the `islands-router` features to get client-side navigation without hydrating
the whole application.

## Server functions

Server functions may use any error implementing `FromServerFnError`. Account
for `ServerFnErrorErr` in `extract()` code and for different request/response
error types in WebSocket streams.

The `Websocket` protocol carries encoded `BoxedStream` values through a server
function. It does not integrate with Resources or SSR; explicitly consume the
returned stream on the client. Server-function macros accept repeated
`#[middleware]`, aliased `Result` types, and suffixed argument names.

Available codecs include additional HTTP methods, direct `bitcode`, and
Serde-backed `bitcode`. Ordinary large request bodies obey Axum and Actix body
limits, so configure those frameworks when needed; multipart is unaffected.

## Lazy code and routes

With a matching `cargo-leptos`, `#[lazy]` turns synchronous or asynchronous
functions into lazy-loaded async functions. Stack `#[server]` and `#[lazy]`
for a lazy server function. `#[lazy_route]` divides a `LazyRoute` into data and
view halves; nested route data and lazy views load concurrently before
navigation. Lazy output supports hashed filenames, and `lazy_preload` can
preload lazy code.

## cargo-leptos workflow

Prefer a pinned prebuilt `cargo-leptos` archive when one exists for the target
platform, and verify its SHA-256 checksum. Development hot reloading works on
stable Rust. If asset hashing is enabled, render styles with
`HashedStylesheet`; `Stylesheet` does not perform the CLI hashing integration.

## Final review

- Check every branch for a consistent typed view or explicit erasure.
- Check routes for typed paths, a `Routes` fallback, and correct nesting.
- Check SSR shells, hydration entry points, and explicit configuration.
- Check signal storage against thread-safety requirements and guard lifetimes.
- Check server-function protocols, error conversions, and request limits.
- Check CLI, framework, and workspace-crate versions independently.
