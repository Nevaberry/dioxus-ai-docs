---
name: bun-knowledge-patch
description: Bun
version: "1.4.0"
license: MIT
metadata:
  author: Nevaberry
---


# Bun Knowledge Patch

Use this skill for Bun runtime, package-manager, bundler, test-runner, server,
database, and Node.js-compatibility work. Establish the project's actual Bun
release before applying version-attributed guidance from the references.

Read only the references relevant to the task. When project code, tests, or
observed behavior disagree with this guidance, treat the project as decisive.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/build-and-frontend.md](references/build-and-frontend.md) | Bundling, HTML/CSS, loaders, plugins, sourcemaps, bytecode, and executables |
| [references/databases-and-storage.md](references/databases-and-storage.md) | `Bun.SQL`, PostgreSQL, MySQL, SQLite, Redis, S3, archives, and secrets |
| [references/http-and-networking.md](references/http-and-networking.md) | `Bun.serve()`, routes, fetch, WebSockets, sockets, TLS, DNS, proxies, and cookies |
| [references/node-compatibility.md](references/node-compatibility.md) | Node core APIs, workers, process behavior, VM, inspector, native addons, and compatibility gaps |
| [references/packages-and-workspaces.md](references/packages-and-workspaces.md) | Installs, lockfiles, dependencies, workspaces, registries, audits, and publishing |
| [references/runtime-and-platform.md](references/runtime-and-platform.md) | Bun-native APIs, JavaScript/Web APIs, shell, subprocesses, formats, profiling, and platforms |
| [references/testing.md](references/testing.md) | `bun:test`, discovery, concurrency, isolation, sharding, coverage, mocks, and snapshots |

## Breaking changes and upgrade traps

### TLS verification is stricter

- `fetch()` runs `tls.checkServerIdentity` before sending request bytes and for
  every redirect hop.
- `tls.connect({ host })` uses `host` for SNI and certificate identity.
- `Bun.connect()`, `socket.upgradeTLS()`, `RedisClient`, and listener APIs with
  `requestCert: true` verify by default. Supply the correct `ca` and
  `servername`, or use literal `rejectUnauthorized: false` only when intended.

### The reported Node boundary changed

- Bun reports Node.js 26, native-addon ABI `147`, and Node-API version 10.
- The obsolete `res.writeHeader()` alias is removed; use `writeHead()`.
- A paused `readable.read()` without a size returns one buffered chunk, not the
  whole buffer.

### FFI C strings are JavaScript strings

- A `cstring` return or callback argument is now a string; a null pointer is
  `null`.
- `new CString(ptr)` returns a string without `.ptr`, `.byteLength`, or
  `.arrayBuffer`. Preserve the original pointer when native code must free it.

### Lockfiles migrate forward

- New `bun.lock` files use `lockfileVersion: 2`; existing v0/v1 files migrate
  during `bun install`.
- Nested or version-scoped overrides require version 3, which older Bun
  releases cannot read.

### Environment loading depends on invocation mode

- When Bun is invoked as `node` through `bun --bun`, `bunx --bun`, or a `node`
  symlink, it does not auto-load `.env*` files.
- Pass `node --env-file=.env script.js` when Node mode needs that file.
- Outside Node mode, `bun run --no-env-file` or root-level `env = false` skips
  automatic discovery; an explicit `--env-file` is still loaded.

### Structured-data parsing is stricter

- YAML follows YAML 1.2: `yes`, `no`, `on`, and `off` are strings; only
  `true` and `false` spellings are booleans.
- `Bun.JSONC.parse()` throws `SyntaxError` for invalid or empty input.
- TOML rejects unquoted strings, adjacent key/value pairs without a newline,
  and integers beyond `Number.MAX_SAFE_INTEGER`.

### Loader and transform behavior changed

- Runtime `.css` imports default-export `{}` rather than an absolute path.
- Bare `import "."` and `import ".."` resolve a directory's package entry or
  index file rather than a same-named sibling.
- New projects select TypeScript 7-compatible settings and `typescript@^7`.
- `"jsx": "react-jsx"` selects production `jsx`/`jsxs`; use
  `"react-jsxdev"` explicitly for `jsxDEV`.

### Socket, mapping, cron, and shell parameters changed

- `Bun.Socket#setKeepAlive(true, initialDelay)` treats the delay as
  milliseconds; values below 1000 leave `TCP_KEEPIDLE` unchanged.
- `Bun.mmap(path, { offset })` exposes the requested byte at index zero; remove
  old page-alignment compensation.
- `Bun.cron.parse()` and in-process `Bun.cron()` use local time. Pass
  `{ tz: "UTC" }` as the final argument to retain UTC.
- `Bun.$` expands only literal `*`, `**`, and braces in the template. Patterns
  from interpolation, variables, command substitution, or quotes stay literal.

### Fetch and server conformance tightened

- Duplicate response/request headers are comma-joined except `Set-Cookie`,
  which remains available through `getSetCookie()`.
- Cloning a consumed or locked body throws immediately. Network failures reject
  with `TypeError` and mark a failed body as used.
- A method route uses `GET` for `HEAD` only when no `HEAD` handler exists.
- Invalid `Bun.serve()` ports throw; an invalid response status goes through
  `error()` to a default `500` response.

### Mock, containment, and SQL semantics tightened

- `jest.resetAllMocks()` and `vi.resetAllMocks()` now discard implementations
  as well as call history; use `clearAllMocks()` to retain implementations.
