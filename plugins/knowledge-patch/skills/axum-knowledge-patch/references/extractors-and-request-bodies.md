# Extractors and request bodies

## Native async extractor implementations

Axum 0.8 extractor traits use return-position `impl Trait` in traits. Remove `#[async_trait]` from custom `FromRequestParts` and `FromRequest` implementations and implement their methods with native `async fn`.

## Optional extraction semantics

`Option<T>` requires `T` to implement `OptionalFromRequestParts` or `OptionalFromRequest`. An optional implementation must separate true absence from other rejection conditions:

- Return `None` only for absence.
- Preserve invalid credentials, malformed values, and operational errors as rejection responses.
- Do not depend on `Option<T>` swallowing every rejection from `T`.

Built-in support is intentionally selective. `Query` does not implement `OptionalFromRequestParts`, so `Option<Query<T>>` is unavailable. Later axum 0.8 releases add optional extraction for `Json`, `Extension`, and `Multipart`, enabling `Option<Json<T>>`, `Option<Extension<T>>`, and `Option<Multipart>` with the same absence-versus-error distinction.

## Structured deserialization errors

`Query` and `Form` use `serde_path_to_error`. Their rejections can identify the field path at which deserialization failed instead of reporting only a generic parse error.

`FailedToDeserializePathParams::kind` can return `ErrorKind::DeserializeError`. That variant carries:

- the named path parameter's key;
- its input value; and
- the deserializer's message.

Handle the variant when matching path error kinds and use its input context when producing diagnostics.

## Strict JSON documents

The `Json` extractor accepts exactly one JSON document. It rejects a body that contains a valid document followed by trailing content rather than accepting only the valid prefix.

## Body-limit control

`DefaultBodyLimit::apply` has allowed a custom extractor to change the default body limit from inside extraction since axum-core 0.5.3.

Axum-extra's streaming and multipart extractors now honor limits more consistently:

- `JsonLines` applies axum's default body limit as of 0.12.5.
- Axum-extra 0.12.6 returns a specific error when its multipart body limit is exceeded.

## Axum-extra multipart behavior

The `multipart` feature is no longer enabled by default; select it explicitly to use `axum_extra::extract::Multipart`.

Unlike axum's multipart extractor, the axum-extra extractor enforces field exclusivity at runtime. Code must finish or release one field before advancing in a way that violates that exclusivity.

The unreleased multipart implementation also hardens `Content-Disposition`: it escapes parameter values and rejects newlines in field names and filenames.

## Typed-header absence

Use either of these APIs to distinguish an absent typed header from another parse failure:

- `TypedHeaderRejection::is_missing`
- `TypedHeaderRejectionReason::is_missing`

This avoids manually matching every rejection variant merely to detect absence.

## Host and Scheme lifecycle

Axum 0.8 removes `Host` from `axum::extract`; import the still-available form as `axum_extra::extract::Host`.

Treat this as a migration bridge rather than a permanent destination:

- Axum-extra 0.12.4 deprecates `Host` and `Scheme`.
- The unreleased axum-extra line removes `Host`, `Scheme`, `OptionalPath`, `HostRejection`, and `HostRejection::FailedToResolveHost`.
- Releases that still provide `Host` include the port number in its authority result.

