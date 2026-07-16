# Configuration, tooling, and APIs

## Typed configuration imports

`astro:config/client` and `astro:config/server` expose typed project configuration throughout an Astro project while the client module includes only a safe subset (`5.2.0`). They began behind `experimental.serializeConfig` and became stable without the flag in `5.7.0`.

```ts
import { trailingSlash } from 'astro:config/client';
```

## Programmatic configuration

`astro/config` exports `mergeConfig(base, partial)` and `validateConfig(value)` (`5.4.0`). `mergeConfig` layers a partial configuration with the same rules used by an integration's `updateConfig`; `validateConfig` validates a candidate and fills defaults.

The `build()` API accepts a second `BuildOptions` argument (`5.4.0`):

- `devOutput` creates a development-style build and defaults to `false`.
- `teardownCompiler` controls cleanup of the compiler WASM instance and defaults to `true`.

```js
import { build } from 'astro';

await build({}, {
  devOutput: true,
  teardownCompiler: false,
});
```

## Development server security

`server.allowedHosts` restricts `astro dev` and `astro preview` responses to requests whose `Host` header matches a configured hostname, reducing DNS-rebinding exposure (`5.4.0`). The CLI form is `--allowed-hosts=host1,host2`. Allow only domains under project control.

Adapter preview entrypoints receive the same `allowedHosts` value and should enforce it in their own servers (`6.2.0`).

## Generated tag order

Astro normally reverses multiple `<style>` and `<script>` tags in generated HTML. `experimental.preserveScriptOrder` emits both tag types in definition order (`5.5.0`). Remove any compensating source-order reversal when enabling it.

## Developer tools

### Chrome workspace

`experimental.chromeDevtoolsWorkspace` configures the dev server as a Chrome DevTools workspace source, allowing edits in the Sources panel to be written back to local project files (`5.13.0`).

### Dev toolbar placement

`devToolbar.placement` defines a project-wide default toolbar position so it does not overlap fixed UI (`5.17.0`). Individual developers can still override the position through the toolbar.

```js
export default defineConfig({
  devToolbar: { placement: 'bottom-left' },
});
```

### Preview shortcuts

In the terminal attached to `astro preview`, enter `o` to open the site in a browser or `q` to stop the preview server (`5.16.0`).

## Compiler selection

Astro 6 can try the Rust-based `.astro` compiler by installing `@astrojs/compiler-rs` and enabling `experimental.rustCompiler` (`6.0.0`):

```sh
npm install @astrojs/compiler-rs
```

```js
export default defineConfig({
  experimental: { rustCompiler: true },
});
```

When testing the Astro 7 alpha described in `6.2.0`, the Rust compiler became the default and only compiler, so the experimental flag had to be removed.

## HTML compression

`compressHTML: 'jsx'` strips whitespace with JSX rules for consistent output between `.astro` and `.tsx` (`6.2.0`). Indented multiline text is joined with spaces, while content inside `<pre>` is preserved.

```js
export default defineConfig({
  compressHTML: 'jsx',
});
```

## Structured and custom logging

### Preview API

`experimental.logger` accepts the built-in JSON handler or a package-backed custom handler (`6.2.0`):

```js
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  experimental: { logger: logHandlers.json() },
});
```

The equivalent CLI switch was `--experimentalJson` for `astro dev`, `astro sync`, and `astro build`. A custom declaration uses `logger: { entrypoint: '@org/custom-logger' }`. The module default-exports a factory returning an `AstroLoggerDestination`; its `write()` method receives `AstroLoggerMessage` values and can use `matchesLevel()` from `astro/logger` for filtering.

### Stable API

Astro 7 moves `logger` to the top level and replaces `--experimentalJson` with `--json` (`7.0.0`). `logHandlers.compose()` sends messages to several destinations:

```js
import { defineConfig, logHandlers } from 'astro/config';

export default defineConfig({
  logger: logHandlers.compose(
    logHandlers.console(),
    logHandlers.json(),
  ),
});
```

JSON logging is selected automatically when the managed background server is activated by a recognized automation environment.

## Managed background development server

`astro dev --background` waits for readiness, prints the URL and process ID, and detaches (`7.0.0`). Repeated starts return the lockfile-managed existing instance. Use the readiness endpoint at `/_astro/status` or the management commands:

```sh
astro dev status
astro dev logs
astro dev stop
```
