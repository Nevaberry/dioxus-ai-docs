# Builds and frontend development

## Build-result and output changes

### Failure and sourcemaps (`1.2-guide`, `1.2.19`)

`Bun.build()` rejects on build failure rather than returning errors in
`result.logs`; set `throw: false` to retain the old result-based flow.
`bun build --sourcemap` defaults to separate linked `.js.map` files; request
`--sourcemap=inline` for inline maps. The JS API accepts `sourcemap: true`; the
boolean was previously ignored.

### Core build controls (`1.2-guide`)

Available controls include:

- Cross-compilation with `--compile --target=bun-windows-x64`, Windows icon and
  hidden-console settings.
- `--format=cjs`, `--packages=external`, `--env="PUBLIC_*"`, `--drop=console`,
  `--banner`, `--footer`, and `--ignore-dce-annotations`.
- `--bytecode`, which emits a required `.jsc` beside each `.js`, skips async
  functions, generators, and `eval`, and can be about eight times the source
  size.
- `Bun.embeddedFiles`, listing assets embedded into a compiled executable.

## HTML and frontend serving

### HTML imports and the route option (`1.2-guide`, `1.2.3`)

Imported HTML makes `Bun.serve` bundle its linked scripts and styles. The
original option name was `static`; it was renamed to `routes`, which adds path
parameters, `req.params`, per-method handlers, wildcards, async handlers and an
optional fallback `fetch` function.

```ts
import page from "./index.html";

Bun.serve({
  routes: {
    "/": page,
    "/api/:id": req => Response.json(req.params),
  },
});
```

`server.reload({ static: ... })` was the original runtime swap form. Treat
`routes` as the current configuration name.

### Zero-config dev server (`1.2.3`, `1.2.12`)

`bun ./index.html` starts a server on port 3000 and bundles/hot-reloads linked
JS/JSX/TS and CSS. A quoted HTML glob creates a multi-page app with routes based
on file paths. `--console` streams browser console output to the terminal.

`Bun.serve` exposes the same stream through
`development: { console: true, hmr: true }`; messages are prefixed `[browser]`.

### Client-time constants (`1.2.3`, `1.2.4`)

Under `[serve.static]`, `env` selects variables inlined as `process.env.*` and
`define` maps identifiers to JavaScript source strings containing arbitrary JSON
constants.

```toml
[serve.static]
env = "BUN_PUBLIC_*"
define = { CONFIG = "{ \"version\": \"1.0\", \"beta\": false }" }
```

### HTML minification (`1.2.1`)

HTML-import minification defaults to off when `development: true` and on when
development is false. Override aggregate or whitespace/identifier/syntax
minification in `[serve.static]`; plugins are configured there too.

### Ahead-of-time HTML (`1.2.17`)

Server-side HTML imports are bundled by `bun build`: referenced scripts and
styles become assets and the server is wired to serve them. This works for a
normal build or one-file `--compile`; `bun --hot` retains on-demand HMR.

```sh
bun build ./src/server.ts --target=bun --outdir ./dist
bun build ./src/server.ts --compile --outfile=my-app
```

### Production and self-contained HTML (`1.3-guide`, `1.3.10`, `1.3.13`)

- `bun build ./index.html --production --outdir=dist` bundles production
  frontend settings.
- An HTML entry can be a normal `--compile` input for a full-stack executable.
- `--compile --target=browser` requires all entrypoints to be HTML and emits one
  file with JS/CSS inline and assets as data URIs; it cannot combine with
  `--splitting`.
- File-loader assets imported from JS are also inlined in that browser output.

### Production sourcemap serving (`1.4`)

HTML routes do not serve sourcemaps outside development by default. Set
`sourcemap` under `[serve.static]` when a different policy is required.

## CSS, JSX, React, and framework support

### CSS bundling and modules (`1.2-guide`, `1.2.5`)

CSS entrypoints resolve `@import`; CSS reachable from a JS/TS entrypoint is
flattened into one output. `.module.css` automatically rewrites class and ID
names and exports the name map. `composes` works within a file, from another
module, or from `global`.

### Svelte and HMR (`1.2.5`)

`bun-plugin-svelte` supplies bundler/dev-server integration, HMR, TypeScript in
`<script lang="ts">`, and browser/Bun/Node targets. The HMR runtime supports
`import.meta.hot.accept()` and dependency callbacks plus `on`/`off` events.
Bun event names use `bun:` prefixes while Vite `vite:` aliases also work.
Production builds dead-code-eliminate these calls.
Documented Bun events include `bun:beforeUpdate`, `bun:afterUpdate`,
`bun:error`, and `bun:ws:connect`.

### HMR URL semantics (`1.2.20`)

In browser HMR, `import.meta.url` uses `window.location.origin` rather than a
`bun://` URL.

