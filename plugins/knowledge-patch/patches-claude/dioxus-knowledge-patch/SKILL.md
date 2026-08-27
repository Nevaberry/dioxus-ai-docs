---
name: dioxus-knowledge-patch
description: Dioxus
version: "0.8.0-alpha.1"
license: MIT
metadata:
  author: Nevaberry
---



# Dioxus Knowledge Patch

Use this skill when creating, migrating, debugging, testing, or packaging a Dioxus
application. Inspect manifests and the target platform, then open the matching
topic reference.

> [!CAUTION]
> This skill includes guidance for `0.8.0-alpha.1`; prerelease guidance may
> change before stable release.

## Reference index

| Reference | Topics |
| --- | --- |
| [components-reactivity.md](references/components-reactivity.md) | Components, props, errors, signals, stores, hooks, tasks, suspense, and events |
| [assets-styling-ui.md](references/assets-styling-ui.md) | Assets, RSX, attributes, CSS, Tailwind, document elements, evaluation, and accessible UI |
| [fullstack-routing.md](references/fullstack-routing.md) | Server functions, Axum, SSR, hydration, forms, streams, WebSockets, files, SSG, and routing |
| [cli-platforms-bundling.md](references/cli-platforms-bundling.md) | CLI, project configuration, Web, Desktop, Mobile, FFI, logging, deployment, and installers |
| [renderers-testing-internals.md](references/renderers-testing-internals.md) | Native and custom renderers, direct SSR, tests, hot reload, hot-patching, and WASM splitting |
| [migration-edge-cases.md](references/migration-edge-cases.md) | Breaking API changes, dependency boundaries, behavioral fixes, and prerelease cautions |
| [ecosystem-sdk-components.md](references/ecosystem-sdk-components.md) | SDK services, persistence, timers, primitives, styled components, and virtual lists |

## First checks

- Read `Cargo.toml`, `Cargo.lock`, `Dioxus.toml`, enabled Cargo features, target
  platform, and installed `dx` version before changing an API or build command.
- Prefer the unified `dioxus` crate and prelude. Fullstack client and server
  builds require different companion features.
- Build fullstack browser and server targets with their separate companion
  features; do not treat `fullstack` alone as a platform.
- Run `dx doctor` before diagnosing native SDK, toolchain, or system-library
  failures. Use `dx print` to reproduce DX's Cargo and linker arguments.
- Treat alpha guidance as opt-in and verify its exact version before applying it.

## Breaking changes and deprecations

### Components return a result

Current components return `Element`, which is a result-like render value.
Propagate ordinary errors with `?` to the nearest
`ErrorBoundary`; render nothing with `rsx! {}`. Do not use the removed
`VNode::None` or the old `.throw()?` migration form in current code.

```rust
fn Counter() -> Element {
    let mut count = use_signal(|| 0);
    rsx! {
        button { onclick: move |_| count += 1, "{count}" }
    }
}
```

Use `dioxus::Result<T>`/`dioxus::Ok(value)` when an async reactive primitive
needs the cloneable `CapturedError` form. Dioxus errors otherwise interoperate
with `anyhow` and its context and downcast APIs.

### Prefer readable props and store lenses

Use `ReadSignal<T>` for readable reactive props. Signals, memos, store lenses,
and plain values decay into it, so one prop supports reactive and untracked
callers. `ReadOnlySignal` is deprecated.

```rust
#[component]
fn Title(title: ReadSignal<String>) -> Element {
    rsx! { h1 { "{title}" } }
}
```

Use `Store` when children need reactive access to individual collection entries
or nested fields. Generated lens types are intentionally unnamed, so generic
helpers should accept `Readable` or `Writable` bounds rather than spelling the
second `Store` parameter.

### Launch and features are platform-selected

Launch through `dioxus::launch`, `LaunchBuilder`, or `dioxus::serve`. Do not add
old renderer launch crates or `dioxus-lib`. A fullstack configuration needs a
client renderer and server target separately:

```toml
[features]
default = []
web = ["dioxus/web", "dioxus/fullstack"]
server = ["dioxus/server", "dioxus/fullstack"]
desktop = ["dioxus/desktop"]
```

The router is not a default feature. `dioxus::serve` requires `server`, while
`LaunchBuilder` requires `launch`; stores are re-exported under `signals`, not a
separate `stores` feature.

### Events cancel browser defaults synchronously

Call `event.prevent_default()` before any `.await`. Web forms submit by default,
so cancel `onsubmit` when Rust handles the request. LiveView handlers execute on
the server and cannot cancel a browser default in time; use a synchronous raw
browser listener for that case.

