# Migration and Configuration

## Imports and constructor names

Most APIs formerly exported from the crate root are available from the
prelude (since 0.7.0):

```rust
use leptos::prelude::*;
```

Router APIs are grouped by purpose:

```rust
use leptos_router::components::*;
use leptos_router::hooks::*;
```

Constructors use idiomatic Rust naming. In particular, replace
`create_signal(...)` with `signal(...)` and `create_rw_signal(...)` with
`RwSignal::new(...)`. Apply the corresponding constructor-style migration to
other reactive primitives rather than searching for another `create_*` free
function.

## Thread-safe and local storage

Reactive primitives use `SyncStorage` by default and therefore require their
data to be `Send + Sync` (since 0.7.0). For `Rc` or another thread-local type,
select `LocalStorage` or use an API's `_local` constructor:

```rust
let shared = RwSignal::new("value");
let local = RwSignal::new_local(std::rc::Rc::new("value"));
```

Do not weaken thread-safety elsewhere merely to accommodate a local value;
make the storage decision at the reactive primitive.

## Leptos options and configuration

`LeptosOptions` string fields are `Arc<str>` (since 0.7.0). Borrow them or
call `.as_ref()` where a consumer expects `&str`.

`LeptosOptions` and `ConfFile` do not implement `Default` (since 0.8.0).
Construct or load them explicitly instead of calling `LeptosOptions::default()`
or `ConfFile::default()`.

Use `LeptosOptions::css_file_path` for the configured stylesheet path. Do not
use the briefly introduced `css_path` spelling; it was replaced within the
same release line.

## Dependency alignment

Workspace crates receive patch releases independently (since 0.8.0). Do not
assume `leptos`, `leptos_macro`, `server_fn_macro`, and other related crates
always have the same patch number. Let the resolver select compatible releases
or specify compatible versions per crate.

The Axum integration targets Axum 0.8. If an application directly depends on
Axum in addition to using reexported integration types, update the direct
dependency and its changed route syntax at the same time.

## Feature and component migrations

The Cargo feature formerly named `experimental-islands` is named `islands`
(since 0.7.0). Use the separate `islands-router` features when an islands
application also needs client-side navigation.

`Stylesheet` does not automatically participate in `cargo-leptos` filename
hashing. When hashed asset filenames are enabled, use `HashedStylesheet` and
provide the corresponding props.
