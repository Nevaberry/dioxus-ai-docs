# Configuration and manager

## Vite builder configuration loading

The Vite builder accepts `configLoader` through its builder options. Place the
option with the builder configuration rather than treating it as a standalone
preview feature.

When configuration-loading behavior differs between environments, inspect the
resolved Storybook builder options before assuming the project's Vite config is
being loaded by the expected mechanism.

## Experimental CLI and MCP passthrough

Storybook core bundles an experimental `storybook ai` command. Enable its MCP
passthrough with the `STORYBOOK_FEATURE_AI_CLI` environment variable.

The command:

- accepts `-p` as shorthand for `--port`;
- discovers Storybook instances by working directory;
- also discovers instances by configuration directory.

The two discovery bases matter when the command is launched from a monorepo
root, a package directory, or a custom Storybook config directory.

## Browser launch controls

Agent-driven development no longer opens the browser automatically. Storybook
respects `BROWSER` and `BROWSER_ARGS`, so automation can request an explicit
browser command and arguments when a browser should be launched.

Do not interpret the absence of an automatically opened browser as a failed
server start. Check the server URL and process state independently.

## Experimental feature flags

Two feature flags opt projects into worker or review infrastructure:

```js
export default {
  features: {
    experimentalDocgenServer: true,
    experimentalReview: true,
  },
};
```

- `experimentalDocgenServer` enables the worker-backed React metadata service
  shared by MCP, Docs, Controls, and ArgTypes.
- `experimentalReview` enables AI-curated visual changesets and search results.
  It is unset by default so CLI integrations can enable it deliberately.

Keep these flags explicit in project configuration when their behavior is a
required part of local development or CI.

## Manager favicon

A favicon supplied through `manager-head` can override the manager's default
favicon:

```html
<link rel="icon" href="/favicon.svg" />
```

Place the link in the manager head customization, not the preview document, when
the target is the Storybook manager UI.

## Legacy viewport configuration

Using the legacy `defaultViewport` parameter emits a warning. Treat the warning
as migration work even if the requested viewport still appears, and avoid
copying the legacy parameter into new stories or configuration.

Batch attribution: `9.0-10.0`, `10.5.0`.
