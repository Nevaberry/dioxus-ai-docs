# Assets, Styling, RSX, and UI Escape Hatches

Use this reference for linker-discovered assets, directory assets, RSX
attribute semantics, component forwarding, CSS and Tailwind, document-head
elements, JavaScript evaluation, and browser/native UI escape hatches.

## Asset declarations and retention

### Current asset form

The unstable 0.5.0 Manganis form used `mg!`. Since 0.6.0, declare an asset with
`asset!`; the linker discovers declarations even in an upstream library, and
the CLI can minify and deduplicate CSS and emit content-hashed image variants.
Paths begin with `/` and resolve from the current crate root, not the source
file or process working directory.

```rust
let logo = asset!("/assets/logo.png");
```

The hash argument previously required by `asset!` was removed in 0.7.0.
Project-root `/public` files are copied to fixed output paths rather than
content-hashed asset paths.

### Rust reachability controls bundling

An asset is bundled only if its returned `Asset` survives Rust optimization.
Reference exported library assets from the final app, or mark an intentionally
indirect static as used:

```rust
#[used]
static CERTS: Asset = asset!("/assets/keys.cert");
```

### Directories and runtime resolution

`asset!` can include a directory, but its emitted directory name is hashed.
Build child paths from the formatted `Asset`:

```rust
let logging_js = format!("{}/logging.js", asset!("/assets/posthog-js"));
```

`read_asset_bytes` fetches on Web and reads the bundle on native targets.
`asset_path` is limited to filesystem-backed targets and does not work on Web
or Android.

### Processing options

The second argument is an `AssetOptions` builder. Use variant constructors for
typed transformations, such as `AssetOptions::image()`; the old
`ImageAssetOptions::new()` form does not apply.

```rust
let image = asset!(
    "/assets/image.png",
    AssetOptions::image().with_format(ImageFormat::Avif),
);
let stable = asset!(
    "/assets/static/ferrous_wave.png",
    AssetOptions::builder().with_hash_suffix(false),
);
```

Disabling the hash suffix gives a stable output name. Unrecognized files copy
unchanged, and `.scss` assets are compiled and hot-reloaded.

### Preview asset pipeline

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The asset pipeline no longer falls back to 0.7 behavior. Migrate projects that
relied on that compatibility path. The pipeline also accepts generated assets,
so build-produced inputs can participate in normal processing.

## RSX attributes and nodes

### Spreads, merging, and precedence

Since 0.5.0, `#[props(extends = element)]` can collect an element's normal
attributes into a component and `..attributes` can forward them. Repeated
attributes such as `class` merge with spaces where appropriate.

General attribute spreads apply in source order, and later values override
earlier ones. A dynamic `None` removes an attribute entirely; HTML boolean
attributes normalize false values where appropriate.

```rust
rsx! {
    div {
        "aria-current": if active { Some("page") } else { None },
        ..extra_attributes
    }
}
```

### Unknown attributes and web components

Quote unknown names, including `data-*` and raw string event attributes, to
bypass the compile-time attribute set. A dashed tag creates an untyped web
component, so all of its attributes must be quoted.

```rust
rsx! {
    my-web-component {
        "name": "hello, {name}",
        "age": age + 10,
    }
}
```

References to supported values have a blanket `IntoAttributeValue`
implementation since 0.7.6, and `inert` is a recognized global attribute.

### Props spreads and required optional props

Inside a component invocation, `..props` spreads a constructed props value and
explicit fields override it. `Option<T>` props are optional at the call site by
default; `#[props(!optional)]` requires callers to pass even `None`.
`#[props(into)]` enables `Into` conversion, while `String` already supports
formatted RSX values.

### Dynamic nodes and keys

A braced expression accepts any `IntoDynNode`: strings, `Element`,
`Option<T>`, and iterators of dynamic nodes can be inserted directly.

