---
name: vite-knowledge-patch
description: Vite
version: "8.1.0"
license: MIT
metadata:
  author: Nevaberry
---


# Vite Knowledge Patch

Use this skill when configuring, upgrading, extending, or troubleshooting
Vite. Inspect the installed Vite and Node.js versions before applying
version-sensitive guidance, then open the topic reference that matches the
work at hand.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Builds and Dependency Optimization](references/build-optimization.md) | Chunk import maps, cache reuse, shared plugins, and the Rolldown trial package |
| [Development Server and Assets](references/dev-server-assets.md) | Bundled development, worker HMR, ports, top-level inputs, globs, and HTML assets |
| [Migration and Runtime Requirements](references/migration-requirements.md) | Node.js support, browser targets, Vitest compatibility, and removed APIs |
| [Plugin and Framework APIs](references/plugin-api.md) | Environment API and coordinated multi-environment builds |
| [Resolution and Module Interoperability](references/resolution-modules.md) | ESM-only packaging, CommonJS loading, and direct WebAssembly ESM imports |
| [Transforms, TypeScript, and Styles](references/transforms-styles.md) | Lightning CSS interoperability and Sass legacy API removal |

## Start With Upgrade Blockers

### Verify the Exact Node.js Runtime

Before upgrading a project or CI image, inspect `node --version`.

- Vite 7 requires Node.js 20.19+ or 22.12+.
- Node.js 18 is below that floor.
- Node.js 21 was already unsupported by Vite 6.
- Do not treat every Node.js 20 or 22 release as sufficient; the minor
  versions matter.

The newer minimums provide unflagged `require(esm)`. Vite can therefore be
distributed as ESM-only while keeping its JavaScript API loadable from
CommonJS.

### Remove Deleted APIs

Search an upgrading project for both deprecated interfaces:

```sh
rg "splitVendorChunkPlugin|legacy API" .
```

Vite 7 removes:

- Sass legacy API support.
- `splitVendorChunkPlugin`.

Migrate either dependency before expecting the upgraded build to work.

### Recheck the Default Browser Target

The default `build.target` is now `'baseline-widely-available'`, fixed for
each Vite major, rather than `'modules'`. In Vite 7, the default means:

| Browser | Minimum |
| --- | --- |
| Chrome | 107 |
| Edge | 107 |
| Firefox | 104 |
| Safari | 16.0 |

Set `build.target` explicitly when the application's browser contract differs
from those defaults. Leaving the target unset does not preserve the previous
output compatibility.

### Pair Vite With a Supported Vitest

Vite 7 support begins with Vitest 3.2. Upgrade an older Vitest installation
alongside Vite instead of treating that combination as an application bug.

## High-Value Configuration

### Try Bundled Development for Large Browser Applications

Experimental bundled development serves bundled ESM while retaining HMR. It
can reduce the per-module request overhead that slows startup and reloads in
large browser applications.

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

The mode remains experimental and limited. Validate development behavior
before adopting it for the whole team. Worker-file changes can participate in
HMR when using the newer bundled-development implementation.

### Stabilize Chunk Relationships With an Import Map

`build.chunkImportMap` uses an import map so a changed chunk hash does not
cascade into every importing chunk. This can preserve more cached files
between deployments.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: { chunkImportMap: true },
})
```

Do not combine this option with `experimental.renderBuiltUrl`; they are
incompatible. Client chunk import maps also work with `sharedPlugins: true`,
so framework integrations can share plugin instances while using the option.

### Import WebAssembly Exports Directly

WebAssembly ESM integration supports direct named exports from `.wasm` files:

```ts
import { add } from './add.wasm'

console.log(add(1, 2))
```

A `?init` wrapper is not required for this direct ESM form.

### Extend Asset Discovery for Custom HTML

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

### Match Globbed Files Without Case Sensitivity

Pass `caseSensitive: false` to `import.meta.glob` when filename case should
not affect the match:

```ts
const modules = import.meta.glob('./dir/module*.js', {
  caseSensitive: false,
})
```

### Use a Random Available Development Port

Set `server.port` to `0` for an ephemeral port. This is useful for isolated
tests and concurrent development servers.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  server: { port: 0 },
})
```

### Use the Expanded Lightning CSS Integration

With `css.transformer: 'lightningcss'`, CSS files can import external CSS
files and plugins can register file dependencies. These capabilities close
two interoperability gaps with the PostCSS transformer.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  css: { transformer: 'lightningcss' },
})
```

## Framework and Plugin Integration

The experimental Environment API lets framework and plugin authors implement
development integrations that more closely match production. Normal
single-client SPA behavior is unchanged, and existing custom SSR applications
remain backward compatible.

For coordinated build work, the API exposes a `buildApp` hook so plugins can
coordinate builds across multiple environments. Keep experimental integration
code isolated behind framework or plugin boundaries.

Configured top-level inputs are included in the development server's
`server.fs.allow` calculation and resolved through plugins. Plugin-provided
entries can therefore participate in input resolution while remaining
permitted by filesystem checks.

To evaluate the future Rolldown-based bundler, replace the `vite` package with
`rolldown-vite`. It is a drop-in trial package for testing the future bundler
before it becomes the default. Test plugin and build behavior before
committing to it.

## Working Checklist

1. Verify the exact Node.js minor version used locally and in CI.
2. Search for the removed Sass and chunk-splitting interfaces.
3. Decide whether the default browser target matches the product contract.
4. Upgrade Vitest to a supported pairing when necessary.
5. Keep experimental options explicit and respect their incompatibilities.
6. Check dev-server filesystem access when plugins resolve top-level inputs.
7. Open the relevant reference file before editing config or plugin code.
