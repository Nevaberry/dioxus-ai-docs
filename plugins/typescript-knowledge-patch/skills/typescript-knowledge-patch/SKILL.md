---
name: typescript-knowledge-patch
description: "TypeScript changes since training cutoff (latest: 5.9) — import defer, --module node20, ArrayBuffer breaking change, TypeScript 7 native Go port (tsgo). Load before working with TypeScript."
license: MIT
version: "5.9"
metadata:
  author: Nevaberry
---

# TypeScript 5.9+ Knowledge Patch

Claude's baseline knowledge covers TypeScript through 5.8. This skill provides features from 5.9 (May 2025) onwards.

**Source**: https://devblogs.microsoft.com/typescript/

<!-- APPEND NEW VERSIONS BELOW THIS LINE -->

## 5.9

| Feature | What to know |
|---------|-------------|
| `import defer` | `import defer * as ns from "mod"` — defers module execution until first property access. Namespace imports only. Requires `--module preserve` or `esnext`. |
| `--module node20` | Stable pinned option for Node.js 20. Implies `--target es2023`. |
| `ArrayBuffer` breaking change | `ArrayBuffer` is no longer supertype of `TypedArray`. Fix: use `Uint8Array<ArrayBuffer>`, access `.buffer`, or update `@types/node`. |
| Type argument inference | Generic type inference fixes may introduce new errors from "leaked" type variables. Fix by adding explicit type arguments to generic function calls. |

## TypeScript 7 (Native Port)

| Topic | What to know |
|-------|-------------|
| Versioning | TS 6.0 = **last JS release** (no 6.1). TS 7.x = native Go rewrite (`tsgo`). Repo: `microsoft/typescript-go` |
| Install | `npm install -D @typescript/native-preview` → `npx tsgo` |
| TS 6/7 breaking changes | `--strict` on by default, `--target es5` removed, `--baseUrl` removed, `--moduleResolution node10` removed |
| Migration tool | `npx @andrewbranch/ts5to6 --fixBaseUrl` / `--fixRootDir` |
| Full details | See `references/typescript-7-transition.md` |

