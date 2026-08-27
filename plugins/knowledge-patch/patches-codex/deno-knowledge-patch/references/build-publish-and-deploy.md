# Build, Publish, and Deploy

Use this reference for the following topic-specific compatibility details.

## Additional publishable import schemes (2.3.0)

`deno publish` accepts dependencies using the `virtual:` and `cloudflare:` schemes, allowing packages built for tools that use those specifiers to pass publication processing.

## Assets in compiled executables (2.1-guide)

`deno compile --include` embeds local files or directories in an executable. The program reads them through their normal paths, commonly relative to `import.meta.dirname`; remote assets cannot be included.

```sh
deno compile --include ./names.csv --include ./data/ main.ts
```

```ts
const names = Deno.readTextFile(import.meta.dirname + "/names.csv");
```

## Bundled compilation (2.9-guide)

The experimental `deno compile --bundle` tree-shakes an entrypoint into one module before embedding it instead of including the entire resolved `node_modules` tree. It can be combined with `--minify` for smaller npm-heavy executables.

```sh
deno compile --bundle --minify --output app main.ts
```

## Bundled npm dependencies (2.5-guide)

Deno's npm compatibility now supports packages that declare `bundleDependencies` in `package.json`.

## Bundler behavior in workers and cross-runtime projects (2.6-guide)

Bundling now works from Web Workers, and `bun:` and `cloudflare:` imports remain external by default. `Deno.bundle()` output files are typed as `Uint8Array<ArrayBuffer>`.

## Bundler target and entry-point compatibility (2.6.0)

Browser-targeted `Deno.bundle()` output no longer attempts to use `createRequire`, JSR entry points now receive the correct `import.meta.main` transform, and bundling is supported on Android.

## Bundler-style TypeScript resolution (2.5-guide)

`deno check` now supports `compilerOptions.moduleResolution: "bundler"`, completing more of the configuration expected by standard SvelteKit and Next.js project templates.

```json
{ "compilerOptions": { "moduleResolution": "bundler" } }
```

## Compiled executable size reporting (2.2.0)

`deno compile` now reports the sizes of remote modules and metadata, making their contributions visible when investigating executable size.

## Compiled global installs (2.7-guide)

`deno install --global --compile` compiles an npm package into a standalone executable that starts without an installed Deno runtime.

```sh
deno install --global --compile -A npm:@anthropic-ai/claude-code
```

## Compiled Node filesystem access (2.8.0)

Node `fs` APIs can now access files in a `deno compile` executable's virtual filesystem, reducing the need to use Deno-specific file APIs for embedded assets.

## Compiled-install flag combinations (2.7.0)

Compiled installs now work with `--force`, and global compiled installs support `--allow-scripts` when trusted lifecycle scripts are required.

## Compiler-option dependencies in lockfiles (2.1.0)

The lockfile now tracks dependencies referenced through TypeScript compiler options, so those dependencies participate in locked resolution.

## Data URL bundling (2.7.0)

The bundler now handles data URLs through esbuild, so data-URL modules can participate in a bundle graph.

## Declaration-producing bundles (2.9-guide)

`deno bundle --declaration` emits one rolled-up, self-contained `.d.ts` per entrypoint beside the JavaScript output. Browser-platform bundles also honor object-form `package.json` `browser` mappings, including module stubs.

```sh
deno bundle mod.ts --outdir dist --declaration
```

## Declarative compile assets (2.8-guide)

The `compile` configuration in `deno.json` accepts `include` and `exclude`, allowing embedded data-file selection to live in project configuration instead of repeated CLI flags.

## Deployment file filters (2.7.0)

Deployment configuration now supports `include` and `exclude`, allowing the set of files sent to a deployment to be selected explicitly.

## HTML bundle entry points (2.5-guide)

`deno bundle` accepts HTML entry points, finds their module scripts, bundles imported global CSS, and rewrites the output HTML to content-hashed asset paths. HTML entries also work with `Deno.bundle()`.

```sh
deno bundle --outdir dist index.html
```

## Included package assets (2.9.0)

`deno pack` now includes assets matched by `publish.include` in the generated tarball, so explicitly selected non-module files are shipped with the package.

## Native dependencies, exclusions, and build detection in compiled executables (2.3-guide)

`deno compile` can now package programs that use Deno FFI or Node native add-ons. It can also exclude paths from an included tree, and `Deno.build.standalone` lets code detect that it is running from a self-contained executable.

