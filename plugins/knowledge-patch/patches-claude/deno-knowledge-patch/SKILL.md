---
name: deno-knowledge-patch
description: Deno
version: "2.9.0"
license: MIT
metadata:
  author: Nevaberry
---


# Deno Knowledge Patch

Use this skill when choosing current Deno runtime APIs, CLI options, configuration, dependency behavior, Node compatibility, or deployment workflows. Open the topic reference before changing a project because several commands, flags, APIs, and defaults changed more than once.

## Working approach

1. Inspect `deno --version`, `deno.json` or `deno.jsonc`, `package.json`, `deno.lock`, workspace files, and CI commands.
2. Read every reference relevant to the requested change; later version-attributed guidance supersedes earlier behavior only where it explicitly changes it.
3. Preserve least-privilege permissions. Do not add `-A` merely to silence a permission failure.
4. Keep manifest and lockfile changes together, and prefer frozen installation modes in CI.
5. Treat the project's manifests, code, tests, and observed behavior as authoritative when they conflict with general guidance.
6. Verify with the narrowest applicable built-ins: `deno check`, `deno lint`, `deno fmt --check`, `deno test`, and the requested build or package command.

## Reference index

| Reference | Topics |
| --- | --- |
| [Build, publish, and deploy](references/build-publish-and-deploy.md) | Compilation, bundling, transpilation, packaging, publication, and deployment |
| [Dependencies and workspaces](references/dependencies-and-workspaces.md) | Manifests, registries, npm and JSR resolution, lockfiles, installs, catalogs, and workspaces |
| [Desktop and ecosystem](references/desktop-and-ecosystem.md) | Desktop applications, notebooks, Fresh, Deploy, Sandbox, and registry consumers |
| [Deno 2 migration](references/migration.md) | Removed surfaces, stricter checks, changed output, and changed defaults |
| [Networking and observability](references/networking-and-observability.md) | HTTP, sockets, TLS, WebSockets, QUIC, inspectors, profiles, and OpenTelemetry |
| [Node compatibility](references/node-compatibility.md) | CommonJS, Node APIs, timers, workers, IPC, SQLite, tests, and diagnostics |
| [Permissions and security](references/permissions-and-security.md) | Permission sets, allow and deny precedence, audit logs, scripts, and supply-chain policy |
| [Runtime and Web APIs](references/runtime-and-web-apis.md) | Files, subprocesses, WebAssembly, Temporal, cryptography, graphics, and Web APIs |
| [Testing, linting, and formatting](references/testing-lint-and-format.md) | Tests, snapshots, retries, sharding, coverage, benchmarks, lint plugins, and formatters |
| [Tooling and editor](references/tooling-and-editor.md) | Type checking, TypeScript configuration, tasks, caching, CLI workflows, upgrades, and language-server behavior |

## Migrate breaking surfaces first

### Replace removed commands and flags

- Remove `deno vendor` workflows.
- Do not assume `deno bundle` is still absent: it returned as an experimental esbuild-backed command with npm and JSR support.
- Replace explicit-entrypoint `deno cache` workflows with `deno install --entrypoint`.
- Remove obsolete `--allow-hrtime`, `--allow-none`, `--trace-ops`, `--ts`, generic `--unstable`, `--lock-write`, and old `--jobs` uses.
- Check task guidance before removing a newer `deno task --jobs` option because task concurrency later reused that name.
- Use specific unstable flags or configuration entries instead of the removed generic flag.
- Upgrade away from the faulty 2.3.0 build to 2.3.1 when version metadata is wrong.

### Replace removed runtime APIs

- Replace `Deno.run()` with `Deno.Command` or current subprocess helpers.
- Replace `Deno.serveHttp()` with `Deno.serve()`.
- Replace `Deno.isatty()` with the applicable terminal property.
- Use `Deno.FsFile`, Web streams, and current filesystem helpers instead of resource IDs, `Deno.File`, `Deno.Buffer`, removed reader and writer interfaces, and resource-oriented free functions.
- Do not construct `Deno.FsFile` directly or read `.rid` properties.
- Move WebGPU window dimensions to the `UnsafeWindowSurface` constructor.
- Use current TLS option names; legacy certificate-file and certificate-chain fields were removed.

