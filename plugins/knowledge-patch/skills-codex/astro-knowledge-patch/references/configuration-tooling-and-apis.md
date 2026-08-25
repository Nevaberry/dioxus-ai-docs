# Configuration, tooling, and APIs

## Typed configuration imports

Astro 5.2.0 introduced typed `astro:config/client` and `astro:config/server` imports behind `experimental.serializeConfig`; the client module exposes only a safe subset. They became stable in 5.7.0, so remove the flag.

## Host allowlists

Since 5.4.0, `server.allowedHosts` limits dev and preview responses by `Host` header to reduce DNS-rebinding risk. The CLI equivalent for either command is `--allowed-hosts=host1,host2`. Allow only controlled domains. Since 6.2.0, adapter preview entrypoints receive this list too.

## Programmatic configuration and builds

Since 5.4.0, `mergeConfig(base, partial)` applies integration-style `updateConfig` layering, while `validateConfig(value)` validates and fills defaults.

The same batch adds a second `BuildOptions` argument to `build(config, options)`: `devOutput` creates a development-style build and defaults to `false`; `teardownCompiler` controls cleanup of compiler WASM and defaults to `true`.

## HTML, style, and script output

Astro normally reverses multiple generated `<style>` and `<script>` tags. Since 5.5.0, `experimental.preserveScriptOrder` emits both in definition order; reorder code that compensated for reversal.

Since 6.2.0, `compressHTML: 'jsx'` strips whitespace using JSX rules: indented multiline text joins with spaces, while `<pre>` content is preserved.

## Development UI and preview controls

Since 5.13.0, `experimental.chromeDevtoolsWorkspace` configures the project as a Chrome DevTools workspace so edits in the Sources panel save to local files.

Since 5.17.0, `devToolbar.placement` sets a project default such as `bottom-left`; each developer may still override it through the toolbar.

In the terminal running `astro preview` since 5.16.0, type `o` then Enter to open a browser or `q` then Enter to stop the server.

## Rust compiler

Astro 6.0.0 provides the experimental Rust `.astro` compiler after installing `@astrojs/compiler-rs` and enabling `experimental.rustCompiler`. The Astro 7 alpha described in 6.2.0 makes it the default and only compiler, so remove that flag when testing the alpha.

## Structured logging

Astro 6.2.0 introduced `experimental.logger` with `logHandlers.json()` or `{ entrypoint }`; CLI `--experimentalJson` selected JSON for dev, sync, and build. A custom entrypoint default-exports a factory returning `AstroLoggerDestination`; its `write()` receives `AstroLoggerMessage`, and `matchesLevel()` from `astro/logger` filters levels.

In 7.0.0, move configuration to top-level `logger` and replace the flag with `--json`. `logHandlers.compose()` sends messages to multiple destinations, such as console plus JSON.

In 7.0.1-7.2.4, `logger.entrypoint` accepts `URL` objects and project-relative paths beginning `./` or `../`, resolved from the project root; package specifiers and absolute paths remain valid. `AstroRuntimeLogger` is now public for typing runtime logger functions.

## Managed background servers

Since 7.0.0, `astro dev --background` waits for readiness, prints URL/PID, and detaches. Repeated starts return the lockfile-managed instance; `/_astro/status` reports readiness. Use `astro dev status`, `logs`, and `stop`. Detected automation environments may enable this mode automatically.

In 7.0.1-7.2.4, `astro preview --background` follows the same pattern with `preview status`, `logs --follow`, and `stop`. Detected automation may enable it; set `ASTRO_PREVIEW_BACKGROUND=0` to opt out.

Use `astro dev --ignore-lock` to start an untracked parallel foreground server. It cannot combine with `--background`, automatic background mode, or `--force`; management subcommands do not see it.

## Package-manager detection

In 7.0.1-7.2.4, Astro install commands also inspect `package.json` `devEngines` when detecting the package manager.
