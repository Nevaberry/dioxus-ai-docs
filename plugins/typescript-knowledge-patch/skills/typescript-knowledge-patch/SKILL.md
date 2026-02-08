---
name: typescript-knowledge-patch
description: This skill should be used when writing TypeScript code, using "import defer", "--module node20", "tsc --init", working with ArrayBuffer types, or any TypeScript features from version 5.9 onwards.
license: MIT
metadata:
  author: Nevaberry
  version: "5.9"
---

# TypeScript 5.9+ Knowledge Patch

Claude's baseline knowledge covers TypeScript through 5.8. This skill provides features from 5.9 (May 2025) onwards.

## 5.9 (2025-05-22)

### `import defer` Syntax

New ECMAScript proposal for deferred module evaluation. The module's code isn't executed until you access one of its exports, enabling lazy loading without dynamic `import()`.

```typescript
import defer * as feature from "./some-feature.js";

// Module not executed yet
console.log("Starting up...");

// Module executes NOW when property is accessed
console.log(feature.specialConstant);
```

**Constraints:**
- Only namespace imports allowed (`import defer * as name`)
- No named imports (`import defer { x }`) or default imports
- Requires `--module preserve` or `--module esnext`

### `--module node20`

Stable module option modeling Node.js 20 behavior. Unlike `nodenext` (which tracks latest Node.js):
- Remains stable—won't change with future Node.js releases
- Implies `--target es2023` (not `esnext`)
- Supports CommonJS requiring ESM modules
- Rejects deprecated import assertions

Use `node20` for predictable behavior; use `nodenext` to track latest Node.js features.

### Updated `tsc --init` Defaults

Generated `tsconfig.json` is now minimal with modern prescriptive defaults:

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "nodenext",
    "strict": true,
    "moduleDetection": "force",
    "noUncheckedSideEffectImports": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

Commented-out options removed in favor of editor autocompletion.

### Breaking Change: `ArrayBuffer` Type Narrowing

`ArrayBuffer` no longer supertypes `TypedArray` buffer variants. Code passing typed array buffers may need updates:

```typescript
// ❌ May error in 5.9
function process(buf: ArrayBuffer) { /* ... */ }
const arr = new Uint8Array(10);
process(arr); // Error: Uint8Array not assignable to ArrayBuffer

// ✅ Fix: access the underlying buffer
process(arr.buffer);

// ✅ Or: explicitly type the TypedArray
const arr = new Uint8Array<ArrayBuffer>(10);
```

Update `@types/node` if encountering `Buffer` compatibility issues.

### Breaking Change: Type Argument Inference

Changes to prevent type variable "leaks" during inference. Some code may require explicit generic type arguments:

```typescript
// Before: type inferred (possibly incorrectly)
const result = someGenericFunction(value);

// After: may need explicit type argument
const result = someGenericFunction<ExpectedType>(value);
```

---

## TypeScript 7 (Native Port)

TS7 rewrites the compiler in Go. TS6 is the last JS-based release.
**Details:** See [references/typescript-7-transition.md](references/typescript-7-transition.md)
