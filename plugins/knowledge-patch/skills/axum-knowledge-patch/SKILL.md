---
name: axum-knowledge-patch
description: Axum
license: MIT
version: "0.8.0"
metadata:
  author: Nevaberry
---

# Axum Knowledge Patch

Baseline: Axum through 0.7.x. Covered range: `0.8-guide` and `0.8.0`, plus the included `axum-core`, `axum-extra`, and `axum-macros` companion-crate batches.

## Reference index

| Reference | Topics |
| --- | --- |
| [routing-and-serving.md](references/routing-and-serving.md) | Handler and service bounds, path arity, generic listeners, static and typed routing, trailing-slash redirects |
| [extractors-and-request-bodies.md](references/extractors-and-request-bodies.md) | Native async extractors, optional extraction, validation errors, strict JSON, body limits, multipart, typed headers, Host and Scheme |
| [websockets-and-streaming.md](references/websockets-and-streaming.md) | WebSocket payloads and closure, HTTP/2 routing, subprotocols, fused streams, SSE |
| [responses-and-middleware.md](references/responses-and-middleware.md) | Response status parts, unknown-size bodies, redirects, body normalization, content disposition, tracing |
| [dependency-and-release-compatibility.md](references/dependency-and-release-compatibility.md) | Rust version requirements, yanked releases, axum-extra feature flags, prost compatibility, axum-macros fix |

## Apply this patch

1. Check `Cargo.lock` and feature selections before changing code; companion-crate behavior differs by patch release and several APIs are unreleased.
2. Address breaking routing, extractor, serving, and WebSocket changes first.
3. Read the matching reference before changing multipart, typed routing, response-body types, or feature flags.
4. Preserve rejection semantics: distinguish an absent value from malformed credentials, invalid input, and operational failure.
5. Avoid pinning a yanked release; see the compatibility reference for the affected versions.

## Breaking changes and deprecations

### Remove `#[async_trait]` from custom extractors

Axum 0.8 uses return-position `impl Trait` in `FromRequestParts` and `FromRequest`. Implement their methods with native `async fn`; do not retain the old `#[async_trait]` annotation.

### Make routed handlers and services `Sync`

Anything added to `Router` or `MethodRouter` must now satisfy `Sync`. Audit:

- handler captures;
- shared application state;
- custom services passed to routing APIs; and
- values held across handler futures when they affect the routed type's bounds.

Replace non-thread-safe captures or wrap state in an appropriately thread-safe representation.

### Match tuple paths at exact arity

`Path<(A, B)>` and tuple-struct targets reject a route match unless the number of captured parameters is exact. Do not depend on extra captures being ignored. Align the route pattern and extractor target, or use a named struct that represents every capture.

### Preserve meaningful optional-extractor failures

`Option<T>` no longer converts every `T` rejection to `None`. `T` must implement `OptionalFromRequestParts` or `OptionalFromRequest` so true absence can become `None` while invalid input or operational failures remain error responses.

Do not use `Option<Query<T>>`: `Query` does not implement `OptionalFromRequestParts`. Later 0.8 releases support optional `Json`, `Extension`, and `Multipart` extraction.

### Update `Host` usage carefully

Axum 0.8 moves `Host` from `axum::extract` to `axum_extra::extract::Host`. Axum-extra 0.12.4 then deprecates `Host` and `Scheme`, and its unreleased line removes both. Also account for these details:

- the authority returned by versions that still contain `Host` includes the port;
- the unreleased removal also covers `HostRejection` and `FailedToResolveHost`; and
- `OptionalPath` is removed in that unreleased line as well.

### Configure streams through the listener

`axum::serve` is generic over listener and IO types. `Serve::tcp_nodelay` and `WithGracefulShutdown::tcp_nodelay` no longer exist; apply TCP and stream settings through `axum::serve::ListenerExt`.

### Convert WebSocket payloads and send close frames

`Message` now uses `Bytes` instead of `Vec<u8>` and `Utf8Bytes` instead of `String`. Convert owned values where needed:

```rust
socket.send(Message::Text("hello".into())).await?;
```

`WebSocket::close` is removed. Close explicitly:

```rust
socket.send(Message::Close(None)).await?;
```

For HTTP/2 WebSockets, route with a method-agnostic handler so the HTTP/2 connection method is accepted:

```rust
Router::new().route("/ws", any(ws_endpoint))
```

