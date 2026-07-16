# Desktop and Ecosystem
Build desktop applications, use notebooks, and integrate with the wider Deno ecosystem.
## Contents
- [Desktop applications](#desktop-applications)
- [Jupyter](#jupyter)
- [Frameworks and hosted services](#frameworks-and-hosted-services)
- [Platforms and releases](#platforms-and-releases)

## Desktop applications

### Desktop engines and distribution (2.9-guide)

`deno desktop` defaults to the operating system's `webview` engine, while `--backend cef` bundles Chromium for a consistent cross-platform engine. Output extensions select `.app`, `.dmg`, `.exe`, `.msi`, `.AppImage`, `.deb`, or `.rpm`; `--target` cross-compiles, `--all-targets` builds every supported target, and `--compress` creates a self-extracting artifact.

```sh
deno desktop --backend cef main.ts
deno desktop --target x86_64-pc-windows-msvc main.ts
deno desktop --all-targets main.ts
```

### Experimental desktop applications (2.9-guide)

The experimental `deno desktop` command builds a script or detected web-framework project into a self-contained native application whose UI runs in a webview; an entrypoint's `Deno.serve()` automatically binds to the address opened by that webview. With no entrypoint (or `.`) it shares `deno compile`'s framework detection, and `--hmr` enables hot replacement during development.

```ts
Deno.serve(() => new Response("<!doctype html><h1>Hello</h1>", {
  headers: { "content-type": "text/html" },
}));
```

```sh
deno desktop main.ts
deno desktop --hmr
```

### Native desktop integration (2.9-guide)

`Deno.BrowserWindow` controls windows, menus, visibility, DevTools, and functions exposed to page JavaScript through a `bindings` namespace. `Deno.Tray`, macOS `Deno.Dock`, native `prompt`/`alert`/`confirm` dialogs, and `Deno.autoUpdate()` provide system integration without third-party desktop packages.

```ts
const tray = new Deno.Tray();
tray.setIcon(await Deno.readFile("./icon.png"));
const panel = tray.attachPanel({ url: "https://localhost:8000/panel" });
panel.window.bind("doThing", async () => { /* ... */ });
```

## Jupyter

### Cross-cell Jupyter type information (2.3-guide)

In VS Code Jupyter notebooks, variables, modules, and type definitions from earlier cells are now shared with later cells for recognition and type checking.

### Named Jupyter kernels (2.4-guide)

`deno jupyter --install` accepts `--name` for the kernel identifier and `--display` for its selector label, and refuses to overwrite an existing kernel unless `--force` is supplied.

```sh
deno jupyter --install --name=deno_24 --display='Deno 2.4 kernel'
```

### Rich Jupyter output (2.0-guide)

`deno jupyter` can emit images, graphs, and HTML rather than only plain-text output.

### WebGPU values in Jupyter (2.2.0)

`GPUTexture` and `GPUBuffer` values can now be displayed in Deno Jupyter notebooks, allowing notebook workflows to inspect WebGPU results directly.

## Frameworks and hosted services

### Fresh 2.0 Vite integration (release-and-news-index)

Fresh 2.0 beta can optionally use Vite, adding hot reloading, faster startup, React aliasing, and access to the Vite plugin ecosystem.

### Fresh 2.3 rendering and platform support (release-and-news-index)

Fresh 2.3 supports true zero-JavaScript pages, View Transitions, CSP nonces, IP filtering, and the Temporal API inside islands.

### Generally available Deno Deploy (release-and-news-index)

Deno Deploy reached general availability in February 2026, making the hosted platform a production release rather than a preview offering.

### Isolated untrusted-code environments (release-and-news-index)

Deno Sandbox provides instantly available Linux microVMs with defense-in-depth isolation for running untrusted code.

### JSR packages through pnpm and Yarn (release-and-news-index)

JSR packages can be consumed with pnpm and Yarn; using Deno itself is not required merely to access the registry.

### Next.js SSR on Deno Deploy (release-and-news-index)

Deno Deploy supports running server-side-rendered Next.js applications.

## Platforms and releases

### Six-month LTS channel (2.0-guide)

Starting with Deno 2.1, an LTS branch receives backported critical fixes for six months. At the end of each six-month period, a new LTS branch is cut from the latest stable release.

### Windows on ARM builds (2.7-guide)

Deno now publishes official native Windows ARM builds under the `aarch64-pc-windows-msvc` target; the standard PowerShell installer selects them on compatible machines.
