# Renderers, Testing, Hot-Patching, and Internals

## Desktop and renderer services

Desktop custom asset handlers can stream bytes directly from Rust into the WebView without a JavaScript encoding layer. File drops use the normal event system and provide full paths rather than requiring external interception.

Desktop child windows can overlay an existing WGPU or OpenGL window, and an application with its own windows can provide Dioxus a custom event loop. System-tray support is available. The `dioxus-document` abstraction lets a custom renderer implement the `Document` service used by `Title`, `Script`, and `eval`; `dioxus-history` makes `Link` and `Router` renderer-independent. A custom renderer crate can enable `third-party-renderer` to suppress the no-active-platform warning.

## Dioxus Native and Blitz

Dioxus Native, introduced in 0.7.0, is an experimental WGPU renderer built on the separately reusable Blitz engine. It covers accessibility, events, assets, HTML/CSS layout, and text painting. Less-common CSS and JavaScript-dependent pages remain incomplete, so it is not a drop-in browser.

Native rendering can embed Dioxus in Bevy or WGPU applications and run on embedded Linux. Dioxus Native adds application-defined custom elements in 0.8.0-alpha.0 along with broader incremental-rendering improvements.

LiveView remains supported but is deprioritized in favor of Fullstack and may be removed. Its router renders without a separate renderer-specific integration, but it does not synchronize with browser history. The older TUI renderer is deprecated and remains only in Blitz's legacy tree.

## Rust hot-patching with Subsecond

### Runtime behavior

The 0.7.0 Subsecond integration patches Dioxus components and server functions on Web, Desktop, and Mobile while retaining running state. It can serve any Rust project, but non-Dioxus code needs explicit `subsecond::call` synchronization points. Changed struct layouts are not migrated.

```rust
loop {
    std::thread::sleep(std::time::Duration::from_secs(1));
    subsecond::call(|| tick());
}
```

In the initial stable workflow, opt in with `dx serve --hotpatch`. Patches were limited to the tip crate even though RSX hot reload spanned a workspace. Existing globals survived, renamed globals became new globals, and changed static initializers were not rerun. Workspace crate hot-patching arrived in 0.7.4; do not apply the earlier tip-crate limitation to versions with that support.

```sh
dx serve --hotpatch
```

Thread-local values defined in the patched tip crate reset to their initializer on each patch, while dependency thread-locals behave normally. Destructors for newly introduced globals do not run. Patching supports the iOS Simulator, but not code-signed physical iOS devices.

Linux thin/patch linking forwards `-B` linker search paths as of 0.7.5. Preview hot-patching is enabled by default in 0.8.0-alpha.0, whose watcher covers `Cargo.toml`, configured watch paths, and Cargo-discovered dependency files.

## WebAssembly splitting

### Route and function split points

`#[wasm_split]` on a route emits it as a lazy WebAssembly chunk fetched during first navigation. A named `#[wasm_split(name)]` can instead mark an async function as a statically discovered, Web-only boundary; calling and awaiting it loads its module before executing.

```rust
#[wasm_split(admin_panel)]
async fn load_admin_panel() -> AdminPanel {
    AdminPanel::new()
}

let panel = load_admin_panel().await;
```

The build passes through `keep_names` as of 0.7.4 for better WebAssembly stack traces. Bundled split chunks use content-hashed filenames as of 0.7.6.

### Low-level lazy loaders

Libraries can declare `#[lazy_loader(extern "auto")]`. The generated `LazyLoader::load().await` reports load success, and `.call(args)` returns `SplitLoaderError::NotLoaded` or `LoadFailed` when invocation cannot proceed. The `"auto"` ABI groups all discovered modules into one load unit.

```rust
#[lazy_loader(extern "auto")]
fn my_lazy_fn(x: i32) -> i32;
```

## Custom renderer contracts

### API migrations

A renderer moving to 0.6.0 must:

- use `dioxus_devtools::connect`;
- expose each custom element as a module containing `TAG_NAME`, `NAME_SPACE`, and attribute constants;
- provide top-level `completions::CompleteWithBraces`;
- route event attributes through `eventname::call_with_explicit_closure`;
- implement `FileEngine::file_size` and `HtmlEventConverter::convert_resize_data`;
- stop selecting the removed `dioxus-html` `web`/`native` features.

In 0.7.0, renderer event attributes convert into `ListenerCallback<T>` rather than component-facing `EventHandler<Event<T>>`.

### Mutation stack machine

A renderer consumes static templates plus `Mutation` edits as a stack machine. It maintains reusable `ElementId` mappings, reserves ID 0 for the root, and tolerates reclaimed IDs. Its event loop waits for platform input and `VirtualDom::wait_for_work`, applies generated mutations, and translates native input into Dioxus `UserEvent` values.

When a template is first used, it appears in `Mutations.templates`; build and cache its static tree before applying related edits. `LoadTemplate`, `CreatePlaceholder`, and `CreateTextNode` push nodes. Append, insert, and replace edits consume nodes. Dynamic paths inside cloned templates locate placeholders for operations such as `HydrateText`.

## Direct SSR

`dioxus_ssr::render_element` renders an RSX value directly. To render a `VirtualDom`, rebuild it first and pass a shared reference to `dioxus_ssr::render`.

```rust
let element_html = dioxus_ssr::render_element(rsx! { div { "hello" } });

let mut vdom = VirtualDom::new(App);
vdom.rebuild_in_place();
let vdom_html = dioxus_ssr::render(&vdom);
```

A `VirtualDom` is not `Send` and cannot be held across `.await`. Stateful low-level SSR must keep each DOM on a dedicated thread and communicate through channels, or use a pool of thread-bound DOMs.

## Testing

Component output can be asserted by rendering RSX with `dioxus-ssr`. There is no complete hook-testing harness; manually drive a `VirtualDom` for hook tests. End-to-end browser tests can let Playwright own the development server through its `webServer` configuration.

```js
webServer: {
    command: "dx serve",
    port: 8080,
    reuseExistingServer: !process.env.CI,
}
```

For custom renderer tests, verify template caching, stack order, reclaimed IDs, hydration edits, event conversion, and concurrent wakeups from both the platform and `wait_for_work`.

## LiveView browser escape hatches

LiveView handlers normally round-trip through the server. A quoted raw event attribute executes JavaScript in the browser for latency-sensitive interaction or synchronous default prevention.

```rust
rsx! {
    input { "oninput": "console.log('input changed!')" }
}
```

LiveView routing does not synchronize its route state with browser history. Treat it as renderer-local routing rather than `WebHistory` behavior.

## Native plugin FFI

Manganis added native Mobile FFI in 0.7.4. `#[manganis::ffi]` source assets may be Swift, Kotlin, Java, or C files/directories; DX bundles and compiles them into the generated project and creates Rust interfaces. Foreign blocks may declare opaque objects with `pub type`; arguments must be pointer-like or otherwise coercible across the language boundary.

```rust
#[manganis::ffi("/src/ios")]
extern "Swift" {
    pub type SomeSwiftObject;
    pub fn do_thing(this: &SomeSwiftObject) -> Option<u32>;
}
```

Calls use runtime lookup such as JNI or Objective-C. Native compilation occurs after `rustc`, so Rust code cannot consume headers or other outputs generated by that native compilation. Plugin libraries also cannot add permissions automatically; document the required application-level `[permissions]` entries.
