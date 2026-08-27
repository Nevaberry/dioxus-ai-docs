# Assets, Styling, RSX, and UI Escape Hatches

## Asset collection and lifetime

`asset!` declares an asset from an absolute path rooted at the current crate,
for example `asset!("/assets/logo.png")`. Since `0.6.0`, metadata is collected
from a linker section, which allows assets declared by dependency crates to be
optimized, deduplicated, hashed, and included in the final application.

The linker does not imply retention: if the resulting `Asset` is optimized away,
the file is not bundled. This allows libraries to expose assets without forcing
all of them into every consumer. Keep the value reachable from application code
or annotate an intentionally indirect static:

```rust
#[used]
static CERTS: Asset = asset!("/assets/keys.cert");
```

The `0.5.0` predecessor was the standalone `manganis` crate's `mg!` macro.
Current code should use `asset!`; see the migration reference before editing a
project actually pinned to that older API.

## Directories and asset options

`asset!` accepts a directory. The emitted directory name is hashed, so derive a
child URL from the returned `Asset` rather than the source folder name:

```rust
let root = asset!("/assets/posthog-js");
let logging_js = format!("{root}/logging.js");
```

The optional second argument is an `AssetOptions` builder and can, among other
things, disable the hash suffix:

```rust
let image = asset!(
    "/assets/ferrous.png",
    AssetOptions::builder().with_hash_suffix(false),
);
```

SCSS files declared this way compile to CSS without extra setup and participate
in hot reload.

### Generated inputs

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

The asset pipeline accepts files generated during the build, not only files
already committed to the project tree.

## Reading asset contents

An `Asset` is a URL-like `Display` value, not its bytes. Use the separate
`dioxus-asset-resolver` crate to locate or read the bundle entry:

- `read_asset_bytes` fetches over the network on web and reads from the native
  bundle elsewhere.
- `asset_path` returns a filesystem path only for native desktop—not web or
  Android bundles.
- `serve_asset` resolves from the asset's display string.

```rust
let css = dioxus_asset_resolver::serve_asset(
    &asset!("/assets/main.css").to_string(),
);
```

## Static public files and stylesheets

Since `0.7.0`, a project-root `/public` directory is merged into the bundle
verbatim for files such as `robots.txt`, favicons, and `.well-known` metadata.
It is distinct from optimized `asset!` content. Asset references no longer need
to contain a content hash; the CLI controls hashing.

In `0.5.0`, CSS referenced by RSX was watched and streamed into running web,
desktop, and fullstack apps, but not mobile; the Tailwind watcher participated in
the same hot reload. Current `dx` recognizes a root `tailwind.css`, detects
Tailwind 3 or 4, and manages the watcher. Configure non-default paths with
`tailwind_input` and `tailwind_output` in `Dioxus.toml`.

Since `0.7.3`, first-party scoped CSS and CSS modules can locally rewrite class
names for a component instead of placing every rule in global CSS. Global CSS,
inline styles, document stylesheets, and Tailwind remain valid alternatives.

## Document elements and evaluation

The `document` namespace provides `Title`, `Link`, `Stylesheet`, `Style`, `Meta`,
and `Script`. During SSR, elements are collected, deduplicated, and minified into
`<head>`; render critical entries before an out-of-order streaming commit if
crawlers must see them.

```rust
use dioxus::document::{Stylesheet, Title};

rsx! {
    Title { "Dioxus app" }
    Stylesheet { href: asset!("/assets/main.css") }
}
```

The document and history abstractions were split into standalone crates in
`0.6.0`, allowing any renderer to implement `Document` and support document
components, `eval`, links, and routing without a renderer-specific router flag.

An `eval` handle receives typed values with `.recv::<T>().await`. JavaScript run
through it gets a `dioxus` global; `dioxus.send(value)` pushes a value to Rust.

## Conditional and repeated attributes

An attribute value may be a bare `if` expression. Without an `else`, false
removes the attribute; do not add a semicolon after the expression. `Option<T>`
works the same way, and false HTML boolean attributes become absent.

`class:` is repeatable and each value is appended. Prefer separate literal
class attributes for Tailwind because its scanner cannot discover class names
assembled by Rust string formatting.

```rust
button {
    class: "btn",
    class: if active() { "btn-active" },
    background_color: if dark() { "black" } else { "white" },
}
```

`IntoAttributeValue` accepts references since `0.7.6`, avoiding an otherwise
unnecessary clone or dereference. The `inert` global HTML attribute is also
available since that release.

## Components, spreads, and keyed fragments

A wrapper can collect typed element attributes with `#[props(extends = img)]`
on a `Vec<Attribute>` and forward them using `..attributes`. Component props use
Rust struct-update syntax (`Card { field: value, ..props }`), where explicit
fields win.

When a loop body emits several roots, only the first node supplies the list key.
If that node cannot carry a key, wrap the roots in `Fragment` and key it:

```rust
for item in items.iter() {
    Fragment { key: "{item.id}",
        div { "{item.name}" }
        div { "{item.description}" }
    }
}
```

The compiler has warned about ineffective non-first-node keys since `0.7.2`.

## Custom elements and raw attributes

Any dashed tag name is emitted as an untyped web component. It has no known
attribute vocabulary, so quote every attribute name. A typed Dioxus wrapper is
usually safer:

```rust
#[component]
fn UserBadge(name: String) -> Element {
    rsx! { user-badge { "name": name } }
}
```

Quoted attribute names are also an escape hatch for raw browser listeners:

```rust
button { "onclick": "navigator.clipboard.writeText(document.title)", "Copy" }
```

Use the latter for a genuinely browser-side behavior, such as cancelling a
LiveView default before the round trip, rather than as the normal event API.

## Building attribute lists dynamically

The `dioxus-attributes` crate supplies `attributes!`, which constructs the
`Vec<Attribute>` needed by spread syntax from ordinary Rust:

```rust
let attrs = attributes!(div {
    class: "my-class",
    "data-custom": "value",
    onclick: |_| tracing::info!("clicked"),
});
rsx! { div { ..attrs } }
```

## Form-control SSR parity

> **Prerelease (`0.8.0-alpha.1`):** This guidance may change before stable release.

SSR translates `initial_value`, `checked`, and `selected` into their HTML
equivalents, so server-rendered controls start in the same state that hydration
expects.

## UI and accessibility checks

- Use first-party primitives when keyboard focus, roving order, and ARIA
  behavior matter; the ecosystem reference documents their non-obvious props.
- Ensure every dynamic list puts a stable key on its first root.
- Confirm `None` or a false conditional removes an attribute rather than
  serializing an unintended empty value.
- For unknown/custom attributes, use quoted names and test the actual renderer.
- Retain every asset that must ship and validate final URLs after optimization.
