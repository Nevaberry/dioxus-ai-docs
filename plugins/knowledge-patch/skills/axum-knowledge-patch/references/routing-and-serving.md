# Routing and serving

## Handler and service bounds

Handlers and services added to `Router` or `MethodRouter` must satisfy `Sync` in axum 0.8.0. This includes the routed value itself and any captured state that determines whether it is safe to share between threads. Replace non-`Sync` captures or service internals before registering them.

## Exact path arity

`Path<(A, B)>` and tuple-struct extraction require exactly as many captured route parameters as the target contains. A route with extra captures is rejected rather than partially deserialized. Keep each tuple or tuple struct aligned with its route pattern.

## Generic serving

`axum::serve` is generic over listener and IO abstractions. Configure TCP or other stream behavior on the listener through `axum::serve::ListenerExt`.

The following convenience methods have been removed:

- `Serve::tcp_nodelay`
- `WithGracefulShutdown::tcp_nodelay`

Move equivalent configuration to the listener rather than attempting to apply it to the returned serving future.

## Compile-time static paths

Axum-extra's `vpath!` validates static paths at compile time. Starting in axum-extra 0.12.6, colon and star captures such as `:id` and `*rest` fail compilation. Use brace syntax:

```rust
vpath!("/users/{user_id}")
```

## Method-specific trailing-slash redirects

In the unreleased axum-extra API, `RouterExt::route_with_tsr` installs a redirect only for methods handled by the supplied `MethodRouter`. This permits separate method routers on the same path without both installing a method-independent redirect:

```rust
Router::new()
    .route_with_tsr("/path", get(get_handler))
    .route_with_tsr("/path", post(post_handler))
```

Do not infer this behavior for a released axum-extra version without checking that version's API.

## Typed routing

Axum-extra typed routing now covers more request shapes:

- Register typed `CONNECT` routes with `RouterExt::typed_connect`.
- Construct a typed path plus query string with `TypedPath::with_query_params`.
- Give typed paths custom rejection types, including with `WithRejection<TypedPath, _>`.

