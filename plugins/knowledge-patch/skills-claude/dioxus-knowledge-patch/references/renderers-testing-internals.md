# Renderers, Testing, Hot-Patching, and Internals

## Renderer choices

The maintained first-party directions are web, desktop, mobile (a thin layer
over the desktop webview), and native. LiveView remains supported but is
deprioritized in favor of fullstack and may be removed; avoid beginning new
architecture on it. `dioxus-tui` is deprecated and lives on a legacy Blitz
branch.

Dioxus Native/Blitz, introduced publicly around `0.7.0`, renders through WGPU
without a webview, using Taffy for layout, Stylo for CSS, and Vello for painting.
Blitz can also be used as a modular HTML/CSS engine. Native CSS coverage and
performance are still works in progress.

The `native-dom` package isolates the bridge between Blitz and `dioxus-core`,
allowing a host such as a Bevy game to keep ownership of its window/input loop
while embedding a Dioxus UI. Native apps can import
`dioxus_native::prelude::*` since `0.7.3`.

## Writing a custom renderer

The renderer applies Dioxus's `Mutation` stream and feeds platform events back;
Dioxus owns the virtual tree, diffing, memory management, and event dispatch.
Mutations form a stack machine rather than a list of direct node addresses:

- `LoadTemplate`, `CreatePlaceholder`, and `CreateTextNode` push real nodes.
- `AppendChildren`, `InsertAfter`, `InsertBefore`, `ReplacePlaceholder`, and
  `ReplaceWith` pop nodes; their `m` field is the count.
- The mount node starts on the stack as `ElementId(0)`.
- Other instructions include `AssignId`, `HydrateText`, `SetAttribute`,
  `SetText`, listener add/remove, `Remove`, and `PushRoot`.

Dioxus reclaims `ElementId`s after removal. Store renderer nodes in a sparse
`Vec<Option<T>>` indexed by ID and grow it as needed; never assume an ID remains
globally unique.

`LoadTemplate` names a compile-time-static `Template` delivered the first time
it is used. Clone it per instantiation. `node_paths` and `attr_paths` are child-
index paths from a root to dynamic holes, which later mutations hydrate or
replace.

```rust
Template {
    name: "main.rs:1:1:0",
    roots: &[TemplateNode::Element {
        tag: "h1",
        namespace: None,
        attrs: &[],
        children: &[TemplateNode::DynamicText { id: 0 }],
    }],
    node_paths: &[&[0, 0]],
    attr_paths: &[],
}
```

HTML and SVG namespaces are helpers that compile away. A renderer may define
its own element/attribute namespace while retaining components, hooks, and
shared state.

## RSX hot reload

RSX hot reload and compiled-code patching are separate systems. Since `0.6.0`,
RSX reload covers formatted strings in markup and component props, literal prop
values, nested RSX in loops/conditions, and component children.

To decide whether an edit is data-only, the dev server blanks each `rsx!` body
and doc comment in old and new files and compares the remaining Rust. Any other
Rust change triggers a rebuild. Inside RSX, it rematches a pool of dynamic items
from the last compilation, so these can reload:

- literal changes and markup restructuring;
- moving attributes;
- reusing an already compiled formatted segment such as `"{count}"`.

A new Rust expression, changed control-flow condition, or changed number of
`rsx!` macros forces a full rebuild.

## Subsecond compiled-code patching

Introduced in `0.7.0`, Subsecond patches compiled Rust functions into a running
process without discarding application state. Dioxus components and server
functions are automatic. Other Rust code crosses an explicit
`dioxus::subsecond::call` site, which is also a synchronization point where a
framework can drop listeners or recreate state.

```rust
loop {
    std::thread::sleep(std::time::Duration::from_secs(1));
    dioxus::subsecond::call(|| tick());
}
```

Starter integrations exist for Axum, Bevy, and Ratatui. A non-Dioxus program can
connect through `dioxus_devtools::connect_subsecond()` and route hot code through
`dioxus_devtools::subsecond::call`. For an async entry point,
`serve_subsecond_with_args` drops and recreates the future around each patch.

### Default serve behavior

> **Prerelease (`0.8.0-alpha.0`):** This guidance may change before stable release.

Compiled-code hot-patching is enabled by default under `dx serve`; the explicit
`--hotpatch` flag is unnecessary. The watcher also reacts to manifest changes
and configured watch paths.

### Hard limits

Subsecond uses a global indirection/jump table. A struct size or alignment change
cannot migrate live state and may crash rather than gracefully rebuild. Dispose
or migrate affected state and force a full restart.