### Enable axum-extra 0.12 utilities explicitly

Select the feature for each utility you use: `cached`, `handler`, `middleware`, `optional-path`, `routing`, or `with-rejection`. The accidental `async-stream` feature is gone. Since 0.12.3, `typed-routing` also enables `routing`.

The axum-extra `multipart` feature is no longer enabled by default. Enable it explicitly when using `axum_extra::extract::Multipart`.

### Use brace-style static captures

As of axum-extra 0.12.6, `vpath!` rejects `:var` and `*var` syntax at compile time. Use braces:

```rust
vpath!("/users/{user_id}")
```

### Account for response-body normalization

Axum-extra 0.12 `option_layer` maps the wrapped service response body to `axum::body::Body`. Remove constraints that require another concrete response-body type after that layer.

## High-use extractor and request behavior

### Surface precise input errors

`Query` and `Form` use `serde_path_to_error`, so rejections can identify the failing field path. Path extraction can return `ErrorKind::DeserializeError` with the named parameter's key, value, and deserializer message. Include that variant in exhaustive matching and use its context in diagnostics.

The `Json` extractor now rejects trailing content after a valid JSON document. Send exactly one document per request body.

### Apply limits consistently

Use `DefaultBodyLimit::apply` inside a custom extractor when it must change the default limit; this has been available since axum-core 0.5.3.

Axum-extra's `JsonLines` observes the default body limit as of 0.12.5. Its multipart extractor enforces field exclusivity at runtime and, as of 0.12.6, reports body-limit overflow with a specific error.

### Distinguish missing typed headers

Use `TypedHeaderRejection::is_missing` or `TypedHeaderRejectionReason::is_missing` to distinguish an absent header from a malformed one.

## High-use routing and streaming features

### Negotiate WebSocket subprotocols explicitly

Use `WebSocketUpgrade::requested_protocols` to inspect client offers, `set_selected_protocol` to choose one dynamically, and `selected_protocol` to read the result. `WebSocket` also implements `FusedStream` for consumers that need termination-aware stream behavior.

### Emit binary SSE data without Tokio coupling

SSE events accept arbitrary binary payload data. The `sse` module and `Sse` type no longer require axum's `tokio` feature, which permits `default-features = false` configurations without enabling that feature solely for SSE.

### Use expanded typed routing

Use `RouterExt::typed_connect` for typed `CONNECT` routes and `TypedPath::with_query_params` to construct typed paths with query parameters. Typed paths support custom rejection types, including `WithRejection<TypedPath, _>`.

In the unreleased axum-extra API, `route_with_tsr` installs redirects only for methods present on its `MethodRouter`, so separate method routers can share a path without duplicate method-independent redirects.

## High-use response behavior

### Change status from response parts

The unreleased axum-core API exposes `ResponseParts::status` and `status_mut` to `IntoResponseParts` implementations:

```rust
*response_parts.status_mut() = StatusCode::CREATED;
```

### Represent unknown-size bodies

The unreleased `Body::unknown()` represents a body with unknown size, including useful `HEAD` response cases. Converting `()` into a response, directly or through response parts such as `HeaderMap` and `Extensions`, now yields an unknown-size body.

### Expect response-time redirect validation

An invalid header value passed to a `Redirect` constructor does not panic immediately. Its `IntoResponse` conversion produces HTTP 500.

### Preserve exact bytes intentionally

Since axum-extra 0.12.3, `ErasedJson::pretty` appends a newline. Update exact-body assertions and byte-preserving consumers.

Axum-extra 0.12.6 escapes backslashes and double quotes in `Attachment` and `FileStream` filenames. Its unreleased multipart implementation also escapes `Content-Disposition` parameters and rejects newlines in field names and filenames.

## Compatibility checkpoints

- Use Rust 1.75 or newer for axum 0.8.0, 1.78 or newer from 0.8.5, and 1.80 or newer from 0.8.9.
- Avoid yanked axum 0.8.2, axum-core 0.5.1, and axum-extra 0.11.0.
- Align axum-extra 0.12 `Protobuf` integrations and generated message types with `prost` 0.14.
- Axum-macros 0.5.1 fixes `TypedPath` derivation when `OptionalFromRequestParts` is imported.
- Enable axum-extra's `tracing` feature to log built-in extractor rejections at the `axum::rejection=trace` target.

