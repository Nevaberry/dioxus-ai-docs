---
name: dioxus-knowledge-patch
description: Dioxus
license: MIT
version: 0.7.9
metadata:
  author: Nevaberry
---

# Dioxus Knowledge Patch

Use this skill when creating, migrating, debugging, testing, or packaging a Dioxus application. Start with the quick references below, then open the topic file that matches the work at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [components-reactivity.md](references/components-reactivity.md) | Components, props, signals, stores, hooks, tasks, resources, suspense, errors, events |
| [assets-styling-ui.md](references/assets-styling-ui.md) | Assets, RSX, attributes, CSS, Tailwind, document elements, evaluation, accessible UI |
| [fullstack-routing.md](references/fullstack-routing.md) | Server functions, Axum, SSR, hydration, forms, streaming, WebSockets, files, routing |
| [cli-platforms-bundling.md](references/cli-platforms-bundling.md) | CLI, project configuration, Web/Desktop/Mobile, logging, debugging, deployment, installers |
| [renderers-testing-internals.md](references/renderers-testing-internals.md) | Native and custom renderers, LiveView, direct SSR, tests, hot-patching, WASM splitting, native plugins |
| [migration-edge-cases.md](references/migration-edge-cases.md) | Breaking API changes, deprecations, dependency boundaries, behavioral edge cases, preview cautions |
| [ecosystem-sdk-components.md](references/ecosystem-sdk-components.md) | Styled components, primitives, virtual lists, attributes, SDK services, persistence, timers |

## First checks

- Inspect `Cargo.toml`, `Cargo.lock`, `Dioxus.toml`, enabled platform features, and the installed `dx` version before changing APIs.
- Keep client-only and server-only dependencies behind their respective Cargo features; a server-function body does not hide adjacent native code from the client build.
- Prefer the unified `dioxus` crate and its current prelude. Low-level runtime and renderer APIs often require explicit imports.
- Run `dx doctor` when a native or mobile build fails before diagnosing Rust code.
- Treat prerelease APIs as opt-in. Do not apply preview-only behavior to a stable application without checking its dependency version.

## Breaking changes and deprecations

### Components no longer take a scope

Components take props directly, `Element` is static and result-based, and runtime helpers do not need a `Scope` argument.

```rust
fn Counter() -> Element {
    let mut count = use_signal(|| 0);
    rsx! {
        button { onclick: move |_| count += 1, "{count}" }
    }
}
```

Use `rsx! {}` to render nothing. Ordinary errors can propagate with `?` into an ancestor `ErrorBoundary`; do not use the removed `VNode::None` pattern.

### Prefer readable props and store lenses

Use `ReadSignal<T>` for reactive readable props. RSX can decay a signal, memo, store lens, or plain value into it. Generic store helpers should accept `Readable` or `Writable` bounds because generated lens types are intentionally unnamed.

```rust
#[component]
fn Title(title: ReadSignal<String>) -> Element {
    rsx! { h1 { "{title}" } }
}
```

`ReadOnlySignal` is deprecated. Use current readable interfaces, and use `Store` for collections whose children need per-item reactive lenses.

### Launch and features are platform-selected

Use `dioxus::launch` or `LaunchBuilder`. Renderer features live on the main `dioxus` crate; fullstack client and server builds must enable `web` and `server` separately.

```toml
[features]
web = ["dioxus/web"]
desktop = ["dioxus/desktop"]
server = ["dioxus/server"]
```

The old `dioxus-lib` crate is gone. Use `dioxus` with the `lib` feature when only the framework library layer is required.

### Event cancellation is synchronous

Call `event.prevent_default()` before any `.await`. Web forms submit by default, so cancel `onsubmit` when the application handles submission itself. LiveView executes Rust handlers on the server and cannot cancel a browser default in time; use synchronous browser-side JavaScript there.

### Asset paths and options changed

`asset!` paths are absolute from the current crate root and begin with `/`. Use `AssetOptions` and its variant constructors; do not use the old `mg!` or `ImageAssetOptions::new()` forms.

```rust
let image = asset!(
    "/assets/image.png",
    AssetOptions::image().with_format(ImageFormat::Avif),
);
```

### Fullstack types are Dioxus-facing

Use explicit route macros for durable APIs, especially for native clients. Dioxus's `ServerFnError` is not the identically named generic `server_fn` type, and public dependency boundaries should align with the versions expected by Dioxus.

If a locked stable project fails after the dependency corrections associated with 0.7.5, run `cargo update` before changing source code.

## Reactivity and async work

### Reads create subscriptions