Dioxus `0.7.4` added workspace-aware hot-patching orchestration. At the
low-level patch boundary, only the selected tip crate is patched; changes in
other workspace crates or dependencies require a separate build or patch
boundary.

Other limits:

- Tip-crate thread locals reset on every patch; dependency thread locals keep
  their values.
- Static initializer changes are not observed.
- Newly introduced globals never run their destructors; renaming a global makes
  it a new global.
- Supported targets include desktop Linux/macOS/Windows on x86_64/aarch64,
  Android, iOS simulator, and WASM. Signed iOS devices are excluded.

Press `r` in the `dx serve` TUI when these limits require a full rebuild.

## WASM splitting

`#[wasm_split(name)]` on an async function moves that function and code reachable
only through it into an on-demand module. Awaiting it loads the module
transparently. Outputs include `main.wasm`, split-point `module_*` files, shared
`chunk_*` files, and a `__wasm_split.js` loader. All modules share the main
module's memory and indirect function table, so ordinary Rust values cross the
boundary.

```rust
#[wasm_split(admin_panel)]
async fn load_admin_panel() -> AdminPanel {
    AdminPanel::new()
}
```

Libraries can declare a split boundary with `#[lazy_loader]`. It yields a
`LazyLoader<Args, Return>` whose async `.load()` prepares the code and whose
synchronous `.call(args)` returns `NotLoaded` or `LoadFailed` when unavailable.
`extern "auto"` merges discovered code into a single module.

```rust
#[lazy_loader(extern "auto")]
fn my_lazy_fn(value: i32) -> i32;
```

Split points must be async and are discovered at compile time; there are no
dynamic imports. The splitter needs the pre-`wasm-bindgen` binary with
relocations, debug symbols, and LTO, so use `dx`, not a hand-built `wasm-pack`
pipeline. Router variants can expose the same mechanism through
`#[wasm_split("/route")]` and display a loading state during navigation.

## Testing hooks with `VirtualDom`

There is no dedicated hook-test library. Wrap the hook in a test component,
create a `VirtualDom`, call `rebuild_in_place()` for the first render, then drain
scheduled work with `wait_for_work()` and
`render_immediate(&mut NoOpMutations)`. Run assertions inside the root reactive
scope. `NoOpMutations` lives under `dioxus::dioxus_core`, not the prelude.

```rust
use dioxus::{dioxus_core::NoOpMutations, prelude::*};
use futures::FutureExt;

let mut vdom = VirtualDom::new_with_props(mock_app, props);
vdom.rebuild_in_place();

while vdom.wait_for_work().now_or_never().is_some() {
    vdom.render_immediate(&mut NoOpMutations);
}

vdom.in_scope(ScopeId::ROOT, || {
    assert_eq!(dioxus::core::generation(), 4);
});
```

Inside the component, `dioxus::core::generation()` reports its render count and
`dioxus::core::schedule_update()` returns an `Arc<dyn Fn()>` that forces another
pass, allowing a test to advance a hook through successive generations.

## Comparing RSX output

Elements are not directly comparable. Render both with standalone SSR and
compare their strings; `render_element` takes an owned `Element`.

```rust
fn assert_rsx_eq(first: Element, second: Element) {
    pretty_assertions::assert_str_eq!(
        dioxus_ssr::render_element(first),
        dioxus_ssr::render_element(second),
    );
}
```

For browser end-to-end tests, point Playwright's `webServer.command` at
`dx serve` on port 8080 and allow a generous first-build timeout. Rust source
debugging in Chrome requires the DWARF-aware extension.

## Standalone SSR and `!Send` virtual DOMs

`dioxus-ssr` works inside any web framework without `dioxus-fullstack`. Build
such a normal Rust service with `cargo run`, not `dx serve`. `render_element`
takes owned RSX output; `render(&vdom)` needs a `VirtualDom` rebuilt first.

```rust
let mut vdom = VirtualDom::new(app);
vdom.rebuild_in_place();
let html = dioxus_ssr::render(&vdom);
```

A `VirtualDom` is not `Send` and must remain on its creating thread. A
`Send`-requiring handler may construct and render one to a `String`, but cannot
hold it across `.await`. Retained-state SSR therefore needs one DOM per thread
communicating over channels, or a thread-local pool.

## Renderer verification

- Cache and clone templates exactly when first delivered.
- Reuse reclaimed `ElementId`s safely and validate sparse storage growth.
- Test the mutation push/pop count and root stack state.
- Convert platform event data back into the types expected by Dioxus.
- Exercise hydration paths separately from fresh mounts.
- Force full rebuilds for state-layout changes and dependency edits that exceed
  hot-patch boundaries.
