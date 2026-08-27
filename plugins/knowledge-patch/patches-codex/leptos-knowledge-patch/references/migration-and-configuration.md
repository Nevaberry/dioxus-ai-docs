# Migration and Configuration

## Imports and constructors

Common framework APIs moved behind `use leptos::prelude::*` in 0.7.0. Router
components live under `leptos_router::components`, while router hooks live
under `leptos_router::hooks`.

Constructors use idiomatic Rust names:

- Replace `create_signal(...)` with `signal(...)`.
- Replace `create_rw_signal(...)` with `RwSignal::new(...)`.
- Prefer equivalent associated constructors for other reactive types.

## Reactive storage defaults

Reactive primitives use thread-safe `SyncStorage` by default (since 0.7.0),
so their stored values must be `Send + Sync`. For `Rc` or other thread-local
values, select `LocalStorage` explicitly or use an API's `_local` constructor.

```rust
let shared = RwSignal::new("value");
let local = RwSignal::new_local(std::rc::Rc::new("value"));
```

## Configuration construction

`LeptosOptions` and `ConfFile` no longer implement `Default` (since 0.8.0).
Load configuration or construct these values explicitly instead of calling
`LeptosOptions::default()` or `ConfFile::default()`.

The string fields in `LeptosOptions` are `Arc<str>` (since 0.7.0). Borrow the
field or call `.as_ref()` when a downstream API requires `&str`.

Use `LeptosOptions::css_file_path` to read the configured stylesheet path
(since 0.8.0). The briefly introduced `css_path` name was replaced in the
same release line; do not build against that intermediate spelling.

## Workspace dependency versions

Leptos workspace crates can have different patch versions (since 0.8.0).
Resolve a mutually compatible version for each crate rather than assuming
`leptos`, `leptos_macro`, `server_fn_macro`, and the rest of the workspace all
receive matching patch bumps.

Applications with a direct Axum dependency should align it with Axum 0.8 and
update their route syntax; the Leptos integration targets that Axum line and
reexports some Axum types.

## Islands features

The former `experimental-islands` Cargo feature was renamed to `islands` in
0.7.0. For client-side route navigation in an islands application without
hydrating the full app, enable the relevant `islands-router` features added in
0.8.0.

## Thread-local wrapper cleanup

`LocalResource` no longer exposes `SendWrapper` in returned values (since
0.8.0). Remove wrapper-specific calls such as `.as_deref()` and use the value
directly. Actions likewise no longer expose `SendOption` in their public API.