```sh
deno compile --allow-ffi --include assets --exclude assets/test-data main.ts
```

```ts
if (Deno.build.standalone) console.log("running as a compiled executable");
```

## npm tarballs from Deno projects (2.8-guide)

`deno pack` turns a Deno or JSR project into an npm-publishable tarball: it transpiles reachable exported modules, emits declarations, generates `package.json`, and rewrites JSR, npm, and relative TypeScript specifiers for npm consumers. Selection is export-graph based and deterministic rather than a copy of the whole directory.

```sh
deno pack --dry-run
deno pack --set-version 2.0.0 --output my-package.tgz
```

## Per-member compiler options (2.2-guide)

Each workspace member may define its own `compilerOptions` in its local `deno.json`, so browser and server packages can use different libraries while inheriting unrelated root settings.

```json
{ "compilerOptions": { "lib": ["dom", "esnext"] } }
```

## Persistent compiled-application storage (2.9-guide)

Default `Deno.openKv()`, `localStorage`, and Cache API data in a compiled binary now persist under a per-application platform data directory instead of remaining in memory. `--app-name` selects the identity, defaults to the output filename, and allows renamed or separately built binaries to share the same store.

```sh
deno compile --unstable-kv --app-name notes --output notes main.ts
```

## Preloads in compiled executables (2.6.0)

`deno compile` now accepts `--preload`; the preload module runs before the main module when the resulting executable starts.

```sh
deno compile --preload ./setup.ts --output app ./main.ts
```

## Preserving names in bundles (2.7.0)

`deno bundle --keep-names` preserves names in generated output when bundling would otherwise rewrite them.

```sh
deno bundle --keep-names --outdir dist main.ts
```

## Published local-path dependencies (2.8-guide)

When registry metadata contains stray `file:` or `link:` dependencies, Deno now skips those entries instead of failing resolution; the referenced development-only code is expected to be present in the published tarball.

## Published version override (2.1-guide)

`deno publish --set-version` overrides the version in `deno.json` for that publication. It works only when publishing one package, not a workspace.

```sh
deno publish --set-version 0.2.0
```

## Raw imports cannot be published (2.4.0)

`deno publish` rejects packages containing text or byte imports, even though those imports are supported by runtime, bundle, and compile workflows.

## Restored JavaScript bundling (2.4-guide)

`deno bundle` is available again, now backed by esbuild and able to bundle npm and JSR dependencies for Deno or browser targets with tree shaking, minification, and source maps. The restored command is still marked experimental.

```sh
deno bundle --minify --platform browser --sourcemap=external --output bundle.js app.jsx
```

## Runtime bundling API (2.5-guide)

Experimental `Deno.bundle()` bundles JavaScript or TypeScript programmatically and requires `--unstable-bundle`; its options include entry points, output directory, platform, and minification.

```ts
await Deno.bundle({
  entrypoints: ["./main.ts"],
  outputDir: "dist",
  platform: "browser",
  minify: true,
});
```

## Self-extracting compiled programs (2.7-guide)

`deno compile --self-extracting` extracts embedded files on first run and then uses the real filesystem, enabling full Node APIs and native addons that cannot operate against the usual in-memory filesystem. It extracts beside the executable when writable, otherwise under the platform data directory.

```sh
deno compile --self-extracting -A main.ts -o my-app
```

## Sloppy imports in compiled programs (2.2.0)

`deno compile` now supports sloppy imports, so programs using that resolution mode can be compiled as executables.

## Stable deployment command (2.4.0)

`deno deploy` is no longer behind an unstable flag, so deployment workflows can invoke the command through the stable CLI.

## Standalone source transpilation (2.8-guide)

`deno transpile` strips types from TypeScript, JSX, or TSX without bundling, rewriting modules, or loading project configuration. It supports multiple inputs, `--outdir`, separate or inline source maps, and declaration emission.

```sh
deno transpile src/mod.ts --outdir dist --source-map separate --declaration
```

## Verbatim compiled assets (2.9-guide)

`deno compile --include-as-is` embeds files or directories in the executable's virtual filesystem without module resolution or transpilation, complementing `--include` for prebuilt bundles and data assets. Both flags may be used in one build.

```sh
deno compile --include-as-is dist/ --allow-read server.ts
```

## Windows executable signing and icons (2.0-guide)

`deno compile` supports code signing and custom icons for Windows executables.

## Workspace deployment includes (2.9.1)

Deployment configuration now preserves include entries from workspace members instead of stripping them.
