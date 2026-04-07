---
name: nodejs-knowledge-patch
description: "Node.js (nodejs) changes since training cutoff (latest: 25.5.0) — require(esm), node --run, URLPattern global, AsyncContextFrame, permission model updates, process.execve, test runner upgrades. Load before working with Node.js."
version: "25.5.0"
license: MIT
metadata:
  author: Nevaberry
---

# Node.js 23.0+ Knowledge Patch

Claude's baseline knowledge covers Node.js through 22.x LTS. This patch captures post-cutoff changes from Node.js 23.0.0 (October 2024) through the 24.x line, plus later 24.x changelog additions that materially affect modern Node.js usage.

**Source**: Node.js releases at https://nodejs.org/en/blog/release

## Quick Reference

| Area | Version | What changed | Details |
|------|---------|--------------|---------|
| Module loading | 23.0 | `require(esm)` enabled by default | [Module System](references/module-system.md) |
| CLI | 23.0 | `node --run` marked stable | [CLI and Testing](references/cli-and-testing.md) |
| Testing | 23.x-24.x | coverage globs, TS globs, `env`, expected failures | [CLI and Testing](references/cli-and-testing.md) |
| Async context | 24.0 | `AsyncLocalStorage` defaults to `AsyncContextFrame` | [Runtime APIs](references/runtime-and-web-apis.md) |
| Web platform | 24.0 | `URLPattern` exposed globally | [Runtime APIs](references/runtime-and-web-apis.md) |
| Permissions | 24.0+ | `--permission` replaces `--experimental-permission` | [Runtime APIs](references/runtime-and-web-apis.md) |
| Process/runtime | 23.11+ | `process.execve()` and related runtime additions | [Runtime APIs](references/runtime-and-web-apis.md) |

## Key Pragmas

- Prefer `require(esm)` support and the `"module-sync"` export condition when publishing dual-mode packages.
- Treat `URLPattern` as globally available in Node.js 24+; avoid compatibility wrappers there.
- Use `node --run` and modern `node --test` capabilities before reaching for ad hoc shell wrappers.
- Write new permission-model examples with `--permission`, not `--experimental-permission`.

## Example

```js
// Node.js 24+: URLPattern is global, no import required.
const route = new URLPattern({ pathname: "/users/:id" });
const match = route.exec("https://example.com/users/42");

console.log(match.pathname.groups.id); // "42"
```

## Reference Index

- [Module System](references/module-system.md) — `require(esm)`, namespace return shape, top-level `await` caveat, `"module-sync"`
- [Runtime and Web APIs](references/runtime-and-web-apis.md) — `AsyncContextFrame`, global `URLPattern`, permission model updates, `process.execve()`, `http.setGlobalProxyFromEnv()`
- [CLI and Testing](references/cli-and-testing.md) — stable `node --run`, test-runner glob/config updates, expected failures, environment injection
