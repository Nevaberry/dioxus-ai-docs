# Migration Notes and Edge Cases

Use this reference while upgrading an application or diagnosing behavior that
depends on an exact framework, CLI, renderer, or dependency version.

## Component and runtime migration

### Scope and element changes

The 0.5.0 line removed component `Scope` arguments and bump lifetimes. Runtime
helpers no longer take a scope, `Element` is static, and signal handles are
copyable independently of their values.

The 0.6.0 line changed `Element` from optional to result-based. Replace
`VNode::None` with `rsx! {}` and propagate ordinary errors with `?`; older
`.throw()` calls are usually unnecessary.

### Props

The 0.6.0 props derive rejects names beginning with an uppercase letter.
`#[props(into)]` is ignored on `String`, because string props accept
`ToString`; explicitly convert a type that implements only `Into<String>` or
add `ToString`.

`ReadOnlySignal` was deprecated in 0.7.0. Prefer `ReadSignal`, `ReadStore`, or a
generic `Readable` bound. Generated generic props stopped requiring excess
`Clone` bounds in 0.7.6.

### Global and coroutine APIs

During 0.6.0, `GlobalSignal` and `GlobalMemo` became aliases over `Global`, and
`.resolve()` replaced `.signal()` and `.memo()`. `use_coroutine` now accepts
`FnMut`, allowing the closure to restart without rerendering its component.

### Prelude removals

In 0.7.0, `schedule_update` and `schedule_update_any` stopped being prelude
exports. `Runtime`, `queue_effect`, and `provide_root_context` also require
explicit imports. Conversely, `use_drop` entered the prelude in 0.7.2.

## Crate and dependency boundaries

### Unified framework crate

The `dioxus-lib` crate was removed in 0.7.0. Use the main crate with its `lib`
feature and replace `dioxus_lib` paths:

```toml
[dependencies]
dioxus = { version = "0.7", default-features = false, features = ["lib"] }
```

### Fullstack public types

Dioxus's `ServerFnError` is distinct from the identically named generic
`server_fn` type and converts into `dioxus::Error`. Imports and public
signatures may need adjustment.

When types cross Dioxus APIs, direct dependencies must align with the expected
ecosystem versions, including Axum 0.8, Wry 0.52, and server-fn 0.7 for the
stable 0.7 boundary.

### Refresh a stale lockfile

The 0.7.5 release corrected dependency minimums, including `futures`, without
publishing a new `dioxus` crate. A preexisting lockfile can retain versions too
old to compile:

```sh
cargo update
```

Try this before rewriting application code.

## Router migration

With the Web feature enabled, 0.6.0 `#[derive(Routable)]` rejects variant fields
that do not appear in that variant's route pattern. `ToRouteSegments` now
borrows `&self`, so implement it for `T`, not `&T`.

Web hash history arrived in 0.7.0. Configure browser, hash, LiveView, or memory
history explicitly instead of relying on feature inference. Web base paths are
normalized by trimming surrounding slashes since 0.7.2.

## Forms and event defaults

Event cancellation became synchronous in 0.6.0. The
`dioxus_prevent_default` attribute is obsolete; invoke
`event.prevent_default()` before any `.await`.

Web form behavior changed again in 0.7.0: submission is allowed by default.
Call `prevent_default()` in `onsubmit` when Rust handles the form. Desktop
blocks page navigation separately. LiveView cannot cancel a browser default
from a server-side Rust handler; attach synchronous browser JavaScript.

## Asset migration

The 0.5.0 beta pipeline used the separate Manganis `mg!` macro. The 0.6.0
stable linker-discovered form is `asset!`, and paths are crate-root absolute
with a leading `/`.

The 0.7.0 asset surface unifies configuration under `AssetOptions`. Use
variant-specific builders such as:

```rust
let image = asset!(
    "/assets/image.png",
    AssetOptions::image().with_format(ImageFormat::Avif),
);
```

Configured icon paths have resolved from the crate, not the CLI working
directory, since 0.7.2.

## Server and renderer migration

The 0.6.0 custom server API changed:

- Cargo feature `dioxus/axum` became `dioxus/server`;
- `serve_dioxus_application` takes the component directly;
- `register_server_fns` became `register_server_functions`;
- `ServeConfigBuilder::build` is fallible; and
- `RenderHandleState::new` takes `ServeConfig`.

Bind a development custom server to
`dioxus_cli_config::fullstack_address_or_localhost()` so the CLI proxy can
reach it.

Custom-renderer element modules, event conversion, file engine, resize data,
and document/history service changes are detailed in
[renderers-testing-internals.md](renderers-testing-internals.md).

## Desktop, file, and tool behavior

- Desktop `new_window` is async as of 0.7.0.
- Tokio-backed Desktop file dialogs are async as of 0.7.1.
- `WebFileData::file_path` returns `webkitRelativePath` as of 0.7.2.
- Native file-drop events provide full paths as of 0.7.3.
- `FileStream::from_response` rejects unsuccessful HTTP statuses as of 0.7.2.
- The CLI overrides Cargo profile stripping and performs LLVM stripping itself
  as of 0.7.2.
- A key after the first node in multi-node RSX is ineffective and warns as of
  0.7.2.

## Release-specific operational fixes

### 0.7.4

WebSocket values implement standard stream and sink interfaces, the WASM
builder passes `keep_names`, native FFI can package Swift/Kotlin/Java sources,
iOS widgets can join the app bundle, and tray clicks can show the main window.

### 0.7.5

`#[get]` endpoint errors are no longer rewritten into redirects. Linux
hot-patch linking preserves `-B` search paths. Windows gains AArch64 CLI and
`wasm_opt` support, while WiX Candle receives its FIPS-compliance flag.

### 0.7.6

Web event panics no longer brick later interaction. References can become
attribute values, `inert` is typed, `Action` implements `PartialEq`, split-WASM
filenames are content-hashed, Windows icons work in serve and bundle, Cursor
can host debug sessions, completions are generated by `dx completions`, and
FreeBSD is recognized for `esbuild`.

### 0.7.7

JavaScript asset snippets are classified as ESM, CommonJS, UMD, or generic
JavaScript before invoking `esbuild`, fixing non-ESM bundling.

### 0.7.9

CLI version output includes the current Git SHA, Cargo-installed binaries carry
their version, and self-update works for that install path.

## Preview migration matrix

### Source-built CLI

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

The initial alpha required `cargo install dioxus-cli --locked`.

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The later alpha pins the problematic dependency and restores
`cargo install dioxus-cli`. Apply the command for the selected alpha rather than
averaging the two release-specific rules.

### Component and store contracts

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

Generated component props are non-exhaustive, and derived store accessors
preserve Rust visibility.

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

`ReadStore` conversion from `MappedMutSignal` requires a readable lens.

### Assets and bundles

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The stable 0.7 asset fallback is removed, generated assets enter the pipeline,
and whole resource directories can be copied by the bundler.

### URL and HTTP behavior

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

External navigation can be intercepted, and SSG preserves HTTPS route URLs.

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

Child routes retain query/hash fragments, response-body read errors propagate,
and Fullstack server URL configuration may be repeated or replaced.

### Renderer and event behavior

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

Native rendering accepts custom elements, while hot-patching is on by default
and the watcher discovers Cargo workspace and dependency files.

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

Selection, `beforeinput`, clipboard paste payloads, native synthetic clicks,
and browser-correct SSR form-attribute translation are available.
