---
name: bun-knowledge-patch
description: Bun 1.3.14 compatibility. Use for Bun work.
license: MIT
version: "1.3.14"
metadata:
  author: Nevaberry
---

# Bun Knowledge Patch

Use this skill when implementing or reviewing Bun applications, libraries,
tooling, packages, tests, or migrations. Start with the quick references below,
then open the topic file that matches the task. In a topic, later entries
supersede earlier defaults or limitations.

## Reference index

| Reference | Topics |
|-----------|--------|
| [`build-and-frontend.md`](references/build-and-frontend.md) | Build behavior, HTML entrypoints, CSS, HMR, plugins, transpilation, standalone executables |
| [`databases-and-storage.md`](references/databases-and-storage.md) | Unified SQL, PostgreSQL, MySQL/MariaDB, SQLite, Redis/Valkey, S3-compatible storage |
| [`http-and-networking.md`](references/http-and-networking.md) | Routes, cookies, WebSockets, fetch, proxies, HTTP protocols, TLS, TCP, UDP, DNS |
| [`node-compatibility.md`](references/node-compatibility.md) | Core modules, loading, filesystem, crypto, VM, workers, native addons, remaining gaps |
| [`packages-and-workspaces.md`](references/packages-and-workspaces.md) | Lockfiles, installs, linker modes, workspaces, catalogs, scripts, audits, publishing |
| [`runtime-and-platform.md`](references/runtime-and-platform.md) | CLI and process behavior, data formats, terminal APIs, profiling, cron, platforms |
| [`testing.md`](references/testing.md) | Discovery, concurrency, assertions, snapshots, mocks, timers, coverage, reporters |

## Critical behavior and default changes

### Use `routes`, not the former `static` server option

`Bun.serve()` accepts handlers, method maps, imported HTML, `Response`, and
`Bun.file()` values under `routes`. Supplying `routes` makes `fetch` optional.

```ts
import homepage from "./index.html";

const server = Bun.serve({
  routes: {
    "/": homepage,
    "/health": new Response("ok"),
    "/users/:id": req => Response.json({ id: req.params.id }),
    "/users": {
      GET: () => Response.json([]),
      POST: async req => Response.json(await req.json()),
    },
  },
});
```

Static responses receive ETags, and whole-file responses automatically honor
single byte ranges. Method-specific routes take precedence over `/*`.

### Treat build failures as rejected promises

`Bun.build()` rejects when a build fails. Use `throw: false` only when code is
intentionally written to inspect an unsuccessful `BuildOutput`.

```ts
const result = await Bun.build({
  entrypoints: ["./src/index.ts"],
  outdir: "./dist",
  throw: false,
});

if (!result.success) console.error(result.logs);
```

Bare `bun build --sourcemap` creates linked `.map` files. Use
`--sourcemap=inline` when inline maps are required. The `Bun.Build.Target` type
was renamed to `Bun.Build.CompileTarget`.

### Account for package-manager defaults

- New workspace projects use the isolated linker; existing workspace behavior
  remains pinned by the lockfile unless configuration explicitly selects a
  linker.
- `bun run` starts a discovered package script in the directory containing its
  `package.json`, not the invocation subdirectory.
- New lockfiles are text JSONC files named `bun.lock`; npm, Yarn v1, and pnpm
  projects can migrate while preserving resolved versions.
- `bun install --frozen-lockfile` includes sorted and unused `overrides` in its
  consistency check.
- Lifecycle scripts for `file:`, `link:`, Git, and GitHub dependencies require
  explicit trust.

### Account for test-runner failure semantics

An uncaught exception or rejected promise between test cases fails the run. An
empty or unmatched filtered run also fails unless `--pass-with-no-tests` is
present. In CI, focused tests and new snapshots without an update flag are
errors.

### Review compatibility-sensitive defaults

- The Redis client has no idle timeout by default, so idle connections remain
  open until explicitly closed.
- WebSocket clients negotiate `permessage-deflate` by default.
- `bun -p` means `--print`; it is not a port alias.
- `Bun.Spawn.OptionsObject` is deprecated in favor of
  `Bun.Spawn.BaseOptions`.
- Standalone executables load deployment-time `.env` and `bunfig.toml` unless
  disabled at build time, but do not load `tsconfig.json` or `package.json`
  unless explicitly enabled.

## HTTP server essentials

### Cookies and WebSocket upgrades

Mutating `request.cookies` adds `Set-Cookie` headers to the returned response.
Cookies set before `server.upgrade()` are carried onto the `101` response.

