# Builds and frontend development

Use this reference for bundling, HTML and CSS development, transpilation, plugins, and standalone executables.

Entries are grouped by developer task. When entries describe evolving behavior, the later attribution supersedes earlier defaults or limitations.

## Breaking behavior and type changes

### Build failure semantics *(1.2-guide)*

`Bun.build()` now rejects its promise on build errors instead of resolving with errors only in `logs`. Set `throw: false` to retain the old result-inspection behavior.

### CLI alias and sourcemap defaults *(1.2-guide)*

`bun -p` now means `bun --print`, replacing its former `--port` meaning. Bare `bun build --sourcemap` now emits linked `.map` files; request the previous behavior explicitly with `--sourcemap=inline`.

## HTML and frontend development

### HTML entrypoints *(1.2-guide)*

An imported HTML file can be assigned to a `Bun.serve()` static route. Bun bundles its module scripts and linked stylesheets, rewrites their URLs to generated static assets, and serves the transformed HTML.

```ts
import homepage from "./index.html";
Bun.serve({ static: { "/": homepage }, fetch: () => new Response("Not found", { status: 404 }) });
```

### Built-in CSS bundling *(1.2-guide)*

`bun build` now accepts CSS entrypoints, resolves and flattens `@import` dependencies, and handles referenced assets. Importing CSS from JavaScript or TypeScript produces one combined CSS output for that module entrypoint alongside its JavaScript bundle.

```sh
bun build ./index.ts --outdir=dist
```

### HTML-import minification controls *(since 1.2.1)*

Minification for HTML imports can be disabled wholly or by whitespace, identifier, and syntax transforms under `[serve.static]`. If omitted, it defaults off for `Bun.serve({ development: true })` and on for `development: false`.

```toml
[serve.static]
minify = false
# Or set minify.whitespace, minify.identifiers, and minify.syntax separately.
```

### HTML entrypoint development server *(since 1.2.3)*

Running an HTML file directly starts a zero-configuration frontend server with bundling, JSX/TypeScript transpilation, CSS handling, and hot reloading. A glob creates routes for multiple HTML entrypoints.

```sh
bun ./index.html
bun './**/*.html'
```

HTML imports can also expose selected environment variables to client code as `process.env.*`:

```toml
[serve.static]
env = "BUN_PUBLIC_*"
```

### Frontend setup and dependency analysis *(since 1.2.3)*

`bun init` adds a React template with frontend tooling and a lightweight backend. For existing component code, `bun create ./MyComponent.tsx` scans imports, installs missing packages, and detects tooling such as Tailwind CSS and shadcn/ui; `bun install --analyze` performs the dependency-discovery step directly and records missing imports in `package.json`.

```sh
bun create ./MyComponent.tsx
bun install --analyze src/**/*.ts
```

### Official Svelte plugin *(since 1.2.5)*

The `bun-plugin-svelte` package adds Svelte components, component-level TypeScript, and HMR to Bun's bundler and development server. Its build target can be `"browser"`, `"bun"`, or `"node"` for client or server components.

```ts
import { SveltePlugin } from "bun-plugin-svelte";

Bun.build({
  entrypoints: ["src/index.ts"],
  outdir: "dist",
  target: "browser",
  plugins: [SveltePlugin({ development: true })],
});
```

### CSS modules *(since 1.2.5)*

Files ending in `.module.css` are automatically scoped and default-import as a class-name map. CSS Modules `composes` can reference classes in the same file, another module, or the global scope.

```ts
import styles from "./style.module.css";
const button = document.createElement("button");
button.className = styles.button;
```

### Modern HMR API and events *(since 1.2.5)*

The development server supports self-acceptance and dependency acceptance through `import.meta.hot.accept()`, including synchronous ESM imports; these calls are dead-code eliminated in production. `on()` and `off()` handle lifecycle events such as `bun:beforeUpdate`, `bun:afterUpdate`, `bun:error`, and `bun:ws:connect`, with Vite-prefixed event names also accepted.

```ts
import.meta.hot.accept("./foo", newFoo => updateState(newFoo));
import.meta.hot.on("bun:beforeUpdate", () => console.log("updating"));
```

### Svelte package and module resolution *(since 1.2.6)*

`bun-plugin-svelte` now honors packages' `"svelte"` export condition and correctly transpiles imported `.svelte.ts` modules before compilation, enabling packages such as `@threlte/core` and TypeScript Svelte helper modules.

