# Routing, SSR, and Integrations

## Typed route definitions

Route definitions changed in 0.7.0:

- Put the required `fallback` on `Routes`, not `Router`.
- Use `FlatRoutes` for unnested routes.
- Use `ParentRoute` for routes with children.
- Replace string paths with typed path segments; `path!` is the concise
  migration syntax.

```rust
view! {
    <Routes fallback=|| "Not found">
        <ParentRoute path=path!("/posts") view=Posts>
            <Route path=path!(":id") view=Post/>
        </ParentRoute>
    </Routes>
}
```

## Multi-valued parameters

`ParamsMap` can hold multiple query-string values for one key (since 0.7.0).
Its API distinguishes appending from replacing and fetching one value from
fetching every value. Choose the operation explicitly rather than assuming a
single-value map.

The `Params` derive macro works on stable Rust as of 0.8.0; typed parameter
structs no longer need nightly solely for the derive.

## Reactive protection and fallback responses

`ProtectedRoute` reacts when its condition changes and participates in
Suspense (since 0.7.0). Authorization can therefore depend on Resources or
other asynchronous reactive state rather than being checked only once during
navigation.

Route fallbacks can set a custom response status or redirect as of 0.8.0;
they are not limited to rendering fallback view content.

## Browser view transitions

Set `transition=true` on `Routes` or `FlatRoutes` to use the browser View
Transition API during navigation (since 0.7.0). Style the classes placed on
the document element:

- `.routing-progress`
- `.router-back`
- `.router-outlet-{n}`

## Application-owned document shell

SSR applications own and return the complete HTML document as of 0.7.0. The
shell must include `<!DOCTYPE html>`, `html`, `head`, and `body`, together with
`AutoReload`, `HydrationScripts`, and `MetaTags`.

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

## SSR and hydration entry points

`get_configuration` is synchronous as of 0.7.0. The
`.leptos_routes(...)` integration no longer accepts `LeptosOptions`. Hydrated
applications should enter through `leptos::mount::hydrate_body`; use
`mount_to_body` only for client-side rendering.

## Axum integration

The integration targets Axum 0.8 as of 0.8.0, including its changed route
syntax. Upgrade a direct Axum dependency alongside Leptos because Leptos
reexports some Axum types.

## Islands routing

Enable the `islands-router` features introduced in 0.8.0 to add client-side
navigation to islands applications without hydrating the whole application.
The base islands Cargo feature is named `islands`; `experimental-islands` was
renamed in 0.7.0.
