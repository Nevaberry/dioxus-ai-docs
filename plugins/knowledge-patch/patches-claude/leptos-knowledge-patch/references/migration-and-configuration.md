# Migration and Configuration

## Imports and constructors

The common API moved behind the prelude (since 0.7.0):

```rust
use leptos::prelude::*;
```

Router APIs are organized under `leptos_router::components` and
`leptos_router::hooks`. Update root-level imports accordingly.

Constructor names now follow idiomatic Rust naming. Replace calls such as
`create_signal(...)` with `signal(...)`, and replace `create_rw_signal(...)`
with `RwSignal::new(...)`.

## Automatic update batching

The explicit `batch` function was removed in 0.7.0. Reactive updates receive
the batching behavior automatically, so remove manual `batch(...)` wrappers.

## Explicit configuration construction

`LeptosOptions` and `ConfFile` no longer implement `Default` (since 0.8.0).
Load configuration or construct these values explicitly rather than calling
`LeptosOptions::default()` or `ConfFile::default()`.

`LeptosOptions` string fields use `Arc<str>` (since 0.7.0). When another API
requires `&str`, borrow the field or call `.as_ref()` instead of moving or
expecting an owned `String`.

## Configured stylesheet paths

Read the configured stylesheet through `LeptosOptions::css_file_path` (since
0.8.0). The briefly introduced `css_path` spelling was replaced in the same
release line; do not build against that transient name.

When `cargo-leptos` asset hashing is enabled, render the stylesheet with
`HashedStylesheet` (since 0.7.0). `Stylesheet` no longer supplies the CLI's file
hashing integration automatically.

## Feature names

Rename the `experimental-islands` Cargo feature to `islands` when migrating
feature lists (since 0.7.0). For client-side routing in an islands application,
enable the separate `islands-router` features described in
[Routing, SSR, and integrations](routing-ssr-and-integrations.md).

## Dependency alignment

Direct Axum dependencies must use Axum 0.8 with the current integration and
its changed route syntax (since 0.8.0). Leptos reexports some Axum types, so a
stale direct dependency can otherwise create incompatible duplicate types.

Leptos workspace crates do not necessarily share a patch number (since
0.8.0). Resolve compatible versions for `leptos`, `leptos_macro`,
`server_fn_macro`, and other workspace crates independently instead of forcing
identical patch versions.
