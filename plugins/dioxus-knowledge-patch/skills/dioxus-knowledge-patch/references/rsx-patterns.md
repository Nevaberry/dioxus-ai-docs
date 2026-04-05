# RSX Patterns

## Component Syntax (0.5+)

Components now accept props directly. The `'bump` lifetime is gone.

```rust
// OLD (0.4): fn App(cx: Scope) -> Element
// NEW (0.5):
#[component]
fn App() -> Element {
    rsx! { "Hello" }
}

#[component]
fn Counter(initial: i32) -> Element {
    let mut count = use_signal(|| initial);
    rsx! { button { onclick: move |_| count += 1, "{count}" } }
}
```

## Conditional Rendering

```rust
rsx! {
    // Option 1: if expression
    if show_header {
        Header {}
    }

    // Option 2: if-else
    if logged_in {
        Dashboard {}
    } else {
        LoginForm {}
    }

    // Option 3: match
    match status {
        Status::Loading => rsx! { Spinner {} },
        Status::Error(e) => rsx! { "Error: {e}" },
        Status::Ready(data) => rsx! { Content { data } },
    }

    // Option 4: conditional attribute
    div { class: if active { "active" }, "Content" }
}
```

## Lists and Iteration

```rust
rsx! {
    ul {
        for item in items.iter() {
            li { key: "{item.id}", "{item.name}" }  // key for efficient diffing
        }
    }

    // With index
    for (i, item) in items.iter().enumerate() {
        div { key: "{i}", "{item}" }
    }
}
```

## Event Handling

```rust
rsx! {
    button {
        onclick: move |event| {
            println!("Clicked at {:?}", event.client_coordinates());
        },
        "Click me"
    }

    input {
        value: "{text}",
        oninput: move |e| text.set(e.value()),  // Controlled input
    }

    form {
        onsubmit: move |e| {
            e.prevent_default();
            handle_submit();
        },
        // form fields...
    }
}
```

### Synchronous prevent_default (0.6+)

No more attribute hack - call method directly:

```rust
// OLD: a { dioxus_prevent_default: "onclick", onclick: handler }
// NEW:
a {
    onclick: move |e| {
        e.prevent_default();
        handler(e);
    },
}
```

### New Event Handlers (0.6+)

Dioxus-specific handlers (no JS needed):

```rust
div {
    onresize: move |rect| println!("size: {:?}", rect.size()),
    onvisible: move |visible| println!("visible: {visible}"),
}
```

### Events (0.7.3+)

```rust
div {
    onauxclick: move |e| println!("aux button: {:?}", e.button()),
    onscrollend: move |_| println!("scroll finished"),
}
```

## Common Attributes

```rust
rsx! {
    div {
        id: "main",
        class: "container mx-auto",
        style: "color: red;",

        // Boolean attributes
        button { disabled: true, "Can't click" }
        input { autofocus: true }

        // Dangerous HTML (use sparingly)
        div { dangerous_inner_html: "<b>Raw HTML</b>" }
    }
}
```

### Attribute Merging (0.5+)

Multiple same-name attributes merge with space delimiter:

```rust
rsx! {
    div { class: "base", class: if enabled { "active" }, }
    // renders: class="base active" when enabled
}
```

## Component Children

```rust
#[component]
fn Card(children: Element) -> Element {
    rsx! {
        div { class: "card",
            {children}
        }
    }
}

// Usage
rsx! {
    Card {
        h1 { "Title" }
        p { "Content goes here" }
    }
}
```

## Props Patterns

```rust
// Optional props with defaults
#[component]
fn Button(
    label: String,
    #[props(default)] disabled: bool,           // defaults to false
    #[props(default = "primary")] variant: &'static str,
    #[props(optional)] icon: Option<String>,    // explicitly optional
) -> Element {
    rsx! { button { disabled, class: "{variant}", "{label}" } }
}

// Props that take owned vs borrowed
#[component]
fn Display(
    text: String,           // Takes ownership (needs .clone() at call site)
    #[props(into)] id: String,  // Accepts anything Into<String>
) -> Element {
    rsx! { div { id, "{text}" } }
}

// Usage
rsx! {
    Button { label: "Submit" }  // uses defaults
    Button { label: "Delete", variant: "danger", disabled: true }
    Display { text: name.clone(), id: "header" }  // "header" auto-converts
}
```

