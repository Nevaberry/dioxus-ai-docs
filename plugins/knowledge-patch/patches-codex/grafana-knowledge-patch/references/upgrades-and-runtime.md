# Upgrades, Runtime, and Removed Configuration

Use this reference for upgrade sequencing, changed defaults, feature-toggle
lifecycle, executable and image changes, rendering, server configuration, and
Grafana Live.

## Major-upgrade runbooks

### Grafana 12 data-source UID audit (12.0-upgrade)

`failWrongDSUID` is enabled by default. Before upgrade, find malformed or
over-40-character UIDs, create replacement data sources, and update dashboard and
alert-query references. REST and provisioning writes reject malformed UIDs.

### Grafana 12 annotation migration (12.0-upgrade)

The upgrade rewrites the full `annotation` table and its indexes to populate
`dashboard_uid`. Back up the database and reserve two to three times the table
size. Reclaim space later during low traffic because PostgreSQL `VACUUM FULL`,
MySQL `OPTIMIZE TABLE`, and SQLite `VACUUM` lock work.

### Grafana 12 plugin compatibility (12.0-upgrade)

Plugin CLI installation enforces `grafanaDependency`. There is no compatibility
bypass except deliberately installing a ZIP.

### Avoid Grafana 13.0.0 with affected Git Sync (13.0-upgrade)

Grafana 13.0.0 was withdrawn because affected self-managed Git Sync deployments
can lose or revert dashboards and folders. Upgrade directly to 13.0.1 or later.
For mixed local and Git-managed content, restore the pre-upgrade database first;
a full-instance Git Sync deployment can instead resync from Git.

### React 19 sequencing (13.0-upgrade)

Update the existing Grafana line to its latest patch, update and validate every
plugin, and only then upgrade to Grafana 13.

### Unified Storage rollback (13.0-upgrade)

The first Grafana 13 startup performs a recorded, one-way dashboard and folder
migration. A binary downgrade reads stale legacy tables. Restore the pre-upgrade
database for rollback.

## Commands, images, and operating-system dependencies

### Docker glibc binaries (since 11.6.0)

Grafana Docker images use Grafana-provided glibc 2.40 binaries. Validate custom
images and native plugins against that libc runtime.

### Docker repository transition (since 12.2.0)

`grafana/grafana-oss` is deprecated. Change image references to
`grafana/grafana`.

### Alpine base transition (since 12.3.0)

From 12.3.8, Alpine-based images use Alpine 3.24.1. Recheck packages and runtime
assumptions in derived images.

### Renderer custom CAs (since 12.3.0)

From 12.3.5, Image Renderer supports custom CA certificates for privately trusted
TLS rendering connections.

### Removed command names (13.0-upgrade)

`grafana-cli` and `grafana-server` are removed. Update services, containers, CI,
and scripts to use `grafana cli` and `grafana server`.

### Ubuntu base transition (since 13.0.0)

The Ubuntu image moves from Ubuntu 22.04 to 24.04. Recheck package availability
and runtime assumptions in derived images.

## Rendering runtime

### Plugin-mode TLS (since 11.6.0)

Image Renderer supports SSL in plugin mode on releases where that mode is
available.

### Separate renderer service and JWT (13.0-upgrade)

Plugin-mode rendering is removed. Run a separate renderer service and set the
same nonempty, non-`-` `[rendering] renderer_token` in both services.
`renderAuthJWT` is enabled by default. Setting it to false temporarily restores
the earlier database-backed opaque-token behavior.

## Server, networking, and Grafana Live

### Short URLs and native histograms (since 12.4.0)

Short URLs default to never expiring. Grafana HTTP metrics use native histograms
by default, with classic histograms configurable.

### Live client queue size (since 12.4.0)

Grafana Live adds `client_queue_max_size`.

### HTTP compression default (since 13.0.0)

`server.enable_gzip` defaults to `true`. Explicitly disable it if a proxy or other
layer must be the only compression point.

### Unix sockets (since 13.0.0)

Grafana can serve HTTPS and HTTP/2 over a Unix domain socket and listen on TCP and
a Unix socket simultaneously. Redis remote cache supports `network=unix`.

### Grafana Live RBAC (since 13.0.0)

Pushing data to Grafana Live requires authorization through RBAC.

### Grafana Live Redis URLs (since 13.2.0)

`ha_engine_address` accepts `redis://` and TLS-enabled `rediss://` URLs for Live
high availability.

## Default changes to pin explicitly

### Cloud Migrations enabled (since 11.5.0)

Cloud Migrations is enabled by default and has a dedicated assistant role.

