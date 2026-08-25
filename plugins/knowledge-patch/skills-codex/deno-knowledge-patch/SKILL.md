---
name: deno-knowledge-patch
description: Deno
version: 2.9.0
license: MIT
metadata:
  author: Nevaberry
---


# Deno Knowledge Patch

Use this skill when choosing Deno APIs, CLI flags, configuration, dependency behavior, or compatibility surfaces. Read the relevant topic reference before changing a project because several commands, APIs, stability gates, and defaults changed during Deno 2.

## Working approach

1. Inspect `deno --version`, `deno.json` or `deno.jsonc`, `package.json`, `deno.lock`, workspace configuration, and CI commands.
2. Open every reference relevant to the requested change; later version-attributed guidance supersedes earlier behavior only where it explicitly says so.
3. Preserve the project's chosen manifest and node-modules layout. Keep manifest and lockfile changes together.
4. Keep permissions narrow. Do not add `-A` merely to silence a failure.
5. Verify with the smallest applicable commands: `deno check`, `deno lint`, `deno fmt --check`, `deno test`, and the requested build, package, or deploy command.

## Reference index

| Reference | Topics |
| --- | --- |
| [Build, publish, and deploy](references/build-publish-and-deploy.md) | `deno compile`, bundling, transpilation, tarballs, publication, and deployment |
| [Dependencies and workspaces](references/dependencies-and-workspaces.md) | Manifests, registries, npm/JSR resolution, lockfiles, installs, updates, catalogs, and workspaces |
| [Desktop and ecosystem](references/desktop-and-ecosystem.md) | Desktop applications, Jupyter, Fresh, Deploy, Sandbox, JSR consumers, and platform releases |
| [Deno 2 migration](references/migration.md) | Removed APIs, configuration validation, changed defaults, and runtime baselines |
| [Networking, servers, and observability](references/networking-and-observability.md) | HTTP, sockets, TLS, WebSockets, QUIC, OpenTelemetry, inspectors, and profiling |
| [Node compatibility](references/node-compatibility.md) | CommonJS, globals, timers, Node modules, filesystem, workers, networking, SQLite, tests, and diagnostics |
| [Permissions and dependency security](references/permissions-and-security.md) | Permission sets, precedence, tracing, brokers, audits, lifecycle trust, and dependency hardening |
| [Runtime and Web APIs](references/runtime-and-web-apis.md) | Filesystem, WebAssembly, Temporal, cryptography, graphics, subprocesses, events, and Web APIs |
| [Testing, coverage, linting, and formatting](references/testing-lint-and-format.md) | Tests, snapshots, retries, sharding, coverage, benchmarks, lint plugins, and formatting |
| [Type checking, tasks, CLI, and editor tooling](references/tooling-and-editor.md) | TypeScript configuration, checking, tasks, caching, upgrades, and language-server behavior |

## Migrate breaking surfaces first

### Replace removed commands and flags

- Remove `deno vendor` workflows.
- Do not assume `deno bundle` is still absent: it returned as an experimental esbuild-backed command with npm and JSR support.
- Replace `deno cache <entrypoint>` with `deno install --entrypoint <entrypoint>` when an explicit entry point must be cached.
- Remove obsolete `--allow-hrtime`, `--allow-none`, `--trace-ops`, `--ts`, generic `--unstable`, and `--lock-write` uses.
- Distinguish the removed generic `--jobs` flag from the later `deno task --jobs` workspace-concurrency option.
- Use feature-specific unstable flags or configuration entries where a feature remains gated.

### Replace removed runtime APIs

- Replace `Deno.run()` with `Deno.Command` or the current subprocess APIs.
- Replace `Deno.serveHttp()` with `Deno.serve()`.
- Replace `Deno.isatty()` with the applicable terminal property.
- Use `Deno.FsFile` methods, Web streams, and current filesystem helpers instead of removed resource IDs, `Deno.File`, `Deno.Buffer`, reader/writer interfaces, and resource-oriented free functions.
- Do not construct `Deno.FsFile` directly or read `.rid` properties.
- Move WebGPU window dimensions to the `UnsafeWindowSurface` constructor.
- Replace removed TLS certificate-file and certificate-chain option fields with current TLS options.

### Reconcile stricter checking and configuration