### JSX purity and direct options (`1.2.22`, `1.2.23`)

JSX is treated as pure and unused elements may be removed. Set
`jsxSideEffects: true` to retain JSX whose component bodies have side effects.
`Bun.build({ jsx })` configures runtime, import source, factory, fragment,
development and side effects without requiring `tsconfig.json`.

### React transforms (`1.3.6`, `1.4`)

`reactFastRefresh: true` matches `--react-fast-refresh` and injects the refresh
transform for all targets. `bun build --react-compiler`, or
`reactCompiler: true`, runs React's automatic memoization compiler directly in
Bun's parser.

## Plugins

### Native pre-parse hook (`1.2-guide`)

`onBeforeParse()` runs an N-API addon over raw source without copying or string
conversion. Register namespace/filter plus `napiModule` and exported symbol.
The `bun-native-plugin` Rust crate exposes `define_bun_plugin!`, `#[bun]`, and
`set_output_source_code(..., BunLoader::...)`.

```ts
build.onBeforeParse(
  { namespace: "file", filter: "**/*.tsx" },
  { napiModule: plugin, symbol: "transform" },
);
```

### End hook and entrypoint hooks (`1.2.22`)

`build.onEnd(result)` runs after success or failure with the `BuildOutput`.
`onResolve` and `onLoad` also run for entrypoint files, enabling virtual
entrypoints.

### Runtime path resolution (`1.4-3`)

A runtime `Bun.plugin()` `onResolve` hook may return a normal filesystem path in
the default `file` namespace. It no longer comes back as an unloadable
`file:/abs/path`.

## Standalone executables

### Signing and Windows metadata (`1.2.4`, `1.2.19`, `1.2.21`)

Compiled macOS binaries are code-signable. Windows payloads live in a `.bun` PE
section so Authenticode signing stays valid. JS `compile` accepts `true`, a
target string, or an object with target/output and Windows icon/title/version
metadata, while retaining build-plugin support; corresponding CLI flags cover
`--windows-title`, `--windows-publisher`, `--windows-version`,
`--windows-description`, and `--windows-copyright`.

### Runtime flags and executable mode (`1.2.16`, `1.2.21`)

- `BUN_BE_BUN=1` makes a compiled app run its embedded runtime as a general Bun
  CLI.
- `--compile-exec-argv` bakes runtime flags into the binary and exposes them as
  `process.execArgv`.
- Compiled binaries no longer add an extra executable-name entry to
  `process.argv`, restoring normal `util.parseArgs` behavior (`1.2.22`).

### Config autoload (`1.3.3`, `1.3.4`)

Compiled programs otherwise read `.env` and `bunfig.toml` at runtime; disable
with `--no-compile-autoload-dotenv` and
`--no-compile-autoload-bunfig`, or the matching `compile` object fields.

They no longer load deployment-directory `tsconfig.json` or `package.json` by
default. Opt in with `--compile-autoload-tsconfig` and
`--compile-autoload-package-json` or `autoloadTsconfig`/`autoloadPackageJson`.

`Bun.build({ compile: true })` emits external sourcemaps so standalone stack
traces refer to original files rather than `/$bunfs/root/` (`1.3.1`).

### Local cross-compilation binary (`1.3.6`, `1.4-2`)

`--compile-executable-path=/path/to/bun-target` and JS `executablePath` use a
local target binary rather than downloading one, including for air-gapped
cross-compilation.

### Targets and bytecode (`1.3.9`, `1.4`)

- Compile objects accept SIMD-specific Linux targets such as
  `bun-linux-x64-modern` and `bun-linux-x64-baseline`.
- `--bytecode` can use ESM with `--compile`; ESM bytecode unlocks top-level
  await, `import.meta`, dynamic imports and code splitting. Without an explicit
  format, bytecode still defaults to CommonJS.

### Embedded filesystem and assets (`1.2.3`, `1.4`)

Files imported with `{ type: "file" }` are accessible from compiled programs
through async/sync `node:fs`. `--asset <file-or-dir>` embeds original paths;
`/$bunfs/` behaves like a directory tree for existence, stat, lstat, access and
directory enumeration, including recursive and `withFileTypes` forms.

### Linux executable layout (`1.3.12`, `1.4-2`)

Linux binaries embed modules in a `.bun` ELF section mapped with `PT_LOAD`
instead of reading `/proc/self/exe`, allowing `chmod 111` execution and zero
startup file I/O. NixOS/Guix builds normalize `PT_INTERP` to the FHS path.

`Bun.isStandaloneExecutable` is an allocation-free read-only boolean indicating
compiled execution (`1.4-2`).

## Build inputs and analysis

### Virtual files (`1.3.6`)

