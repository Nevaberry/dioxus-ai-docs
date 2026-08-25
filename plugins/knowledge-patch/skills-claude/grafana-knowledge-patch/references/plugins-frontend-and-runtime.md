# Plugins, frontend APIs, and runtime

## Plugin installation and compatibility

Grafana blocks installation of plugin versions whose Angular version is unsupported. Administrators can also disable version installation for selected plugin types. (11.5.0)

`grafana cli plugins install` enforces the plugin's `grafanaDependency` against the running Grafana version. There is no bypass; use ZIP installation only for a deliberate incompatible install. (12.0-upgrade)

The `plugins update-all` operation no longer performs a separate uninstall. Automation must not rely on an intermediate absent-plugin state. (11.6.0)

Plugin dependency-version support and secrets-manager plugin support are removed. (12.0.0)

## Frontend framework migrations

### Angular removal

Grafana 12 removes Angular from the frontend. Migrate Angular plugins and extensions to supported APIs before upgrading. (12.0.0)

`HideAngularDeprec` is later removed from configuration. (12.2.0)

### React 19 sequence

Grafana 13 uses React 19. First update the existing Grafana release line to its latest patch, then update and validate all plugins, and only then upgrade Grafana. (13.0-upgrade)

Plugins can share `react-dom/client` and `react-dom/server`. (13.0.0)

## Plugin manifests and isolation

Plugin SRI checks are generally available through `pluginsSriChecks`. (12.0.0)

Community plugins—and Enterprise community/PPT plugins—can use experimental sandbox isolation. Plugin manifests require `routes[].path`. (12.4.0)

Every object in `plugin.json.includes` must declare `type`. (13.0.0)

A plugin feature toggle can require TLS 1.3. Use it only after confirming all plugin-side TLS endpoints support the protocol. (13.2.0)

## Extensions and plugin context

### Extension API changes

Extensions can share functions as well as components. Components from `usePluginComponents` expose registry metadata. (11.6.0)

Observable APIs expose registered extension components and links; deprecated extension APIs are removed. (12.0.0)

Plugins receive `PluginContext` even with Scenes disabled, and context exposes Azure SSO settings. Grafana no longer validates paths for UI link extensions, changing which links can be registered. (12.3.0)

Link extensions support `openInNewTab`. (12.4.0)

### Plugin context types

`usePluginContext` exposes its `PluginMeta` generic. (12.1.0)

## Frontend API clients and data-source access

Packaged frontend API clients cover all endpoints, provide normal and lazy hooks, and add the headers required for PATCH requests. (12.3.0)

Asynchronous APIs and hooks replace `datasourceSrv`; migrate plugin and frontend code to the async access pattern. (13.1.0)

## UI component changes

### Comboboxes and layout

`Select` is deprecated in favor of `Combobox`. `MultiCombobox` and `UsersIndicator` are exported by `@grafana/ui`; `InlineField.error` accepts `React.ReactNode`. (11.6.0)

`Combobox` supports grouping. `Stack` and `Grid` accept `columnGap` and `rowGap`. (12.0.0)

`Combobox` later replaces its item-disabling API with `isItemDisabled`. (13.0.0)

### Slider, collapse, and toolbar

`Collapse.collapsible` is deprecated. `Slider.inputId` is required, and Slider can control whether its input is visible. (12.3.0)

Slider accepts decimal values. A childless `ToolbarButton` must have `tooltip` or `aria-label`. `InteractiveTable` adds `disableSortRemove` and `sortDescFirst`; it resets pagination for data changes only when `autoResetPage` requests it. (12.4.0)

### Gauge, modal, and removed APIs

The Gauge visualization is generally available, but the `Gauge` component is removed from `@grafana/ui`. Deprecated `Modal` properties and `SeriesIcon.noMargin` are removed; no-margin behavior is the default. The Graph graveyard API is deleted. (13.0.0)

### Branded loading

`PageLoader` is exported from `@grafana/ui` and automatically applies custom branding. (13.2.0)

## Image Renderer

### TLS and certificates

Plugin-mode Image Renderer supports SSL in 11.6. (11.6.0)

Starting in 12.3.5, Image Renderer accepts custom CA certificates for rendering connections protected by privately trusted TLS. (12.3.0)

### Separate-service migration and JWT

Plugin mode is removed in Grafana 13; run the renderer as a separate service. `renderAuthJWT` is enabled by default. Set the same nonempty, non-`-` token in Grafana and the renderer, then restart Grafana. (13.0-upgrade)

```ini
[rendering]
renderer_token = replace-with-a-shared-secret
```

To temporarily restore the older database-backed opaque token:

```ini
[feature_toggles]
renderAuthJWT = false
```

## Plugin process environment

Plugin subprocesses no longer inherit host environment variables by default. Pass required settings deliberately. External AWS plugins still receive AWS SDK credential-chain variables. `PLUGIN_UNIX_SOCKET_DIR` identifies the socket directory for deployments with restricted temporary directories. (12.4.0)

## Server networking and defaults

### Compression and sockets

`server.enable_gzip` defaults to `true`; explicitly turn it off if a proxy or another layer owns compression. (13.0.0)

Grafana can serve HTTPS and HTTP/2 on a Unix socket and can listen on TCP and a Unix socket together. Redis remote caching accepts `network=unix`. (13.0.0)

### Short URLs and Grafana Live

Short URLs default to never expiring. Grafana Live adds `client_queue_max_size`. (12.4.0)

Grafana Live high availability accepts `redis://` and TLS-enabled `rediss://` URLs in `ha_engine_address`. (13.2.0)

## Database and unified-storage transport

Unified Storage supports PostgreSQL `verify-full` and prefers TLS when the Grafana database connection uses SSL. (11.5.0)

When WAL is disabled, Grafana restores SQLite journal mode rather than leaving the database in WAL. (13.2.0)

## Container and build runtimes

Grafana's frontend build moves to Node 22. `react-router-dom` returns as a Grafana UI dependency for plugins. (11.5.0)

The Docker image uses Grafana-provided glibc 2.40 binaries; verify custom images and native plugin assumptions against that libc. (11.6.0)

Move image references from deprecated `grafana/grafana-oss` to `grafana/grafana`. (12.2.0)

Starting in 12.3.8, Alpine-derived images use Alpine 3.24.1. (12.3.0)

The Ubuntu base moves from 22.04 to 24.04. Revalidate package names, libraries, and native runtime dependencies in derived images. (13.0.0)

## Boot data and frontend deprecations

`GrafanaBootData.config.apps`, `GrafanaBootData.config.panels`, and `getFolderByUID` are deprecated. The Datagrid panel and `localeFormatPreference` toggle are also deprecated. (12.4.0)

The Faro v2 transition removes `web_vitals_attribution_enabled`. (12.4.0)
