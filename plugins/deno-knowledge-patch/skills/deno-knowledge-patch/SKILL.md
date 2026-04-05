---
name: deno-knowledge-patch
description: >
  Deno 2.2–2.7 features: permission sets, dx command, deno bundle, Temporal API,
  OpenTelemetry, lint plugins, test hooks, deno compile improvements, deno audit,
  and configuration changes. Load before writing Deno 2.2+ code.
license: MIT
metadata:
  author: Nevaberry
  version: "2.7"
---

# Deno 2.2+ Knowledge Patch

Claude's baseline knowledge covers Deno through 2.1. This skill provides features from 2.2 (February 2025) onwards.

## Reference Index

- [Permissions & Security](references/permissions-security.md) — Permission sets in deno.json, `-P` flag, permission broker, `--ignore-read`/`--ignore-env`, audit permissions logging
- [Toolchain & CLI](references/toolchain-cli.md) — `deno bundle`, `deno compile`, `deno create`, `dx` (npx equivalent), `deno audit`, `deno add` flags, `deno approve-scripts`, task enhancements
- [Runtime APIs](references/runtime-apis.md) — `Temporal` (stable), `Deno.spawn()`, `FsFile.tryLock()`, Wasm source imports, Brotli streams, SHA3, `ChildProcess` convenience methods
- [Server & Networking](references/server-networking.md) — `Deno.serve` options, QUIC/WebTransport, WebSocket headers, `Deno.HttpClient` proxy, OpenTelemetry
- [Testing & Coverage](references/testing-coverage.md) — Test hooks (`beforeAll`/`afterAll`), auto coverage reports, ignore comments, bench options
- [Configuration](references/configuration.md) — `links` (local npm packages), `minimumDependencyAge`, `"publish": false`, `jsr:` in package.json, `DENO_COMPAT`, node globals
- [Linting & Type Checking](references/linting-checking.md) — Lint plugin system, new default rules, `--unstable-tsgo`, `--check-js`, `--fail-fast`

## Quick Reference

### Key CLI Commands (new)

| Command | Purpose | Since |
|---------|---------|-------|
| `dx cowsay "Hello"` | Run package binaries (like npx) | 2.6 |
| `deno bundle --minify main.ts` | Bundle with esbuild | 2.4 |
| `deno create npm:vite -- my-app` | Scaffold projects | 2.7 |
| `deno audit` | Scan deps for CVEs | 2.6 |
| `deno audit --socket` | Also check socket.dev | 2.6 |
| `deno approve-scripts` | Approve lifecycle scripts interactively | 2.6 |
| `deno add --npm chalk react` | Add multiple npm packages | 2.3 |
| `deno add --jsr @std/fs @std/path` | Add multiple JSR packages | 2.3 |
| `deno add --save-exact npm:express` | Pin exact version (no caret) | 2.7 |
| `deno check` | Type-check all project files (no args needed) | 2.3 |
| `deno check --unstable-tsgo main.ts` | Go-based fast type checker | 2.6 |
| `deno install --compile -A npm:pkg` | Compile npm pkg to binary | 2.7 |

### Permission Sets

```jsonc
// deno.json
{
  "permissions": {
    "default": { "read": ["./data"], "env": true },
    "dev": { "read": true, "write": true, "net": true }
  }
}
```
```bash
deno run -P main.ts     # uses "default" set
deno run -P=dev main.ts # uses "dev" set
```

### OpenTelemetry (stable since 2.4)

```bash
OTEL_DENO=1 deno --allow-net server.ts
```

Auto-instruments `console.log`, `Deno.serve`, `fetch`, and `Deno.cron`. Use `npm:@opentelemetry/api` for custom spans/metrics.

### Temporal API (stable since 2.7)

```ts
const now = Temporal.Now.zonedDateTimeISO();
const date = Temporal.PlainDate.from("2026-01-15");
const duration = Temporal.Duration.from({ hours: 2, minutes: 30 });
```

### Local npm Package Linking

```jsonc
// deno.json — use "links" (was "patch" in 2.3, renamed in 2.4)
{
  "nodeModulesDir": "auto",
  "links": ["../path/to/local_npm_package"]
}
```

### Test Hooks (2.5+)

```ts
Deno.test.beforeAll(() => { /* setup */ });
Deno.test.afterAll(() => { /* teardown */ });
Deno.test.beforeEach(() => { /* per-test setup */ });
Deno.test.afterEach(() => { /* per-test teardown */ });
```

### Subprocess Convenience (2.7+, unstable)

```ts
const child = Deno.spawn("deno", ["fmt", "--check"], { stdout: "inherit" });
const output = await Deno.spawnAndWait("git", ["status"]);
```

### Import Text/Bytes (2.4+, unstable)

```ts
import message from "./hello.txt" with { type: "text" };    // string
import bytes from "./image.png" with { type: "bytes" };      // Uint8Array
```

### Breaking/Notable Changes

| Change | Since |
|--------|-------|
| `Deno.cwd()` no longer needs `--allow-read` | 2.2 |
| `Deno.execPath()` no longer needs `--allow-read` | 2.4 |
| Node globals (`Buffer`, `global`, `setImmediate`) available everywhere | 2.4 |
| `@types/node` included by default | 2.6 |
| `node:sqlite` module available | 2.2 |
| `--unstable-otel` no longer required (just `OTEL_DENO=1`) | 2.4 |
| `--unstable-temporal` no longer required | 2.7 |
| `"patch"` renamed to `"links"` in deno.json | 2.4 |
