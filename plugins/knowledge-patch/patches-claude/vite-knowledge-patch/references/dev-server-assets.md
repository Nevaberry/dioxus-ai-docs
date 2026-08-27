# Development Server, HMR, Globs, and Assets

## Enable Experimental Bundled Development

Since `8.1.0`, large browser applications can opt into bundled ESM during
development while retaining HMR. Bundling reduces per-module request overhead
that can slow startup and reloads.

Enable the limited experimental mode from the CLI:

```sh
vite --experimental-bundle
```

Or enable it in Vite configuration:

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  experimental: { bundledDev: true },
})
```

The mode is still experimental and limited, so verify project and framework
development behavior before making it the team default.

## Accept Worker HMR in Bundled Development

In `8.1.5-8.2.1`, experimental bundled development accepts HMR updates for
worker files. Worker changes can participate in hot updates instead of using
the earlier fallback behavior.

This capability applies to the bundled development mode; it does not make that
mode non-experimental.

## Use an Ephemeral Development-Server Port

In `8.1.5-8.2.1`, `server.port: 0` asks Vite to choose a random available
port. This is useful for isolated tests and concurrent development servers
that should not contend for a fixed port.

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  server: { port: 0 },
})
```

## Resolve Top-Level Inputs Through Plugins

In `8.1.5-8.2.1`, configured top-level inputs are included in the development
server's `server.fs.allow` calculation. Vite also resolves those inputs
through plugins.

Plugin-provided entries can consequently participate in input resolution and
remain permitted by the development server's filesystem checks. When a custom
input is unexpectedly denied or skipped, verify that it is configured as a
top-level input and inspect the plugin that resolves it.

## Match Globs Without Case Sensitivity

Since `8.1.0`, set `caseSensitive: false` on `import.meta.glob` to match
filenames regardless of case:

```ts
const modules = import.meta.glob('./dir/module*.js', {
  caseSensitive: false,
})
```

Use the option deliberately when the application wants case-insensitive
matching rather than relying on host-filesystem behavior.

## Add Custom HTML Asset Sources

Since `8.1.0`, `html.additionalAssetSources` extends asset discovery to custom
elements and nonstandard attributes. Referenced files then enter Vite's normal
asset-processing pipeline.

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

Map each element name to the attribute or attributes that contain asset URLs.
