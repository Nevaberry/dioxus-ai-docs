# Assets, Styling, RSX, and UI Escape Hatches

## Asset pipeline

### From Manganis declarations to `asset!`

The 0.5.0 beta asset system used the separate unstable Manganis crate and `mg!`; the CLI discovered, checked, bundled, and optimized those declarations. In 0.6.0 the linker-discovered pipeline stabilized around `asset!`, including declarations originating in upstream libraries. It minifies and deduplicates collected CSS and emits optimized, content-hashed image variants.

```rust
rsx! {
    img { src: asset!("/assets/image.png") }
}
```

`asset!` no longer needs an explicit hash. Its source path must start with `/` and is resolved from the root of the current crate, not the Rust source file or shell working directory. Files under a project-root `public` directory are copied to fixed paths without an `asset!` declaration.

### Reachability controls retention

An asset is bundled only when the returned `Asset` survives Rust optimization. An unused declaration can disappear from the CLI input. Reference an exported library asset from the final application or mark a deliberately indirect static `#[used]`.

```rust
#[used]
static CERTS: Asset = asset!("/assets/keys.cert");
```

Whole directories may be declared, but the emitted directory name is hashed. Derive child paths from the formatted `Asset` rather than assuming the source directory name.

```rust
let logging_js = format!("{}/logging.js", asset!("/assets/posthog-js"));
```

For programmatic access, `read_asset_bytes` fetches on Web and reads the bundle on native targets. `asset_path` only works on filesystem-backed targets; it does not work on Web or Android.

### Per-asset processing

The second argument accepts `AssetOptions`. A stable output name can disable the content-hash suffix; unrecognized files are copied as-is, and `.scss` inputs are compiled and hot-reloaded.

```rust
let stable = asset!(
    "/assets/static/ferrous_wave.png",
    AssetOptions::builder().with_hash_suffix(false),
);

static THEME: Asset = asset!("/assets/theme.scss");
```

Manganis 0.7 uses variant constructors on the unified builder, such as `AssetOptions::image()`, instead of `ImageAssetOptions::new()`.

```rust
let image = asset!(
    "/assets/image.png",
    AssetOptions::image().with_format(ImageFormat::Avif),
);
```

## Hot reload, CSS, and Tailwind

`dx serve` watches RSX-linked CSS across Web, Desktop, and Fullstack, including generated Tailwind output; Desktop preserves window state across recompiles. Since 0.6.0, RSX hot reload covers formatted text, attributes, component properties, primitive literal props, and nested RSX inside loops, conditionals, and children across Web, Desktop, and Mobile.

Dioxus added scoped CSS and CSS modules in 0.7.3, allowing component-local style isolation.

### Automatic Tailwind

When a project-root `tailwind.css` exists, DX detects Tailwind 3 or 4, downloads the needed tool, and starts its watcher. For Tailwind 4, the input must import Tailwind and explicitly scan Rust sources. DX writes the generated result to `/assets/tailwind.css`; include that stylesheet in the app. `tailwind_input` and `tailwind_output` in `Dioxus.toml` override both paths.

```css
@import "tailwindcss";
@source "./src/**/*.{rs,html,css}";
```

```rust
rsx! {
    document::Stylesheet { href: asset!("/assets/tailwind.css") }
}
```

For editor completion inside RSX, the VS Code Tailwind extension can treat Rust as HTML and extract `class: "..."` values.

```json
{
  "tailwindCSS.experimental.classRegex": ["class: \"(.*)\""],
  "tailwindCSS.includeLanguages": { "rust": "html" }
}
```

## Attributes and spreads

### Forward element properties

`#[props(extends = element)]` lets a component accept that element's standard attributes. Store them in `Vec<Attribute>` and spread them onto the wrapped element. Repeated values such as `class` merge with spaces, which keeps conditional utility classes composable.

```rust
#[derive(Props, PartialEq, Clone)]
struct Props {
    #[props(extends = img)]
    attributes: Vec<Attribute>,
}

fn ImgPlus(props: Props) -> Element {
    rsx! { img { ..props.attributes } }
}

rsx! {
    div { class: "rounded", class: if enabled { "text-white" } }
}
```

Dynamic attributes accept `None` to remove the attribute entirely. HTML boolean attributes normalize false values when appropriate. Spreads apply in source order and later values take precedence.

```rust
rsx! {
    div {
        "aria-current": if active { Some("page") } else { None },
        ..extra_attributes
    }
}
```

Component prop spreads follow the same override idea: explicit invocation fields override fields supplied by `..props`.

### Unknown attributes and web components

Quote an attribute name to bypass the compile-time attribute set, including `data-*` and raw string event handlers. Dashed element names become untyped Web Components, and all their attributes must be quoted.

```rust
rsx! {
    my-web-component {
        "name": "hello, {name}",
        "age": age + 10,
    }
}
```

References have a blanket `IntoAttributeValue` implementation as of 0.7.6, so supported values can be borrowed directly. The HTML global `inert` attribute is also recognized.

```rust
let class = String::from("panel");
rsx! { section { class: &class, inert: true, "Unavailable" } }
```

### Keys and dynamic nodes

In a multi-node RSX body, only a key on the first node is effective; later keys warn and do not key the group. Braced expressions accept any `IntoDynNode`, including strings, `Element`, `Option<T>`, and iterators of dynamic-node values, so optional content and generated lists need not be collected first.

```rust
let warning = show_warning.then(|| rsx! { p { "Check this" } });
let rows = items.iter().map(|item| rsx! {
    li { key: "{item.id}", "{item.name}" }
});

rsx! { {warning} {rows} }
```

## Document head and JavaScript evaluation

Cross-platform elements in `dioxus::document` include `Title`, `Link`, `Stylesheet`, `Style`, `Meta`, and `Script`. Server rendering collects, deduplicates, and minifies head entries, so leaf components can safely declare their metadata and preload links.

```rust
use dioxus::document::{Stylesheet, Title};

rsx! {
    Title { "WebAssembly rocks!" }
    Stylesheet { href: asset!("/assets/main.css") }
}
```

The 0.6 prelude stopped exporting `eval`; use `document::eval`. Evaluation handles deserialize directly with `.recv::<T>().await`. Inside evaluated JavaScript, `dioxus.send(...)` sends a value to Rust and `dioxus.recv()` awaits one from Rust on Web and Desktop.

```rust
let mut eval = document::eval(r#"
    dioxus.send("ready");
    console.log(await dioxus.recv());
"#);

let ready = eval.recv::<String>().await.unwrap();
eval.send(format!("received {ready}")).unwrap();
```

## Observers and UI primitives

`onresize` and `onvisible` are non-HTML handlers that create the required resize and intersection observers without custom JavaScript. `onmounted` yields a live element handle for focus and scrolling. `auxclick` and `scrollend` entered the event set in 0.7.3.

Dioxus Primitives supplies 28 unstyled, Radix-style foundational components with keyboard and ARIA behavior for Web, Desktop, and Mobile. They are designed for composition and restyling. Copyable shadcn-style implementations and their usage constraints are covered in [ecosystem-sdk-components.md](ecosystem-sdk-components.md).

## Web and bundler details

The JavaScript asset path detects ESM, CommonJS, UMD, and generic scripts and invokes esbuild with matching flags as of 0.7.7; this avoids treating every snippet as ESM. The CLI honors `NPM_CONFIG_REGISTRY` for esbuild downloads in 0.8.0-alpha.0.

For Web deployments, `dx bundle` can emit AVIF images, compress WebAssembly, minify output, and Brotli-precompress release assets. These are DX transformations, not plain Cargo behavior.