### Alert retries (since 11.5.0)

Alerting `max_attempts` defaults to 3. `state_periodic_save_batch_size` controls
periodic persistence batching.

### Recording rules enabled (since 12.1.0)

Recording rules are enabled by default. Review write destinations and use
`default_datasource_uid` where appropriate.

### Compressed alert state (since 12.2.0)

`alertingSaveStateCompressed` is enabled by default. The toggle is later removed
in 13.2.0, so do not depend on switching back through that flag.

### Logs visualization and match behavior (since 12.4.0)

The new Logs visualization is enabled by default. CloudWatch **Match exact**
defaults to false.

### Provisioning and Git Sync (since 13.0.0)

Provisioning and Git Sync are enabled by default. Folder metadata and dashboard
restore are also enabled by default.

### Scripted dashboards disabled (since 13.2.0)

Scripted dashboards are deprecated and disabled by default.

### Unified Storage garbage collection (since 13.2.0)

Garbage collection defaults dry-run to false, so configured runs perform real
cleanup unless dry-run is explicitly selected.

## Feature-toggle lifecycle

Remove dead flags from configuration. A feature promoted to general availability
or enabled by default may continue without its flag; a removed experimental
feature may disappear entirely. Do not infer which case applies from flag removal
alone.

### Feature transitions (since 11.5.0)

`newFiltersUI` is generally available. `cloudwatchMetricInsightsCrossAccount` and
`publicDashboards` are removed and no longer gate their features.

### Removed gates (since 11.6.0)

Remove `sqlQuerybuilderFunctionParameters`, `openSearchBackendFlowEnabled`,
`managedPluginsInstall`, and `accessControlOnCall`. Alerting also removes
`alertingNoNormalState`.

### Grafana 12 removals (since 12.0.0)

Remove `alertingNoDataErrorExecution`, the Loki Alert State History toggles,
`queryOverLive`, `live-service-web-worker`, `userStorageAPI`, and
`traceQLStreaming`. Experimental `dashboardRestore` functionality is removed.

### Removed configuration gates (since 12.2.0)

Remove `prometheusCodeModeMetricNamesSearch`, `HideAngularDeprec`, and the
nested-folders feature flag.

### Experimental API-server flag removed (since 12.3.0)

Delete the deprecated experimental API-server toggle from configuration.

### Cloud Migration configuration (since 12.4.0)

The Cloud Migrations feature toggle is removed. A configuration setting now
disables the feature.

### Removed 12.4 gates and features (since 12.4.0)

Remove `logRequestsInstrumentedAsUnknown`, `pinNavItems`, `unifiedHistory`,
`individualCookiePreferences`, `permissionsFilterRemoveSubquery`,
`logRowsPopoverMenu`, `logsInfiniteScrolling`, `exploreMetricsRelatedLogs`, and
`postgresDSUsePGX`. Drilldown Investigations and CSV drag-and-drop snapshot
queries are removed.

### 12.4 deprecations and cleanup (since 12.4.0)

`localeFormatPreference`, the Datagrid panel, `GrafanaBootData.config.apps`,
`GrafanaBootData.config.panels`, and `getFolderByUID` are deprecated. Library
Elements deprecates `folderFilter` for `folderFilterUIDs`. Faro v2 removes
`web_vitals_attribution_enabled`.

### Direct environment configuration (since 13.0.0)

Feature toggles can be set directly through environment variables.
`GF_FEATURE_TOGGLES_ENABLE` and `[feature_toggles] enable` are deprecated.
`newFiltersUI` and `kubernetesAlertingRules` are removed.

### Removed 13.1 toggles (since 13.1.0)

Remove `alertRuleUseFiredAtForStartsAt`, `dashboardScene`,
`publicDashboardsScene`, and `logsPanelControls`.

### Removed 13.2 alerting toggles (since 13.2.0)

Remove `AlertingCentralHistory` and `alertingSaveStateCompressed`.

## Other removed or changed runtime behavior

### Memcached and Loki settings (since 12.1.0)

Enterprise caching removes Memcached `reconnect_interval`. Loki removes
`lokiQuerySplittingConfig` and experimental predefined operations.

### Plugin host environment (since 12.4.0)

Plugin processes do not inherit host environment variables by default. External
AWS plugins retain SDK credential-chain variables; plugins receive
`PLUGIN_UNIX_SOCKET_DIR`.

### SQLite journal restoration (since 13.2.0)

When WAL is disabled, Grafana restores SQLite's journal mode instead of leaving
the database in WAL mode.
