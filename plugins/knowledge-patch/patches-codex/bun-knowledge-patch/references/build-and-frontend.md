# Builds and frontend development

Use this reference for bundling, transpilation, HTML/CSS development, plugins, sourcemaps, bytecode, and standalone executables.

## `$NODE_PATH` bundler resolution

*Batch: `1.2.18`.*

`bun build` now searches the module directories in `$NODE_PATH`, extending the runtime support added earlier to bundled bare imports.

```sh
NODE_PATH=./src bun build ./entry.js --outdir ./out
```

## Ahead-of-time server-side HTML bundling

*Batch: `1.2.17`.*

`bun build` can now follow an HTML import from a server entrypoint, bundle its referenced client-side scripts and styles, and configure the built server to serve those assets. Use a Bun target for a deployable bundle or `--compile` for a self-contained full-stack executable.

```sh
bun build ./src/server.ts --target=bun --outdir=dist
bun build ./src/server.ts --compile --outfile=my-app
```

## Boolean sourcemap option

*Batch: `1.2.19`.*

`Bun.build({ sourcemap: true })` now generates a sourcemap; callers may use the boolean form as well as the existing string modes.

## Browser console streaming

*Batch: `1.2.12`.*

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

## Build failure semantics

*Batch: `1.2-guide`.*

`Bun.build()` now rejects its promise on build errors instead of resolving with errors only in `logs`. Set `throw: false` to retain the old result-inspection behavior.

## Built-in CSS bundling

*Batch: `1.2-guide`.*

`bun build` now accepts CSS entrypoints, resolves and flattens `@import` dependencies, and handles referenced assets. Importing CSS from JavaScript or TypeScript produces one combined CSS output for that module entrypoint alongside its JavaScript bundle.

```sh
bun build ./index.ts --outdir=dist
```

## Built-in React Compiler

*Batch: `1.4`.*

`bun build --react-compiler` or `reactCompiler: true` runs React's auto-memoization compiler directly in Bun's build pipeline, without a Babel or SWC plugin.

```ts
await Bun.build({
  entrypoints: ["./src/index.tsx"],
  outdir: "./dist",
  reactCompiler: true,
});
```

## Bundler plugin completion hooks

*Batch: `1.2.22`.*

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

## Bundler resolution and metadata

*Batch: `1.4-2`.*

Wildcard package exports are retried with known extensions, unresolved `require()`/`require.resolve()`/dynamic imports inside `catch` become runtime throws instead of build failures, and browser-target builds honor `package.json` browser remaps for Node built-ins. Metafile import paths now equal the corresponding `inputs` key, so `metafile.inputs[import.path]` resolves directly.

## Bytecode caches

*Batch: `1.2-guide`.*

`bun build --bytecode` emits JavaScriptCore `.jsc` caches, either beside normal output or inside a standalone executable. The corresponding `.js` file is still required for non-compiled output, and async functions, generators, and `eval` are not currently bytecode-compiled.

```sh
bun build --bytecode --outdir=dist app.ts
```

## CLI alias and sourcemap defaults

*Batch: `1.2-guide`.*

`bun -p` now means `bun --print`, replacing its former `--port` meaning. Bare `bun build --sourcemap` now emits linked `.map` files; request the previous behavior explicitly with `--sourcemap=inline`.

## Code-signable Windows executables

*Batch: `1.2.19`.*

Windows executables produced by `bun build --compile` can now be Authenticode-signed after compilation without invalidating their embedded source and assets.

```sh
bun build ./app.ts --compile --outfile app.exe
signtool.exe sign /f MyCert.pfx /p MyPassword app.exe
```

## CommonJS bundler output and detection

*Batch: `1.2-guide`.*

`bun build --format=cjs` now emits CommonJS. For otherwise ambiguous source, a leading `"use strict"` is treated as a last-chance CommonJS signal; conversely, `require.main === module` is rewritten to `import.meta.main`, so that check can coexist with ESM imports.

