---
name: typescript-knowledge-patch
description: TypeScript changes since training cutoff (latest 5.9, plus TS 7.0/tsgo transition) — import defer, --module node20, ArrayBuffer breaking change, tsgo migration. Load before working with TypeScript 5.9+.
version: "5.9.0"
license: MIT
metadata:
  author: Nevaberry
---

# TypeScript 5.9+ Knowledge Patch

Claude's baseline knowledge covers TypeScript through 5.8. This skill provides features from 5.9 (2025-06-17) onwards, plus the TypeScript 7.0 (tsgo) transition roadmap.

## Quick Reference

### New Features (5.9)

| Feature | Syntax / Option | Notes |
|---------|----------------|-------|
| Deferred imports | `import defer * as ns from "./mod.js"` | Module loaded but not executed until accessed |
| `--module node20` | Stable pinned module mode | Models Node.js v20, implies `--target es2023` |

### Breaking Changes (5.9)

| Change | Impact | Fix |
|--------|--------|-----|
| `ArrayBuffer` not supertype of `TypedArray` | `Buffer`/`Uint8Array` not assignable to `ArrayBuffer` | Update `@types/node`, use `Uint8Array<ArrayBuffer>`, or access `.buffer` |
| Type argument inference fixes | New errors in generic function calls | Add explicit type arguments |

### TS 7.0 New Defaults (Breaking)

| Setting | Old Default | New Default |
|---------|-------------|-------------|
| `--strict` | off | **on** |
| `--target` | `es3` | latest stable ES (e.g. `es2025`) |
| `--target es5` | supported | **removed** (`es2015` minimum) |
| `--baseUrl` | supported | **removed** (use `paths` + explicit `rootDir`) |
| `--moduleResolution node10` | supported | **removed** (use `bundler` or `nodenext`) |
| `rootDir` | inferred | defaults to `.` |

### TS Version Roadmap

| Version | Role | Status |
|---------|------|--------|
| 5.9 | Current stable | Released 2025-06-17 |
| 6.0 | Last JavaScript-based release | Transition release for 7.0 prep |
| 7.0 (`tsgo`) | Native Go port | In development, type-checking ~99.6% complete |

---

## Key Features

### `import defer` Syntax (5.9)

Deferred module evaluation — module is loaded but NOT executed until you access an export:

```typescript
import * as feature from './some-feature.js';

// Module not yet evaluated - no side effects

console.log(feature.specialConstant); // NOW the module executes
```

Only namespace imports are allowed — named/default imports are errors:

```typescript
// Not allowed
import { doSomething } from 'some-module';
import defaultExport from 'some-module';

// Only this form
import * as ns from 'some-module';
```

Not downleveled by TypeScript. Requires `--module preserve` or `--module esnext`.

### `--module node20` (5.9)

Stable pinned alternative to `--module nodenext`. Models Node.js v20 behavior and won't gain new features over time. Implies `--target es2023` (unlike `nodenext` which implies `esnext`).

### Breaking: `ArrayBuffer` No Longer Supertype of `TypedArray` (5.9)

`ArrayBuffer` is no longer assignable from `TypedArray` types (including Node.js `Buffer`). Common errors:

```
Type 'Buffer' is not assignable to type 'Uint8Array<ArrayBufferLike>'.
Type 'ArrayBufferLike' is not assignable to type 'ArrayBuffer'.
```

Fixes:
- Update `@types/node` to latest
- Use explicit buffer types: `Uint8Array<ArrayBuffer>` instead of plain `Uint8Array`
- Access `.buffer` property when passing a `TypedArray` to a function expecting `ArrayBuffer`

### Type Argument Inference Changes (5.9)

Inference leak fixes may introduce new errors in generic function calls. Fix by adding explicit type arguments.

---

## TS 6.0 / 7.0 Transition Overview

**TS 6.0** is the last JavaScript-based release. There will be no 6.1. After 6.0, all development shifts to the Go-based TypeScript 7.0 (`tsgo`). 6.0 will only receive security and high-severity patches.

### Migration Tool: `ts5to6`

```bash
npx @andrewbranch/ts5to6 --fixBaseUrl your-tsconfig.json
npx @andrewbranch/ts5to6 --fixRootDir your-tsconfig.json
```

Automatically updates `baseUrl` and `rootDir` settings across project references.

### tsgo Compiler Status

`--build` mode, `--incremental`, and project references now work. Type-checking is near-complete (99.6% of error-producing test cases pass).

Current limitations:
- Emit only supports down to `es2021` (no `es2015`-`es2020` yet, no decorator downlevel)
- `--watch` may be less efficient — workaround: `nodemon` + `tsgo --incremental`
- No stable API — tools using the TypeScript Strada API won't work yet

### Architecture: Standard LSP

tsgo uses the standard Language Server Protocol instead of the custom TSServer protocol. Language service plugins that depend on the old protocol won't work.

See `references/typescript-7-transition.md` for full details on tsgo, JSDoc changes, and migration.

---

## Reference Files

| File | Contents |
|------|----------|
| [typescript-7-transition.md](references/typescript-7-transition.md) | tsgo compiler details, new defaults, migration tool, JSDoc changes, LSP architecture |
