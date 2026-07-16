# Type Checking, Tasks, CLI, and Editor Tooling
Configure type checking, automate tasks, use project and CLI utilities, and integrate editors and language servers.
## Contents
- [Type checking and configuration](#type-checking-and-configuration)
- [Tasks and shell](#tasks-and-shell)
- [CLI and project setup](#cli-and-project-setup)
- [Editor and language server](#editor-and-language-server)
- [Watch and upgrade workflows](#watch-and-upgrade-workflows)

## Type checking and configuration

### Argument-free project checking (2.3-guide)

Running `deno check` without file arguments now behaves like `deno check .`, checking the current directory rather than requiring an explicit target.

### Bundler-style TypeScript resolution (2.5-guide)

`deno check` now supports `compilerOptions.moduleResolution: "bundler"`, completing more of the configuration expected by standard SvelteKit and Next.js project templates.

```json
{ "compilerOptions": { "moduleResolution": "bundler" } }
```

### Escaped non-BMP characters in configuration (2.6.0)

JSON configuration now correctly decodes UTF-16 surrogate pairs in Unicode escape sequences, so generated `deno.json` files can represent non-BMP characters this way.

```json
{ "tasks": { "rocket": "echo \uD83D\uDE80" } }
```

### Expanded `tsconfig.json` project support (2.4-guide)

`tsconfig.json` handling now honors `references`, `extends`, `files`, `include`, and `exclude`, so referenced projects and configured file boundaries participate in Deno tooling.

### Experimental `tsgo` and type-tooling support (2.6-guide)

`deno check` can use the experimental Go-based checker through `--unstable-tsgo` or `DENO_UNSTABLE_TSGO=1`. Checking now supports `compilerOptions.paths` and `isolatedDeclarations` and applies `skipLibCheck` to graph errors; the language server adds `source.organizeImports` and recognizes individual `describe`/`it` tests.

```sh
deno check --unstable-tsgo main.ts
```

### JavaScript checking from the CLI (2.7-guide)

`deno check --check-js` type-checks JavaScript without per-file `@ts-check` comments or a persistent `compilerOptions.checkJs` setting.

```sh
deno check --check-js main.js
```

### JSDoc imports during checking (2.2-guide)

`deno check` now respects JSDoc `@import` tags, allowing JavaScript files to import types inline without a runtime import.

```js
/** @import { add } from "./add.ts" */
/** @param {typeof add} fn */
export const callAdd = (fn) => fn(1, 2);
```

### Per-member compiler options (2.2-guide)

Each workspace member may define its own `compilerOptions` in its local `deno.json`, so browser and server packages can use different libraries while inheriting unrelated root settings.

```json
{ "compilerOptions": { "lib": ["dom", "esnext"] } }
```

### Project-scoped `tsconfig.json` discovery (2.4.0)

Automatic `tsconfig.json` discovery is disabled when a project has neither `deno.json` nor `package.json`, and `--no-config` suppresses that discovery explicitly.

### `rootDirs` support in the checker (2.5.0)

`deno check` now honors `compilerOptions.rootDirs` from `tsconfig.json`, extending the option beyond its earlier language-server support.

```json
{
  "compilerOptions": {
    "rootDirs": ["src", "generated"]
  }
}
```

### Watch-mode type checking (2.8.0)

`deno check --watch` keeps the checker running and rechecks when its inputs change.

```sh
deno check --watch src/main.ts
```

### Workspace TypeScript configuration (2.3.0)

`deno check` detects a `tsconfig.json` at the workspace root and supports TypeScript's `erasableSyntaxOnly` compiler option, allowing that restriction to participate in Deno type checking.

```json
{ "compilerOptions": { "erasableSyntaxOnly": true } }
```

## Tasks and shell

### Additional task controls (2.9-guide)

`--if-present` makes a missing task succeed, `--env-file` loads dotenv values without forwarding the flag into the task command, and `!(...)` groups exclude matching task names from a wildcard selection.

```sh
deno task --if-present optional
deno task --env-file=.env build
deno task "test:*(!e2e|interactive)"
```

### Dynamic task completions (2.6-guide)

Regenerate shell completions with `deno completions --dynamic` to make task suggestions follow the current `deno.json`.

### Frozen task execution (2.2.0)

`deno task` now accepts `--frozen`, allowing CI tasks to require an up-to-date lockfile without modifying it.

```sh
deno task --frozen build
```

### Input-based task caching (2.9-guide)

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

### npm-compatible package script environment (2.9.0)

Scripts from `package.json` now receive npm lifecycle environment variables, including `npm_execpath`, `npm_node_execpath`, and `npm_command`, improving compatibility with scripts that inspect how npm launched them.

### Parallel task output and shell behavior (2.8-guide)

Concurrent task output is automatically prefixed and color-coded by task name, including subprocess output. The task shell adds `set -e` / `set -o errexit`, `set +e`, and the `:` null command.

### Structured tasks and dependencies (2.1-guide)

A task may be an object with `command`, `description`, and `dependencies`; descriptions replace the removed use of JSONC comments as task descriptions. Dependencies run in parallel before the task, cycles are rejected, and a shared dependency in a diamond is run only once.

```json
{
  "tasks": {
    "build": "deno run -RW build.ts",
    "generate": "deno run -RW generate.ts",
    "serve": {
      "description": "Start the dev server",
      "command": "deno run -RN server.ts",
      "dependencies": ["build", "generate"]
    }
  }
}
```

### Task and script discovery (2.5-guide)

Invoking `deno run` without an argument now lists available `deno.json` tasks and `package.json` scripts instead of only reporting a missing script argument.

### Task concurrency control (2.9-guide)

For workspace runs, `deno task --jobs` (`-j`, also `--concurrency`) caps parallel tasks, overrides `DENO_JOBS`, and defaults to the available CPU count.

```sh
deno task --recursive --jobs 1 build
```

### Task patterns and dependency-only groups (2.2-guide)

A quoted `*` may appear anywhere in a task-name argument; every matching task runs in parallel. A task object may also omit `command` and exist only to group dependencies.

```json
{
  "tasks": {
    "dev-client": "deno run --watch client.ts",
    "dev-server": "deno run --watch server.ts",
    "dev": { "dependencies": ["dev-client", "dev-server"] }
  }
}
```

```sh
deno task "dev-*"
```

Signals are forwarded to subtasks on Unix and child processes are terminated with their task on Windows. Command-line arguments are passed only to the root task, not to its dependencies.

### Task-shell controls and glob default (2.7-guide)

The task shell supports `set -o pipefail` and configurable `shopt` behavior for `nullglob`, `failglob`, and `globstar`. `failglob` is now off by default, matching Bash and preventing unmatched wildcard-like URL characters from failing a task.

### Task-shell expansion (2.3.0)

The `deno task` shell now supports backtick command substitution and basic tilde expansion, so task commands can use forms such as `` `command` `` and `~/path`.

### Workspace and ad-hoc task execution (2.1-guide)

`deno task --recursive` runs a task across workspace members, `--filter` selects members, and `--eval` executes the task shell without a configured task. Workspace member declarations also accept wildcard package patterns, although task dependencies cannot yet cross packages.

```sh
deno task --recursive dev
deno task --filter "client/" dev
deno task --eval 'echo $(pwd)'
```

## CLI and project setup

### Automatic `deno eval` module detection (2.8-guide)

`deno eval` now detects CommonJS versus ES module syntax in the supplied snippet without requiring the caller to select a mode.

### Bare configured entry points (2.4-guide)

`deno run` resolves bare entry-point specifiers through the project's `imports` map, including npm, JSR, and prefix mappings. The `run` subcommand itself may still be omitted.

```json
{
  "imports": {
    "file-server": "jsr:@std/http/file-server"
  }
}
```

```sh
deno run file-server
```

### Data URL preloads (2.5.0)

`--preload` no longer splits a data URL at its comma, so an inline startup module can be passed directly.

```sh
deno run --preload='data:text/javascript,globalThis.ready=true' main.ts
```

### Emit-cache and V8 controls (2.3.0)

Deno recognizes `DENO_EMIT_CACHE_MODE` for selecting its emit-cache mode, and the V8 flag pass-through now accepts `--single-threaded`.

```sh
deno run --v8-flags=--single-threaded main.ts
```

### Empty project initialization (2.6-guide)

`deno init --empty` creates only an empty `deno.json` for projects that do not want generated starter files.

### Explicit packages for `deno x` (2.8-guide)

`deno x --package` (or `-p`) selects the package when its published binary has a different name.

```sh
deno x --package npm:typescript tsc
```

### Forced terminal color (2.3-guide)

Deno now honors `FORCE_COLOR`, allowing color output to be enabled even when automatic terminal detection would disable it.

### Full CLI help (2.3.0)

`--help=full` exposes the expanded command help when the normal help view omits advanced options.

### JSR template initialization (2.7.0)

`deno init --jsr <package>` initializes a project from a JSR template package.

```sh
deno init --jsr @scope/template
```

### Native source-map application (2.6-guide)

When formatting an exception stack, the runtime now detects `//# sourceMappingURL=...` comments and applies their source maps; internal frames are also filtered and project paths are shown relatively.

### Non-interactive npm initialization (2.6.0)

`deno init --npm` accepts `--yes` to bypass its permission prompt, which allows npm project scaffolding to run unattended.

```sh
deno init --npm vite --yes
```

### npm and JSR project creation (2.7-guide)

`deno create npm:<name>` resolves an npm `create-<name>` package, while a JSR template package must export `./create`.

```sh
deno create npm:vite -- my-project
deno create jsr:@std/http
```

### npm package documentation (2.8-guide)

`deno doc` can render npm packages, including packages whose entry points do not ship type declarations.

### npm scaffolding and dependency updates (2.1-guide)

`deno init --npm <name>` runs an npm-style project initializer and prompts before granting its script all permissions. `deno outdated` checks both `deno.json` and `package.json`; `--update` respects declared ranges by default, while `--latest` may cross them, package arguments select versions or filters, and `--recursive` covers a workspace.

```sh
deno init --npm vite
deno outdated --update
deno outdated --recursive --update --latest
deno outdated --update chalk@5.2 @std/async@1.0.6
```

### Package binaries with `dx` (2.6-guide)

`dx` is an `npx`-style runner for npm and JSR package binaries; install the alias with `deno x --install-alias`, and unqualified names default to `npm:` while local files are rejected. It grants all permissions unless another permission flag is supplied, prompts before downloading, and runs lifecycle scripts when that prompt is accepted.

```sh
dx cowsay "Hello, Deno!"
```

### Selective cache cleaning (2.3.0)

`deno clean --except <paths>` removes cached data except what is required to run the named paths, making it possible to reclaim cache space without evicting a selected application.

```sh
deno clean --except main.ts
```

### Workspace-aware version bumps (2.8-guide)

`deno bump-version patch|minor|major|prerelease` updates a package manifest; at a workspace root it bumps every member and rewrites matching `jsr:` constraints in root configuration and import maps. With no increment it derives per-package changes from Conventional Commits, while `--base`, `--start`, and `--dry-run` control the comparison and preview.

```sh
deno bump-version --base=main --dry-run
```

## Editor and language server

### Broader editor auto-import discovery (2.4-guide)

The language server can now find auto-imports through bare workspace specifiers, mapped npm resolutions, and locally patched JSR packages.

### Language-server configuration behavior (2.1-guide)

Project-local `deno.json` formatting settings take precedence over editor settings. The language server also completes relative manifest dependencies, npm dependencies, and `@deno-types` directives.

### Language-server framework support (2.2-guide)

The language server now understands `compilerOptions.rootDirs` and `compilerOptions.types`, ambient imports, wildcard module augmentation, and npm `<reference types>` augmentation. It also completes `.wasm` imports, uses `node:` for Node built-in auto-imports, improves npm auto-imports, and formats SCSS, Sass, Less, SQL, Svelte, Vue, and other component files.

### Template formatting and editor configuration (2.0.0)

The formatter recognizes `.vto` and `.njk` files. The language server's unstable-feature setting accepts a list, and type auto-imports use `import type`.

## Watch and upgrade workflows

### Delta runtime upgrades (2.8-guide)

`deno upgrade` uses checksum-verified binary deltas when available and falls back to a full archive automatically; `--no-delta` forces a full download.

```sh
deno upgrade --no-delta
```

### Pull-request runtime builds (2.8-guide)

`deno upgrade pr <number>` installs the matching-platform binary built by a pull request through an installed and authenticated `gh` CLI. `--output` preserves the current installation and `--dry-run` previews the selection.

```sh
deno upgrade --output ./deno-pr pr 34227
```

### Verified runtime upgrades (2.7-guide)

`deno upgrade --checksum=<sha256>` verifies the downloaded runtime against the supplied SHA-256 checksum; per-platform checksum files are published beside release archives.

```sh
deno upgrade --checksum=<sha256-hash> 2.7.0
```

### Watched environment files (2.5-guide)

When `--watch` and `--env-file` are used together, edits to the environment file now reload its environment variables automatically.
