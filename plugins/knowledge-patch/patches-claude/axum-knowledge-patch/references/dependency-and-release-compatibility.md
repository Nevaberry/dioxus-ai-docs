# Dependency and release compatibility

## Minimum supported Rust version

The axum 0.8 line raises its compiler requirement in stages:

| Axum release | Minimum Rust version |
| --- | --- |
| 0.8.0 | 1.75 |
| 0.8.5 | 1.78 |
| 0.8.9 | 1.80 |

Set the workspace toolchain and package `rust-version` for the newest selected axum release, not merely for the start of the 0.8 series.

## Yanked releases

Do not newly pin these releases:

| Crate | Yanked release | Reason given |
| --- | --- | --- |
| `axum` | 0.8.2 | It introduced an unforeseen breaking change. |
| `axum-core` | 0.5.1 | It introduced an unforeseen breaking change. |
| `axum-extra` | 0.11.0 | It introduced an unforeseen breaking change. |

Choose another compatible release from the relevant line.

## Axum-extra 0.12 feature selection

Version 0.12 gates utilities behind explicit features:

| Utility family | Feature |
| --- | --- |
| `Cached` | `cached` |
| Handler utilities | `handler` |
| Middleware utilities | `middleware` |
| `OptionalPath` | `optional-path` |
| Routing utilities | `routing` |
| `WithRejection` | `with-rejection` |

The accidentally exposed `async-stream` feature has been removed. Since axum-extra 0.12.3, selecting `typed-routing` also selects `routing`.

Multipart is separately opt-in: select `multipart` when using axum-extra's multipart extractor.

## Protobuf dependency alignment

Axum-extra 0.12 upgrades its `Protobuf` extractor and response integration to `prost` 0.14. Align generated message types and direct `prost` dependencies with 0.14 to avoid trait or type mismatches across prost versions.

## Axum-macros compatibility

Axum-macros 0.5.1 fixes a compile failure in `TypedPath` derivation that occurred merely when `OptionalFromRequestParts` was in scope. Use at least that patch release when combining the derive with optional-extractor imports.

