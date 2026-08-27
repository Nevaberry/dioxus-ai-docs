# Builds and Dependency Optimization

## Experimental bundled development

Large browser applications can opt into bundled ESM during development while
retaining HMR (since 8.1.0). Bundling reduces the per-module request overhead
that can slow startup and reloads in applications with large module graphs.

Enable the mode from the CLI:

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

The feature remains experimental and limited. Validate framework integration,
startup, reloads, and HMR behavior against the project's real development
workflow before enabling it broadly.

## Worker HMR in bundled development

Bundled development accepts HMR updates for worker files (since
8.1.5-8.2.1). Worker edits can participate in hot updates rather than needing
the previous fallback behavior.

Exercise both ordinary module updates and worker updates when qualifying
bundled development. Worker HMR belongs to the experimental bundled mode and
does not make the mode generally stable.

## Chunk import maps

Set `build.chunkImportMap` to use an import map for built chunks (since 8.1.0):

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: { chunkImportMap: true },
})
```

Without this indirection, a changed chunk hash can cascade into every importing
chunk. The import map can keep those importer files stable and improve cache
reuse across deployments.

`build.chunkImportMap` is experimental and currently incompatible with
`experimental.renderBuiltUrl`. Do not enable both in the same build.

## Chunk import maps with shared plugins

Client chunk import maps work with `sharedPlugins: true` (since
8.1.5-8.2.1). Framework integrations can therefore share plugin instances and
still enable `build.chunkImportMap` for client builds.

Test the shared plugin lifecycle together with generated client chunk
references; this combination connects framework-level plugin coordination with
an experimental build feature.

## Trying the Rolldown-powered package

The `rolldown-vite` package can replace `vite` as a drop-in way to try the
future Rolldown-based bundler before it becomes the default (since 7.0.0).

Treat the package swap as an evaluation. Run the normal production build and
exercise framework and plugin behavior before committing the team to it,
because drop-in packaging does not guarantee that every integration behaves
identically.
