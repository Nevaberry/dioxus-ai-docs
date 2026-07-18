---
name: deno-knowledge-patch
description: Deno
license: MIT
version: 2.9.0
metadata:
  author: Nevaberry
---

# Deno Knowledge Patch

Use this skill to choose current Deno APIs, CLI flags, configuration, and compatibility behavior. Check the relevant topic reference before changing a project because several features were removed, restored, stabilized, or given new defaults.

## Working approach

1. Inspect `deno --version`, `deno.json` or `deno.jsonc`, `package.json`, `deno.lock`, workspace configuration, and the commands used by CI.
2. Open every reference relevant to the requested change. Follow the exact option names and stability gates documented there.
3. Treat a later version-attributed statement as superseding an earlier one only for the behavior it explicitly changes.
4. Preserve least-privilege permissions. Do not add `-A` merely to bypass a permission failure.
5. Keep manifest and lockfile changes together, and use frozen or CI installation modes when reproducibility matters.
6. Verify with the narrowest applicable built-in commands: `deno check`, `deno lint`, `deno fmt --check`, `deno test`, and the requested build or package command.

## Reference index

| Reference | Topics |
| --- | --- |
| [Build, publish, and deploy](references/build-publish-and-deploy.md) | `deno compile`, bundling, transpilation, package tarballs, publication, and deployment |
| [Dependencies and workspaces](references/dependencies-and-workspaces.md) | Manifests, registries, npm/JSR resolution, lockfiles, installs, updates, catalogs, and workspaces |
| [Desktop and ecosystem](references/desktop-and-ecosystem.md) | Desktop applications, Jupyter, Fresh, Deploy, Sandbox, JSR consumers, and platform releases |
| [Deno 2 migration](references/migration.md) | Removed APIs and flags, configuration validation, changed defaults, and runtime baselines |
| [Networking and observability](references/networking-and-observability.md) | HTTP servers and clients, sockets, TLS, WebSockets, QUIC, OpenTelemetry, inspectors, and profiling |
| [Node compatibility](references/node-compatibility.md) | CommonJS, globals, timers, Node modules, filesystem, workers, networking, SQLite, tests, and diagnostics |
| [Permissions and security](references/permissions-and-security.md) | Permission sets and precedence, tracing, audit logs, brokers, dependency audits, lifecycle trust, and hardening |
| [Runtime and Web APIs](references/runtime-and-web-apis.md) | Filesystem, WebAssembly, Temporal, Web APIs, cryptography, graphics, types, subprocesses, and events |
| [Testing, linting, and formatting](references/testing-lint-and-format.md) | Tests, snapshots, retries, sharding, coverage, benchmarks, lint plugins, and multi-language formatting |
| [Tooling and editor](references/tooling-and-editor.md) | Type checking, TypeScript configuration, tasks, task caching, CLI utilities, upgrades, and language-server behavior |

## Migrate breaking surfaces first

### Replace removed commands and flags

- Remove uses of `deno vendor`.
- Do not assume `deno bundle` stayed removed: it returned as an experimental esbuild-backed command with npm and JSR support.
- Replace `deno cache <entrypoint>` workflows with `deno install --entrypoint <entrypoint>` where an explicit entry point must be cached.
- Remove obsolete `--allow-hrtime`, `--allow-none`, `--trace-ops`, `--ts`, generic `--unstable`, `--lock-write`, and old `--jobs` uses. Check the task reference before changing a newer `deno task --jobs` command, because task concurrency later reused that name.
- Use specific unstable feature flags or configuration entries rather than the removed generic flag.

### Replace removed runtime APIs

- Replace `Deno.run()` with `Deno.Command` or the documented subprocess APIs.
- Replace `Deno.serveHttp()` with `Deno.serve()`.
- Replace `Deno.isatty()` with the applicable terminal property.
- Use `Deno.FsFile` methods, Web streams, and current filesystem helpers instead of removed resource IDs, `Deno.File`, `Deno.Buffer`, reader/writer interfaces, and resource-oriented free functions.
- Do not construct `Deno.FsFile` directly or read `.rid` properties.
- Move WebGPU window dimensions to the `UnsafeWindowSurface` constructor.
- Use current TLS option names; legacy certificate-file and certificate-chain fields were removed from connection/listener option types.

### Reconcile stricter checking and configuration

