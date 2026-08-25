# Type Checking, Tasks, CLI, and Editor Tooling

Use this reference for the following topic-specific compatibility details.

## `rootDirs` support in the checker (2.5.0)

`deno check` now honors `compilerOptions.rootDirs` from `tsconfig.json`, extending the option beyond its earlier language-server support.

```json
{
  "compilerOptions": {
    "rootDirs": ["src", "generated"]
  }
}
```

## Additional task controls (2.9-guide)

`--if-present` makes a missing task succeed, `--env-file` loads dotenv values without forwarding the flag into the task command, and `!(...)` groups exclude matching task names from a wildcard selection.

```sh
deno task --if-present optional
deno task --env-file=.env build
deno task "test:*(!e2e|interactive)"
```

## Argument-free project checking (2.3-guide)

Running `deno check` without file arguments now behaves like `deno check .`, checking the current directory rather than requiring an explicit target.

## Broader editor auto-import discovery (2.4-guide)

The language server can now find auto-imports through bare workspace specifiers, mapped npm resolutions, and locally patched JSR packages.

## CLI path escaping and runtime logging (2.0.0)

In path-based flags, a doubled comma escapes a literal comma inside a value. Runtime logging is configured with `DENO_LOG` instead of `RUST_LOG`.

```sh
deno run --allow-read=/tmp/with,,comma main.ts
```

## Delta runtime upgrades (2.8-guide)

`deno upgrade` uses checksum-verified binary deltas when available and falls back to a full archive automatically; `--no-delta` forces a full download.

```sh
deno upgrade --no-delta
```

## Dynamic task completions (2.6-guide)

Regenerate shell completions with `deno completions --dynamic` to make task suggestions follow the current `deno.json`.

## Emit-cache and V8 controls (2.3.0)

Deno recognizes `DENO_EMIT_CACHE_MODE` for selecting its emit-cache mode, and the V8 flag pass-through now accepts `--single-threaded`.

```sh
deno run --v8-flags=--single-threaded main.ts
```

## Escaped non-BMP characters in configuration (2.6.0)

JSON configuration now correctly decodes UTF-16 surrogate pairs in Unicode escape sequences, so generated `deno.json` files can represent non-BMP characters this way.

```json
{ "tasks": { "rocket": "echo \uD83D\uDE80" } }
```

## Frozen task execution (2.2.0)

`deno task` now accepts `--frozen`, allowing CI tasks to require an up-to-date lockfile without modifying it.

```sh
deno task --frozen build
```

## Full CLI help (2.3.0)

`--help=full` exposes the expanded command help when the normal help view omits advanced options.

## Input-based task caching (2.9-guide)

Object-form tasks can declare `files` inputs and `output` artifacts; after a successful run, Deno fingerprints the command, matched contents, listed environment variables, dependency results, arguments, host, and runtime version, then skips matching work and restores outputs. Empty input matches, npm scripts, and tasks without commands remain uncacheable, and a dependency rerun invalidates its dependents.

```json
{
  "tasks": {
    "build": {
      "command": "deno run -A build.ts",
      "files": ["src/**/*.ts"],
      "output": ["dist/**"]
    }
  }
}
```

## JavaScript checking from the CLI (2.7-guide)

`deno check --check-js` type-checks JavaScript without per-file `@ts-check` comments or a persistent `compilerOptions.checkJs` setting.

```sh
deno check --check-js main.js
```

## JSDoc imports during checking (2.2-guide)

`deno check` now respects JSDoc `@import` tags, allowing JavaScript files to import types inline without a runtime import.

```js
/** @import { add } from "./add.ts" */
/** @param {typeof add} fn */
export const callAdd = (fn) => fn(1, 2);
```

## Parallel task output and shell behavior (2.8-guide)

Concurrent task output is automatically prefixed and color-coded by task name, including subprocess output. The task shell adds `set -e` / `set -o errexit`, `set +e`, and the `:` null command.

## Selective cache cleaning (2.3.0)

`deno clean --except <paths>` removes cached data except what is required to run the named paths, making it possible to reclaim cache space without evicting a selected application.

```sh
deno clean --except main.ts
```

## Task and script discovery (2.5-guide)

Invoking `deno run` without an argument now lists available `deno.json` tasks and `package.json` scripts instead of only reporting a missing script argument.

## Task concurrency control (2.9-guide)

For workspace runs, `deno task --jobs` (`-j`, also `--concurrency`) caps parallel tasks, overrides `DENO_JOBS`, and defaults to the available CPU count.

```sh
deno task --recursive --jobs 1 build
```

## Task-shell controls and glob default (2.7-guide)

The task shell supports `set -o pipefail` and configurable `shopt` behavior for `nullglob`, `failglob`, and `globstar`. `failglob` is now off by default, matching Bash and preventing unmatched wildcard-like URL characters from failing a task.

## Task-shell expansion (2.3.0)

The `deno task` shell now supports backtick command substitution and basic tilde expansion, so task commands can use forms such as `` `command` `` and `~/path`.

## TypeScript 5.7 typed arrays (2.2-guide)

Deno 2.2 uses TypeScript 5.7, where typed arrays are generic over their backing `ArrayBufferLike`. Code can distinguish `Uint8Array<ArrayBuffer>` from `Uint8Array<SharedArrayBuffer>`; Buffer-related assignability errors after upgrading may require a newer `@types/node`.

```ts
const shared: Uint8Array<SharedArrayBuffer> =
  new Uint8Array(new SharedArrayBuffer(8));
```

## Unstable subprocess helpers (2.7.0)

The unstable runtime API adds `Deno.spawn()`, `Deno.spawnAndWait()`, and `Deno.spawnAndWaitSync()` for spawning a process or spawning one and waiting for its result.

## Verified runtime upgrades (2.7-guide)

`deno upgrade --checksum=<sha256>` verifies the downloaded runtime against the supplied SHA-256 checksum; per-platform checksum files are published beside release archives.

```sh
deno upgrade --checksum=<sha256-hash> 2.7.0
```

## Watch-mode type checking (2.8.0)

`deno check --watch` keeps the checker running and rechecks when its inputs change.

```sh
deno check --watch src/main.ts
```

## Web Cache location reporting (2.1.0)

`deno info` now reports the Web Cache location, making its on-disk storage discoverable from the CLI.