```rust
let warning = show_warning.then(|| rsx! { p { "Check this" } });
let rows = items.iter().map(|item| rsx! {
    li { key: "{item.id}", "{item.name}" }
});
rsx! { {warning} {rows} }
```

In a multi-node RSX body, only a key on the first node is effective; keys later
in the body have warned since 0.7.2.

### Preview SSR form attributes

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

SSR translates `initial_value`, `checked`, and `selected` into their proper
HTML attributes so generated form markup has browser-correct initial state.

## CSS, scoped styles, and Tailwind

Scoped CSS and CSS modules have been available since 0.7.3 for
component-isolated styles.

When a root `tailwind.css` exists, DX automatically downloads and runs the
Tailwind 3 or 4 watcher. Tailwind 4 input must import Tailwind and explicitly
scan Rust sources:

```css
@import "tailwindcss";
@source "./src/**/*.{rs,html,css}";
```

DX writes generated CSS to `/assets/tailwind.css` by default. Include it with a
document stylesheet; `tailwind_input` and `tailwind_output` in `Dioxus.toml`
override the paths.

```rust
rsx! {
    document::Stylesheet { href: asset!("/assets/tailwind.css") }
}
```

For editor completion, configure the Tailwind extension to treat Rust as HTML
and recognize Dioxus class syntax:

```json
{
  "tailwindCSS.experimental.classRegex": ["class: \"(.*)\""],
  "tailwindCSS.includeLanguages": { "rust": "html" }
}
```

## Document-head elements

Since 0.6.0, `dioxus::document` provides `Title`, `Link`, `Stylesheet`, `Style`,
`Meta`, and related elements across renderers. Server rendering collects,
deduplicates, and minifies head entries, so nested components may declare their
own metadata and preload links.

Custom renderers can implement the `Document` service from `dioxus-document`
to support those elements plus scripts and evaluation.

## JavaScript evaluation

`eval` moved out of the prelude in 0.6.0; call `document::eval`. The Rust handle
deserializes directly with `.recv::<T>().await` and sends with `.send(...)`.
Inside the evaluated JavaScript, use `dioxus.send(...)` to send to Rust and
`await dioxus.recv()` to receive from Rust.

```rust
let mut eval = document::eval(r#"
    dioxus.send("ready");
    console.log(await dioxus.recv());
"#);
let ready = eval.recv::<String>().await.unwrap();
eval.send(format!("received {ready}")).unwrap();
```

This message bridge works on Web and Desktop.

## Browser and native UI escape hatches

### Renderer-specific event data

Use `event.downcast::<T>()` when portable event data is insufficient. Raw
quoted event attributes run JavaScript directly; this is particularly useful
in LiveView for latency-sensitive handlers and browser-default cancellation.

```rust
rsx! {
    input { "oninput": "console.log('input changed!')" }
}
```

### Mount handles and browser observers

`onmounted` yields a live element handle after first mount for focus and
scrolling. `onresize` and `onvisible` create browser observation without custom
JavaScript.

### Custom index templates

A custom web `index.html` participates in hot reload but must retain the mount
point:

```html
<div id="main"></div>
```

### Preview native DOM clicks

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The native DOM can synthesize click events, allowing programmatic dispatch
without physical pointer input.

## Hot reload versus asset and code rebuilds

`dx serve` has watched CSS referenced by RSX on Web, Desktop, and Fullstack
since 0.5.0. By 0.6.0 RSX hot reload covered formatted text, attributes,
component props, primitive literal props, and nested RSX in loops,
conditionals, and children across Web, Desktop, and Mobile.

Do not confuse RSX hot reload with Rust hot-patching. In the stable 0.7
workflow, `dx serve --hotpatch` patches the tip crate, while dependency or
other workspace-crate edits require rebuilding even though RSX hot reload
spans the workspace. Existing globals survive a code patch; renamed globals
become new globals, and changed static initializers are not observed. Later
workspace and preview behavior is detailed in
[renderers-testing-internals.md](renderers-testing-internals.md).
