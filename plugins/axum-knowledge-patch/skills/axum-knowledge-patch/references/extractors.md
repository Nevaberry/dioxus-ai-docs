# Extractors

## `#[async_trait]` Removed From Extractor Traits (0.8.0)

`FromRequestParts` and `FromRequest` use native async fn in traits (RPITIT). Remove `#[async_trait]` from custom extractor impls:

```rust
// Before (0.7)
#[async_trait]
impl<S> FromRequestParts<S> for MyExtractor where S: Send + Sync {
    type Rejection = StatusCode;
    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> { todo!() }
}
// After (0.8) — no #[async_trait], same signature
impl<S> FromRequestParts<S> for MyExtractor where S: Send + Sync {
    type Rejection = StatusCode;
    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> { todo!() }
}
```

## `Option<T>` Uses `OptionalFromRequestParts` (0.8.0)

`Option<T>` no longer silently swallows all errors as `None`. `T` must implement `OptionalFromRequestParts` (or `OptionalFromRequest`).

- **Missing value** → `None`
- **Invalid/malformed value** → rejection error

This is a breaking change if you relied on `Option<T>` catching all extraction failures.

## `Option<Json<T>>` and `Option<Extension<T>>` (0.8.3)

`Json` implements `OptionalFromRequest` and `Extension` implements `OptionalFromRequestParts` as of 0.8.3:

```rust
async fn handler(body: Option<Json<MyPayload>>) -> impl IntoResponse {
    match body {
        Some(Json(payload)) => { /* process payload */ }
        None => { /* no body sent */ }
    }
}
```

Missing body/extension → `None`, malformed input → rejection.

## `Option<Multipart>` (0.8.5)

`Multipart` implements `OptionalFromRequest`. Missing multipart body → `None`, invalid → rejection.

## `Host` Extractor Moved (0.8.0)

`Host` extractor moved from `axum` to `axum-extra`.
