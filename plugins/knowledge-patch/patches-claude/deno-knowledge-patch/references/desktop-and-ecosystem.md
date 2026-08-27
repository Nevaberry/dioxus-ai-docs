# Desktop and Ecosystem

Build desktop applications and use Deno's surrounding notebook, framework, registry, sandbox, and hosting ecosystem.

## Cross-cell Jupyter type information (2.3-guide)

In VS Code Jupyter notebooks, variables, modules, and type definitions from earlier cells are now shared with later cells for recognition and type checking.

## Default desktop window title (2.9.1)

A desktop window without an explicit title now uses the application name instead of `laufey_webview`.

## Desktop deep-link schemes (2.9.1)

Desktop bundles can register deep-link URL schemes at bundle time, allowing installed applications to be opened through custom URLs.

## Desktop directory-collision safety (2.9.1)

Desktop packaging no longer deletes an existing user directory merely because its name collides with the application name.

## Desktop engines and distribution (2.9-guide)

`deno desktop` defaults to the operating system's `webview` engine, while `--backend cef` bundles Chromium for a consistent cross-platform engine. Output extensions select `.app`, `.dmg`, `.exe`, `.msi`, `.AppImage`, `.deb`, or `.rpm`; `--target` cross-compiles, `--all-targets` builds every supported target, and `--compress` creates a self-extracting artifact.

```sh
deno desktop --backend cef main.ts
deno desktop --target x86_64-pc-windows-msvc main.ts
deno desktop --all-targets main.ts
```

## Desktop project discovery and adapters (2.9.1)

`deno desktop .` now discovers `deno.json` in the selected project directory. It also detects SvelteKit projects using `adapter-node` and reports unsupported adapters explicitly.

## Desktop-aware type checking (2.9.1)

`deno check --desktop` type-checks an entry point for the Deno Desktop environment.

```sh
deno check --desktop main.ts
```

## Experimental desktop applications (2.9-guide)

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

## Fresh 2.0 Vite integration (release-and-news-index)

Fresh 2.0 beta can optionally use Vite, adding hot reloading, faster startup, React aliasing, and access to the Vite plugin ecosystem.

## Fresh 2.3 rendering and platform support (release-and-news-index)

Fresh 2.3 supports true zero-JavaScript pages, View Transitions, CSP nonces, IP filtering, and the Temporal API inside islands.

## Generally available Deno Deploy (release-and-news-index)

Deno Deploy reached general availability in February 2026, making the hosted platform a production release rather than a preview offering.

## Isolated untrusted-code environments (release-and-news-index)

Deno Sandbox provides instantly available Linux microVMs with defense-in-depth isolation for running untrusted code.

## JSR packages through pnpm and Yarn (release-and-news-index)

JSR packages can be consumed with pnpm and Yarn; using Deno itself is not required merely to access the registry.

## Named Jupyter kernels (2.4-guide)

`deno jupyter --install` accepts `--name` for the kernel identifier and `--display` for its selector label, and refuses to overwrite an existing kernel unless `--force` is supplied.

```sh
deno jupyter --install --name=deno_24 --display='Deno 2.4 kernel'
```

## Native desktop integration (2.9-guide)

`Deno.BrowserWindow` controls windows, menus, visibility, DevTools, and functions exposed to page JavaScript through a `bindings` namespace. `Deno.Tray`, macOS `Deno.Dock`, native `prompt`/`alert`/`confirm` dialogs, and `Deno.autoUpdate()` provide system integration without third-party desktop packages.

```ts
const tray = new Deno.Tray();
tray.setIcon(await Deno.readFile("./icon.png"));
const panel = tray.attachPanel({ url: "https://localhost:8000/panel" });
panel.window.bind("doThing", async () => { /* ... */ });
```

## Next.js SSR on Deno Deploy (release-and-news-index)

Deno Deploy supports running server-side-rendered Next.js applications.

## Rich Jupyter output (2.0-guide)

`deno jupyter` can emit images, graphs, and HTML rather than only plain-text output.

## Six-month LTS channel (2.0-guide)

Starting with Deno 2.1, an LTS branch receives backported critical fixes for six months. At the end of each six-month period, a new LTS branch is cut from the latest stable release.

## WebGPU values in Jupyter (2.2.0)

`GPUTexture` and `GPUBuffer` values can now be displayed in Deno Jupyter notebooks, allowing notebook workflows to inspect WebGPU results directly.

## Windows on ARM builds (2.7-guide)

Deno now publishes official native Windows ARM builds under the `aarch64-pc-windows-msvc` target; the standard PowerShell installer selects them on compatible machines.