- Expect unsupported `compilerOptions` to fail validation.
- Add `override` where required by `noImplicitOverride`.
- Narrow caught values before use because catch variables are `unknown`.
- Do not use remote import maps or the removed `files` field in `deno.json`.
- Account for `tsconfig.json` discovery, project references, `rootDirs`, `paths`, `types`, `extends`, `include`, `exclude`, and per-workspace-member compiler options as documented.
- Update Buffer and typed-array annotations when generic backing-buffer types expose `ArrayBuffer` versus `SharedArrayBuffer` differences.

### Recheck changed defaults

- Treat timer handles as Node-style `NodeJS.Timeout` objects; do not require numeric IDs.
- Pass `deno fmt .` when formatting without a discovered configuration and without explicit files.
- Enable test operation and resource sanitizers explicitly when a suite depends on them.
- Enable `Deno.serve()` compression explicitly with `automaticCompression: true` or `DENO_SERVE_AUTOMATIC_COMPRESSION=1`.
- Specify a UDP hostname if binding all interfaces through the newer `0.0.0.0` default is undesirable.
- Expect a default npm minimum release age unless configuration opts out or selects another duration.
- Do not infer decoded response-body size from retained `content-length` after automatic decompression.

## Manage dependencies deliberately

### Choose the target manifest

- Let package commands use the project manifest selected by Deno, or force `package.json` with `--package-json`.
- Persist that choice with `preferPackageJson` when package-management commands should consistently target `package.json`.
- Use `jsr:` in explicit imports and JSR dependency declarations; current CLI package arguments default to npm when unprefixed.
- Use `--save-exact` or `--exact` when reproducibility requires a pinned version instead of the default caret range.

### Install and update reproducibly

```sh
deno install
deno update
deno update --lockfile-only
deno ci
```

- Use `deno ci` only with a lockfile; it removes `node_modules` and validates a frozen install.
- Use `deno install --lockfile-only` to resolve and update the lock without fetching or installing packages.
- Use `deno install --prod` to omit development dependencies and type packages.
- Use `--os` and `--arch` when resolving target-specific optional dependencies for another platform.
- Inspect dependency paths with `deno why` and declared dependency trees with `deno list`.

### Configure workspaces and registries

- Combine `deno.json` and `package.json` members in one workspace when needed.
- Put shared dependency versions in `catalog` or named `catalogs`; reference them with `catalog:` specifiers.
- Use `links` for local npm package redirects; treat older `patch` configuration as deprecated.
- Keep scoped registry and authentication settings in `.npmrc`, including mTLS and release-age policy when required.
- Choose isolated or hoisted `node_modules` with `nodeModulesLinker` according to tool expectations.

## Build and distribute

### Bundle or transpile

```sh
deno bundle --platform browser --outdir dist app.ts
deno transpile src/mod.ts --outdir dist --source-map separate --declaration
```

- Use `deno bundle` for a dependency graph; use `deno transpile` to strip types without bundling, rewriting modules, or loading project configuration.
- Use HTML bundle entries when scripts and global CSS should be discovered and rewritten to hashed assets.
- Add `--declaration` for rolled-up declaration output and `--keep-names` when generated names must remain stable.

### Compile executables

```sh
deno compile --include assets/ --output app main.ts
```

- Use `--include` for resolved embedded assets and `--include-as-is` for verbatim files or directories.
- Use `compile.include` and `compile.exclude` in `deno.json` when asset selection belongs in project configuration.
- Use `--self-extracting` for native add-ons or Node APIs that need a real filesystem.
- Use experimental `--bundle` with `--minify` when tree-shaking npm-heavy executables is more important than embedding the complete graph.
- Set `--app-name` when compiled KV, local-storage, or Cache data must keep a stable application identity.

### Package, publish, and deploy

- Use `deno pack` to generate an npm tarball with transpiled exports, declarations, rewritten specifiers, and selected publish assets.
- Set `"publish": false` on private workspace members.
- Do not publish packages containing raw text or byte imports.
- Use deployment `include` and `exclude` filters to control uploaded files.

## Test, lint, and format

```sh
deno check .
deno lint
deno fmt --check .
deno test --coverage
```

