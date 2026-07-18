---
name: vite-knowledge-patch
description: Vite
license: MIT
version: 8.1.0
metadata:
  author: Nevaberry
---

# Vite Knowledge Patch

Use this skill when configuring, upgrading, extending, or troubleshooting Vite.
Start with the migration checks, then open the topic reference that matches the
work at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [Builds and dependency optimization](references/build-optimization.md) | Bundled development, chunk import maps, and the Rolldown-backed package |
| [Development server and assets](references/dev-server-assets.md) | HMR-aware bundled development, case-insensitive globs, and custom HTML asset sources |
| [Migration and runtime requirements](references/migration-requirements.md) | Node.js support, browser targets, Vitest compatibility, and removed APIs |
| [Plugin and framework APIs](references/plugin-api.md) | Environment API and coordinated multi-environment builds |
| [Resolution and module interoperability](references/resolution-modules.md) | ESM-only packaging, CommonJS loading, and direct WebAssembly ESM imports |
| [Transforms, TypeScript, and styles](references/transforms-styles.md) | Lightning CSS interoperability and Sass legacy API removal |

## Upgrade blockers first

### Check the Node.js runtime

Before upgrading a project or CI image, inspect `node --version`.

- Vite 7 requires Node.js 20.19+ or 22.12+.
- Node.js 18 is below that floor.
- Node.js 21 was already unsupported by Vite 6.
- Do not treat an arbitrary Node.js 20 or 22 release as sufficient; the minor
  versions matter.

The newer minimums provide unflagged `require(esm)`. Vite can therefore be
distributed as ESM-only while keeping its JavaScript API loadable from
CommonJS.

### Remove deleted APIs

Search an upgrading project for both of these before changing the Vite major:

```sh
rg "splitVendorChunkPlugin|legacy API" .
```

Vite 7 removes:

- Sass legacy API support.
- `splitVendorChunkPlugin`.

Migrate either dependency before expecting the upgraded build to work.

### Recheck the default browser target

The default `build.target` is now `'baseline-widely-available'`, fixed for each
Vite major, rather than `'modules'`. In Vite 7, that default means Chrome 107,
Edge 107, Firefox 104, and Safari 16.0.

Set `build.target` explicitly when the application's browser contract differs
from those defaults. Do not assume that leaving the target unset preserves the
previous output compatibility.

### Pair Vite with a supported Vitest

Vite 7 support begins with Vitest 3.2. Upgrade older Vitest installations when
upgrading Vite rather than diagnosing the combination as an application bug.

## High-value configuration

### Try bundled development for large browser applications

The experimental bundled development mode serves bundled ESM while retaining
HMR. It can reduce per-module request overhead that slows startup and reloads
in large applications.

Enable it from the CLI:

```sh
vite --experimental-bundle
```

Or enable it in configuration:

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  experimental: { bundledDev: true },
})
```

The mode remains experimental and limited. Validate framework integration and
development behavior before adopting it for the whole team.

### Stabilize chunk relationships with an import map

`build.chunkImportMap` prevents a changed chunk hash from cascading into every
chunk that imports it. This can preserve more cached files between deployments.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: { chunkImportMap: true },
})
```

Do not combine this option with `experimental.renderBuiltUrl`; the two are
currently incompatible.

### Import WebAssembly exports directly

WebAssembly ESM integration supports direct named exports from `.wasm` files:

```ts
import { add } from './add.wasm'

console.log(add(1, 2))
```

A `?init` wrapper is not required for this direct ESM form.

### Extend asset discovery for custom HTML

Use `html.additionalAssetSources` when custom elements or nonstandard
attributes contain asset URLs:

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  html: {
    additionalAssetSources: {
      'html-import': { srcAttributes: 'src' },
      img: { srcAttributes: ['data-src-dark', 'data-src-light'] },
    },
  },
})
```

Those files then enter Vite's normal asset-processing pipeline.

### Match globbed files without case sensitivity

Pass `caseSensitive: false` to `import.meta.glob` when filename case should not
affect the match:

```ts
const modules = import.meta.glob('./dir/module*.js', {
  caseSensitive: false,
})
```

### Use the expanded Lightning CSS integration

With `css.transformer: 'lightningcss'`, CSS files can import external CSS files
and plugins can register file dependencies. These capabilities close two prior
compatibility gaps with the PostCSS transformer.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  css: { transformer: 'lightningcss' },
})
```

## Framework and bundler integration

The experimental Environment API lets framework and plugin authors implement
development integrations that more closely match production. Normal
single-client SPA behavior is unchanged, and existing custom SSR applications
remain backward compatible.

For coordinated build work, the API exposes a `buildApp` hook so plugins
can coordinate builds across multiple environments. Treat the API as
experimental and keep integration code isolated behind framework or plugin
boundaries.

To evaluate the future Rolldown-based bundler, replace the `vite` package with
`rolldown-vite`. It is intended as a drop-in trial package before Rolldown
becomes the default; test plugin and build behavior before committing to it.

## Working checklist

1. Verify the exact Node.js minor version used locally and in CI.
2. Search for removed Sass and chunk-splitting APIs.
3. Decide whether the default browser target matches the product contract.
4. Upgrade Vitest to a supported pairing when necessary.
5. Keep experimental options explicit and validate their incompatibilities.
6. Open the relevant reference file before editing config or plugin code.
