# TypeScript 7 (Native Port) Transition Guide

## Overview

TypeScript is being rewritten from JavaScript to Go for ~10x performance. The native version will be released as **TypeScript 7.0** (`tsgo`).

## Versioning

| Version | Codebase | Role |
|---------|----------|------|
| 5.9 | JavaScript | Current stable |
| 6.0 | JavaScript | **Last JS-based release**. Bridge/transition — adds deprecations to align with TS 7. No 6.1 planned, patches only for security/regressions. |
| 7.x | Go (native) | Native port |

- Codenames: **Strada** (JS codebase), **Corsa** (native port)
- Repo: `microsoft/typescript-go`

## What changes for users

- **Same type system** — TS 7 aims for full parity with TS 5.x/6.x type checking
- **New CLI binary**: `tsgo` (instead of `tsc` via Node.js)
- **Language Server Protocol (LSP)** — TS 7 moves to standard LSP instead of the custom tsserver protocol
- **New compiler API** — the current `ts.*` programmatic API will not work with Corsa. API is still in progress.
- **Side-by-side usage** — install both `typescript` (6.0) and `@typescript/native-preview` (7.0). Use `tsgo` for fast type-checking, `tsc` for tooling that needs the Strada API.

## Trying the native preview today

```bash
npm install -D @typescript/native-preview
npx tsgo --project ./tsconfig.json
npx tsgo -b some.tsconfig.json # --build mode works
```

VS Code extension: search "TypeScript Native Preview" in marketplace, then enable with:
```json
"typescript.experimental.useTsgo": true
```

`tsgo` will eventually be renamed to `tsc` in the `typescript` package.

## TS 6.0 / 7.0 breaking changes (deprecations)

These are removed in TS 7.0 and deprecated in TS 6.0:

| Change | Details |
|--------|---------|
| `--strict` on by default | No longer need to specify it |
| `--target` defaults to latest stable ES | e.g. `es2025` instead of `es3` |
| `--target es5` removed | `es2015` is the lowest supported target |
| `--baseUrl` removed | Use `paths` with explicit base or remove |
| `--moduleResolution node10`/`node` removed | Use `bundler`, `nodenext`, or `node20` |
| `rootDir` defaults to `.` | Using `outDir` requires explicit `rootDir`, or top-level sources must be alongside `tsconfig.json` |

### Migration tool

```bash
npx @andrewbranch/ts5to6 --fixBaseUrl your-tsconfig.json
npx @andrewbranch/ts5to6 --fixRootDir your-tsconfig.json
```

## Current limitations (preview)

**Working**: type-checking, `--build`, `--incremental`, project references, editor features (completions, auto-imports, go-to-definition, find-all-references, rename, hover, signature help, formatting).

**Not yet complete**:
- Downlevel emit only goes back to `es2021` (no `es2015`–`es2020` targets yet, no decorator compilation)
- `--declaration` emit still in progress
- `--watch` mode may be less efficient (workaround: use `nodemon` + `tsgo --incremental`)
- No Strada API compatibility — linters/formatters using `ts.*` API won't work with Corsa

## JSDoc / JavaScript checking changes

TypeScript 7 **rewrote** (not ported) JS/JSDoc type-checking. Dropped patterns:

- `@enum` and `@constructor` tags not recognized
- `Object` is no longer treated as `any`
- `String` is no longer treated as `string`
- `Foo` is no longer interpreted as `typeof Foo` where the latter would be valid in TS
- `any`/`unknown`/`undefined`-typed parameters are no longer implicitly optional

JS codebases may see new errors. Use more idiomatic/modern JSDoc patterns.

## Migration path

1. Upgrade to TS 6.0 first (addresses deprecations)
2. Run `ts5to6` tool to fix `baseUrl` and `rootDir` automatically
3. Fix remaining TS 6 breaking changes (module resolution, target, etc.)
4. Install `@typescript/native-preview` side-by-side for fast type-checking
5. Switch fully to TS 7 when it supports your project's needs
