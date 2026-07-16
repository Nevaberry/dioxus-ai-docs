# Builds and Dependency Optimization

## Bundled development

Large browser applications can opt into experimental bundled ESM during
development while retaining HMR (since 8.1.0). Bundling reduces the per-module
request overhead that can otherwise slow initial startup and reloads.

Enable it at the command line:

```sh
vite --experimental-bundle
```

Or in Vite configuration:

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  experimental: {
    bundledDev: true,
  },
})
```

This mode is still experimental and limited. Confirm that the application's
framework, plugins, HMR boundaries, startup, and reload behavior work as
expected before adopting it broadly.

## Chunk import maps

Enable `build.chunkImportMap` to use an import map for built chunks (since
8.1.0):

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    chunkImportMap: true,
  },
})
```

Without this mechanism, changing a chunk hash can change the import reference
embedded in every importing chunk, cascading new hashes through the graph. The
import map isolates that relationship and improves cache reuse across
deployments.

`build.chunkImportMap` is currently incompatible with
`experimental.renderBuiltUrl`. Choose one of the two mechanisms rather than
combining them.

## Trying the Rolldown-based bundler

The `rolldown-vite` package is a drop-in replacement for `vite` that exposes the
future Rolldown-powered implementation (since 7.0.0). It allows projects to
exercise that bundler before it becomes Vite's default.

Treat the package swap as an evaluation step: run the project's builds and
plugin integration checks even though the package is designed to be drop-in.
