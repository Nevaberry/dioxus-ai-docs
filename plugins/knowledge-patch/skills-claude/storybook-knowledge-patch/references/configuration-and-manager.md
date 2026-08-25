# Configuration and Manager

## Vite builder configuration loading

The Vite builder accepts `configLoader` through its builder options (since
`10.5.0`). Place the option under the builder configuration rather than
treating it as a top-level Storybook option.

Use it when the project must control how its Vite configuration is loaded, and
verify that both development and static builds select the intended config.

## Experimental command-line automation

### Enable the AI CLI

The experimental, core-bundled `storybook ai` command provides MCP passthrough
when `STORYBOOK_FEATURE_AI_CLI` is enabled (since `10.5.0`). The command:

- accepts `-p` as shorthand for `--port`;
- discovers running instances by working directory or config directory.

Set the feature environment variable only in workflows that intentionally use
the experimental command. Directory-aware discovery means callers do not need
to assume one globally selected instance.

### Control browser launching

Agent-driven development does not automatically open a browser (since
`10.5.0`). When browser launching is requested, Storybook respects `BROWSER`
and `BROWSER_ARGS`.

Set those variables in the process environment that launches Storybook. Do
not diagnose the absence of an automatically opened tab as preview startup
failure; check the server URL and process output first.

## Manager favicon

A favicon supplied through `manager-head` overrides the manager's default
favicon (since `10.5.0`):

```html
<link rel="icon" href="/favicon.svg" />
```

Use a path that remains valid in the deployed static Storybook, not only on the
development server.

## Legacy viewport configuration

The legacy `defaultViewport` parameter emits a warning as of `10.5.0`. A
preview that still renders with the parameter is not warning-free; locate and
migrate the legacy parameter rather than suppressing the diagnostic.

Check project-level and component-level parameters because either scope can be
the warning source.

## Linting with oxlint

As of `10.5.1`, the Storybook ESLint plugin provides plugin metadata and
documents oxlint usage. Its Storybook rules can therefore participate in an
oxlint-based lint setup.

Follow the plugin's oxlint configuration form rather than assuming an ESLint
flat-config object can be copied unchanged.

## AI setup dependency

Storybook's AI setup guidance targets `msw-storybook-addon` v3 as of `10.5.1`.
Use that major version when following the setup instructions; an older addon
major can produce dependency or API mismatches with the documented workflow.