- `toContain()` uses `===`: `-0` matches `0`, while `NaN` does not match itself.
- MySQL `DATETIME` and `TIMESTAMP` values decode as UTC. MariaDB JSON columns
  decode to JavaScript values.
- PostgreSQL honors `PGSSLMODE` unless a URL option overrides it, and infinite
  dates/timestamps decode as numeric infinities.

### Package-manager edge cases changed

- Project `bunfig.toml` wins over `.npmrc` for duplicate settings.
- `bun update <missing-name>` fails rather than adding the package.
- `--production` limits updates to production and optional dependencies;
  interactive mode updates only the selection.
- With non-TTY input, `bun init` behaves as `-y`, while `bun update -i` errors.
- New workspace projects use isolated installs; existing projects can retain a
  hoisted default recorded by the lockfile's `configVersion`.

### Older migration hazards still matter

- `Bun.serve()` uses `routes` rather than the earlier `static` option.
- `Bun.build()` rejects on build errors; set `throw: false` to inspect an error
  result instead.
- `bun -p` means `--print`, not `--port`.
- Bare `bun build --sourcemap` creates linked maps; request inline maps with
  `--sourcemap=inline`.
- Package scripts start in the directory containing the discovered
  `package.json`, not the invoking shell's subdirectory.
- `Bun.Build.Target` was renamed to `Bun.Build.CompileTarget`.

## High-value package workflows

- Inspect why a package exists with `bun why <package>`.
- Preview dependency source changes with `bun pm diff`; it flags changed files,
  new lifecycle scripts, and new sensitive built-in imports.
- Remediate advisories with `bun audit fix --dry-run`, then `bun audit fix`;
  major-version fixes require `--latest`.
- Consolidate compatible duplicate versions with `bun dedupe`; use `--check`
  in CI.
- Remove packages absent from the lockfile with `bun prune`; add
  `--production` to remove development dependencies.
- `bun update` updates transitive dependencies. Selectors can be names or globs
  and can use `--latest`.
- `bun add`, `bun remove`, and `bun update` accept `--filter`; `web...` includes
  dependencies and `...web` includes dependents.
- `bun add <pkg> --catalog` writes the root catalog and uses `catalog:` in the
  workspace.

## High-value server and fetch APIs

Serve directories directly through routes:

```ts
Bun.serve({
  routes: { "/static/*": { dir: "./public" } },
});
```

Directory routes handle content types, validators, conditional and range
requests, and `index.html`. Paths are normalized; on Linux, symlinks cannot
escape the route root.

Compress buffered fetch bodies with `compress`; streaming bodies are unchanged:

```ts
await fetch(url, {
  method: "POST",
  body: largeJsonString,
  compress: "gzip",
});
```

Use `Request.textStream()` or `Response.textStream()` for decoded UTF-8 string
streams that preserve split multibyte characters, strip a leading BOM, and
replace invalid sequences.

## High-value build and executable APIs

- Enable the built-in React auto-memoization compiler with
  `bun build --react-compiler` or `reactCompiler: true`.
- Embed assets with repeatable `bun build --compile --asset <path>`; locate them
  relative to `import.meta.dir`.
- `Bun.isStandaloneExecutable` reports whether code is in a compiled binary.
- Embedded native libraries can be opened with `dlopen()`.
- Standalone builds can use `splitting: true`, and embedded CommonJS entrypoints
  can require one another.
- For a self-contained browser file, compile HTML with
  `bun build --compile --target=browser ./index.html`; every entrypoint must be
  HTML and splitting is unavailable in this mode.

## High-value testing workflows

- Use `bun test --isolate` for a fresh global per file and cleanup between files.
- Use `bun test --parallel[=N]` for worker-process distribution; it implies
  isolation.
- Use `bun test --shard=M/N` for deterministic CI shards.
- Use `bun test --changed[=ref]` to select tests through the import graph.
- Record durations with `--update-timings`, then use `--timings=<path>` to
  balance shards and prioritize slow files.
- Use `--path-ignore-patterns` or `test.pathIgnorePatterns` to prune discovery.
- Concurrent tests cannot use assertion-count checks or file snapshots; inline
  snapshots remain supported.
- `expectTypeOf` assertions are runtime no-ops; also run
  `bunx tsc --noEmit` for type tests.

## High-value data and storage APIs

- `Bun.SQL` selects PostgreSQL, MySQL/MariaDB, or SQLite from its URL or adapter
  and uses tagged queries across adapters.
- SQL object helpers omit `undefined` insert properties so defaults apply, and
  bulk inserts collect columns across every row.
- SQLite `sql.unsafe()` and `sql.file()` accept named parameter objects.
- `Bun.s3` provides lazy Blob-like files, reads, writes, multipart writers,
  listings, presigned URLs, Requester Pays, and response metadata controls.
- Redis supports binary reads, database URL paths, Pub/Sub, TLS, retry cleanup,
  and reconnectable duplicates.
- `Bun.Archive` reads and creates tar archives and can write locally or to S3.

## Compatibility boundaries

The detailed compatibility reference distinguishes implemented Node APIs from
remaining gaps. In particular, verify code that depends on exact
`node:perf_hooks` behavior, V8 serialization interchange, low-level promise
hooks, child-process socket-handle IPC, or Node module-loader internals. Later
entries in that reference supersede earlier compatibility snapshots when the
project runs the later release.