### Global selectors in CSS Modules *(since 1.2.6)*

CSS Modules now process `:global()` correctly, preserving the enclosed selector instead of applying module scoping.

```css
:global(.button) {
  color: blue;
}
```

### HTML imports can select the text loader *(since 1.2.10)*

An `.html` file can now be imported as raw text with an import attribute instead of being forced through HTML entrypoint handling.

```ts
import html from "./template.html" with { type: "text" };
```

### Browser console streaming *(since 1.2.12)*

Frontend dev servers can forward browser `console.log` and `console.error` calls to the launching terminal, prefixed with `[browser]`. Enable it with `--console` for an HTML entrypoint or `development.console` in `Bun.serve()`.

```sh
bun ./index.html --console
```

```ts
import homepage from "./index.html";

Bun.serve({
  development: { console: true, hmr: true },
  routes: { "/": homepage },
});
```

### Editable Chrome DevTools workspaces *(since 1.2.15)*

The frontend development server now exposes automatic workspace folders to Chrome DevTools, allowing served project files to be edited directly in the browser.

### Ahead-of-time server-side HTML bundling *(since 1.2.17)*

`bun build` can now follow an HTML import from a server entrypoint, bundle its referenced client-side scripts and styles, and configure the built server to serve those assets. Use a Bun target for a deployable bundle or `--compile` for a self-contained full-stack executable.

```sh
bun build ./src/server.ts --target=bun --outdir=dist
bun build ./src/server.ts --compile --outfile=my-app
```

### Production HTML builds *(1.3-guide)*

An HTML entrypoint can be bundled for deployment with the production build mode.

```sh
bun build ./index.html --production --outdir=dist
```

### CSS view-transition selector arguments *(since 1.3.2)*

The CSS parser, bundler, and minifier now accept class selector arguments in view-transition pseudo-elements such as `::view-transition-old()`, `::view-transition-new()`, `::view-transition-group()`, and `::view-transition-image-pair()`.

```css
::view-transition-old(.slide-out) {
  animation: slide-out 200ms;
}
```

### Self-contained browser HTML compilation *(since 1.3.10)*

Compiling an HTML entrypoint with the browser target inlines its bundled JavaScript and CSS and converts asset references to `data:` URLs, producing an HTML file that can run directly from a `file://` URL. Every entrypoint must be HTML, and this mode cannot be combined with splitting.

```sh
bun build --compile --target=browser ./index.html
```

### Native headless browser automation *(since 1.3.12)*

`Bun.WebView` drives the system WebKit view on macOS or Chrome/Chromium through CDP cross-platform. Selector actions wait for visible, stable, unobscured elements and dispatch trusted OS-level input; the API also covers navigation, evaluation, screenshots, scrolling, page state, events, and raw CDP calls.

```ts
await using view = new Bun.WebView({ width: 800, height: 600 });
await view.navigate("https://example.com");
await view.click("a.docs");
const title = await view.evaluate("document.title");
await Bun.write("page.png", await view.screenshot({ format: "png" }));
```

## Bundler configuration, plugins, and analysis

### Native pre-parse plugins *(1.2-guide)*

Plugins gain `onBeforeParse()`, a low-overhead source transformation hook implemented by an N-API addon rather than JavaScript. Registration supplies the file filter plus the native module and exported symbol.

```ts
build.onBeforeParse(
  { namespace: "file", filter: "**/*.tsx" },
  { napiModule: nativePlugin, symbol: "transform" },
);
```

### New build controls *(1.2-guide)*

The CLI and `Bun.build()` can inject matching environment variables (`--env='PUBLIC_*'` / `env`), drop calls (`--drop` / `drop`), add `banner` and `footer` text, and leave all package imports external (`--packages external` / `packages: "external"`). `--ignore-dce-annotations` disables `@__PURE__` and similar annotations when incorrect annotations remove required side effects.

### Static-file compile-time defines *(since 1.2.4)*

`[serve.static].define` in `bunfig.toml` inlines constants into static-file bundles. Unlike exposed environment variables, define values can contain arbitrary JSON encoded as JavaScript inside a TOML string.

```toml
[serve.static]
define = { CONFIG = "{ \"version\": \"1.0\", \"beta\": false }" }
```

### `$NODE_PATH` bundler resolution *(since 1.2.18)*