`Bun.build({ files })` provides in-memory modules whose string, Blob,
TypedArray, or ArrayBuffer contents override disk paths. Virtual and disk files
may import each other.

### Metafiles (`1.3.6`, `1.3.8`, `1.4-2`)

`metafile: true` returns esbuild-format `inputs`/`outputs` maps. CLI
`--metafile <path>` writes JSON. `--metafile-md[=path]` adds a Markdown report
with summaries, largest inputs, dependency chains, a full graph and searchable
markers; the JS option may name JSON and Markdown outputs together.

Bundled import paths in the metafile now equal the imported file's `inputs`
key, so `metafile.inputs[path]` resolves correctly.

### Bundle-time feature flags (`1.3.5`)

`feature(name)` from `bun:bundle` becomes a literal and enables dead-code
elimination. Repeat `--feature=NAME` for build/run/test or pass
`features: [...]`; augmenting `bun:bundle`'s `Registry.features` makes allowed
names type-checkable.

### Barrel optimization (`1.3.10`)

Pure re-export-only barrels load only imported submodules. Packages with
`sideEffects: false` get this automatically; otherwise use `optimizeImports`.
A local export or namespace import disables optimization, while `export *`
targets are always loaded.

### `sideEffects` globs (`1.2.21`)

The bundler honors glob syntax `*`, `?`, `**`, `[]`, and `{}` in a package's
`sideEffects`; a glob no longer de-optimizes the whole package.

## Module formats, loaders, and transforms

### CommonJS detection (`1.2-guide`)

A no-import/no-export file beginning with `"use strict"` is CommonJS rather
than ESM. `require.main === module` rewrites to `import.meta.main` without
forcing CommonJS.

### CommonJS output (`1.3.1`)

For `--format=cjs`, `import.meta.path`, `.dirname`, and `.file` become CommonJS
equivalents. `import.meta.url` is not rewritten.

### Decorators (`1.3.10`, `1.3.11`, `1.4-2`)

Standard stage-3 decorators are supported when `experimentalDecorators` is not
set, including methods, accessors, fields, classes, private auto-accessors,
initializer hooks, metadata and standard ordering. Legacy semantics remain for
`experimentalDecorators: true`.

`Bun.Transpiler` honors `experimentalDecorators` and
`emitDecoratorMetadata`; metadata alone also selects legacy behavior.
`scan()`/`scanImports()` respect `trimUnusedImports`.

### Target-dependent `using` (`1.3.14`)

Bun targets emit `using`/`await using` natively rather than helper lowering,
including compiled and bytecode builds. Browser and Node targets still lower.
This changes bundle output and disposal stack traces and fixes `using` in `.cjs`
failing because a CommonJS function wrapper was expected.

The public type name `Bun.Build.Target` became `Bun.Build.CompileTarget`
(`1.3.7`).

### Loader and resolver changes (`1.4-2`)

- `import "."` and `".."` resolve directories through index files or package
  `main`.
- Runtime `.css` default-imports `{}` rather than an absolute path. Module CSS
  still differs under bundling.
- `.xml` imports parsed XML; `--loader .xml:file` restores a file path.
- `jsx: react-jsx` always emits production `jsx`/`jsxs`; use `react-jsxdev` for
  `jsxDEV`. Explicit `NODE_ENV` wins.
- `useDefineForClassFields: false` moves initializers into the constructor after
  parameter properties and drops declaration-only fields.
- Missing wildcard export/import targets retry known extensions, including
  `.ts` for `.js`.
- Builtin and `bun` ESM imports no longer eagerly evaluate lazy exports.
- An unresolvable import inside a `catch` becomes a runtime throw rather than a
  build failure. Bundled namespace keys enumerate in sorted order.
- Browser builds apply package `browser` remaps for Node builtins before Bun's
  polyfills.

### Minified names (`1.2.22`)

`--minify-syntax` removes unused names from function/class expressions. If code
depends on `.name`, use `--keep-names` or `keepNames: true`.

### Splitting and unresolved imports (`1.4-2`, `1.4-3`)

`allowUnresolved: string[]` supports dynamic-import glob shapes. Splitting with
CommonJS or IIFE output fails with an ESM-only error rather than panicking;
`Bun.build()` does allow `splitting: true` together with `compile`.

Assignment to an ESM import is a runtime `TypeError` at the write when running
source, even in dead code; `bun build` continues to reject it at bundle time.

## Platform build notes

Native Windows ARM64 and its compile target were added in `1.3.10`. In `1.4-2`,
official FreeBSD x86_64/aarch64 and experimental Android builds ship; the Linux
glibc floor is 2.17 with a kernel 3.10 `memfd_create` fallback, and x64 releases
are baseline-only. Bun also runs in Windows AppContainer and read-only
directories.
