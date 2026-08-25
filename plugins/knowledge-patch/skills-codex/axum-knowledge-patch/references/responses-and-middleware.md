# Responses and middleware

## Mutable status in response parts

The unreleased axum-core API lets custom `IntoResponseParts` implementations inspect or change the response status through `ResponseParts::status` and `ResponseParts::status_mut`:

```rust
*response_parts.status_mut() = StatusCode::CREATED;
```

Do not assume these methods exist in a released axum-core version without checking the selected API.

## Unknown-size response bodies

The unreleased `Body::unknown()` represents a response body whose size is not known. This is useful when constructing `HEAD` responses without asserting a zero-sized representation.

Converting `()` into a response now produces an unknown-size body. The same applies when unit conversion happens indirectly through response parts such as `HeaderMap`, `Extensions`, and similar values.

## Redirect validation

An invalid header value given to a `Redirect` constructor no longer causes an immediate panic. Validation failure surfaces when converting it with `IntoResponse`, which produces HTTP 500. Test the produced response when redirect input is not a compile-time constant.

## Optional-layer body normalization

Axum-extra 0.12 `option_layer` maps the wrapped service's response body to `axum::body::Body`. This erases a different concrete response-body type that callers may previously have exposed or constrained. Adjust service bounds and response annotations accordingly.

## Exact JSON response bytes

Starting with axum-extra 0.12.3, `ErasedJson::pretty` adds a trailing newline to its response body. Include that byte in exact-body assertions and account for it in consumers that preserve bytes verbatim.

## Content-Disposition hardening

Axum-extra 0.12.6 escapes backslashes and double quotes in filenames emitted by `Attachment` and `FileStream`. This prevents a filename from injecting another header parameter.

The unreleased multipart implementation applies related protection by escaping `Content-Disposition` parameters and rejecting newlines in multipart field names and filenames.

## Extractor rejection tracing

Enable axum-extra's `tracing` feature to log built-in extractor rejections. Configure the normal tracing filter for the target:

```text
axum::rejection=trace
```
