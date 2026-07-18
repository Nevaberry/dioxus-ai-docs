---
name: typescript-knowledge-patch
description: TypeScript
license: MIT
version: 7.0.0
metadata:
  author: Nevaberry
---

# TypeScript Knowledge Patch

Use this guide when upgrading compiler configuration, choosing module settings,
adopting the native compiler, or repairing newly exposed type and JavaScript
checking errors. Follow the linked references when a migration needs all edge
cases and compatibility details.

## Reference index

| Reference | Topics |
| --- | --- |
| [Configuration, modules, and project migration](references/configuration-and-modules.md) | Generated configs, changed defaults, module modes, resolution, removed options, syntax migrations, and explicit-file compilation |
| [JavaScript and JSDoc migration](references/javascript-and-jsdoc.md) | Parameter checking, removed JSDoc forms, constructor functions, variadics, overloads, expandos, CommonJS, and declaration emit |
| [Native compiler and tooling](references/native-compiler-and-tooling.md) | Stable and preview packages, compiler API compatibility, editor support, emit/watch limits, worker controls, build concurrency, and hover tooling |
| [Types and standard libraries](references/types-and-standard-library.md) | Buffer typing, inference changes, ES2025, Temporal, collection upserts, iterable DOM declarations, and Unicode template inference |

## Migration-first quick reference

### Re-pin configuration that relied on old defaults

Compiler defaults now favor modern, strict projects. Audit every inherited or
omitted option before accepting an upgrade:

| Setting | New behavior | Typical migration action |
| --- | --- | --- |
| `strict` | Defaults to `true` | Fix strictness errors or explicitly preserve the old value temporarily |
| `module` | Defaults to `esnext` | Choose a runtime-appropriate mode explicitly |
| `target` | Floats with the current year and is currently `es2025` | Pin a target when reproducible output matters |
| `noUncheckedSideEffectImports` | Defaults to `true` | Add declarations for intentional side-effect-only imports |
| `libReplacement` | Defaults to `false` | Set `true` only when replacement library packages are required |
| `rootDir` | Defaults to the `tsconfig.json` directory | Set the previous source root explicitly to preserve output paths |
| `types` | Omission behaves like `[]` | List global packages such as `node` or `jest` explicitly |

Imported declarations still work when `types` is empty. Use `types: ["*"]` only
as a temporary compatibility bridge for automatic global `@types` discovery.

### Replace retired resolution and emit choices

| Old choice | Replacement or action |
| --- | --- |
| `moduleResolution: "node"` or `"node10"` | Use `bundler`, `nodenext`, or `node20` |
| Classic module resolution | Migrate; it is removed |
| `module: "amd"`, `"umd"`, `"systemjs"`, or `"none"` | Move to a supported ESM or CommonJS strategy |
| `outFile` | Use per-module output and a bundler when one artifact is needed |
| `target: "es5"` | Target at least ES2015 |
| Explicit `downlevelIteration` | Remove the deprecated setting and validate emitted iteration behavior |
| `baseUrl` as a bare-import search root | Remove it and put config-relative prefixes directly in `paths` |

`ignoreDeprecations: "6.0"` is only a temporary bridge for options that are
still deprecated rather than removed. Do not build a long-term configuration
around it.

### Update syntax whose legacy form now errors

```ts
namespace Utilities {
  export const ready = true;
}

import data from "./data.json" with { type: "json" };
const lazyData = import("./data.json", { with: { type: "json" } });
```

- Replace `module Foo {}` with `namespace Foo {}`. Ambient
  `declare module "name"` declarations remain supported.
- Replace static and dynamic import assertions with `with` attributes.
- Replace `/// <reference no-default-lib="true"/>` with `noLib` or
  `libReplacement` configuration.
- Remove attempts to disable `esModuleInterop`,
  `allowSyntheticDefaultImports`, or strict-mode semantics.

### Preserve project layout and config intent

An omitted `rootDir` in a project config now means the config directory, not
the inferred common source directory. Pin it when using `outDir`:

```json
{
  "compilerOptions": {
    "rootDir": "./src",
    "outDir": "./dist"
  },
  "include": ["./src"]
}
```