## Compile-target type rename

*Batch: `1.3.7`.*

The TypeScript type `Bun.Build.Target` was renamed to `Bun.Build.CompileTarget`; update annotations that used the old name.

## Compile-time feature flags

*Batch: `1.3.5`.*

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

## Cross-compiled executables

*Batch: `1.2-guide`.*

`bun build --compile` can target another supported platform, such as `--target=bun-windows-x64`; Windows builds also accept `--windows-icon` and `--windows-hide-console`. Compiled programs can inspect bundled assets through the iterable `embeddedFiles` export from `bun`.

## CSS modules

*Batch: `1.2.5`.*

Files ending in `.module.css` are automatically scoped and default-import as a class-name map. CSS Modules `composes` can reference classes in the same file, another module, or the global scope.

```ts
import styles from "./style.module.css";
const button = document.createElement("button");
button.className = styles.button;
```

## CSS view-transition selector arguments

*Batch: `1.3.2`.*

The CSS parser, bundler, and minifier now accept class selector arguments in view-transition pseudo-elements such as `::view-transition-old()`, `::view-transition-new()`, `::view-transition-group()`, and `::view-transition-image-pair()`.

```css
::view-transition-old(.slide-out) {
  animation: slide-out 200ms;
}
```

## Custom CommonJS extension loaders

*Batch: `1.2.9`.*

Bun now supports `require.extensions`, allowing CommonJS code to register a loader for a file extension.

```js
require.extensions[".custom"] = (module, filename) => {
  module._compile('module.exports = "loaded";', filename);
};
const value = require("./file.custom");
```

## Editable Chrome DevTools workspaces

*Batch: `1.2.15`.*

The frontend development server now exposes automatic workspace folders to Chrome DevTools, allowing served project files to be edited directly in the browser.

## Embedded executable runtime flags

*Batch: `1.2.21`.*

`bun build --compile-exec-argv` embeds Bun runtime arguments into a standalone executable; they take effect on launch and appear in `process.execArgv`.

```sh
bun build ./cli.ts --compile --compile-exec-argv="--smol --user-agent=MyApp/1.0"
```

## Embedded files through `node:fs`

*Batch: `1.2.3`.*

Files embedded in a compiled executable with a `file` import can now be passed to async `fs.readFile()` and `fs.stat()`, as well as sync `readFileSync()`, `statSync()`, and `existsSync()`.

```ts
import { promises as fs } from "node:fs";
import asset from "./asset.txt" with { type: "file" };

const contents = await fs.readFile(asset);
const stats = await fs.stat(asset);
```

## Esbuild-compatible build metafiles

*Batch: `1.3.6`.*

`Bun.build({ metafile: true })` returns `result.metafile` in esbuild's format, with input and output byte sizes, imports, exports, entry points, and contributing inputs. The CLI form writes the metadata directly with `--metafile <path>`.

```ts
const result = await Bun.build({
  entrypoints: ["./src/index.ts"],
  outdir: "./dist",
  metafile: true,
});
await Bun.write("./dist/meta.json", JSON.stringify(result.metafile));
```

## ESM bytecode in compiled executables

*Batch: `1.3.9`.*

Compiled executables can now combine `--bytecode` with `--format=esm`. Omitting `--format` still selects CommonJS.

```sh
bun build --compile --bytecode --format=esm app.ts
```

## Executable asset embedding

*Batch: `1.4`.*

`bun build --compile --asset <path>` embeds files or directories while preserving their names; code can locate them relative to `import.meta.dir`. Embedded `/$bunfs/` paths support filesystem existence, metadata, access, and directory-reading APIs, including recursive and `withFileTypes` reads.

```sh
bun build ./build/index.js --compile \
  --asset ./build/client --asset ./build/prerendered \
  --outfile server
```

## Global selectors in CSS Modules

*Batch: `1.2.6`.*

