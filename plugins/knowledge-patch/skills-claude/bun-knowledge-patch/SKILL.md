---
name: bun-knowledge-patch
description: Bun
version: 1.4.0
license: MIT
metadata:
  author: Nevaberry
---


# Bun Knowledge Patch

Use this skill when working on Bun applications, packages, builds, tests, servers,
or Node.js compatibility. Check the relevant reference before relying on older Bun
behavior or translating Node-oriented code.

## Reference index

| Reference | Topics |
| --- | --- |
| [Builds and frontend](references/build-and-frontend.md) | Bundling, compiled executables, HTML/CSS, loaders, plugins, decorators, HMR, React, metafiles |
| [Databases and storage](references/databases-and-storage.md) | `Bun.SQL`, Postgres/MySQL/SQLite, `bun:sqlite`, S3, Redis, secrets, archives, images |
| [HTTP and networking](references/http-and-networking.md) | `Bun.serve`, Fetch, WebSocket, TLS, HTTP/2/3, QUIC, UDP, Unix sockets, proxies |
| [Node.js compatibility](references/node-compatibility.md) | Implemented and missing Node APIs, module hooks, workers, child processes, streams, crypto |
| [Packages and workspaces](references/packages-and-workspaces.md) | Installs, lockfiles, linkers, catalogs, scripts, audit, publish, workspace commands |
| [Runtime and platform](references/runtime-and-platform.md) | Runtime APIs, files, subprocesses, formats, terminal text, profiling, cron, platform behavior |
| [Testing](references/testing.md) | `bun:test`, `node:test`, concurrency, sharding, timers, mocks, coverage, reporters |

## Upgrade hazards to check first

### Installation layout is lockfile-driven

New workspace projects can use isolated installs, but existing projects do not
change linker merely because Bun is upgraded. `bun.lock`/`bun.lockb`
`configVersion` decides defaults: version `1` plus workspaces is isolated;
version `0` is hoisted. Set `[install] linker = "isolated"` or
`bun install --linker=isolated` when an existing monorepo needs isolation. See
[packages and workspaces](references/packages-and-workspaces.md).

### TLS verification is stricter

Connections that formerly tolerated hostname or client-certificate problems may
now fail. `tls.connect()` derives SNI and identity from `host` when `servername`
is absent; Bun socket TLS APIs default to `rejectUnauthorized: true`; Redis TLS
checks the URL host; and only literal `rejectUnauthorized: false` disables
verification. Review each TLS caller, including redirects and per-host
`Bun.serve` configurations. See
[HTTP and networking](references/http-and-networking.md).

### Fetch bodies, headers, and errors align more closely with the spec

Duplicate headers are joined, disturbed or locked bodies cannot be cloned,
network failures are `TypeError`s, option errors reject asynchronously, aborts
can error an already-arrived body, request header bytes are Latin-1, and only
301/302/303/307/308 trigger `redirect: "error"`. Clone before reading and
reissue a failed fetch rather than rereading its body.

### Server shutdown and WebSocket return values changed

`server.stop()` is asynchronous and waits for the last connection; use
`server.stop(true)` for forced closure, including after graceful stop began.
`publish()` returns `0` for no delivery, `-1` for backpressure, or a byte count;
do not compare it with payload length as a success test. Upgrade validation also
tightened WebSocket handshakes, close codes, reasons, and ping/pong lengths.

### Runtime semantics changed in several small but breaking ways

- `bun run <script>` uses the package directory as cwd.
- `Bun.build()` rejects on failure unless `throw: false` is set.
- `bun -p` means `--print`, not `--port`.
- `bun build --sourcemap` defaults to linked sourcemaps.
- `require()` of an unknown extension executes it as JavaScript.
- `Bun.$` expands only literal `*`, `**`, and brace globs.
- `Bun.cron` parsing and in-process scheduling use local time; pass
  `{ tz: "UTC" }` for UTC.
- `Bun.mmap({ offset })` returns a view beginning exactly at the offset.
- `child_process.spawn()` streams always emit `Buffer`s regardless of
  `options.encoding`.

See [runtime and platform](references/runtime-and-platform.md) for exact behavior
and other changed error types, signal rules, filesystem semantics, and platform
constraints.

### Package and test commands have stricter failure modes

`bun update <name>` exits `1` when the package is not already depended on;
interactive update exits `1` without a TTY. Under `CI=true`, `bun test` rejects
`test.only()` and creation of new snapshots without an update flag. Zero matched
tests fail unless `--pass-with-no-tests` is used, while an empty test shard exits
successfully. See the package and testing references before changing CI scripts.

## High-value server features

### Route values

