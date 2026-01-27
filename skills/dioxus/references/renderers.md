# Renderers Quick Reference

All renderers implement `WriteMutations` trait for DOM changes.

## Available Renderers

| Renderer | Package | Use Case |
|----------|---------|----------|
| Web | dioxus-web | WASM/browser via Sledgehammer JS |
| Desktop | dioxus-desktop | Wry/Tao webview |
| Native | dioxus-native | Blitz/Vello GPU (not a browser) |
| LiveView | dioxus-liveview | WebSocket streaming, server-side DOM |
| SSR | dioxus-ssr | Server-side HTML rendering |

## WriteMutations Trait

```rust
trait WriteMutations {
    fn append_children(id, count);
    fn assign_node_id(path, id);
    fn create_placeholder(id);
    fn create_text_node(value, id);
    fn load_template(template, index, id);
    fn replace_node_with(id, count);
    fn set_attribute(name, ns, value, id);
    fn create_event_listener(name, id);
    fn remove_node(id);
}
```

## Key Differences

**Web**: Direct JS via wasm-bindgen, Sledgehammer interpreter

**Desktop**: WebSocket mutation transmission, `dioxus://` protocol for assets

**Native**: Blitz layout engine + Vello GPU rendering (CSS 2.1+, flexbox)

**LiveView**: Server holds VirtualDOM, binary protocol over WebSocket

## Launch Pattern

```rust
// Web
dioxus::launch(app);

// Desktop with config
dioxus::LaunchBuilder::desktop()
    .with_cfg(Config::new().with_window(WindowBuilder::new()))
    .launch(app);

// Fullstack
#[cfg(feature = "server")]
dioxus::LaunchBuilder::server().launch(app);
#[cfg(feature = "web")]
dioxus::LaunchBuilder::web().launch(app);
```