CSS Modules now process `:global()` correctly, preserving the enclosed selector instead of applying module scoping.

```css
:global(.button) {
  color: blue;
}
```

## HTML attribute semantics

*Batch: `1.4-4`.*

`HTMLRewriter` returns `""` rather than `null` for present-but-empty attributes, including boolean attributes. Its `setAttribute()` and `removeAttribute()` methods now throw when passed invalid arguments instead of returning an `Error` value.

## HTML entrypoint development server

*Batch: `1.2.3`.*

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

## HTML entrypoints

*Batch: `1.2-guide`.*

An imported HTML file can be assigned to a `Bun.serve()` static route. Bun bundles its module scripts and linked stylesheets, rewrites their URLs to generated static assets, and serves the transformed HTML.

```ts
import homepage from "./index.html";
Bun.serve({ static: { "/": homepage }, fetch: () => new Response("Not found", { status: 404 }) });
```

## HTML imports can select the text loader

*Batch: `1.2.10`.*

An `.html` file can now be imported as raw text with an import attribute instead of being forced through HTML entrypoint handling.

```ts
import html from "./template.html" with { type: "text" };
```

## HTML-import minification controls

*Batch: `1.2.1`.*

Minification for HTML imports can be disabled wholly or by whitespace, identifier, and syntax transforms under `[serve.static]`. If omitted, it defaults off for `Bun.serve({ development: true })` and on for `development: false`.

```toml
[serve.static]
minify = false
# Or set minify.whitespace, minify.identifiers, and minify.syntax separately.
```

## JSX side-effect preservation

*Batch: `1.2.22`.*

The bundler treats JSX expressions as pure by default, so unused JSX can be removed. Set `jsxSideEffects` when rendering a component must be retained for its side effects.

```json
{
  "compilerOptions": { "jsxSideEffects": true }
}
```

## Legacy decorator settings in `Bun.Transpiler`

*Batch: `1.3.11`.*

`Bun.Transpiler` now honors `experimentalDecorators` and `emitDecoratorMetadata` from `tsconfig` instead of always emitting standard decorators. Enabling `emitDecoratorMetadata` selects the legacy TypeScript decorator behavior even when `experimentalDecorators` is not explicitly set, restoring compatibility with frameworks that consume legacy metadata.

## Legal-comment source maps

*Batch: `1.3.1`.*

`bun build` source maps now map preserved multiline legal comments, including CRLF comments, back to their original source locations so license tooling and debuggers can trace them accurately.

## Linux standalone executable portability

*Batch: `1.3.12`.*

Linux executables produced by `bun build --compile` now run with execute-only permissions, without needing read access to `/proc/self/exe`. Builds created on NixOS or Guix also use a normalized ELF interpreter path instead of being tied to the originating Nix generation.

```sh
bun build --compile app.ts --outfile app
chmod 111 app
./app
```

## Linux x64 compile-target typings

*Batch: `1.3.9`.*

`Bun.Build.CompileTarget` now includes the valid `bun-linux-x64-baseline` and `bun-linux-x64-modern` targets, so programmatic cross-compilation to those variants type-checks.

```ts
const target: Bun.Build.CompileTarget = "bun-linux-x64-modern";
```

## macOS executable code signing

*Batch: `1.3-guide`.*

Standalone macOS executables produced by `bun build --compile` can now be signed after compilation with the platform `codesign` tool.

```sh
bun build --compile ./app.ts --outfile myapp
codesign --sign "Developer ID" ./myapp
```

## Markdown build metafiles

*Batch: `1.3.8`.*

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

## Method-specific static and HTML routes

*Batch: `1.2.14`.*

`Bun.serve({ routes })` can now restrict static `Response` values and imported HTML routes to particular HTTP methods. Method-specific routes also take precedence over the global `/*` route.

## Minified function and class names

*Batch: `1.2.22`.*

