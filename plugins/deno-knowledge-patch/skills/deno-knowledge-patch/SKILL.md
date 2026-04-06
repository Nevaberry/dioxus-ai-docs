---
name: deno-knowledge-patch
description: "Deno changes since training cutoff (latest: 2.7.0) \u2014 Deno.spawn(), permission sets, deno audit, lint plugin API, QUIC, OpenTelemetry. Load before working with Deno."
version: "2.7.0"
license: MIT
metadata:
  author: Nevaberry
---

# Deno Knowledge Patch

Claude Opus 4.6 knows Deno through 1.x. This skill provides features from Deno 2.2 (2025-02-19) through 2.7 (2026-02-25).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Permissions | [references/permissions.md](references/permissions.md) | Permission sets in config, `--ignore-read`/`--ignore-env`, subdomain wildcards, CIDR |
| CLI commands | [references/cli-commands.md](references/cli-commands.md) | `dx`, `deno bundle`, `deno audit`, `deno create`, `deno compile` enhancements |
| Testing & benchmarks | [references/testing.md](references/testing.md) | Setup/teardown hooks, coverage auto-report, bench iteration control |
| Package management | [references/package-and-config.md](references/package-and-config.md) | `links`, `minimumDependencyAge`, `jsr:` in package.json, `--npm`/`--jsr` flags |
| Developer tooling | [references/developer-tooling.md](references/developer-tooling.md) | Lint plugin API, `deno fmt` tagged templates, new lint rules |
| Runtime APIs | [references/runtime-apis.md](references/runtime-apis.md) | `Deno.spawn()`, `FsFile.tryLock()`, Brotli, SHA3, OTel, WebSocket headers, QUIC |
| Module system & compat | [references/module-system.md](references/module-system.md) | Import text/bytes, Wasm source phase, `--preload`, `DENO_COMPAT=1`, node globals |

---

## Quick Reference

### Permission sets (2.5+)

Define named permission sets in `deno.json`:
```json
{
  "permissions": {
    "default": {
      "read": [
        "./data"
      ],
      "env": true
    },
    "dev": {
      "read": true,
      "write": true,
      "net": true
    }
  }
}
```
```bash
deno run -P main.ts     # uses "default" set
deno run -P=dev main.ts # uses "dev" set
```

### Ignore permissions (2.6+)

Return `NotFound`/`undefined` instead of throwing for denied resources:
```bash
deno run --ignore-read=/etc --ignore-env=AWS_SECRET_KEY main.ts
```

---

### OpenTelemetry (stable since 2.4)

```bash
OTEL_DENO=1 deno --allow-net server.ts
```
Auto-instruments `console.log`, `Deno.serve`, `fetch`. Custom spans via `npm:@opentelemetry/api`.

---

### Key new CLI commands

| Command | Version | Purpose |
|---|---|---|
| `dx` / `deno x` | 2.6 | Run package binaries (like `npx`) |
| `deno bundle` | 2.4 | esbuild-based bundler (restored) |
| `deno audit` | 2.6 | Scan deps for CVEs |
| `deno create` | 2.7 | Scaffold from templates |
| `deno approve-scripts` | 2.6 | Approve npm lifecycle scripts |

---

### Test hooks (2.5+)

```ts
Deno.test.beforeAll(() => { /* once before all tests */ });
Deno.test.beforeEach(() => { /* before each test */ });
Deno.test.afterEach(() => { /* after each test */ });
Deno.test.afterAll(() => { /* once after all tests */ });
```

---

### `Deno.spawn()` subprocess shorthands (2.7, unstable)

```ts
const child = Deno.spawn("deno", ["fmt", "--check"], { stdout: "inherit" });
const output = await Deno.spawnAndWait("git", ["status"]);
const result = Deno.spawnAndWaitSync("echo", ["done"]);
```

---

### Import text and bytes (2.4+, unstable)

```ts
import message from "./hello.txt" with { type: "text" };    // string
import bytes from "./image.png" with { type: "bytes" };      // Uint8Array
```

### Wasm source phase imports (2.6+)

```ts
import source addModule from "./add.wasm";
const { add } = WebAssembly.instantiate(addModule).exports;
```

---

### Node.js compatibility

| Feature | Version |
|---|---|
| `DENO_COMPAT=1` (enables all compat flags) | 2.4 |
| `Buffer`, `global`, `setImmediate` always available | 2.4 |
| `@types/node` included by default | 2.6 |
| `jsr:` scheme in `package.json` | 2.7 |
| `package.json` `overrides` field supported | 2.7 |

---

### Package linking (formerly `patch`)

```json
{ "links": ["../path/to/local_npm_package"] }
```
Requires `"nodeModulesDir": "auto"` or `"manual"`. Renamed from `"patch"` in 2.4.

---

### Coverage auto-report (2.3+)

`deno test --coverage` now auto-generates the report. Ignore comments:
```ts
// deno-coverage-ignore          — single line
// deno-coverage-ignore-start    — block start
// deno-coverage-ignore-stop     — block end
// deno-coverage-ignore-file     — entire file
```

---

### Lint plugin API (2.2+, unstable)

```json
{ "lint": { "plugins": ["./my-plugin.ts", "jsr:@scope/plugin"] } }
```
```ts
export default {
  name: "my-plugin",
  rules: {
    "no-foo": {
      create(context) {
        return {
          VariableDeclarator(node) {
            if (node.id.type === "Identifier" && node.id.name === "foo") {
              context.report({ node, message: "Don't use foo" });
            }
          },
        };
      },
    },
  },
} satisfies Deno.lint.Plugin;
```

---

## Reference Files

| File | Contents |
|---|---|
| [permissions.md](references/permissions.md) | Permission sets, `--ignore-read`/`--ignore-env`, subdomain wildcards, CIDR, `--deny-import` |
| [cli-commands.md](references/cli-commands.md) | `dx`, `deno bundle`, `deno audit`, `deno create`, `deno compile`, `deno install --compile`, `deno approve-scripts`, `deno task` |
| [testing.md](references/testing.md) | Test hooks, coverage auto-report and ignore comments, bench iteration control |
| [package-and-config.md](references/package-and-config.md) | `links`, `minimumDependencyAge`, `jsr:` in package.json, `overrides`, `--npm`/`--jsr` flags, `"publish": false` |
| [developer-tooling.md](references/developer-tooling.md) | Lint plugin API, `deno fmt` tagged templates, `deno check` no-args, new lint rules |
| [runtime-apis.md](references/runtime-apis.md) | `Deno.spawn()`, `FsFile.tryLock()`, Brotli, SHA3, OTel, ChildProcess methods, `Deno.bundle()` API, WebSocket headers, QUIC/WebTransport |
| [module-system.md](references/module-system.md) | Import text/bytes, Wasm source phase imports, `--preload`, `--require`, `DENO_COMPAT=1`, node globals, `@types/node` |
