# Configuration, Modules, and Project Migration

Batch attribution: `5.9.0`, `6.0.0`.

## Contents

- [Start new configurations intentionally](#start-new-configurations-intentionally)
- [Audit changed compiler defaults](#audit-changed-compiler-defaults)
- [Choose module and resolution modes by runtime](#choose-module-and-resolution-modes-by-runtime)
- [Remove legacy module and emit options](#remove-legacy-module-and-emit-options)
- [Replace `baseUrl`-dependent lookup](#replace-baseurl-dependent-lookup)
- [Adopt mandatory interop and strict-mode assumptions](#adopt-mandatory-interop-and-strict-mode-assumptions)
- [Update module-adjacent syntax](#update-module-adjacent-syntax)
- [Defer module evaluation](#defer-module-evaluation)
- [Compile named files without accidentally bypassing config](#compile-named-files-without-accidentally-bypassing-config)

## Start new configurations intentionally

A flagless `tsc --init` emits a short, active configuration instead of a long
commented option catalog. The generated config selects settings including:

```jsonc
{
  "compilerOptions": {
    "module": "nodenext",
    "target": "esnext",
    "types": [],
    "sourceMap": true,
    "declarationMap": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "jsx": "react-jsx",
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "noUncheckedSideEffectImports": true,
    "moduleDetection": "force",
    "skipLibCheck": true
  }
}
```

Treat this as a prescriptive starting point, not as documentation for every
option. Remove or adjust settings that do not fit the runtime and build chain.

## Audit changed compiler defaults

The compiler defaults now include:

- `strict: true`;
- `module: "esnext"`;
- a floating current-year `target`, currently `es2025`;
- `noUncheckedSideEffectImports: true`; and
- `libReplacement: false`.

Set prior values explicitly when a project must preserve old behavior. In
particular, projects using replacement library packages must opt back in with
`libReplacement: true`.

### Pin `rootDir` to preserve output layout

When compilation uses a `tsconfig.json`, an omitted `rootDir` now means the
directory containing that config. The compiler no longer derives the common
source directory in this case. Command-line compilation without a config still
uses inference.

```json
{
  "compilerOptions": {
    "rootDir": "./src",
    "outDir": "./dist"
  },
  "include": ["./src"]
}
```

Set `rootDir` explicitly before upgrading if the inferred source root formerly
determined the directory structure under `outDir`.

### Opt in to global `@types` packages

Omitting `types` now behaves like `types: []`; visible packages under
`node_modules/@types` are not automatically added to the global scope.
Declarations reached through imports are unaffected.

```json
{
  "compilerOptions": {
    "types": ["node", "jest"]
  }
}
```

Use `types: ["*"]` only as a temporary way to restore automatic enumeration
while identifying the packages the project actually needs.

## Choose module and resolution modes by runtime

### Pin Node.js 20 behavior

`module: "node20"` follows stable Node.js 20 semantics instead of acquiring
future behavior. It implies `target: "es2023"` unless the target is overridden.
By contrast, `nodenext` tracks current Node.js behavior and implies the floating
`esnext` target.

```json
{
  "compilerOptions": {
    "module": "node20"
  }
}
```

### Resolve `#/` package subpaths

Both `moduleResolution: "nodenext"` and `"bundler"` resolve package `imports`
mappings whose keys begin with `#/`, matching newer Node.js 20 releases.

```json
{
  "imports": {
    "#/*": "./dist/*"
  }
}
```

```ts
import * as utils from "#/utils.js";
```

### Combine bundler resolution with CommonJS when necessary

`moduleResolution: "bundler"` may now be paired with `module: "commonjs"`.
This is a migration path for projects that still emit CommonJS but must leave
deprecated `node` or `node10` resolution.

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "moduleResolution": "bundler"
  }
}
```

For bundled ESM, generally move toward `module: "preserve"`. For code executed
directly by Node.js, prefer `nodenext` or the pinned `node20` mode as appropriate.

## Remove legacy module and emit options

The transition is split between immediate removals and options that have only
a temporary deprecation bridge:

| Legacy setting or form | Status and action |
| --- | --- |
| `moduleResolution: "classic"` | Removed; choose a modern resolver |
| `outFile` | Removed; emit modules separately and bundle when needed |
| `module: "amd"`, `"umd"`, `"systemjs"`, or `"none"` | Rejected; choose a supported ESM or CommonJS mode |
| `amd-module` directive | Inert; remove it |
| `target: "es5"` | Deprecated during migration and removed by the native compiler; target at least ES2015 |
| Explicit `downlevelIteration` | Deprecated; remove the explicit option and test runtime behavior |
| `moduleResolution: "node"` or `"node10"` | Deprecated during migration and removed by the native compiler; use `bundler`, `nodenext`, or `node20` |

For settings that remain deprecated rather than removed,
`ignoreDeprecations: "6.0"` can temporarily unblock compilation. The native
compiler removes those settings entirely, so the suppression is not a fix.

## Replace `baseUrl`-dependent lookup

`baseUrl` is deprecated and no longer creates an implicit root for arbitrary
bare specifiers. `paths` does not require `baseUrl`; make each replacement
config-relative instead:

```json
{
  "compilerOptions": {
    "paths": {
      "@app/*": ["./src/app/*"]
    }
  }
}
```

Remove `baseUrl`. Add a `"*"` mapping only when the old catch-all bare-import
lookup was deliberate; otherwise a wildcard can mask missing dependencies.

## Adopt mandatory interop and strict-mode assumptions

`esModuleInterop` and `allowSyntheticDefaultImports` can no longer be set to
`false`; CommonJS-to-ESM interop behavior is always enabled. JavaScript
strict-mode semantics are also assumed for all code, and `alwaysStrict: false`
is no longer accepted. Remove settings that try to disable these behaviors and
repair code that relied on the old semantics.

## Update module-adjacent syntax

### Use namespaces for internal namespaces

`module Foo {}` now produces a deprecation error. Write `namespace Foo {}`:

```ts
namespace Foo {
  export const value = 1;
}
```

Ambient external-module declarations such as `declare module "package-name"`
remain supported.

### Replace import assertions with attributes

Static import assertions and the `assert` option on dynamic `import()` now
error. Use `with` attributes:

```ts
import data from "./data.json" with { type: "json" };

const later = import("./data.json", {
  with: { type: "json" }
});
```

### Replace the default-library reference directive

`/// <reference no-default-lib="true"/>` is no longer the supported control.
Use the `noLib` compiler option when no default library should be loaded, or
use `libReplacement` when supplying replacement library packages.

## Defer module evaluation

`import defer` loads the requested module and its dependencies without
evaluating them. Evaluation begins when code first accesses one of the imported
namespace's exports.

```ts
import defer * as feature from "./feature.js";

feature.start(); // evaluation starts here
```

The syntax accepts only a namespace import. TypeScript emits it unchanged, so
the compiler must use `module: "preserve"` or `"esnext"`, and the runtime or
bundler must support the syntax.

## Compile named files without accidentally bypassing config

Running `tsc file.ts` in a directory containing `tsconfig.json` now reports
TS5112 rather than silently ignoring the project config. Prefer normal project
compilation. If compiling the named files with default options is deliberate,
make that intent explicit:

```sh
tsc --ignoreConfig file.ts
```
