# Routing, SSR, and Integrations

## Define typed routes

Route definitions changed in 0.7.0:

- Put the required `fallback` on `Routes`, not `Router`.
- Use `FlatRoutes` when routes are not nested.
- Use `ParentRoute` for routes with children.
- Express paths as typed segments; `path!` is the concise migration syntax.

```rust
view! {
    <Routes fallback=|| "Not found">
        <ParentRoute path=path!("/posts") view=Posts>
            <Route path=path!(":id") view=Post/>
        </ParentRoute>
    </Routes>
}
```

The `Params` derive works on stable Rust (since 0.8.0), so typed parameter
structs do not require nightly solely for that macro.

## Handle multi-valued parameters

`ParamsMap` represents multiple query-string values per key (since 0.7.0).
Its API distinguishes appending from replacing a value and retrieving one
value from retrieving every value. Choose the operation deliberately rather
than assuming a single-valued map.

## Return fallback responses

Route fallbacks may set a custom response status or redirect instead of only
rendering fallback content (since 0.8.0). Keep the required fallback on
`Routes` even when it produces a response rather than a plain view.

## React to protected-route conditions

`ProtectedRoute` reacts when its condition changes and participates in
Suspense (since 0.7.0). Authorization can therefore depend on a resource or
other asynchronous reactive state; it is not checked just once at navigation.

## Animate navigation

Set `transition=true` on `Routes` or `FlatRoutes` to use the browser View
Transition API (since 0.7.0). The router places animation classes on `<html>`;
CSS can target `.routing-progress`, `.router-back`, and
`.router-outlet-{n}`.

## Route islands on the client

Enable the `islands-router` features for client-side navigation in an islands
application without hydrating the entire application (since 0.8.0). The base
islands feature itself is named `islands`, not `experimental-islands`.

## Return the complete SSR document

The application owns the whole document shell (since 0.7.0), including the
doctype, `html`, `head`, and `body`, plus `AutoReload`, `HydrationScripts`, and
`MetaTags`.

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

## Update SSR and hydration setup

The SSR boilerplate changed in 0.7.0:

- `get_configuration` is synchronous.
- `.leptos_routes(...)` no longer receives `LeptosOptions`.
- Hydration uses `leptos::mount::hydrate_body`.
- `mount_to_body` is for client-side rendering, not hydration.

## Align Axum integration

The integration targets Axum 0.8 and its changed route syntax (since 0.8.0).
Upgrade a direct Axum dependency at the same time. Because Leptos reexports
some Axum types, leaving the direct dependency behind can cause type-version
mismatches.
