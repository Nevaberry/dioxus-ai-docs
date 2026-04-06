# CLI Commands

## `dx` / `deno x` — npx for Deno (2.6+)

Runs package binaries like `npx`. Defaults to `--allow-all`, prompts before download, runs lifecycle scripts automatically. Install alias: `deno x --install-alias`.
```bash
dx cowsay "Hello"
dx --allow-read prettier --check .
```

## `deno bundle` (2.4+)

Restored as esbuild-based bundler. Supports server and browser platforms, tree shaking, minification:
```bash
deno bundle --minify main.ts
deno bundle --platform browser --output bundle.js --sourcemap=external app.jsx
```

### `Deno.bundle()` Runtime API (2.5+, unstable)

Programmatic bundling (requires `--unstable-bundle`):
```ts
const result = await Deno.bundle({
  entrypoints: ["./index.tsx"],
  outputDir: "dist",
  platform: "browser",
  minify: true,
});
```

## `deno audit` (2.6+)

Scan dependencies for CVEs (GitHub database). Optional `--socket` flag checks socket.dev:
```bash
deno audit          # GitHub CVE database
deno audit --socket # + socket.dev malware/quality checks
```

## `deno create` (2.7+)

Scaffold projects from templates:
```bash
deno create npm:vite -- my-project
deno create jsr:@std/http # uses ./create export
```

## `deno compile` Enhancements

### FFI and Node Native Add-ons (2.3+)

`deno compile` now supports FFI and Node native add-ons. New `--exclude` flag:
```bash
deno compile --include folder --exclude folder/sub_folder main.ts
```
`Deno.build.standalone` boolean detects if running inside a compiled binary.

### `--self-extracting` (2.7+)

Extracts embedded files to disk at runtime — enables native addons in compiled binaries:
```bash
deno compile --self-extracting -A main.ts -o my-app
```

## `deno install --compile` (2.7+)

Compile npm packages to standalone executables during global install:
```bash
deno install --global --compile -A npm:@anthropic-ai/claude-code
```

## `deno approve-scripts` (2.6+)

Interactive picker to approve/deny npm lifecycle scripts (`postinstall`, etc.). Saves choices to `allowScripts` in deno.json.

## `deno task` Improvements

### Wildcards and Dependency-only Tasks (2.2+)

Wildcard task names run all matches in parallel (quote to avoid shell expansion):
```sh
deno task "start-*"
```
Tasks without commands group dependencies:
```json
{ "tasks": { "dev": { "dependencies": ["dev-client", "dev-server"] } } }
```

### Shell Improvements (2.7+)

`set -o pipefail` and `shopt` (`nullglob`, `failglob`, `globstar`) now configurable. `failglob` disabled by default to match bash.
