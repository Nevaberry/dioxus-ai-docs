# Renderers, Testing, Hot-Patching, and Internals

Use this reference for Dioxus Native and Blitz, custom renderers, LiveView,
direct SSR, component and browser testing, Subsecond hot-patching, WASM
splitting, and native plugin ABI constraints.

## Dioxus Native and Blitz

Dioxus Native debuted in 0.7.0 as a WGPU renderer backed by the separately
reusable Blitz engine. It provides accessibility, events, assets, HTML/CSS
layout, and text painting, but incomplete less-common CSS and
JavaScript-dependent behavior means it is not a drop-in browser replacement.

The renderer can embed Dioxus in Bevy or WGPU applications and run on embedded
Linux. Desktop can also overlay a child window over an existing WGPU/OpenGL
window or integrate with an application-owned event loop.

### Preview custom native elements

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

The Native renderer accepts application-defined custom elements and includes
broader rendering and incremental-rendering improvements.

## Custom renderer protocol

A renderer owns a `VirtualDom`, waits for both platform input and
`VirtualDom::wait_for_work`, applies generated `Mutation` edits, and converts
native input into Dioxus `UserEvent` values.

The mutation stream is a stack machine:

- Store `ElementId` mappings with root ID 0 and tolerate reclaimed IDs.
- Build and cache each static tree when it first appears in
  `Mutations.templates`.
- `LoadTemplate`, `CreatePlaceholder`, and `CreateTextNode` push nodes.
- Append, insert, and replace operations consume nodes.
- Dynamic template paths locate placeholders for operations such as
  `HydrateText`.

Since 0.6.0, the `dioxus-document` service lets a renderer support document
elements and `eval`; `dioxus-history` supplies `Link` and `Router` independently
of a renderer-specific router feature. Enable `third-party-renderer` to avoid
warnings when no built-in platform is active.

### Custom-renderer migration contracts

When upgrading to 0.6, custom renderers must:

- connect through `dioxus_devtools::connect`;
- expose custom elements as modules with `TAG_NAME`, `NAME_SPACE`, and
  attribute constants;
- provide top-level `completions::CompleteWithBraces`;
- route event attributes through `eventname::call_with_explicit_closure`;
- implement `FileEngine::file_size` and
  `HtmlEventConverter::convert_resize_data`; and
- remove the former `dioxus-html` `web`/`native` features.

In 0.7.0, renderer event attributes convert into `ListenerCallback<T>` rather
than the component-facing `EventHandler<Event<T>>`.

## Direct SSR

Use `dioxus_ssr::render_element` for an RSX value. A `VirtualDom` must be
rebuilt before passing it to `dioxus_ssr::render`.

```rust
let html = dioxus_ssr::render_element(rsx! { div { "hello" } });

let mut vdom = VirtualDom::new(App);
vdom.rebuild_in_place();
let html = dioxus_ssr::render(&vdom);
```

A `VirtualDom` is not `Send` and cannot be held across `.await`. Retained-state
SSR must keep it on its own thread and communicate through channels, or use a
pool of thread-bound virtual DOMs.

## Testing

Render component RSX with `dioxus-ssr` for output assertions. There is no
complete hook-testing helper, so hook tests manually drive a `VirtualDom`.

For browser end-to-end tests, let Playwright own the development server:

```js
webServer: {
    command: "dx serve",
    port: 8080,
    reuseExistingServer: !process.env.CI,
}
```

Custom-renderer tests should cover template caching, stack consumption,
placeholder hydration, reclaimed IDs, event conversion, and wakeups from both
platform and virtual-DOM work.

## LiveView and legacy renderers

LiveView can render the router, but it does not integrate route state with
browser history. Its Rust handlers execute on the server and cannot cancel a
browser default in time; use a quoted raw JavaScript event attribute for
latency-sensitive work or synchronous cancellation.

LiveView remains supported but is deprioritized in favor of Fullstack and may
be removed. The older TUI renderer is deprecated and remains only in Blitz's
legacy tree.

## Rust hot-patching

### Runtime behavior

Subsecond support arrived in 0.7.0 for component and server-function code on
Web, Desktop, and Mobile while preserving application state. Non-Dioxus code
needs explicit `subsecond::call` synchronization points. Changed struct layouts
are not migrated.

```rust
loop {
    std::thread::sleep(std::time::Duration::from_secs(1));
    subsecond::call(|| tick());
}
```

In the stable 0.7 workflow, `dx serve --hotpatch` patches the tip crate. RSX
hot reload can span a workspace while Rust edits in dependencies or other
workspace crates still rebuild. Workspace hot-patching support was added in
0.7.4.

Existing globals survive patches, renamed globals become new globals, and
changes to static initializers are not observed. A thread-local defined in the
patched tip crate resets to its initializer for every patch, while dependency
thread-locals behave normally. Destructors for newly added globals do not run.

Hot-patching supports the iOS Simulator but not code-signed iOS devices. Linux
thin and patch linking has forwarded `-B` linker search paths since 0.7.5.

### Preview default and watcher

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

Hot-patching is enabled by default, and Cargo dependency discovery plus
configured watch paths lets workspace and dependency edits trigger the
appropriate patch, reload, or rebuild.

## WASM splitting

### Route chunks

Since 0.7.0, `#[wasm_split]` can place route variants in independently loaded
WASM chunks. The router downloads a chunk on first navigation and displays a
loading state. Bundle filenames became content-hashed in 0.7.6.

```rust
#[derive(Routable, Clone, PartialEq)]
enum Route {
    #[route("/")]
    Home,
    #[wasm_split("/dashboard")]
    Dashboard,
}
```

### Function split points

`#[wasm_split(name)]` creates a statically discovered, WASM-only async boundary.
Calling and awaiting it loads the module before executing the function.

```rust
#[wasm_split(admin_panel)]
async fn load_admin_panel() -> AdminPanel {
    AdminPanel::new()
}
```

### Low-level loaders

Libraries can declare `#[lazy_loader(extern "auto")]`. Its `LazyLoader` reports
load success through `.load().await`; `.call(args)` returns
`SplitLoaderError::NotLoaded` or `LoadFailed` when invocation is impossible.
The `"auto"` ABI combines discovered modules into one load unit.

## Native plugins

The `manganis::ffi` path added in 0.7.4 bundles Kotlin, Java, and Swift sources
and creates Rust interfaces, making native plugins part of the Dioxus build.

`#[manganis::ffi]` sources may be files or directories of Swift, Kotlin, or C.
Foreign blocks may declare opaque objects with `pub type`; arguments must be
pointer-like or otherwise cross-language-coercible. Runtime lookup uses JNI or
Objective-C.

```rust
#[manganis::ffi("/src/ios")]
extern "Swift" {
    pub type SomeSwiftObject;
    pub fn do_thing(this: &SomeSwiftObject) -> Option<u32>;
}
```

Native compilation runs after `rustc`, so Rust cannot consume headers or other
outputs generated by that compilation. Plugins also cannot inject their own
permissions; document required permissions for the application to place in
`Dioxus.toml`.