### Asset APIs and paths changed

Use `asset!` with crate-root-absolute paths such as `/assets/logo.png`. The old
standalone `manganis::mg!` syntax was transitional. Retain an `Asset` value in
the final program or mark an intentional indirect static `#[used]`, because
link-time collection prunes unused assets.

Build child URLs under directory assets from the formatted hashed `Asset`, not
from the source folder name. Use current `AssetOptions` builders.

## Reactivity and async work

Use `peek()` for a signal read that must not subscribe the current scope, and
`use_reactive` to make otherwise-untracked values into explicit dependencies.

### Pick the task primitive by lifetime

- `use_action` stores the latest result and cancels stale work when called again.
- `spawn` work is cancelled when its component unmounts.
- `spawn_forever` attaches work to the root and must not retain shorter-lived
  signals.
- `use_loader` routes pending and error states through suspense and error
  boundaries without an explicit state match.

## Fullstack quick reference

### Compose the Axum router

`dioxus::server::router(app)` returns the configured static-assets,
server-functions, and SSR router. Ordinary Axum routes added to it win over the
SSR fallback. Import Axum through `dioxus::server::axum` to stay version-aligned.

```rust
#[cfg(feature = "server")]
dioxus::serve(|| async move {
    use dioxus::server::axum::routing::get;
    Ok(dioxus::server::router(app)
        .route("/health", get(|| async { "ok" })))
});
```

Prefer explicit `#[get]`/`#[post]` routes for independently shipped native
clients. The hashed endpoint generated by bare `#[server]` can change with the
function definition.

### Preserve HTTP semantics

- Unrecognized errors become HTTP 500. Use `HttpError`, `OrHttpError`, or a
  serializable typed error with status conversion for intentional responses.
- An `ErrorBoundary` that catches an SSR error must recommit its status through
  `FullstackContext`, or the friendly error page can return 200.
- Out-of-order HTML streaming is opt-in. Once the first chunk commits, headers,
  status, and crawler-visible head content are frozen.

### Keep hydration deterministic

Put synchronous nondeterminism in `use_server_cached` and async values in
`use_server_future`. Their closures must not perform side effects because a
hydrated client may skip them when the server already supplied a value.

## Routing quick reference

Derive `Routable`, mount `Router::<Route> {}`, and navigate with typed variants.
Static segments outrank dynamic segments, which outrank catch-alls; declaration
order breaks ties. Query and hash parse failures default instead of rejecting a
route, while path parse failures allow the next route to match.

```rust
#[derive(Clone, PartialEq, Routable)]
enum Route {
    #[route("/")]
    Home,
    #[route("/post/:id")]
    Post { id: u64 },
}
```

Layouts render children with `Outlet::<Route> {}`. Configure `WebHistory`, hash
history, LiveView history, or memory history explicitly when URL behavior
matters; the default is `MemoryHistory`.

## Assets, styling, and RSX

- Repeat `class:` for conditional classes. Prefer literal class strings so
  Tailwind can discover them.
- Quote unknown attributes and all attributes on dashed custom-element tags.
- In multi-node list output, put `key` on the first node or a keyed `Fragment`.
- Component props spread with Rust struct syntax; explicit fields override the
  spread.
- For Tailwind, configure the input/output paths in `Dioxus.toml` when the
  defaults do not fit and ensure the generated stylesheet is included.

## CLI and platform workflow

```sh
dx doctor
dx serve --web
dx build --raw-json-diagnostics
dx bundle --json-output --verbose
```

DX can serve web, desktop, iOS, Android, fullstack, and ordinary Rust packages.
Native bundles are host-bound; mobile builds also require the platform SDKs,
Rust targets, signing configuration, and permissions. Use `--log-to-file` for
complete diagnostics and the last JSON-output line as a command's structured
result.

Deploy a fullstack web build with both its `public` directory and `server`
executable. The executable reads `IP` and `PORT`; production containers usually
need `IP=0.0.0.0`.

## Verification checklist

- Ensure root-scoped tasks capture only signals that live for the whole app.
- Verify fullstack client and server builds select their intended Cargo features.
- Exercise route fallbacks and deep links on the production host, not only DX's
  development server.
- Test installer resources, sidecars, icons, signing, permissions, widgets, and
  deep links on every target platform.
- For custom renderers, test template caching, reclaimed element IDs, mutation
  stack order, event conversion, and hydration.
- Distinguish RSX hot reload, compiled-code hot-patching, and full rebuilds when
  diagnosing development behavior.
