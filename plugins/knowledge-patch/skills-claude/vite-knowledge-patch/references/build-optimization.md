# Builds and Dependency Optimization

## Keep Chunk Hash Changes Local With Import Maps

Since `8.1.0`, the experimental `build.chunkImportMap` option uses an import
map to stop a changed chunk hash from cascading into every chunk that imports
it. The result is better cache reuse across deployments when only part of the
chunk graph changes.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: { chunkImportMap: true },
})
```

`build.chunkImportMap` is currently incompatible with
`experimental.renderBuiltUrl`. Do not enable both in the same build.

## Combine Chunk Import Maps With Shared Plugins

In `8.1.5-8.2.1`, client chunk import maps work with `sharedPlugins: true`.
Framework integrations can therefore combine shared plugin instances with
`build.chunkImportMap`.

Treat this as an interoperability improvement to the chunk-import-map feature;
it does not remove the incompatibility with `experimental.renderBuiltUrl`.

## Trial the Rolldown-Backed Package

Starting with `7.0.0`, the `rolldown-vite` package can replace `vite` as a
drop-in way to try the future Rolldown-based bundler before it becomes the
default.

Use the alternate package for an evaluation, then exercise the project's
plugins and production build before adopting it. Drop-in package replacement
does not imply that every plugin has identical behavior under the future
bundler.