`bun build` now searches the module directories in `$NODE_PATH`, extending the runtime support added earlier to bundled bare imports.

```sh
NODE_PATH=./src bun build ./entry.js --outdir ./out
```

### Boolean sourcemap option *(since 1.2.19)*

`Bun.build({ sourcemap: true })` now generates a sourcemap; callers may use the boolean form as well as the existing string modes.

### Glob patterns in package side-effect declarations *(since 1.2.21)*

Bun's bundler now interprets `*`, `?`, `**`, `[]`, and `{}` patterns in a package's `sideEffects` array instead of de-optimizing the entire package.

```json
{
  "sideEffects": ["**/*.css", "./src/setup.js", "./src/components/*.js"]
}
```

### Bundler plugin completion hooks *(since 1.2.22)*

Bundler plugins can register `onEnd()`, which runs after either a successful or failed build and receives its `BuildOutput` for cleanup, reporting, or post-processing.

```ts
await Bun.build({
  entrypoints: ["./index.ts"],
  plugins: [{
    name: "report",
    setup(build) {
      build.onEnd(result => console.log(result.success));
    },
  }],
});
```

### Minified function and class names *(since 1.2.22)*

Syntax minification now removes unused names from function and class expressions. Use `--keep-names` or `keepNames: true` when reflection, diagnostics, or application logic depends on `Function.prototype.name`.

```sh
bun build --minify --keep-names ./input.js
```

### Legal-comment source maps *(since 1.3.1)*

`bun build` source maps now map preserved multiline legal comments, including CRLF comments, back to their original source locations so license tooling and debuggers can trace them accurately.

### Compile-time feature flags *(since 1.3.5)*

Import `feature()` from `bun:bundle` to guard code that Bun replaces with `true` or `false` during transpilation. Enable names with repeatable `--feature` flags in `bun build`, `bun run`, or `bun test`; with minification, disabled branches are removed entirely, while `Bun.build()` accepts the same names through `features`.

```ts
import { feature } from "bun:bundle";

if (feature("DEBUG")) console.log("debug details");

await Bun.build({
  entrypoints: ["./app.ts"],
  outdir: "./out",
  features: ["DEBUG"],
});
```

Augmenting the module registry restricts feature names at type-check time:

```ts
declare module "bun:bundle" {
  interface Registry {
    features: "DEBUG" | "PREMIUM";
  }
}
```

### Esbuild-compatible build metafiles *(since 1.3.6)*

`Bun.build({ metafile: true })` returns `result.metafile` in esbuild's format, with input and output byte sizes, imports, exports, entry points, and contributing inputs. The CLI form writes the metadata directly with `--metafile <path>`.

```ts
const result = await Bun.build({
  entrypoints: ["./src/index.ts"],
  outdir: "./dist",
  metafile: true,
});
await Bun.write("./dist/meta.json", JSON.stringify(result.metafile));
```

### Virtual and overlaid build files *(since 1.3.6)*

The `files` option to `Bun.build()` supplies in-memory files or overrides matching disk files; virtual and real files can import one another. Values may be strings, blobs, typed arrays, or array buffers.

```ts
await Bun.build({
  entrypoints: ["/app/index.ts"],
  files: {
    "/app/index.ts": `import { id } from "./generated.ts"; console.log(id);`,
    "/app/generated.ts": `export const id = "build-42";`,
  },
});
```

### Markdown build metafiles *(since 1.3.8)*

`bun build --metafile-md` writes a Markdown bundle analysis to `meta.md`; use `--metafile-md=<path>` to choose a filename. `Bun.build()` can emit JSON and Markdown metafiles together by passing their paths in a `metafile` object.

```sh
bun build entry.js --metafile-md=analysis.md --outdir=dist
```

```ts
await Bun.build({
  entrypoints: ["./entry.js"],
  outdir: "./dist",
  metafile: { json: "meta.json", markdown: "meta.md" },
});
```

## Transpilation, modules, and syntax

### CommonJS bundler output and detection *(1.2-guide)*

`bun build --format=cjs` now emits CommonJS. For otherwise ambiguous source, a leading `"use strict"` is treated as a last-chance CommonJS signal; conversely, `require.main === module` is rewritten to `import.meta.main`, so that check can coexist with ESM imports.

### Import attributes *(1.2-guide)*