Syntax minification now removes unused names from function and class expressions. Use `--keep-names` or `keepNames: true` when reflection, diagnostics, or application logic depends on `Function.prototype.name`.

```sh
bun build --minify --keep-names ./input.js
```

## Modern HMR API and events

*Batch: `1.2.5`.*

The development server supports self-acceptance and dependency acceptance through `import.meta.hot.accept()`, including synchronous ESM imports; these calls are dead-code eliminated in production. `on()` and `off()` handle lifecycle events such as `bun:beforeUpdate`, `bun:afterUpdate`, `bun:error`, and `bun:ws:connect`, with Vite-prefixed event names also accepted.

```ts
import.meta.hot.accept("./foo", newFoo => updateState(newFoo));
import.meta.hot.on("bun:beforeUpdate", () => console.log("updating"));
```

## Native pre-parse plugins

*Batch: `1.2-guide`.*

Plugins gain `onBeforeParse()`, a low-overhead source transformation hook implemented by an N-API addon rather than JavaScript. Registration supplies the file filter plus the native module and exported symbol.

```ts
build.onBeforeParse(
  { namespace: "file", filter: "**/*.tsx" },
  { napiModule: nativePlugin, symbol: "transform" },
);
```

## New build controls

*Batch: `1.2-guide`.*

The CLI and `Bun.build()` can inject matching environment variables (`--env='PUBLIC_*'` / `env`), drop calls (`--drop` / `drop`), add `banner` and `footer` text, and leave all package imports external (`--packages external` / `packages: "external"`). `--ignore-dce-annotations` disables `@__PURE__` and similar annotations when incorrect annotations remove required side effects.

## Node source-map APIs

*Batch: `1.2.19`.*

`node:module` now provides the `SourceMap` class and `findSourceMap()`. A `SourceMap` exposes its payload and can map generated positions with `findEntry()`.

## Non-interactive React project initialization

*Batch: `1.2.14`.*

`bun init --react` selects the React template without a TTY; `--react=tailwind` and `--react=shadcn` select preconfigured variants, which is useful for programmatic scaffolding.

```sh
bun init --react=tailwind
```

## Object-loader default interop

*Batch: `1.2.2`.*

Plugin modules using `loader: "object"` now honor an exported `__esModule: true`: default imports and `require()` return the declared default value rather than a namespace wrapper.

```ts
builder.module("my-module", () => ({
  exports: { default: "hello", __esModule: true },
  loader: "object",
}));

const value = require("my-module"); // "hello"
```

## Official Svelte plugin

*Batch: `1.2.5`.*

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

## Persistent module compile cache

*Batch: `1.4-3`.*

`module.enableCompileCache()` and `NODE_COMPILE_CACHE` persist compiled bytecode between Bun processes using the Node-compatible interface.

## Production HTML builds

*Batch: `1.3-guide`.*

An HTML entrypoint can be bundled for deployment with the production build mode.

```sh
bun build ./index.html --production --outdir=dist
```

## Production HTML sourcemaps

*Batch: `1.4`.*

HTML routes no longer serve sourcemaps in production by default; development mode still does. Choose production behavior explicitly under `[serve.static]`.

```toml
[serve.static]
sourcemap = "linked"
```

## Programmatic executable compilation

*Batch: `1.2.21`.*

`Bun.build()` now creates standalone executables with `compile: true`, a target string, or a configuration object; compiled builds can also use bundler plugins.

```ts
await Bun.build({
  entrypoints: ["./cli.ts"],
  compile: { target: "bun-linux-x64-musl", outfile: "./cli" },
});
```

## Programmatic JSX configuration

*Batch: `1.2.23`.*

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

## Running Bun from a compiled executable

*Batch: `1.2.16`.*

Setting `BUN_BE_BUN` when launching a single-file executable runs its embedded Bun binary instead of the compiled entrypoint.

```sh
BUN_BE_BUN=1 ./my-app --version
```

## Runtime loader changes

