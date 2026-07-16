# Migration Notes and Edge Cases

## Component and runtime migrations

### Scope and element representation

The 0.5.0 component API removed `cx: Scope`, bump lifetimes, and scope arguments from runtime helpers. The 0.6.0 element representation then changed `Element` from `Option<VNode>` to a result. Replace `VNode::None` with `rsx! {}` and propagate ordinary errors with `?`; `.throw()` is only needed when maintaining transitional code from the earlier error API.

`use_signal` handles are `Copy`, but their values remain owned by the creating component and are disposed on unmount. A copied handle is not permission to read it after its owner is gone.

### Signal and global APIs

`ReadOnlySignal` is deprecated in 0.7.0. Prefer `ReadSignal`, `Readable`, or store projections. `GlobalSignal` and `GlobalMemo` became aliases over `Global`; `.resolve()` replaces the former `.signal()` and `.memo()` accessors.

`schedule_update` and `schedule_update_any` are no longer prelude exports. `Runtime`, `queue_effect`, and `provide_root_context` also left the prelude in 0.7.0. Import these low-level APIs explicitly if they are still necessary.

`use_coroutine` accepts `FnMut` as of 0.6.0, so one coroutine closure can restart without forcing its component to rerender.

### Props derive constraints

The 0.6.0 props derive rejects property names beginning with an uppercase letter. It ignores `#[props(into)]` on `String`, because string props already use `ToString`; explicitly convert a type that implements only `Into<String>` or add `ToString`.

Generated generic properties stopped receiving excess `Clone` bounds in 0.7.6. Preview-generated component props are non-exhaustive in 0.8.0-alpha.0, and preview store accessors enforce the source member's Rust visibility.

## Event and RSX behavior changes

Event dispatch is synchronous. Remove `dioxus_prevent_default` and call `event.prevent_default()` before any `.await`. Web form submission is allowed by default in 0.7.0, reversing the 0.6.0 inverted behavior; Desktop separately blocks page navigation. LiveView requires browser-side JavaScript for cancellation.

In multi-node RSX, put the key on the first node; later keys do not apply to the group and warn as of 0.7.2.

Native event access evolved from renderer helpers such as `.web_event()` to downcasting through `event.downcast::<T>()`. A custom renderer's 0.7.0 event attributes convert into `ListenerCallback<T>`, not component-level `EventHandler<Event<T>>`.

## Router migration constraints

With the Web feature enabled, the 0.6.0 `Routable` derive rejects variant fields absent from the route pattern. `ToRouteSegments` now borrows `&self`, so implement it for `T`, not `&T`.

Web routing has a hash-history provider for hosts without path fallback. LiveView's router does not integrate with browser history. Configure history explicitly rather than relying on platform-feature inference.

Applications using preview APIs can opt into a handler for external URL navigation in 0.8.0-alpha.0, allowing navigation away from the app to be intercepted or customized.

## Fullstack server migrations

### Custom server entrypoints

The Cargo feature formerly named `dioxus/axum` is `dioxus/server`. During the 0.6.0 server API transition:

- `serve_dioxus_application` began taking the component directly;
- `register_server_fns` became `register_server_functions`;
- `ServeConfigBuilder::build` became fallible;
- `RenderHandleState::new` gained a `ServeConfig` argument;
- per-platform configuration moved from one Fullstack `Config` into `LaunchBuilder`.

Bind custom development servers with `dioxus_cli_config::fullstack_address_or_localhost()` so DX can reverse-proxy them.

### Public dependency boundaries

The identically named `ServerFnError` is now Dioxus's own type instead of generic `server_fn::ServerFnError`; adjust imports. It converts into `dioxus::Error`. Direct dependency types crossing Dioxus APIs must align with Axum 0.8, Wry 0.52, and server-fn 0.7.

The `dioxus-lib` crate was removed in 0.7.0. Replace `dioxus_lib` paths with `dioxus`; depend on the main crate with `default-features = false, features = ["lib"]` for the framework-only surface.

