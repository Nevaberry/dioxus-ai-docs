# Configuration and manager

## Builder configuration

### Vite config loading

The Vite builder accepts `configLoader` through its builder options (since
`10.5.0`). Put this option under the builder configuration rather than treating
it as a top-level Storybook setting.

## Experimental CLI and development environments

### AI command and instance discovery

The experimental, core-bundled `storybook ai` command provides MCP passthrough
when `STORYBOOK_FEATURE_AI_CLI` is enabled (since `10.5.0`). It accepts `-p` as
shorthand for `--port` and discovers Storybook instances by either working
directory or config directory.

When discovery is ambiguous, supply the intended directory and port instead of
assuming the first running instance is correct.

### Browser launch controls

Agent-driven development does not automatically open a browser (since
`10.5.0`). When browser launch is requested, Storybook respects `BROWSER` and
`BROWSER_ARGS`. Set these explicitly in environments that need a particular
browser executable or launch flags.

## Manager customization

### Favicon override

A favicon injected through `manager-head` can override the manager's default
favicon (since `10.5.0`):

```html
<link rel="icon" href="/favicon.svg" />
```

Confirm that the asset path is available to the manager in both development
and static builds.

## Warnings and migrations

### Legacy viewport default

The legacy `defaultViewport` parameter emits a warning (since `10.5.0`). Treat
the warning as a migration requirement even when the preview still renders and
tests pass.

## Lint and setup integrations

### Oxlint

As of `10.5.1`, the Storybook ESLint plugin provides plugin metadata and
documents use with oxlint. Its Storybook rules can therefore participate in an
oxlint-based lint setup; follow the plugin's oxlint configuration shape instead
of assuming only an ESLint runner can consume the rules.

### AI setup dependency

Storybook's AI setup guidance targets `msw-storybook-addon` v3 as of `10.5.1`.
Use that major version when following the setup instructions so the documented
integration and installed dependency agree.