Static and dynamic imports support `with { type: ... }`; Bun-specific useful types include `json`, `text`, `toml`, and `file`. Dynamic import places the same object under an options object's `with` key.

```ts
import config from "./bunfig.toml" with { type: "toml" };
const { default: text } = await import("./note.txt", { with: { type: "text" } });
```

### Object-loader default interop *(since 1.2.2)*

Plugin modules using `loader: "object"` now honor an exported `__esModule: true`: default imports and `require()` return the declared default value rather than a namespace wrapper.

```ts
builder.module("my-module", () => ({
  exports: { default: "hello", __esModule: true },
  loader: "object",
}));

const value = require("my-module"); // "hello"
```

### TypeScript module-preservation default *(since 1.2.14)*

New default TypeScript configurations now use `"module": "Preserve"` instead of `"ESNext"`, preserving the module syntax written in each file rather than transforming it.

```json
{
  "compilerOptions": { "module": "Preserve" }
}
```

### JSX side-effect preservation *(since 1.2.22)*

The bundler treats JSX expressions as pure by default, so unused JSX can be removed. Set `jsxSideEffects` when rendering a component must be retained for its side effects.

```json
{
  "compilerOptions": { "jsxSideEffects": true }
}
```

### Programmatic JSX configuration *(since 1.2.23)*

`Bun.build()` now accepts a centralized `jsx` object for transform settings that previously came from `tsconfig.json`.

```ts
await Bun.build({
  entrypoints: ["./index.jsx"],
  outdir: "./dist",
  jsx: {
    runtime: "automatic",
    importSource: "preact",
    development: false,
    sideEffects: false,
  },
});
```

### CommonJS transforms for `import.meta` *(since 1.3.1)*

With `--format=cjs`, the bundler now replaces `import.meta.path`, `import.meta.dirname`, and `import.meta.file` with CommonJS-compatible equivalents based on `__filename`, `__dirname`, and `path.basename(module.filename)`. Packages using these properties no longer leave invalid `import.meta` syntax in CommonJS output.

```sh
bun build ./entry.ts --format=cjs --outfile=entry.cjs
```

### REPL transforms with `Bun.Transpiler` *(since 1.3.7)*

`replMode: true` transforms input for persistent interactive evaluation: declarations are hoisted, `const` becomes redeclarable, the final expression is captured, object literals are recognized, and top-level await is wrapped appropriately.

```ts
const transpiler = new Bun.Transpiler({ loader: "tsx", replMode: true });
const transformed = transpiler.transformSync("await Promise.resolve(42)");
```

### Standard ES decorators *(since 1.3.10)*

The transpiler now supports stage-3 standard decorators when `experimentalDecorators` is not enabled, including class and method decorators, field initializer replacement and `addInitializer`, public or private auto-accessors, `Symbol.metadata`, and spec-defined evaluation order. Legacy TypeScript decorators remain available with `experimentalDecorators: true`.

```ts
function logged(method: Function, context: ClassMethodDecoratorContext) {
  return function (this: unknown, ...args: unknown[]) {
    console.log(String(context.name));
    return method.call(this, ...args);
  };
}
class Service {
  @logged run() {}
}
```

### Legacy decorator settings in `Bun.Transpiler` *(since 1.3.11)*

`Bun.Transpiler` now honors `experimentalDecorators` and `emitDecoratorMetadata` from `tsconfig` instead of always emitting standard decorators. Enabling `emitDecoratorMetadata` selects the legacy TypeScript decorator behavior even when `experimentalDecorators` is not explicitly set, restoring compatibility with frameworks that consume legacy metadata.

### Native resource-management syntax in Bun output *(since 1.3.14)*

`bun run`, `Bun.Transpiler({ target: "bun" })`, and `bun build --target=bun` now preserve `using` and `await using` instead of lowering them to helper calls. Browser and Node targets continue to lower the syntax.

## Standalone executables and cross-compilation

### Cross-compiled executables *(1.2-guide)*

`bun build --compile` can target another supported platform, such as `--target=bun-windows-x64`; Windows builds also accept `--windows-icon` and `--windows-hide-console`. Compiled programs can inspect bundled assets through the iterable `embeddedFiles` export from `bun`.

### Bytecode caches *(1.2-guide)*

`bun build --bytecode` emits JavaScriptCore `.jsc` caches, either beside normal output or inside a standalone executable. The corresponding `.js` file is still required for non-compiled output, and async functions, generators, and `eval` are not currently bytecode-compiled.