```ts
Bun.serve({
  routes: {
    "/chat": (req, server) => {
      req.cookies.set("session", "token", {
        httpOnly: true,
        sameSite: "strict",
      });
      return server.upgrade(req)
        ? undefined
        : new Response("Upgrade required", { status: 426 });
    },
  },
  websocket: {
    message(ws, message) {
      ws.send(message);
    },
  },
});
```

Use `Bun.CSRF.generate()` and `Bun.CSRF.verify()` for built-in CSRF tokens.
For graceful shutdown, await `server.stop()`; use Node's
`closeIdleConnections()` when shutting down a compatible HTTP server.

### Fetch and proxy controls

`fetch()` accepts a proxy URL, a `URL`, or `{ url, headers }`. The same proxy
forms work for WebSockets. `NO_PROXY` applies even to an explicit proxy, and
runtime changes to proxy environment variables affect the next request.

## Database and storage essentials

### Unified SQL

`SQL` selects PostgreSQL, MySQL/MariaDB, or SQLite from its URL or adapter.
Tagged-template interpolation parameterizes values; use `unsafe()` only for
intentional raw SQL.

```ts
import { SQL, sql } from "bun";

const users = await sql`SELECT * FROM users WHERE age >= ${18}`;
await sql`INSERT INTO users ${sql({ name: "Ada", active: true })}`;
await sql`UPDATE users SET ${sql({ active: false })} WHERE id = ${users[0].id}`;

await using mysql = new SQL("mysql://user:pass@localhost/app");
await using sqlite = new SQL(":memory:");
```

Object inserts omit `undefined` so database defaults apply. Bulk inserts gather
columns across all rows. Catch `Bun.SQL.SQLError` for common handling or the
adapter-specific subclasses for targeted handling.

### Redis and S3

```ts
import { redis, s3 } from "bun";

await redis.set("session", "active", "EX", 60);
const value = await redis.getBuffer("binary-value");

const object = s3.file("reports/latest.json");
await object.write(JSON.stringify({ ok: true }), {
  contentDisposition: 'attachment; filename="latest.json"',
});
const url = object.presign({ expiresIn: 3600 });
```

Use `RedisClient` for explicit URLs, database selection, TLS, and Pub/Sub. S3
clients support S3-compatible endpoints, virtual-hosted style, listings,
Requester Pays, storage classes, multipart writers, and response metadata on
presigned URLs.

## Build and frontend essentials

HTML entrypoints bundle module scripts, styles, and assets. They can run as a
development server, build as production output, or compile into self-contained
browser HTML. CSS entrypoints, CSS Modules, HMR, and the official Svelte plugin
are supported.

```sh
bun ./index.html
bun build ./index.html --production --outdir=dist
bun build --compile --target=browser ./index.html
```

For analysis, use JSON or Markdown metafiles. For conditional builds, guard
code with `feature()` from `bun:bundle` and enable named features through the
CLI or `Bun.build({ features })`.

Standalone builds support cross-target compilation, embedded runtime flags,
Windows metadata, bytecode, post-build code signing, and programmatic plugins.
Compiled ESM bytecode requires both `--bytecode` and `--format=esm`.

## Test runner essentials

```ts
import { expect, jest, onTestFinished, test } from "bun:test";

test("uses controlled time", () => {
  jest.useFakeTimers({ now: new Date("2026-01-01") });
  const callback = jest.fn();
  setTimeout(callback, 1000);
  jest.advanceTimersByTime(1000);
  expect(callback).toHaveBeenCalledTimes(1);
  jest.useRealTimers();
});

test("retries locally", async () => {
  const resource = { close() {} };
  onTestFinished(() => resource.close());
  expect(await Promise.resolve(true)).toBe(true);
}, { retry: 3 });
```

Use `test.concurrent` for in-file concurrency, `--parallel` for worker-process
file parallelism, `--isolate` for fresh globals, `--shard=M/N` for deterministic
CI shards, and `--changed[=ref]` for Git-aware selection. `expectTypeOf` is a
runtime no-op, so also run a TypeScript type checker.

## Runtime and Node.js compatibility

Built-in runtime APIs include YAML, JSONC, JSON5, JSONL, Markdown, tar archives,
image processing, OS credential storage, cron scheduling, PTYs, ANSI-aware text
measurement, CPU and heap profiling, and a native REPL. Prefer these APIs when
they remove unnecessary package or subprocess dependencies.

Node.js compatibility is broad but not identical. Check the compatibility
reference before depending on low-level module-loader internals, promise hooks,
child-process handle transfer, worker resource limits, OpenSSL engine or FIPS
controls, V8 serialization interchange, `node:sqlite`, or inspector domains
outside the profiler.