Use `routes`, not the original `static` name. Routes support parameters on
`req.params`, wildcards, async handlers, per-method objects, imported HTML,
`Response`, `Bun.file()`, and `{ dir: "./public" }`. File-backed responses get
range handling; static values get validators; directory routes add content type,
index files, normalized lookup, and traversal protection.

```ts
Bun.serve({
  routes: {
    "/api/users/:id": req => Response.json(req.params),
    "/logo.png": Bun.file("./public/logo.png"),
    "/static/*": { dir: "./public" },
  },
});
```

### Frontend development

Running an HTML entry directly starts the frontend dev server with bundling and
hot reload. Imported HTML can be routed from `Bun.serve`, built ahead of time,
or compiled with `--target=browser` into self-contained HTML. Configure client
`env`, `define`, minification, sourcemaps, and plugins under `[serve.static]`.

### Protocol choices

`Bun.serve({ tls, http3: true })` exposes experimental HTTP/3; `fetch()` accepts
an explicit `protocol` for HTTP/1.1, HTTP/2, or HTTP/3. WebSocket supports HTTP
proxying, full TLS options, Unix-socket URL schemes, subprotocol validation, and
client certificates through Fetch's TLS configuration where applicable. Read
the networking reference for unsupported proxy, h2c, push, and Unix-socket
combinations.

## High-value package workflows

The package manager uses text `bun.lock`; migrate an existing binary lockfile
explicitly. It can migrate npm, Yarn, and pnpm lockfiles; operate recursively or
through repeatable workspace filters; manage catalogs; audit and repair
vulnerabilities; prune production installs; deduplicate the lockfile; inspect
dependency reasons; edit package metadata; and build patches for registry, git,
or tarball dependencies.

Use exact trust controls. `trustedDependencies` enables lifecycle scripts,
`ignoreScripts` disables selected packages even if trusted, and
`nativeDependencies` lets Bun link known platform binaries without running
postinstall. Non-npm sources never inherit Bun's built-in trusted list.

## High-value testing workflows

`bun:test` supports concurrent tests within a file, isolated files, worker-level
parallelism, deterministic randomization, git-aware changed tests, sharding, and
timing-aware distribution. These controls have different scopes:

- `test.concurrent` / `describe.concurrent` parallelize async tests in one file.
- `--isolate` gives each file a fresh global within one process.
- `--parallel[=N]` distributes files across worker processes and implies
  isolation.
- `--shard=M/N` selects files after `--changed` filtering.
- `--timings` balances parallel or sharded work by prior wall time.

Use fake timers through `jest`, per-test cleanup with `onTestFinished`, retries
or repeats through test options, and `using` for automatically restored mocks or
spies. Type assertions from `expectTypeOf` are checked by TypeScript, not by the
test runtime.

## High-value data APIs

`Bun.SQL` is a parameterized tagged-template client for Postgres, MySQL/MariaDB,
and SQLite. Prefer tagged templates or `sql.unsafe()`; a plain query-string call
throws. Account for adapter-specific decoding, `undefined` omission in object
helpers, eager `.execute()`, pipelining, typed Postgres arrays, and named SQLite
parameters. Use the storage reference before depending on date, numeric, binary,
JSON, or column-metadata conversions.

Built-ins also cover `bun:sqlite`, S3, Redis/Valkey, OS credential storage,
tar archives, and image processing. Platform support is not uniform: some image
formats are unavailable on Linux, and credential storage uses each OS's native
facility.

## High-value build and runtime APIs

`Bun.build()` supports in-memory `files`, plugins including `onBeforeParse` and
`onEnd`, JSON and Markdown metafiles, feature flags through `bun:bundle`, React
Fast Refresh and the React compiler, barrel optimization, and standalone or
self-contained-browser compilation. Compiled executables have explicit config
autoload and asset-embedding controls; do not assume deployment-directory
`package.json` or `tsconfig.json` is read.

For dependency-free runtime work, review built-in YAML, JSONC, JSON5, JSONL,
XML, TOML, Markdown, archive, image, terminal, PTY, CSRF, cookie, glob, file,
stream, subprocess, cron, profiling, and browser-automation APIs in the runtime
reference. Preserve experimental labels and platform caveats when selecting
them.

## Node.js compatibility

Do not infer complete Node compatibility from module availability. The runtime
implements major Node 26 surfaces, including the socket-based HTTP client,
`node:sqlite`, `node:repl`, `node:test`, workers, cluster handle passing, QUIC,
trace events, inspector, and many stream and crypto additions. Remaining or
different behavior includes loader-hook gaps, JavaScriptCore serialization
format, partial async hooks, selected worker/process exports, and unavailable
utility, crypto, domain, and TLS exports. Check
[Node.js compatibility](references/node-compatibility.md) at the API boundary.
