# Configuration, tooling, and APIs

## Typed configuration imports (5.2.0)

In the Astro 5.2 experimental form, `experimental.serializeConfig` creates
typed `astro:config/client` and `astro:config/server` virtual modules. Only a
safe subset is exposed to client code.

```js
export default defineConfig({
  trailingSlash: 'always',
  experimental: { serializeConfig: true },
});
```

```ts
import { trailingSlash } from 'astro:config/client';
```

The virtual modules are stable and need no flag from 5.7.0.

## Dev and preview host allowlists (5.4.0)

`server.allowedHosts` restricts requests by `Host` header and helps prevent DNS
rebinding. The dev and preview commands also accept a comma-separated
`--allowed-hosts=host1,host2`. Allow only domains under project control.

```js
export default defineConfig({
  server: {
    allowedHosts: [
      'hello.world.example.local',
      'hello.example.local',
    ],
  },
});
```

Adapter-provided preview entrypoints receive the same list in their options
object from 6.2.0.

## Programmatic config and builds (5.4.0)

`mergeConfig(base, partial)` layers configuration using integration-style
`updateConfig` rules. `validateConfig(value)` validates configuration and
fills defaults.

The programmatic `build()` function accepts a second `BuildOptions` argument:
`devOutput` produces a development-style build and defaults to `false`;
`teardownCompiler` controls compiler-WASM cleanup and defaults to `true`.

```js
import { build } from 'astro';
import { mergeConfig, validateConfig } from 'astro/config';

await build({}, {
  devOutput: true,
  teardownCompiler: false,
});
```

## Style and script order (5.5.0)

Astro normally reverses multiple generated `<style>` and `<script>` tags.
`experimental.preserveScriptOrder` emits both in definition order. Reorder any
code that previously compensated for reversal when enabling the flag.

```js
export default defineConfig({
  experimental: { preserveScriptOrder: true },
});
```

## Chrome DevTools workspace (5.13.0)

`experimental.chromeDevtoolsWorkspace` makes the dev server register the
project as a Chrome DevTools workspace source, so edits in the Sources panel
can be saved to local files.

```js
export default defineConfig({
  experimental: { chromeDevtoolsWorkspace: true },
});
```

## Interactive preview shortcuts (5.16.0)

In a terminal running `astro preview`, type `o` followed by Enter to open the
site in a browser, or `q` followed by Enter to stop the server.

## Dev toolbar placement (5.17.0)

Set `devToolbar.placement` to establish a project default that avoids fixed
page UI. Individual developers can still override it through the toolbar.

```js
export default defineConfig({
  devToolbar: { placement: 'bottom-left' },
});
```

## Rust compiler preview (6.0.0)

Install `@astrojs/compiler-rs` and enable `experimental.rustCompiler` to try
the Rust `.astro` compiler under Astro 6.

```sh
npm install @astrojs/compiler-rs
```

```js
export default defineConfig({
  experimental: { rustCompiler: true },
});
```

The Astro 7 toolchain makes Rust the only compiler, so remove the flag when
upgrading.

## Experimental structured logging (6.2.0)

`experimental.logger` accepts `logHandlers.json()` or
`{ entrypoint: '@org/custom-logger' }`. A custom module default-exports a
factory returning an `AstroLoggerDestination`; its `write()` method receives
`AstroLoggerMessage` records and can filter with `matchesLevel()` from
`astro/logger`.

```js
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  experimental: { logger: logHandlers.json() },
});
```

The dev, sync, and build commands can select JSON output with
`--experimentalJson` in this experimental form.

## JSX-style HTML compression (6.2.0)

`compressHTML: 'jsx'` applies JSX whitespace rules consistently to `.astro`
and `.tsx`: indented multiline text joins with spaces, while `<pre>` content
is preserved.

```js
export default defineConfig({
  compressHTML: 'jsx',
});
```

## Managed background development (7.0.0)

`astro dev --background` waits for readiness, prints the server URL and PID,
then detaches. Repeated starts use the lockfile-managed running instance.
`/_astro/status` is a readiness endpoint. Manage it with:

```sh
astro dev status
astro dev logs
astro dev stop
```

Detected automation environments can enable background mode automatically.

## Stable structured logging (7.0.0)

Move `experimental.logger` to top-level `logger` and replace
`--experimentalJson` with `--json`. Detected background automation mode also
enables JSON output automatically. `logHandlers.compose()` fans each record
out to multiple destinations.

```js
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  logger: logHandlers.compose(
    logHandlers.console(),
    logHandlers.json(),
  ),
});
```

## Background preview (7.0.1-7.2.4)

`astro preview --background` also waits for readiness and detaches. Manage it
like the background dev server:

```sh
astro preview status
astro preview logs --follow
astro preview stop
```

Detected automation environments enable background preview automatically. Set
`ASTRO_PREVIEW_BACKGROUND=0` to opt out.

## Custom logger paths and runtime typing (7.0.1-7.2.4)

`logger.entrypoint` accepts URL objects and project-relative `./` or `../`
paths; relative paths resolve from the project root. Package specifiers and
absolute paths remain valid.

```js
export default defineConfig({
  logger: { entrypoint: './src/logger.js' },
});
```

Use the public `AstroRuntimeLogger` interface to type logger functions invoked
at runtime.

## Parallel unmanaged dev servers (7.0.1-7.2.4)

`astro dev --ignore-lock` starts a foreground server without reading or
writing the project lock. It cannot combine with `--background`, automatic
background mode, or `--force`. The `status`, `logs`, and `stop` commands do not
manage this untracked process.

## Package-manager detection (7.0.1-7.2.4)

Astro install commands consider the `devEngines` field in `package.json` when
detecting the project's package manager.