### Prop Spreading (0.5+)

Extend elements to inherit their attributes:

```rust
#[derive(Props, Clone, PartialEq)]
struct MyLinkProps {
    #[props(extends = GlobalAttributes)] // gets class, id, etc.
    attributes: Vec<Attribute>,
}
fn MyLink(props: MyLinkProps) -> Element {
    rsx! { a { ..props.attributes, "Click" } }
}
```

## Element Reference

### Querying Mounted Elements

Use `onmounted` to get element references for DOM queries:

```rust
fn ScrollableList() -> Element {
    let mut container = use_signal(|| None);

    rsx! {
        div {
            onmounted: move |data| container.set(Some(data.data())),
            // children...
        }
        button {
            onclick: move |_| async move {
                if let Some(el) = container() {
                    // Query element
                    let rect = el.get_client_rect().await.unwrap();
                    let scroll = el.get_scroll_size().await.unwrap();

                    // Programmatic scroll
                    el.scroll_to(ScrollBehavior::Smooth, ScrollAxis::Y, 100.0).await;
                }
            },
            "Scroll"
        }
    }
}
```

Available methods: `get_client_rect()`, `get_scroll_size()`, `get_scroll_offset()`, `scroll_to()`, `set_focus()`.

## Error Boundaries (0.5+)

Use `throw` trait to bubble errors up to `ErrorBoundary`:

```rust
fn Fallible() -> Element {
    let data = get_data().throw()?; // returns early, shows in ErrorBoundary
    rsx! { "{data}" }
}

rsx! { ErrorBoundary { handle_error: |err| rsx!{"Error: {err}"}, Fallible {} } }
```

### Element is Result (0.6+)

Use `?` anywhere in components, event handlers, and tasks:

```rust
#[component]
fn Profile(id: u32) -> Element {
    let user = get_user(id)?; // propagates to ErrorBoundary
    rsx! { "{user.name}" }
}
```

## Suspense Boundaries (0.6+)

Show placeholder while async children load:

```rust
rsx! {
    SuspenseBoundary {
        fallback: |_| rsx! { "Loading..." },
        AsyncChild {}
    }
}

fn AsyncChild() -> Element {
    let data = use_resource(fetch_data).suspend()?;  // pauses until ready
    rsx! { "{data}" }
}
```

## Document Elements (0.6+)

Set `<head>` content from components:

```rust
use dioxus::document::{Title, Link, Meta, Style};

rsx! {
    Title { "My Page" }
    Meta { name: "description", content: "..." }
    Link { rel: "stylesheet", href: asset!("/style.css") }
}
```

## Assets (0.6+)

`asset!` replaces `mg!` (Manganis stabilized):

```rust
// OLD: mg!(image("./logo.png"))
// NEW:
const LOGO: Asset = asset!("/assets/logo.png");
rsx! { img { src: LOGO } }
```

### Asset Options

Configure optimization, format conversion, and preloading:

```rust
use dioxus::prelude::*;

// Image: convert to Avif, preload for performance
const HERO: Asset = asset!(
    "/hero.png",
    ImageAssetOptions::new()
        .format(ImageFormat::Avif)
        .preload(true)
);

// CSS: minify and inject in <head>
const STYLES: Asset = asset!(
    "/app.css",
    CssAssetOptions::new().minify(true).preload(true)
);

// JS: minify
const SCRIPT: Asset = asset!("/app.js", JsAssetOptions::new().minify(true));

// Folder: bundle entire directory
const FONTS: Asset = asset!("/fonts", FolderAssetOptions::new());
```

## CSS Modules (0.7.3+)

Component-scoped styles that don't leak globally.

**Option 1: css_module! macro** (recommended - typed class names):
```rust
css_module!(Styles = "/styles.module.css", AssetOptions::css_module());

rsx! {
    div { class: Styles::container,  // Typed const - compile-time checked
        p { class: Styles::title, "Hello" }
    }
}
```

**Option 2: asset! with string interpolation**:
```rust
const STYLES: Asset = asset!("/styles.module.css");

rsx! {
    div { class: "{STYLES}::container",
        p { class: "{STYLES}::title", "Hello" }
    }
}
```