```sh
bun build --bytecode --outdir=dist app.ts
```

### Running Bun from a compiled executable *(since 1.2.16)*

Setting `BUN_BE_BUN` when launching a single-file executable runs its embedded Bun binary instead of the compiled entrypoint.

```sh
BUN_BE_BUN=1 ./my-app --version
```

### Code-signable Windows executables *(since 1.2.19)*

Windows executables produced by `bun build --compile` can now be Authenticode-signed after compilation without invalidating their embedded source and assets.

```sh
bun build ./app.ts --compile --outfile app.exe
signtool.exe sign /f MyCert.pfx /p MyPassword app.exe
```

### Programmatic executable compilation *(since 1.2.21)*

`Bun.build()` now creates standalone executables with `compile: true`, a target string, or a configuration object; compiled builds can also use bundler plugins.

```ts
await Bun.build({
  entrypoints: ["./cli.ts"],
  compile: { target: "bun-linux-x64-musl", outfile: "./cli" },
});
```

### Embedded executable runtime flags *(since 1.2.21)*

`bun build --compile-exec-argv` embeds Bun runtime arguments into a standalone executable; they take effect on launch and appear in `process.execArgv`.

```sh
bun build ./cli.ts --compile --compile-exec-argv="--smol --user-agent=MyApp/1.0"
```

### Windows executable metadata *(since 1.2.21)*

Compiled Windows executables can set title, publisher, version, description, and copyright through matching `--windows-*` flags or `compile.windows` in `Bun.build()`.

```ts
await Bun.build({
  entrypoints: ["./app.js"],
  compile: { windows: { title: "My App", publisher: "Acme", version: "1.2.3.4" } },
});
```

### macOS executable code signing *(1.3-guide)*

Standalone macOS executables produced by `bun build --compile` can now be signed after compilation with the platform `codesign` tool.

```sh
bun build --compile ./app.ts --outfile myapp
codesign --sign "Developer ID" ./myapp
```

### Sourcemaps for programmatically compiled executables *(since 1.3.1)*

`Bun.build({ compile: true, sourcemap: true })` now applies sourcemaps and emits an external map, matching `bun build --compile`; runtime stacks point to original files and lines instead of virtual `$bunfs` paths.

### Standalone executable configuration autoload *(since 1.3.3)*

Compiled executables normally search the directory where they are launched for `.env` and `bunfig.toml`. Disable either source at build time with `--no-compile-autoload-dotenv` and `--no-compile-autoload-bunfig`, or set `compile.autoloadDotenv` and `compile.autoloadBunfig` to `false` in `Bun.build()`.

```sh
bun build --compile --no-compile-autoload-dotenv --no-compile-autoload-bunfig app.ts
```

### Standalone executable config loading *(since 1.3.4)*

Standalone executables no longer load deployment-time `tsconfig.json` or `package.json` files by default. Opt back in at build time with `--compile-autoload-tsconfig` and `--compile-autoload-package-json`, or with `compile.autoloadTsconfig` and `compile.autoloadPackageJson` in `Bun.build()`.

```ts
await Bun.build({
  entrypoints: ["./app.ts"],
  compile: { autoloadTsconfig: true, autoloadPackageJson: true },
});
```

### Compile-target type rename *(since 1.3.7)*

The TypeScript type `Bun.Build.Target` was renamed to `Bun.Build.CompileTarget`; update annotations that used the old name.

### ESM bytecode in compiled executables *(since 1.3.9)*

Compiled executables can now combine `--bytecode` with `--format=esm`. Omitting `--format` still selects CommonJS.

```sh
bun build --compile --bytecode --format=esm app.ts
```

### Linux x64 compile-target typings *(since 1.3.9)*

`Bun.Build.CompileTarget` now includes the valid `bun-linux-x64-baseline` and `bun-linux-x64-modern` targets, so programmatic cross-compilation to those variants type-checks.

```ts
const target: Bun.Build.CompileTarget = "bun-linux-x64-modern";
```

### Linux standalone executable portability *(since 1.3.12)*

Linux executables produced by `bun build --compile` now run with execute-only permissions, without needing read access to `/proc/self/exe`. Builds created on NixOS or Guix also use a normalized ELF interpreter path instead of being tied to the originating Nix generation.

```sh
bun build --compile app.ts --outfile app
chmod 111 app
./app
```