- Use lifecycle hooks, per-test timeouts, retries, repeats, parameterized cases, and built-in snapshots rather than recreating those mechanisms.
- Use `--changed`, `--related`, and `--shard=<index>/<count>` for selective or distributed test runs.
- Set line, branch, and function coverage thresholds when CI must enforce minimums.
- Remember that coverage can include ordinary `deno run` entry points and workers, and can report function coverage.
- Configure JavaScript lint plugins through `lint.plugins`; consult the reference for selectors, comment access, fixes, permissions, and the incomplete ESLint compatibility boundary.
- Set explicit formatter policies for named-specifier sorting, JSON trailing commas, embedded languages, and `.editorconfig` precedence.

## Use Node compatibility intentionally

- Run ESM Node projects with `package.json`, npm workspaces, `node_modules`, and Node-API add-ons under Deno permissions.
- Let `.js` CommonJS detection follow the nearest `package.json`; use compatibility mode only when the bundled fallback behaviors are actually needed.
- Import built-ins with `node:` for clarity even though newer bare built-ins resolve without a flag.
- Expect global `Buffer`, `global`, `setImmediate`, and `clearImmediate`, plus Node-style timer handles.
- Check the Node reference before adding a shim or workaround: filesystem, workers, IPC, loaders, VM modules, networking, TLS, SQLite, test mocks, diagnostics, and crypto expanded substantially.
- Use synchronous `module.registerHooks()` for supported custom resolve/load hooks; do not depend on the intentionally unavailable deprecated registration API.

## Keep permissions and supply chain controls narrow

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

- Opt into named permission sets with `-P`; configured permissions are never applied implicitly.
- Use `--ignore-read` or `--ignore-env` when a dependency should observe a denied resource as absent.
- Trace prompt call stacks with `DENO_TRACE_PERMISSIONS` only while diagnosing because stack collection is expensive.
- Record checks with `DENO_AUDIT_PERMISSIONS`, optionally as span-correlated OpenTelemetry logs.
- Use `deno approve-scripts` to persist explicit lifecycle-script trust.
- Combine audits, vulnerability fixes, minimum release age, and `trust-policy=no-downgrade` according to the project threat model.
- Treat a permission broker as replacing CLI allow, deny, and ignore flags while active.

## Operate servers and telemetry

- Configure `DENO_SERVE_ADDRESS`, `DENO_AUTO_SERVE`, `--open`, startup callbacks, backlog, and explicit compression according to the hosting environment.
- Use custom `Deno.HttpClient` transports for Unix sockets, Linux vsock, proxies, or a bound local address; grant the required network permission.
- Account for Happy Eyeballs connection racing and set `autoSelectFamily: false` only when it must be disabled.
- Use custom WebSocket headers or an HTTP client only in Deno-specific code because browser constructors do not expose those extensions.
- Enable built-in OpenTelemetry with `OTEL_DENO`; choose OTLP or console export and configure sampling and limits through the documented environment variables.
- Use inspector network capture, CPU profiles, permission logs, and TLS key logging only for deliberate diagnostics, and protect their outputs.

## Use modern runtime features

- Use stable `Temporal` directly.
- Import Wasm as a typed module, or use source-phase import syntax when a compiled `WebAssembly.Module` is required.
- Use text import attributes without the old raw-import flag; keep byte and CSS import stability gates in mind.
- Prefer `using` for disposable resources where lexical cleanup fits.
- Use transferable streams, requests, responses, and structured-clone support instead of unnecessary serialization.
- Feature-detect newer cryptographic algorithms with `SubtleCrypto.supports()` before selecting them.
- Use Web Locks for named shared or exclusive coordination whose lifetime matches an async callback.

## Automate tasks and editor workflows

- Express task descriptions and dependencies with object-form tasks; dependencies run first and shared dependencies run once.
- Use `files` and `output` to cache deterministic task results, and declare environment inputs that affect those results.
- Control workspace parallelism with `deno task --jobs`; use `--if-present`, task wildcards, exclusions, and `--env-file` where appropriate.
- Run `deno check` without arguments for the current project, add `--watch` for continuous checking, and use `--check-js` for JavaScript without file comments.
- Expect project-local formatting and compiler configuration to affect the language server and auto-import discovery.
- Verify runtime upgrades by checksum when required, and prefer normal stable artifacts over pull-request builds for production use.

## Treat desktop support as experimental

- Use `deno desktop` for a webview-hosted native application only when experimental APIs and packaging are acceptable.
- Choose the operating-system webview for smaller native integration or the CEF backend for a bundled, consistent engine.
- Use `Deno.BrowserWindow`, tray, dock, dialogs, bindings, and auto-update APIs only after reading the desktop reference for platform and distribution constraints.
