# Plugins and Frontend Development

Use this reference for plugin installation and compatibility, manifests, backend
processes, sandboxing, shared extensions, frontend APIs, UI components, and build
dependencies.

## Installation, compatibility, and packaging

### Version-install restrictions (since 11.5.0)

Grafana prevents installation of a plugin version whose Angular version is
unsupported. Administrators can also disable version installation for selected
plugin types.

### Update-all behavior (since 11.6.0)

`plugins update-all` no longer performs a separate uninstall step. Automation
must not depend on that intermediate uninstalled state.

### CLI dependency enforcement (12.0-upgrade)

`grafana cli plugins install` evaluates the plugin's `grafanaDependency` and
rejects versions incompatible with the running Grafana. There is no compatibility
bypass; deliberate incompatible installation requires the ZIP path.

### SRI checks generally available (since 12.0.0)

The `pluginsSriChecks` feature toggle is generally available.

### Platform removals (since 12.0.0)

Grafana removes plugin dependency-version support and secrets-manager plugin
support.

### Angular removal (since 12.0.0)

Grafana 12 removes Angular from the frontend. Angular-based plugins and extensions
must move to supported frontend APIs.

### React 19 upgrade sequence (13.0-upgrade)

Before upgrading to Grafana 13, update the current Grafana release line to its
latest patch, update and validate every installed plugin, and then perform the
Grafana upgrade. This sequence picks up required React 19 compatibility changes.

## Build and runtime dependencies

### Node and router dependencies (since 11.5.0)

The frontend toolchain uses Node 22. `react-router-dom` is again a Grafana UI
dependency available to plugin development.

### Docker glibc runtime (since 11.6.0)

Grafana's Docker build uses Grafana-provided glibc 2.40 binaries. Recheck native
plugin and custom-image assumptions about the container libc.

### Image Renderer plugin TLS (since 11.6.0)

The Image Renderer supports SSL while running in plugin mode, allowing
TLS-protected rendering connections on releases where plugin mode still exists.

### Image Renderer service migration (13.0-upgrade)

Grafana 13 removes plugin-mode Image Renderer. Run rendering as a separate service.
`renderAuthJWT` is enabled by default; configure the same nonempty, non-`-`
`[rendering] renderer_token` in Grafana and the renderer, then restart Grafana.

```ini
[rendering]
renderer_token = replace-with-a-shared-secret
```

To temporarily restore the earlier database-backed opaque-token behavior:

```ini
[feature_toggles]
renderAuthJWT = false
```

## Backend processes, isolation, and manifests

### Runtime-provided data sources (since 11.5.0)

Apps can register data sources at runtime instead of relying only on statically
installed registrations.

### Backend-only alerting plugin expressions (since 12.0.0)

Expressions work for plugins declaring `backend: true` and `alerting: false` in
`plugin.json`.

### Process environment isolation (since 12.4.0)

Plugin processes no longer receive host environment variables by default.
External AWS plugins retain AWS SDK credential-chain variables. All plugin
processes receive `PLUGIN_UNIX_SOCKET_DIR` for restricted temporary directories.

### Sandbox mode and route paths (since 12.4.0)

Community plugins, and Enterprise community/PPT plugins, can use experimental
sandboxing. Plugin manifests now require `routes[].path`.

### Manifest include types (since 13.0.0)

Every `plugin.json` `includes` entry must declare `type`.

### TLS 1.3 enforcement (since 13.2.0)

A plugin feature toggle can force TLS 1.3 for deployments that require it.

## Extension APIs and plugin context

### Shared extension functions (since 11.6.0)

Plugin extensions can share functions as well as components. Components returned
by `usePluginComponents` expose registry metadata.

### Observable extension APIs (since 12.0.0)

Plugin extensions gain observable APIs for registered components and links;
deprecated extension APIs are removed.

### Plugin metadata generic (since 12.1.0)

`usePluginContext` exposes its `PluginMeta` generic.

### Data-source configuration extensions (since 12.2.0)

Extensions can register data-source configuration components.

### Packaged frontend API clients (since 12.3.0)

Frontend API clients move into a package that covers all endpoints, exposes
regular and lazy hooks, and automatically sends headers required by PATCH.

### Context and link validation (since 12.3.0)

Plugins receive `PluginContext` even when Scenes is disabled. Azure SSO settings
are available through plugin context. Grafana no longer path-validates UI link
extensions, changing which links can be registered.

### Link targets (since 12.4.0)

Link extensions add `openInNewTab`.

### Asynchronous data-source access (since 13.1.0)

New asynchronous APIs and hooks replace `datasourceSrv`; frontend and plugin code
should migrate to the asynchronous access pattern.

## UI component contracts

### Week-start typing (since 11.6.0)

`WeekStart` is typed as `WeekStart | undefined`, not an arbitrary string.

### Combobox migration and exported components (since 11.6.0)

`Select` is deprecated in favor of `Combobox`. `MultiCombobox` and
`UsersIndicator` are exported from `@grafana/ui`. `InlineField.error` accepts a
`React.ReactNode`.

### Grouped Combobox and layout gaps (since 12.0.0)

`Combobox` supports grouping. `Stack` and `Grid` expose `columnGap` and `rowGap`.

### Collapse and Slider changes (since 12.3.0)

`Collapse.collapsible` is deprecated. `Slider.inputId` is required, and Slider
has a prop controlling whether its input is visible.

### Slider, ToolbarButton, and InteractiveTable (since 12.4.0)

`Slider` accepts decimal values. A childless `ToolbarButton` must provide
`tooltip` or `aria-label`. `InteractiveTable` adds `disableSortRemove` and
`sortDescFirst`, and resets pagination on data changes only when `autoResetPage`
requests it.

### Grafana 13 component removals (since 13.0.0)

The Gauge visualization remains, but the `Gauge` component is removed from
`@grafana/ui`. `Combobox` moves to `isItemDisabled`. Deprecated `Modal` props and
`SeriesIcon.noMargin` are removed, with no-margin behavior now the default. The
Graph graveyard API is deleted. Plugins can share `react-dom/client` and
`react-dom/server`.

### Branded PageLoader (since 13.2.0)

`PageLoader` is exported from `@grafana/ui` and automatically applies custom
branding.

## Logs and frontend data contracts

### Custom log grammar (since 13.0.0)

Plugin developers can provide a custom log grammar. OpenTelemetry log formatting
accepts dot-separated label names.

### Boot-data and folder helper deprecations (since 12.4.0)

`GrafanaBootData.config.apps`, `GrafanaBootData.config.panels`, and
`getFolderByUID` are deprecated.

## Removed plugin gates

### Managed-install gate removed (since 11.6.0)

`managedPluginsInstall` is removed and must not gate behavior.

### Angular warning configuration removed (since 12.2.0)

`HideAngularDeprec` is removed.

### Faro v2 configuration removal (since 12.4.0)

The Faro v2 upgrade removes `web_vitals_attribution_enabled`.
