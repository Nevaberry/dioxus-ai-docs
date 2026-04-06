# Module System & Node.js Compatibility

## Import Text and Bytes (2.4+, unstable)

Import non-JS files into the module graph with `--unstable-raw-imports`. Works with `deno compile` and `deno bundle`:
```ts
import message from "./hello.txt" with { type: "text" };    // string
import bytes from "./image.png" with { type: "bytes" };      // Uint8Array
```

## Wasm Source Phase Imports (2.6+)

Import a compiled `WebAssembly.Module` directly (no runtime fetch):
```ts
import source addModule from "./add.wasm";
const { add } = WebAssembly.instantiate(addModule).exports;
```

## `--preload` Flag (2.4+)

Execute code before the main script (available in `deno run`, `deno test`, `deno bench`):
```bash
deno --preload setup.ts main.ts
```

## `--require` Flag for CJS Preloading (2.6+)

Like `--preload` but for CommonJS modules:
```bash
deno run --require ./setup.cjs main.ts
```

## `DENO_COMPAT=1` (2.4+)

Single env var that enables `--unstable-detect-cjs`, `--unstable-node-globals`, `--unstable-bare-node-builtins`, and `--unstable-sloppy-imports` for package.json-first projects. Also, `--unstable-sloppy-imports` is being stabilized to `--sloppy-imports`.

## Node Globals Always Available (2.4+)

`Buffer`, `global`, `setImmediate`, and `clearImmediate` are now available in user code without `--unstable-node-globals`.

## `@types/node` Included by Default (2.6+)

No longer need to manually install `@types/node` — Deno provides Node.js type declarations automatically. Existing project-level `@types/node` still takes precedence.

## `jsr:` Scheme in `package.json` (2.7+)

Use JSR packages directly in package.json without needing deno.json:
```json
{ "dependencies": { "@std/path": "jsr:^1.0.9" } }
```

## `package.json` Overrides (2.7+)

Deno now supports the `overrides` field to pin transitive dependency versions.