### Reconcile stricter checking and configuration

- Expect unsupported `compilerOptions` to fail validation.
- Add `override` where required by `noImplicitOverride`.
- Narrow caught values before use because catch variables are `unknown`.
- Remove remote import maps and the obsolete `files` field from `deno.json`.
- Account for project `tsconfig.json` discovery, references, `rootDirs`, `paths`, `types`, `extends`, `include`, `exclude`, and per-member compiler options.
- Update Buffer and typed-array annotations when generic backing-buffer types expose `ArrayBuffer` versus `SharedArrayBuffer` differences.

### Recheck changed defaults

- Treat timer handles as Node-style `NodeJS.Timeout` objects rather than numeric IDs.
- Pass `deno fmt .` when no configuration or explicit input is discovered.
- Enable test operation and resource sanitizers when a suite relies on them.
- Enable `Deno.serve()` compression explicitly with `automaticCompression: true` or `DENO_SERVE_AUTOMATIC_COMPRESSION=1`.
- Specify a UDP hostname when binding every interface through the `0.0.0.0` default is undesirable.
- Account for the default npm minimum-release-age policy or configure another duration.
- Do not infer decoded body size from retained `content-length` after automatic decompression.
- Pass serializable strings instead of `URL` or `URLSearchParams` objects when crossing a serialization boundary.

## Manage dependencies deliberately

### Choose the target manifest

- Let package commands use the manifest Deno selects, or force `package.json` with `--package-json`.
- Set `preferPackageJson` when package-management commands should consistently target `package.json`.
- Use `jsr:` for JSR package declarations and explicit imports; unprefixed CLI package arguments now default to npm.
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
- Use `--os` and `--arch` when resolving optional dependencies for another target platform.
- Inspect dependency paths with `deno why` and declared dependency trees with `deno list`.

### Configure workspaces and registries

- Combine `deno.json` and `package.json` members in one workspace where needed.
- Put shared versions in `catalog` or named `catalogs`; consume them with `catalog:` specifiers.
- Use `links` for local npm redirects; older `patch` configuration is deprecated.
- Keep scoped registries, authentication, mTLS, release-age, and trust settings in `.npmrc`.
- Choose isolated or hoisted `node_modules` with `nodeModulesLinker` according to tool expectations.

## Build and distribute

### Bundle or transpile

```sh
deno bundle --platform browser --outdir dist app.ts
deno transpile src/mod.ts --outdir dist --source-map separate --declaration
```

- Use `deno bundle` for a dependency graph; use `deno transpile` to strip types without bundling, rewriting modules, or loading project configuration.
- Use an HTML entry when module scripts and global CSS should be discovered and rewritten to hashed assets.
- Add `--declaration` for rolled-up declarations and `--keep-names` when generated names must remain stable.

### Compile executables

```sh
deno compile --include assets/ --output app main.ts
```

- Use `--include` for resolved embedded assets and `--include-as-is` for verbatim files or directories.
- Put `compile.include` and `compile.exclude` in `deno.json` when asset selection belongs in project configuration.
- Use `--self-extracting` for native add-ons or Node APIs that require a real filesystem.
- Use experimental `--bundle` with `--minify` when tree-shaking npm-heavy executables matters more than embedding the complete graph.
- Set `--app-name` when compiled KV, local-storage, or Cache data needs a stable application identity.

### Package, publish, and deploy

- Use `deno pack` to create an npm tarball with transpiled exports, declarations, rewritten specifiers, and selected publish assets.
- Set `"publish": false` on private workspace members.
- Do not publish packages containing raw text or byte imports.
- Use deployment `include` and `exclude` filters to select uploaded files.

## Test, lint, and format

```sh
deno check .
deno lint
deno fmt --check .
deno test --coverage
```

- Use lifecycle hooks, timeouts, retries, repeats, parameterized cases, and built-in snapshots instead of recreating those mechanisms.
- Use `--changed`, `--related`, and `--shard=<index>/<count>` for selective or distributed test runs.
- Set separate line, branch, and function coverage thresholds when CI must enforce minimums.
- Remember that coverage can include ordinary `deno run` entry points and workers, and reports function coverage.
- Configure JavaScript lint plugins through `lint.plugins`; check the reference for selectors, comments, fixes, permissions, and incomplete ESLint compatibility.
- Set explicit formatter policies for named-specifier sorting, JSON trailing commas, embedded languages, and `.editorconfig` precedence.

