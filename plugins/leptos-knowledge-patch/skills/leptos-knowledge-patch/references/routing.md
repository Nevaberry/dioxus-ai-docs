# Routing

Route definitions, navigation, view transitions, and islands routing in 0.7+.

## Type-Safe Route Paths (0.7+)

Route paths are now static types, not strings:

```rust
// 0.6.x
path="/foo/:id"

// 0.7+ — type segments
path=(StaticSegment("foo"), ParamSegment("id"))

// 0.7+ — path! macro (preferred)
path=path!("/foo/:id")
```

## Route Component Changes (0.7+)

- **`fallback` is required** on `<Routes/>` (was optional on `<Router/>` in 0.6.x)
- **`<FlatRoutes/>`** — new component for apps without nested routing (performance optimization)
- **`<ParentRoute/>`** — routes with children must now use this instead of `<Route/>`

```rust
<Router>
    <Routes fallback=|| view! { <p>"Not found"</p> }>
        <Route path=path!("/") view=Home />
        <ParentRoute path=path!("/users") view=UsersLayout>
            <Route path=path!("/:id") view=UserDetail />
        </ParentRoute>
    </Routes>
</Router>

// Or for flat apps:
<Router>
    <FlatRoutes fallback=|| view! { <p>"Not found"</p> }>
        <Route path=path!("/") view=Home />
        <Route path=path!("/about") view=About />
    </FlatRoutes>
</Router>
```

## Reactive ProtectedRoute (0.7+)

The old `ProtectedRoute` checked the condition once synchronously. The new version is reactive and integrates with Suspense, so it can use async data/resources.

## View Transitions API (0.7+)

`<Routes>` and `<FlatRoutes>` have a `transition` prop. When `true`, uses the browser's View Transition API during navigation:

```rust
<Routes transition=true fallback=|| "Not found">
    // ...
</Routes>
```

The router sets CSS classes on `<html>`:
- `.routing-progress` — while navigating
- `.router-back` — during back navigation
- `.router-outlet-{n}` — depth of outlet changing (0 = root)

## `<A/>` Component Changes

### Attribute spreading required (0.7+)

`<A>` no longer has dedicated HTML attribute props (`class`, etc.). Use `{..}` attribute spreading.

### `scroll` prop (0.7.1+)

Controls scrolling behavior on navigation:

```rust
<A href="/page" scroll=false>"No scroll"</A>
```

### `referrerpolicy` attribute (0.8.9+)

The `referrerpolicy` attribute was added to `<a>` elements.

## Islands Router (0.8.0+)

New `islands-router` feature enables client-side routing with islands architecture:

```toml
[features]
islands-router = ["leptos/islands-router"]
```

See the `islands_router` example. Works in 404 routes as of 0.8.8.

## Lazy Routes (0.8.5+)

Routes can be split into a data half and view half, loaded concurrently by the router. See [references/code-splitting.md](code-splitting.md) for full details.

## Nested Routing Ownership Rewrite (0.8.3)

Significant rewrite of how ownership and context propagate through nested routes and `<Outlet/>`s. Context is now correctly propagated. The now-unused `join_contexts` API was removed.

## RouteChildren Clone (0.7.4+)

`RouteChildren` derives `Clone`.

## ParamsMap Changes (0.7+)

`ParamsMap` now supports multiple values per key (matching query string semantics). API differentiates insert-new vs replace, and get-one vs get-all.

### Raw Identifiers in Params (0.7.5+)

`#[derive(Params)]` allows raw identifiers (e.g., `r#type`) as field names for URL parameters that are Rust keywords.

### IntoIterator for &ParamsMap (0.8.16+)

`&ParamsMap` implements `IntoIterator`.

## Navigation Fixes

| Version | Fix |
|---|---|
| 0.8.8 | Only adds to history stack if URL differs from current |
| 0.8.9 | Duplicate history entries eliminated |
| 0.8.10 | Back navigation correctly manages path stack |
| 0.8.13 | URL query/hash no longer incorrectly unescaped on link click |

## HashedStylesheet (0.7+)

`Stylesheet` no longer auto-integrates with cargo-leptos file hashing. Use `HashedStylesheet` instead.
