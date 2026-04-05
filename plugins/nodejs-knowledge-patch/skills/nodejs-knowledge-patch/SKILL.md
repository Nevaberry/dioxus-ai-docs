---
name: nodejs-knowledge-patch
description: "Node.js changes since training cutoff (23.0 through 25.5) -- require(esm), native TypeScript, built-in HTTP proxy, Permission model, Web Storage, URLPattern, Wasm modules, AsyncContextFrame. Load before writing Node.js code targeting v23+."
license: MIT
metadata:
  author: Nevaberry
  version: "25.5.0"
---

# Node.js 23+ Knowledge Patch

Claude's baseline covers Node.js through 22.x LTS. This skill documents features, breaking changes, and new APIs from v23.0 through v25.5.

## Reference Files

| File | Contents |
|------|----------|
| [module-system.md](references/module-system.md) | require(esm), TypeScript stripping, compile cache, Wasm modules |
| [http-networking.md](references/http-networking.md) | Built-in HTTP proxy, HTTP/2 sessions, TLS changes, fetch proxy |
| [test-runner.md](references/test-runner.md) | Auto-await subtests, global setup/teardown, coverage, reporters |
| [async-context.md](references/async-context.md) | AsyncContextFrame default, new constructor options |
| [web-platform-apis.md](references/web-platform-apis.md) | URLPattern global, Web Storage, CloseEvent, ErrorEvent |
| [permissions-security.md](references/permissions-security.md) | --permission flag, --allow-net, --allow-inspector, crypto changes |
| [breaking-changes.md](references/breaking-changes.md) | Deprecations, removals, platform support changes by version |

## Quick Reference: Key Features by Version

| Version | Highlights |
|---------|------------|
| 23.0 | `require(esm)` enabled by default, `module-sync` exports condition |
| 23.6 | TypeScript stripping unflagged (`node file.ts` works) |
| 24.0 | `URLPattern` global, `--permission` flag, test runner auto-await subtests, `AsyncContextFrame` default |
| 24.5 | Built-in HTTP proxy (`NODE_USE_ENV_PROXY`), Wasm modules unflagged, OpenSSL 3.5, Web Locks API |
| 25.0 | Web Storage unflagged, `--allow-net`, `--allow-inspector`, Corepack removed, Wasm JSPI |
| 25.2 | TypeScript type stripping marked **stable** |

## V8 Engine & Language Features (v24+)

These JS features are available starting with Node.js 24 (V8 13.6):

| Feature | Example |
|---------|---------|
| `Float16Array` | `new Float16Array([1.5, 2.5])` |
| Explicit resource management | `using handle = getResource()` / `await using db = connect()` |
| `RegExp.escape()` | `RegExp.escape("a.b") // "a\\.b"` |
| `Error.isError()` | `Error.isError(new TypeError()) // true` |
| Wasm Memory64 | 64-bit WebAssembly memory addressing |

## require(esm) -- Enabled by Default (v23+)

```js
// CJS files can now require() ES modules (if they don't use top-level await)
const { foo } = require('./esm-module.mjs');

// Top-level await in required ESM throws ERR_REQUIRE_ASYNC_MODULE

// Detect support at runtime
if (process.features.require_module) { /* ... */ }
```

Package authors: use `"module-sync"` exports condition to serve native ESM to both `require()` and `import`:

```json
{
  "exports": {
    "module-sync": "./index.mjs",
    "require": "./index.cjs",
    "import": "./index.mjs"
  }
}
```

## Native TypeScript (v23.6+, stable v25.2)

```bash
node file.ts # Just works (type stripping, no emit)
node --eval 'const x: number = 1; console.log(x)'
```

Limitations: no `namespace` keyword (use modules), no decorators that emit code, no `const enum` across files. Transformation is type-stripping only -- no downleveling.

## Built-in HTTP Proxy (v24.5+)

```bash
# Enable via env var
NODE_USE_ENV_PROXY=1 node app.js
# Or CLI flag
node --use-env-proxy app.js
```

Reads `http_proxy`, `https_proxy`, `no_proxy` from environment. Works with `http.request()`, `https.request()`, `fetch()`, and agents.

```js
// Per-agent proxy configuration
import https from 'node:https';
const agent = new https.Agent({
  proxyEnv: { https_proxy: 'http://proxy:8080', no_proxy: 'localhost' }
});
```

## Permission Model (v24+)

```bash
# Flag renamed from --experimental-permission to --permission
node --permission --allow-fs-read=/app --allow-fs-write=/tmp app.js

# Network permissions (v25+)
node --permission --allow-net app.js

# Inspector permissions (v25+)
node --permission --allow-inspector app.js
```

## URLPattern Global (v24+)

```js
// Available globally without import
const pattern = new URLPattern({ pathname: '/users/:id' });
const result = pattern.exec('https://example.com/users/123');
result.pathname.groups.id // "123"
```

## Web Storage (v25+, unflagged)

```js
// localStorage and sessionStorage available globally
localStorage.setItem('key', 'value');
localStorage.getItem('key'); // "value"
// Throws if no storage path configured (--localstorage-path)
```

## Test Runner Changes (v24+)

```js
import { test, suite, before, after } from 'node:test';

// Subtests auto-awaited -- no need to await t.test() (v24)
test('parent', (t) => {
  t.test('child 1', () => { /* ... */ });  // no await needed
  t.test('child 2', () => { /* ... */ });  // runs after child 1
});

// Global setup/teardown (v24)
before(() => { /* runs once before all tests */ });
after(() => { /* runs once after all tests */ });
```

## AsyncLocalStorage (v24+)

```js
import { AsyncLocalStorage } from 'node:async_hooks';

// Now defaults to AsyncContextFrame (faster implementation)
const als = new AsyncLocalStorage({
  name: 'request-context',    // debugging label
  defaultValue: { user: null } // returned when no store is active
});
```

## Wasm Module Imports (v24.5+, unflagged)

```js
// Instance phase import (gets instantiated module)
import { add } from './math.wasm';

// Source phase import (gets uninstantiated module)
import source mathModule from './math.wasm';
const instance = await WebAssembly.instantiate(mathModule, imports);
```

## assert.partialDeepStrictEqual (stable v24+)

```js
import assert from 'node:assert';

// Match subset of properties
assert.partialDeepStrictEqual(
  { name: 'Alice', age: 30, role: 'admin' },
  { name: 'Alice', role: 'admin' }  // age not checked
); // passes
```

## Other Notable Changes

| Feature | Version | Detail |
|---------|---------|--------|
| `node:sqlite` | 23.3+ | Session extension, conflict resolution |
| `tls.setDefaultCACertificates()` | 24.5+ | Dynamically configure CA certs |
| `v8.cpuProfile()` | 25+ | Programmatic CPU profiling |
| `worker.getHeapStatistics()` | 24+ | Per-worker heap stats |
| `navigator.locks` (Web Locks) | 24.5+ | Lock coordination in workers |
| `url.parse()` deprecated | 24+ | Use WHATWG `URL` constructor |
| Corepack removed | 25+ | Install pnpm/yarn separately |
| npm 11 bundled | 24+ | Enhanced perf and security |
| `process.ref()` / `unref()` | 23.6+ | Control event loop liveliness |
| Compile cache portable | 25+ | Share cache across machines |
| Wasm JSPI | 25+ | JS Promise Integration for Wasm |
| `path.matchGlob()` | 23+ | Glob matching for paths |
| `CloseEvent` global | 23+ | Web-compatible close event |
| `ErrorEvent` global | 25+ | Web-compatible error event |

See `references/breaking-changes.md` for the full deprecation/removal timeline.
