# Toolchain & CLI

## `dx`: npx for Deno (2.6+)

New `dx` command runs package binaries (like `npx`). Defaults to `--allow-all`, prompts before download, runs lifecycle scripts automatically. Install alias with `deno x --install-alias`.

```bash
dx cowsay "Hello"            # defaults to npm:cowsay
dx jsr:@std/http/file-server # explicit registry
```

## `deno bundle` (2.4+)

Restored `deno bundle` using esbuild under the hood. Supports minification, platform targeting, and sourcemaps.

```bash
deno bundle --minify main.ts
deno bundle --platform browser --output bundle.js app.jsx
deno bundle --platform browser --output bundle.js --sourcemap=external app.jsx
```

### `Deno.bundle()` Runtime API (2.5+, unstable)

Programmatic bundling via `Deno.bundle()`. Requires `--unstable-bundle`.

```ts
const result = await Deno.bundle({
  entrypoints: ["./index.tsx"],
  outputDir: "dist",
  platform: "browser",
  minify: true,
});
```

HTML files also work as entrypoints: `deno bundle --outdir dist index.html` — bundles referenced scripts and CSS, updates paths with content hashes.

## `deno compile` Enhancements

### FFI and Native Addons (2.3+)

`deno compile` now supports FFI and Node native add-ons.

```bash
deno compile --allow-ffi --allow-env main.ts
```

### `--exclude` (2.3+)

Omit files from the compiled binary:

```bash
deno compile --include folder --exclude folder/sub_folder main.ts
```

### `Deno.build.standalone` (2.3+)

Detect if running in a compiled binary:

```ts
if (Deno.build.standalone) {
  console.log("Running as compiled binary");
}
```

### `--self-extracting` (2.7+)

Extracts embedded files to disk at runtime — enables full Node API support including native addons.

```bash
deno compile --self-extracting main.ts
```

### `deno install --compile` (2.7+)

Compile npm packages to standalone binaries during global install:

```bash
deno install --global --compile -A npm:@anthropic-ai/claude-code
```

## `deno create` (2.7+)

Scaffold projects: `deno create npm:vite -- my-project`.

## `deno audit` (2.6+)

Scans dependencies against GitHub CVE database.

```bash
deno audit          # check GitHub CVE database
deno audit --socket # also check socket.dev (malware, supply chain)
```

Set `SOCKET_API_KEY` for org policies with `--socket`.

### `--ignore` (2.7+)

Filter known CVEs: `deno audit --ignore=CVE-2024-12345,CVE-2024-67890`.

## `deno approve-scripts` (2.6+)

Replaces `deno install --allow-scripts`. Interactive picker to approve/deny lifecycle scripts per package. Choices saved to `allowScripts` in `deno.json`.

## `deno add` Enhancements

### `--npm` and `--jsr` Flags (2.3+)

Add multiple packages from one registry without specifiers:

```bash
deno add --npm chalk react
deno add --jsr @std/fs @std/path
```

### `--save-exact` (2.7+)

Pin exact versions: `deno add --save-exact npm:express` → `"express": "4.21.0"` (no caret).

## `deno check` Enhancements

### No-arg Check (2.3+)

`deno check` (no args) type-checks all files in the project.

### `--check-js` (2.7+)

Type-check JS files without config: `deno check --check-js main.js`.

### `--unstable-tsgo` (2.6+)

Go-based fast TypeScript checker: `deno check --unstable-tsgo main.ts` (or `DENO_UNSTABLE_TSGO=1`).

## `deno fmt --fail-fast` (2.7+)

Stop formatting on first error: `deno fmt --check --fail-fast`.

## `deno install --lockfile-only` (2.6+)

Update lockfile without downloading packages — useful in CI: `deno install --lockfile-only`.

## `deno task` Enhancements

### Wildcards and Dependency-only Tasks (2.2+)

Wildcard task names run matching tasks in parallel. Tasks can have only `dependencies` (no command).

```jsonc
{
  "tasks": {
    "dev-client": "deno run --watch client/mod.ts",
    "dev-server": "deno run --watch server/mod.ts",
    "dev": { "dependencies": ["dev-client", "dev-server"] }
  }
}
// deno task "dev-*"  — runs dev-client and dev-server in parallel
// deno task dev       — runs both via dependencies
```

### `pipefail` and `shopt` (2.7+)

Tasks now support `set -o pipefail` and `shopt` (`nullglob`, `failglob`, `globstar`). `failglob` is off by default.

## `deno run` Bare Specifiers (2.4+)

Import map entries now work as entry points: `deno run file-server` resolves via `deno.json` imports.

## `--preload` Flag (2.4+)

Execute code before the main script. Available for `deno run`, `deno test`, and `deno bench`:

```bash
deno --preload setup.ts main.ts
```

## `--require` Flag (2.6+)

Like `--preload` but for CJS modules: `deno run --require ./setup.cjs main.ts`.