Running `tsc file.ts` beside a `tsconfig.json` reports TS5112 because named
files would otherwise bypass the config. Use the project normally, or use
`tsc --ignoreConfig file.ts` when default compilation is intentional.

### Repair typed-array and backing-buffer errors

Do not assume that a typed array or Node.js `Buffer` is an `ArrayBuffer`.
Update `@types/node` first for `Buffer` failures, then make the backing type or
conversion explicit:

```ts
declare function consume(value: ArrayBuffer): void;

const bytes: Uint8Array<ArrayBuffer> = new Uint8Array([1, 2, 3]);
consume(bytes.buffer);
```

Review APIs mentioning `ArrayBufferLike`, `BufferSource`, or
`Uint8Array<ArrayBufferLike>` rather than hiding the error with a cast.

### Keep API-dependent tools on a compatible compiler

The native compiler does not implement the JavaScript `typescript` compiler
API. Type-check with the native compiler, but keep the compatibility package
for linters, formatters, or extensions that import that API:

```json
{
  "devDependencies": {
    "@typescript/native": "npm:typescript@^7.0.2",
    "typescript": "npm:@typescript/typescript6@^6.0.2"
  }
}
```

This alias gives API-dependent tools the package name they expect while the
native compiler remains separately addressable.

## Module selection

| Project shape | Recommended settings |
| --- | --- |
| Node.js 20 with pinned semantics | `module: "node20"`; the implied target is `es2023` unless overridden |
| Node.js tracking current behavior | `module: "nodenext"`; its implied target floats at `esnext` |
| Bundled ESM | Prefer `module: "preserve"` with `moduleResolution: "bundler"` |
| CommonJS during a resolver migration | `module: "commonjs"` with `moduleResolution: "bundler"` is supported |

Both `nodenext` and `bundler` resolution understand package `imports` entries
beginning with `#/`:

```json
{
  "imports": { "#/*": "./dist/*" }
}
```

## Deferred module evaluation

`import defer` loads a module graph but postpones evaluation until code first
reads an export. It accepts only a namespace import and is emitted unchanged:

```ts
import defer * as feature from "./feature.js";

feature.start(); // first export access triggers evaluation
```

Use `module: "preserve"` or `"esnext"`, and confirm that the runtime or bundler
supports the emitted syntax.

## Standard-library additions

- `target` and `lib` accept `es2025`; the target adds no syntax transforms,
  while its library contains APIs including `RegExp.escape`.
- `Temporal` declarations are available through an `esnext` target, the
  `esnext` library, or the granular `esnext.temporal` library.
- `Map` and `WeakMap` expose `getOrInsert` and `getOrInsertComputed` in
  `esnext`; the computed callback runs only for a missing key.
- `lib.dom.d.ts` now contains iterable and async-iterable DOM declarations,
  so listing `dom.iterable` or `dom.asynciterable` is unnecessary.

## Inference checks

If an upgrade changes a generic result, first add explicit type arguments or
annotations. Inference now prevents type variables from escaping their scope,
and methods that do not use `this` can contribute to inference earlier.

For migration comparisons, `tsc --stableTypeOrdering` aligns type and property
ordering with the native checker. It can slow checking substantially, so use it
diagnostically and repair order-sensitive inference rather than enabling it by
default.

## Native build controls

- `--checkers N` sets experimental checker workers; the default is `4`.
  Use a fixed count for reproducibility or `--checkers 1` to serialize checking.
- `--builders N` sets concurrent project builds under `--build`. Its
  concurrency multiplies with `--checkers`, so budget memory for the product.
- `--singleThreaded` disables parallel parsing, checking, and emit.

Use [Native compiler and tooling](references/native-compiler-and-tooling.md)
for package selection, preview limitations, nightly installs, and editor
settings.

## JavaScript migration checkpoint

JavaScript checking now follows TypeScript-shaped rules more closely. Treat
`any`, `unknown`, and `undefined` parameters as required unless the source makes
them optional; use `typeof` when a JSDoc type refers to a value; replace legacy
constructor functions with classes; and use real rest parameters for variadic
functions. See [JavaScript and JSDoc migration](references/javascript-and-jsdoc.md)
before switching a JavaScript-heavy project to the native checker.