A signal read during rendering subscribes that component. Reads inside an event handler alone do not. Memos, effects, futures, resources, and loaders track reads according to their own execution semantics; use `peek()` for an intentional non-subscribing read.

Signal writes within one runtime step are batched. An `.await` ends the step, permitting pending UI to paint. A dependent memo read immediately after a write recomputes synchronously.

### Pick the right task primitive

- `use_action` stores the latest `Result` and cancels stale work when called again.
- `spawn` owns a `!Send` future for the current component and cancels it on unmount.
- `spawn_forever` attaches app-long work to the root; it must not retain shorter-lived signals.
- Move CPU-bound work to a native thread or Web Worker.

### Resources, loaders, and suspense

`use_resource` restarts when a tracked dependency changes. Use `CapturedError` or `dioxus::Ok` when its result error needs to be cloneable. `use_loader` routes loading and error states through suspense and error boundaries; start independent loaders before the first `?` to avoid waterfalls.

Fullstack suspense data must use a server future so the result can be serialized for hydration. Keep reactive reads in the outer closure.

## Fullstack quick reference

### Compose an Axum server

```rust
#[cfg(feature = "server")]
dioxus::serve(|| async move {
    use dioxus::server::axum::routing::get;

    Ok(dioxus::server::router(app)
        .route("/health", get(|| async { "ok" })))
});
```

Ordinary Axum routes added to the assembled router take precedence over the SSR fallback. Use server-only extractors for request extensions such as authenticated sessions so they never enter the client payload.

### Preserve HTTP semantics

- An unrecognized server error becomes HTTP 500; use `OrHttpError` or a typed error implementing the status conversion traits.
- An `ErrorBoundary` that handles an SSR error must recommit its HTTP status through `FullstackContext`.
- Headers and status freeze when the first streaming chunk commits.
- Native clients support server functions, files, streams, and WebSockets, but not SSR, hydration data, SSG, or `FullstackContext`.

### Keep hydration deterministic

The client reruns the component tree during hydration. Put synchronous nondeterminism in `use_server_cached`, async nondeterminism in a server future or loader, and browser-only reads in `use_effect`. Do not put side effects in server-cached closures.

## Routing quick reference

Derive `Routable`, mount `Router::<Route> {}`, and navigate with typed variants. Matching prefers static paths, then dynamic fields, then catch-alls; enum order breaks ties. Query and hash segments do not reject a route when typed values are absent or malformed.

```rust
#[derive(Clone, PartialEq, Routable)]
enum Route {
    #[route("/")]
    Home,
    #[route("/post/:id")]
    Post { id: u64 },
}
```

Layouts render children through `Outlet::<Route> {}`. Configure a history provider explicitly when URL behavior matters, especially for browser, hash, LiveView, or memory routing.

## Assets, styling, and RSX

- An asset is bundled only when its `Asset` value survives Rust optimization; retain exported library assets from the final app or mark intentional indirect statics `#[used]`.
- Build child paths beneath an asset directory from the formatted hashed `Asset`, not from its source name.
- Attribute spreads apply in source order; later values win. `None` removes a dynamic attribute.
- Quote unknown attributes and all web-component attributes. Dashed tags create untyped web components.
- In multi-node RSX, place a `key` on the first node.
- For Tailwind 4, import Tailwind in the input, scan Rust sources with `@source`, and include DX's generated stylesheet.

## CLI and platform workflow

```sh
dx doctor
dx serve --web
dx build --raw-json-diagnostics
dx bundle --json-output
```

The CLI can serve web, desktop, iOS, Android, fullstack, and ordinary Rust packages. Native bundles are host-bound; mobile builds additionally depend on platform SDKs and signing configuration. Use `--log-to-file` for complete diagnostics and `dx print` when another tool must reproduce DX's build arguments.

For a fullstack web deployment, ship both the generated `public` directory and server executable. Bind production containers with `IP=0.0.0.0`; `dioxus::launch` reads `IP` and `PORT`.

## Verification checklist

- Confirm every hook is called consistently; guarded early returns are supported, but hooks inside branches, loops, or closures are not.
- Check that copied signal handles cannot outlive their owning component.
- Verify server-only code and secrets are absent from the web artifact.
- Exercise route fallbacks on the actual host, not only DX's development server.
- Test installer resources, sidecars, icons, signing, deep links, and permissions on each target platform.
- For custom renderers, test template caching, reclaimed element IDs, mutation stack order, event conversion, and hydration paths.
- For hot-patching, distinguish RSX hot reload, Rust code patches, and full rebuilds; their file and workspace coverage differs.