*Batch: `1.4-2`.*

Runtime `.css` imports now default-export `{}` instead of an absolute path. Bare `import "."` and `import ".."` now resolve the directory's `package.json` entry or index file rather than a same-named sibling file.

## Self-contained browser HTML compilation

*Batch: `1.3.10`.*

Compiling an HTML entrypoint with the browser target inlines its bundled JavaScript and CSS and converts asset references to `data:` URLs, producing an HTML file that can run directly from a `file://` URL. Every entrypoint must be HTML, and this mode cannot be combined with splitting.

```sh
bun build --compile --target=browser ./index.html
```

## Sourcemaps for programmatically compiled executables

*Batch: `1.3.1`.*

`Bun.build({ compile: true, sourcemap: true })` now applies sourcemaps and emits an external map, matching `bun build --compile`; runtime stacks point to original files and lines instead of virtual `$bunfs` paths.

## Standalone executable compatibility

*Batch: `1.4-3`.*

Embedded CommonJS entry points can require one another, and standalone executables apply `BUN_OPTIONS` through `process.execArgv` instead of leaking those flags into `process.argv`. `Bun.build()` also accepts `splitting: true` together with `compile`.

## Standalone executable config loading

*Batch: `1.3.4`.*

Standalone executables no longer load deployment-time `tsconfig.json` or `package.json` files by default. Opt back in at build time with `--compile-autoload-tsconfig` and `--compile-autoload-package-json`, or with `compile.autoloadTsconfig` and `compile.autoloadPackageJson` in `Bun.build()`.

```ts
await Bun.build({
  entrypoints: ["./app.ts"],
  compile: { autoloadTsconfig: true, autoloadPackageJson: true },
});
```

## Standalone executable configuration autoload

*Batch: `1.3.3`.*

Compiled executables normally search the directory where they are launched for `.env` and `bunfig.toml`. Disable either source at build time with `--no-compile-autoload-dotenv` and `--no-compile-autoload-bunfig`, or set `compile.autoloadDotenv` and `compile.autoloadBunfig` to `false` in `Bun.build()`.

```sh
bun build --compile --no-compile-autoload-dotenv --no-compile-autoload-bunfig app.ts
```

## Standalone executable detection

*Batch: `1.4-2`.*

`Bun.isStandaloneExecutable` is a read-only boolean that reports whether code is running inside a `bun build --compile` binary without allocating or inspecting `Bun.embeddedFiles`.

## Standard ES decorators

*Batch: `1.3.10`.*

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

## Static-file compile-time defines

*Batch: `1.2.4`.*

`[serve.static].define` in `bunfig.toml` inlines constants into static-file bundles. Unlike exposed environment variables, define values can contain arbitrary JSON encoded as JavaScript inside a TOML string.

```toml
[serve.static]
define = { CONFIG = "{ \"version\": \"1.0\", \"beta\": false }" }
```

## TypeScript module-preservation default

*Batch: `1.2.14`.*

New default TypeScript configurations now use `"module": "Preserve"` instead of `"ESNext"`, preserving the module syntax written in each file rather than transforming it.

```json
{
  "compilerOptions": { "module": "Preserve" }
}
```

## Virtual and overlaid build files

*Batch: `1.3.6`.*

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

## Windows ARM64 runtime and compile target

*Batch: `1.3.10`.*

Bun now runs natively on Windows ARM64 and standalone executables can target that platform with `bun-windows-arm64`.

```sh
bun build --compile --target=bun-windows-arm64 ./app.ts --outfile myapp
```

## Windows executable metadata

*Batch: `1.2.21`.*

Compiled Windows executables can set title, publisher, version, description, and copyright through matching `--windows-*` flags or `compile.windows` in `Bun.build()`.

```ts
await Bun.build({
  entrypoints: ["./app.js"],
  compile: { windows: { title: "My App", publisher: "Acme", version: "1.2.3.4" } },
});
```