- Unsupported `compilerOptions` now fail validation.
- Add `override` where `noImplicitOverride` requires it.
- Narrow caught values before use because catch variables are `unknown`.
- Do not use remote import maps or the removed `files` field in `deno.json`.
- Account for `tsconfig.json` discovery, project references, `rootDirs`, `paths`, `types`, `extends`, `include`, `exclude`, and per-workspace-member compiler options.
- Update Buffer and typed-array annotations when generic backing-buffer types expose `ArrayBuffer` versus `SharedArrayBuffer` differences.
- Do not remain on Deno 2.3.0 when its incorrect build metadata matters; upgrade to 2.3.1.

### Recheck changed defaults

- Timer handles are Node-style `NodeJS.Timeout` objects, not numeric IDs.
- Run `deno fmt .` when formatting without discovered configuration or explicit files.
- Test operation and resource sanitizers default off; enable them when a suite relies on leak checks.
- `Deno.serve()` response compression is opt-in through `automaticCompression` or `DENO_SERVE_AUTOMATIC_COMPRESSION`.
- `Deno.listenDatagram()` defaults to `0.0.0.0`; specify a hostname if binding all interfaces is undesirable.
- npm dependency resolution applies a default minimum release age unless configuration changes or disables it.
- Automatically decompressed responses retain `content-encoding` and `content-length`; the latter is not the decoded body size.

## Manage dependencies deliberately

### Choose the target manifest

- Let package commands use Deno's selected project manifest, or force `package.json` with `--package-json`.
- Set `preferPackageJson` when package-management commands should consistently target `package.json`.
- Package arguments without a registry prefix default to npm; use `jsr:` for JSR packages and explicit imports.
- Use `--save-exact` or `--exact` when the default caret range is too broad.
- Use `.npmrc` for scoped registries, authentication, mTLS, minimum release age, and trust-policy controls.

### Install and update reproducibly

```sh
deno install
deno update
deno update --lockfile-only
deno ci
```

- `deno ci` requires a lockfile, removes `node_modules`, and enforces frozen resolution.
- `deno install --lockfile-only` resolves and updates the lock without fetching or installing packages.
- `deno install --prod` omits development dependencies and type packages.
- Use `--os` and `--arch` to resolve target-specific optional dependencies for another platform.
- Inspect declared dependencies with `deno list` and resolution paths with `deno why`.

### Configure workspaces and local packages

- A workspace may combine `deno.json` and `package.json` members.
- Put shared versions in `catalog` or named `catalogs`; members use `catalog:` specifiers.
- Use `links` for local npm redirects; older `patch` configuration is deprecated.
- Choose isolated or hoisted `node_modules` through `nodeModulesLinker` based on tool expectations.
- Set `jsrDepsInNodeModules` only when Node-oriented tools need complete JSR tarballs and physical assets.

## Build and distribute

### Bundle or transpile

```sh
deno bundle --platform browser --outdir dist app.ts
deno transpile src/mod.ts --outdir dist --source-map separate --declaration
```

- Use `deno bundle` for a dependency graph; use `deno transpile` to strip types without bundling, rewriting modules, or loading project configuration.
- HTML bundle entries discover module scripts and global CSS and rewrite them to hashed assets.
- Use `--declaration` for rolled-up declaration output and `--keep-names` when generated names must remain stable.

### Compile executables

```sh
deno compile --include assets/ --output app main.ts
```

- Use `--include` for resolved embedded assets and `--include-as-is` for verbatim files or directories.
- Put reusable asset selection under `compile.include` and `compile.exclude` in `deno.json`.
- Use `--self-extracting` when native add-ons or Node APIs need a real filesystem.
- Experimental `--bundle` with `--minify` can shrink npm-heavy executables through tree shaking.
- Set `--app-name` when compiled KV, local-storage, or Cache data needs stable application identity.

### Package, publish, and deploy

- `deno pack` emits an npm tarball with transpiled exports, declarations, rewritten specifiers, and selected publish assets.
- Set `"publish": false` on private workspace members.
- Packages containing text or byte imports cannot be published.
- Deployment `include` and `exclude` filters select uploaded files, including workspace-member entries.

## Test, lint, and format

```sh
deno check .
deno lint
deno fmt --check .
deno test --coverage
```

