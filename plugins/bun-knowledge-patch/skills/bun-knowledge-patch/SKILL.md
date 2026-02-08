---
name: bun-knowledge-patch
description: This skill should be used when writing Bun code, using Bun-specific APIs, bun:* modules, Bun.serve(), bundler features, or any Bun features from 1.2+ (2025-2026).
license: MIT
metadata:
  author: Nevaberry
  version: "1.3.8"
---

# Bun 1.2+ Knowledge Patch

Claude's baseline knowledge covers Bun through 1.1.x. This skill provides features from 1.2 (January 2025) onwards.

## Quick Reference

### HTTP Server (`Bun.serve`)

| Feature | Example |
|---------|---------|
| Routes with params | `"/api/users/:id"` → `req.params.id` |
| Method handlers | `{ GET: fn, POST: fn }` |
| Static routes | `"/health": new Response("OK")` |
| HTML imports | `import page from "./index.html"` |
| Cookies | `req.cookies.set("name", "value")` |
| CSRF | `await Bun.CSRF.generate(sessionId)` |

See `references/http-server.md` for routes, cookies, dev server, WebSocket proxy.

### SQL & Database

| Client | Connection |
|--------|------------|
| PostgreSQL | `import { sql } from "bun"` |
| MySQL/MariaDB | `new SQL("mysql://...")` |
| SQLite | `new SQL(":memory:")` |
| Redis | `import { redis } from "bun"` |

```ts
const users = await sql`SELECT * FROM users WHERE age >= ${minAge}`;
await sql`INSERT INTO users ${sql(user, "name", "email")}`;
```

See `references/sql-database.md` for tagged templates, dynamic columns, Redis pub/sub.

### S3 Storage (`Bun.s3`)

```ts
const file = s3.file("path/file.txt");
await file.text();  // Same API as Bun.file()
await file.write("data");
const url = s3.presign("file", { expiresIn: 3600 });
```

See `references/s3-storage.md` for bucket listing, upload options.

### Test Runner (`bun:test`)

| Feature | API |
|---------|-----|
| Fake timers | `jest.useFakeTimers()` |
| Concurrent tests | `test.concurrent()` |
| Retry flaky | `test("name", fn, { retry: 3 })` |
| Type testing | `expectTypeOf(x).toBeString()` |
| vi global | `vi.fn()`, `vi.mock()`, `vi.spyOn()` |

See `references/test-runner.md` for matchers, mocking, configuration.

### Package Manager

| Command | Purpose |
|---------|---------|
| `bun outdated` | View outdated deps |
| `bun audit` | Security scan |
| `bun why <pkg>` | Dependency path |
| `bun pm pkg get/set` | Manage package.json |
| `bun pm version patch` | Bump version |

See `references/package-manager.md` for workspaces, catalogs, linker modes.

### Bundler (`bun build`)

| Flag | Purpose |
|------|---------|
| `--compile` | Standalone executable |
| `--target=bun-*` | Cross-compile |
| `--production` | Production HTML build |
| `--metafile` / `--metafile-md` | Bundle analysis |
| `--feature=X` | Compile-time flags |

See `references/bundler.md` for plugins, JSX config, virtual files.

### New APIs

| API | Purpose |
|-----|---------|
| `Bun.markdown` | MD → HTML/React |
| `Bun.YAML` | YAML parse/stringify |
| `Bun.JSON5` | JSON5 with comments |
| `Bun.Archive` | Tar creation/extraction |
| `Bun.Terminal` | PTY support |
| `Bun.secrets` | OS credential storage |

See `references/new-apis.md` for JSONC, JSONL, compression, text utilities.

### Runtime & CLI

| Feature | Example |
|---------|---------|
| Spawn timeout | `Bun.spawn({ cmd, timeout: 1000 })` |
| CPU profiling | `bun --cpu-prof script.js` |
| Heap profiling | `bun --heap-prof script.js` |
| Fetch proxy | `fetch(url, { proxy: "http://..." })` |

See `references/runtime-cli.md` for spawn options, profiling, CLI flags.

### Node.js Compatibility

| API | Status |
|-----|--------|
| `fs.glob` | Supported |
| `node:http2` | Supported |
| `node:vm` | SourceTextModule, SyntheticModule |
| `node:inspector` | Profiler API |
| `ReadableStream.json()` | Direct consumption |

See `references/node-compat.md` for full compatibility details.

## Reference Files

| File | Contents |
|------|----------|
| `http-server.md` | Routes, static, cookies, HTML imports, dev server |
| `sql-database.md` | Postgres, MySQL, SQLite, Redis clients |
| `s3-storage.md` | S3 client, presigned URLs, bucket listing |
| `test-runner.md` | Matchers, mocking, fake timers, concurrent |
| `package-manager.md` | Install, audit, workspaces, catalogs |
| `bundler.md` | Compile, plugins, metafile, feature flags |
| `new-apis.md` | Markdown, YAML, JSON5, Archive, Terminal |
| `node-compat.md` | fs.glob, vm, inspector, streams |
| `runtime-cli.md` | Spawn, profiling, CLI flags |

## Critical Examples

### Full-Stack Server with Routes

```ts
import homepage from "./index.html";  // Auto-bundles JS/CSS
import { sql } from "bun";

Bun.serve({
  routes: {
    "/": homepage,
    "/api/users/:id": (req) => {
      const { id } = req.params;
      return Response.json({ id });
    },
    "/api/users": {
      GET: async () => Response.json(await sql`SELECT * FROM users`),
      POST: async (req) => {
        const { name } = await req.json();
        const [user] = await sql`INSERT INTO users (name) VALUES (${name}) RETURNING *`;
        return Response.json(user);
      },
    },
  },
});
```

### Cookies

```ts
// In route handler
req.cookies.set("session", token, { httpOnly: true, sameSite: "strict" });
req.cookies.get("session");
req.cookies.delete("session");
```

### SQL Dynamic Columns

```ts
// Insert/update specific columns from object
await sql`INSERT INTO users ${sql(user, "name", "email")}`;
await sql`UPDATE users SET ${sql(user, "name")} WHERE id = ${user.id}`;

// WHERE IN with array
await sql`SELECT * FROM users WHERE id IN ${sql([1, 2, 3])}`;
```

### Test Runner Essentials

```ts
import { test, expect, jest, mock } from "bun:test";

test("with fake timers", () => {
  jest.useFakeTimers();
  setTimeout(() => {}, 1000);
  jest.advanceTimersByTime(1000);
  jest.useRealTimers();
});

test.concurrent("runs in parallel", async () => {});
test("retry flaky", () => {}, { retry: 3 });
```