```toml
[dependencies]
dioxus = { version = "0.7", default-features = false, features = ["lib"] }
```

### Durable behavior changes

- `FileStream::from_response` checks HTTP status as of 0.7.2; handle unsuccessful responses instead of consuming them as file data.
- `#[get]` endpoint failures remain errors rather than turning into redirects as of 0.7.5.
- Anonymous server functions can use server-only extractors as of 0.7.3.
- Static generation preserves HTTPS route URLs in 0.8.0-alpha.0.
- Native clients should use explicit stable route paths because generated anonymous-server-function URLs can change with code.

## Asset and styling migrations

Replace the unstable 0.5.0 `mg!` declaration with linker-discovered `asset!`. Asset source paths are crate-root absolute since 0.6.0 and must begin with `/`. `asset!` no longer requires a manual hash.

Manganis 0.7 unifies options under `AssetOptions`; use constructors such as `AssetOptions::image()` rather than `ImageAssetOptions::new()`.

The CLI resolves configured icons relative to the crate as of 0.7.2. JavaScript bundling detects ESM, CommonJS, UMD, and generic snippets as of 0.7.7. Preview esbuild downloads honor `NPM_CONFIG_REGISTRY`.

## CLI and lockfile edge cases

### Stable dependency correction

The 0.7.5 release corrected minimum versions for dependencies such as `futures` without publishing a new `dioxus` crate. An existing `Cargo.lock` can retain versions too old to compile. Refresh the lockfile before rewriting source:

```sh
cargo update
```

### Preview CLI install

The 0.8.0-alpha.0 CLI requires `cargo install dioxus-cli --locked` when built from source. Its hot-patching default and broader watcher behavior are preview-only.

### Build and bundle ownership

DX overrides Cargo profile `strip` and performs stripping through LLVM. Desktop bundles can target only the host OS and architecture. Files under `/public` and configured asset directories follow different paths: `/public` has fixed output paths, while `asset!` values are pipeline-managed and usually content-hashed.

## Native platform edge cases

- Desktop `new_window` is async in 0.7.0; Tokio-backed file dialogs are async in 0.7.1.
- Web `WebFileData::file_path` returns `webkitRelativePath` when available as of 0.7.2; native drop events provide full paths as of 0.7.3.
- Android's generated application ID follows `bundle.identifier`, and the minimum SDK is 28.
- An iOS Simulator supports hot-patching; a code-signed physical iOS device does not.
- Native FFI compilation runs after `rustc`, so Rust cannot import headers generated by the Swift/Kotlin/C compilation stage.
- Plugin crates cannot inject app permissions; add their documented permissions to the application's top-level table.

## Hot-patch interpretation

Do not conflate these mechanisms:

- RSX hot reload updates supported literals and nested markup broadly without rebuilding Rust code.
- Initial stable Subsecond patching modifies Rust code in the tip crate while retaining compatible runtime state.
- Workspace Rust patching was added in 0.7.4.
- Structural state migrations, changed static initializers, some dependency changes, and unsupported platforms still require rebuild or restart.
- Preview watcher and default behavior differ from stable releases.

Thread-local state in a patched tip crate resets each patch, renamed globals create new globals, and newly added global destructors are not run.

## Packaging edge cases

- A Fullstack Web bundle contains both `public` and a server executable; deploy both.
- `index_on_404` affects the DX development server, not an external Web host.
- Sidecar source filenames contain target triples, but runtime lookup uses the unsuffixed name.
- WiX `upgrade_code` must remain stable across app updates.
- macOS signing and Windows certificate/timestamp settings are target-specific and should be tested on the host that creates the installer.
- Windows on ARM tooling and FIPS-compatible WiX invocation arrived in 0.7.5.

## Preview boundary

Do not assume stable applications have the following 0.8.0-alpha.0 behavior: default hot-patching, Cargo-aware dependency watching, non-exhaustive generated props, visibility-witness store accessors, external-URL interception, Native custom elements, registry-aware esbuild downloads, or HTTPS-preserving SSG. Check the selected crate and CLI versions before using them.