- Use lifecycle hooks, per-test timeouts, retries, repeats, parameterized cases, and built-in snapshots instead of recreating those mechanisms.
- Use `--changed`, `--related`, and `--shard=<index>/<count>` for selective or distributed test runs.
- Configure line, branch, and function coverage thresholds when CI must enforce minimums.
- Coverage can include ordinary `deno run` entry points and workers and can report function coverage.
- Configure lint plugins through `lint.plugins`; their selector, comment, fix, and permission surfaces are Deno-specific and not fully ESLint-compatible.
- Set explicit formatter policies for named-specifier sorting, JSON trailing commas, embedded languages, and `.editorconfig` precedence.

## Use Node compatibility intentionally

- Deno can run ESM Node projects with `package.json`, npm workspaces, `node_modules`, and Node-API add-ons under Deno permissions.
- Let `.js` CommonJS detection follow the nearest `package.json`; enable compatibility fallback only when automatic detection is insufficient.
- Prefer `node:` for built-in imports even though bare built-ins now resolve without a flag.
- Expect global `Buffer`, `global`, `setImmediate`, and `clearImmediate`, plus Node-style timer handles.
- Check the Node reference before adding shims: filesystem, workers, IPC, module hooks, VM modules, networking, TLS, SQLite, tests, diagnostics, and cryptography have expanded.
- Use synchronous `module.registerHooks()` for supported custom resolution and loading; the deprecated `module.register()` API is intentionally unavailable.

## Keep permissions and supply-chain controls narrow

```json
{
  "permissions": {
    "local-data": { "read": ["./data"], "write": ["./data"] }
  }
}
```

```sh
deno run -P=local-data main.ts
deno audit
```

- Named permission sets are never selected implicitly; opt in with `-P`.
- Use `--ignore-read` or `--ignore-env` when a dependency should observe a denied resource as absent.
- `DENO_TRACE_PERMISSIONS` is diagnostic and expensive; `DENO_AUDIT_PERMISSIONS` records checks.
- Use `deno approve-scripts` for explicit persisted lifecycle-script trust.
- Combine audits, vulnerability fixes, minimum release age, and `trust-policy=no-downgrade` according to the project threat model.
- An active permission broker replaces CLI allow, deny, and ignore flags.

## Operate servers and telemetry

- Configure `DENO_SERVE_ADDRESS`, `DENO_AUTO_SERVE`, `--open`, startup callbacks, backlog, and explicit compression for the hosting environment.
- Custom `Deno.HttpClient` transports support Unix sockets, Linux vsock, proxies, and bound local addresses; grant network permission where required.
- Happy Eyeballs connection racing is on by default; disable it only when the environment requires sequential address-family selection.
- Deno-specific WebSockets can send custom headers or use an HTTP client, unlike browser WebSocket constructors.
- Enable built-in OpenTelemetry with `OTEL_DENO`; select OTLP or console output and configure sampling and limits with the documented environment variables.
- Protect inspector captures, CPU profiles, permission logs, and TLS session-key logs because they can contain sensitive data.

## Use modern runtime features

- Use stable `Temporal` directly.
- Import Wasm as a typed module, or use source-phase syntax for a compiled `WebAssembly.Module`.
- Text import attributes are stable; byte and CSS imports retain stability gates.
- Prefer `using` for disposable resources when lexical cleanup fits.
- Transfer streams, requests, and responses rather than serializing them when worker ownership can move.
- Feature-detect newer cryptographic algorithms with `SubtleCrypto.supports()`.
- Use Web Locks for named shared or exclusive coordination scoped to an async callback.

## Automate tasks and editor workflows

- Object-form tasks can declare descriptions and dependencies; dependencies run first and shared dependencies run once.
- Add `files` and `output` to cache deterministic tasks, including every environment input that affects the result.
- Control workspace parallelism with `deno task --jobs`; use `--if-present`, wildcards, exclusions, and `--env-file` as needed.
- Run `deno check` without arguments for the current project, `--watch` for continuous checking, and `--check-js` for JavaScript without file comments.
- Expect project-local formatting and compiler settings to affect the language server and auto-import discovery.
- Verify upgrades by checksum when required; prefer stable runtime artifacts over pull-request builds for production.

## Treat desktop support as experimental

- Use `deno desktop` only when experimental APIs and packaging are acceptable.
- Choose the operating-system webview for smaller native integration or CEF for a bundled, consistent browser engine.
- Read the desktop reference before using windows, trays, docks, dialogs, bindings, deep links, auto-update, cross-target packaging, or framework adapters.