## Use Node compatibility intentionally

- Run ESM Node projects with `package.json`, npm workspaces, `node_modules`, and Node-API add-ons under Deno permissions.
- Let `.js` CommonJS detection follow the nearest `package.json`; use compatibility mode only for the bundled fallback behaviors it enables.
- Prefer `node:` built-in imports for clarity even though bare built-ins now resolve without a flag.
- Expect global `Buffer`, `global`, `setImmediate`, and `clearImmediate`, plus Node-style timer handles.
- Check the Node reference before adding a shim: filesystem, workers, IPC, module hooks, VM modules, networking, TLS, SQLite, test mocks, diagnostics, and crypto expanded substantially.
- Use synchronous `module.registerHooks()` for supported resolve and load hooks; do not depend on the intentionally unavailable deprecated registration API.

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

- Opt into named permission sets with `-P`; configured permissions are never applied implicitly.
- Use `--ignore-read` or `--ignore-env` when a dependency should observe a denied resource as absent.
- Use `DENO_TRACE_PERMISSIONS` only for diagnosis because stack collection is expensive.
- Record checks with `DENO_AUDIT_PERMISSIONS`, optionally as span-correlated OpenTelemetry logs.
- Persist explicit lifecycle-script trust with `deno approve-scripts`.
- Combine audits, vulnerability fixes, minimum release age, and `trust-policy=no-downgrade` according to the project's threat model.
- Treat an active permission broker as replacing CLI allow, deny, and ignore flags.

## Operate servers and telemetry

- Configure `DENO_SERVE_ADDRESS`, `DENO_AUTO_SERVE`, `--open`, startup callbacks, backlog, and explicit compression for the hosting environment.
- Use custom `Deno.HttpClient` transports for Unix sockets, Linux vsock, proxies, or a bound local address; grant the required network permission.
- Account for Happy Eyeballs connection racing and set `autoSelectFamily: false` only when it must be disabled.
- Use custom WebSocket headers or an HTTP client only in Deno-specific code because browser constructors do not expose those extensions.
- Enable built-in OpenTelemetry with `OTEL_DENO`; choose OTLP or console export and configure sampling and limits through environment variables.
- Use inspector traffic capture, CPU profiles, permission logs, and TLS key logging only for deliberate diagnostics, and protect their outputs.

## Use modern runtime features

- Use stable `Temporal` directly.
- Import Wasm as a typed module, or use source-phase syntax when a compiled `WebAssembly.Module` is required.
- Use stable text import attributes; keep byte and CSS import stability gates in mind.
- Prefer `using` for disposable resources where lexical cleanup fits.
- Use transferable streams, requests, responses, and structured-clone support instead of unnecessary serialization.
- Feature-detect newer cryptographic algorithms with `SubtleCrypto.supports()` before selecting them.
- Use Web Locks for shared or exclusive coordination whose lifetime matches an async callback.

## Automate tasks and editor workflows

- Express task descriptions and dependencies with object-form tasks; shared dependencies run once.
- Use `files` and `output` to cache deterministic task results, and list environment inputs that affect them.
- Control workspace parallelism with `deno task --jobs`; use `--if-present`, wildcards, exclusions, and `--env-file` where appropriate.
- Run `deno check` without arguments for the current project, add `--watch` for continuous checking, and use `--check-js` for JavaScript without file comments.
- Expect project-local formatting and compiler settings to affect language-server behavior and auto-import discovery.
- Verify runtime upgrades by checksum when required, and prefer stable artifacts over pull-request builds for production.

## Treat desktop support as experimental

- Use `deno desktop` for a webview-hosted native application only when experimental APIs and packaging are acceptable.
- Choose the operating-system webview for smaller native integration or CEF for a bundled, consistent engine.
- Read the desktop reference before using `Deno.BrowserWindow`, tray, dock, dialogs, bindings, or auto-update APIs.
