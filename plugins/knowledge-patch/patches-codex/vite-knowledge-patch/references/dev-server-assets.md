# Development Server, Globs, and Assets

## Top-level input integration

Configured top-level inputs participate in development-server setup (since
8.1.5-8.2.1). Vite adds them to the `server.fs.allow` calculation and resolves
them through plugins.

This means plugin-provided entries can participate in input resolution while
remaining permitted by the development server's filesystem checks. When a
custom input fails during development, inspect both plugin resolution and the
computed filesystem allowance instead of bypassing the safety check manually.

## Ephemeral development-server ports

Set `server.port` to `0` to ask Vite to select a random available port (since
8.1.5-8.2.1):

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  server: { port: 0 },
})
```

This is useful for isolated tests and concurrent development servers. Consumers
must discover the selected address from the running server rather than assume
a fixed port.

## Case-insensitive glob matching

Set `caseSensitive: false` on `import.meta.glob` to match filenames regardless
of case (since 8.1.0):

```ts
const modules = import.meta.glob('./dir/module*.js', {
  caseSensitive: false,
})
```

Use the option deliberately when the application treats filename case as
insignificant. The explicit setting makes behavior clear across filesystems
with different case semantics.

## Custom HTML asset sources

Use `html.additionalAssetSources` to extend asset discovery to custom elements
or nonstandard attributes (since 8.1.0):

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

URLs found through these declarations enter Vite's normal asset-processing
pipeline. Prefer this configuration to maintaining a separate transform for
attributes that only need standard asset handling.
