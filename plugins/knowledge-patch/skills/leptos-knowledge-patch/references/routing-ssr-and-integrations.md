# Routing, SSR, and Integrations

## Route definitions

`Routes` requires a `fallback`; the fallback is no longer an optional prop on
`Router` (since 0.7.0). Paths are typed segments rather than unvalidated
strings. `path!` supplies concise migration syntax. Use `ParentRoute` for a
route with children and `FlatRoutes` when routes are not nested:

```rust
view! {
    <Routes fallback=|| "Not found">
        <ParentRoute path=path!("/posts") view=Posts>
            <Route path=path!(":id") view=Post/>
        </ParentRoute>
    </Routes>
}
```

Route fallbacks can set a custom response status or redirect (since 0.8.0),
instead of being limited to fallback view content.

## Parameters

`ParamsMap` stores multiple query-string values for each key (since 0.7.0).
Its API distinguishes appending from replacing and fetching one value from
fetching all values. Choose the operation that matches whether repeated query
parameters are meaningful.

The `Params` derive macro works on stable Rust (since 0.8.0), so typed
parameter structs do not require nightly solely for that derive.

## Reactive protection and transitions

`ProtectedRoute` reacts whenever its condition changes and participates in
Suspense (since 0.7.0). Authorization conditions may therefore depend on a
resource or other asynchronous reactive state; they are not checked only once
during navigation.

Set `transition=true` on `Routes` or `FlatRoutes` to use the browser View
Transition API. During navigation the router places these CSS hooks on the
document element:

- `.routing-progress`;
- `.router-back`;
- `.router-outlet-{n}`.

Use them to distinguish progress, backward navigation, and nested outlets.

## Islands navigation

The `islands-router` features add client-side navigation to islands
applications (since 0.8.0) without forcing the entire application to hydrate.
This is separate from the base `islands` feature.

## Application-owned document shell

SSR applications return the entire HTML document shell (since 0.7.0),
including the doctype, document elements, reload and hydration support, and
metadata:

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

Do not rely on the integration to add those pieces around an application-only
body.

## Configuration, routes, and hydration entry points

`get_configuration` is synchronous. `.leptos_routes(...)` no longer takes a
`LeptosOptions` argument. Hydrating an SSR application uses
`leptos::mount::hydrate_body`; `mount_to_body` is specifically for CSR.

## Axum integration

The integration targets Axum 0.8 (since 0.8.0), including its changed route
syntax. Leptos reexports some Axum types, so upgrade an application's direct
Axum dependency at the same time to avoid mismatched integration types and
APIs.
