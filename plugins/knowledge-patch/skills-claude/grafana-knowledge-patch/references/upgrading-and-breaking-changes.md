# Upgrading and breaking changes

## Upgrade preparation

Inventory the deployed version, edition, database, provisioning and Git Sync flags, enabled feature toggles, renderer mode, installed plugins, command invocations, external HTTP clients, custom roles, container base, and dashboards that consume Grafana metrics. Back up the database before schema or unified-storage changes.

Defaults and removed gates should be handled as configuration migrations. Do not keep an obsolete toggle merely because the underlying feature still exists.

## Crossing into Grafana 12

### Data-source UIDs

Malformed data-source UIDs are rejected by default. Audit the allowed character set and 40-character maximum, create replacement sources, and repoint dashboard and alert JSON. (12.0-upgrade)

### Annotation migration capacity

The 11.x-to-12.x annotation migration rewrites the table and indexes. Back up and reserve two to three times the table's current size; reclaim storage only later in a table-locking maintenance window. (12.0-upgrade)

### Angular and plugin compatibility

Angular frontend support is removed. Update or replace Angular plugins before the upgrade. The plugin CLI enforces `grafanaDependency`; incompatible plugin ZIP installation is possible but should be an explicit exception. (12.0-upgrade, 12.0.0)

## Crossing into Grafana 13

### Avoid 13.0.0 for Git Sync

Grafana 13.0.0 was withdrawn after self-managed Git Sync upgrades could lose or revert dashboards and folders. Upgrade 12.x directly to 13.0.1 or newer. For mixed local/Git resources or uncertain deployment mode, restore the pre-upgrade backup before retrying; an affected database is not repaired by upgrading it alone. (13.0-upgrade)

### Update plugins before React 19

Patch the current Grafana line, update and validate every plugin, and then move to Grafana 13. This sequence supplies the plugin compatibility updates required by React 19. (13.0-upgrade)

### One-way dashboard and folder migration

The initial 13.0 startup moves dashboard and folder authority to unified storage and records completion. A binary downgrade reads stale legacy tables. Restore the pre-upgrade database for rollback; do not modify the stale tables and expect a later upgrade to import those changes. (13.0-upgrade)

### Renderer service migration

Plugin-mode rendering is removed. Deploy Image Renderer as a service and set the same `[rendering] renderer_token` in Grafana and the renderer. JWT renderer authentication is enabled by default. (13.0-upgrade)

### Commands and API families

Replace `grafana-cli` and `grafana-server` with `grafana cli` and `grafana server` in units, images, CI, and scripts. (13.0-upgrade)

The legacy `/api` family is deprecated in favor of versioned Kubernetes-style `/apis` resources. Data-source endpoints addressed by numeric ID are disabled by default; use UIDs. (13.0-upgrade)

### Custom role validation

Remove deprecated annotation permissions, replace wildcard annotation access with organization-annotation and dashboard/folder permissions, and recreate global roles with data-source UID scopes as non-global roles. Existing role scope cannot be changed in place. (13.0-upgrade)

## Feature-toggle transitions

### Promoted or defaulted behavior

`newFiltersUI` is generally available. Cloud Migrations is enabled by default. `alertingApiServer` is enabled by default. (11.5.0)

`ssoSettingsSAML` is generally available and enabled by default, while `alertingSaveStateCompressed` enters public preview. (11.6.0)

`pluginsSriChecks` is generally available, `kubernetesClientDashboardsFolders` and `prometheusRunQueriesInParallel` are on by default, and schema validation is available. (12.0.0)

Improved OAuth/SAML sessions, `ssoSettingsLDAP`, recording rules, and library-panel RBAC are enabled by default. (12.1.0)

`alertingSaveStateCompressed` and `kubernetesDashboards` are enabled by default. (12.2.0)

Logs visualization, native HTTP metric histograms, and no-expiry short URLs become defaults. (12.4.0)

Provisioning, Git Sync, folder metadata, gzip, and dashboard recovery are enabled by default. (13.0.0)

### Removed toggles and configuration in 11.x

`cloudwatchMetricInsightsCrossAccount` and `publicDashboards` are removed; their features are no longer gated. (11.5.0)

Remove `alertingNoNormalState`, `sqlQuerybuilderFunctionParameters`, `openSearchBackendFlowEnabled`, `managedPluginsInstall`, and `accessControlOnCall` from feature-toggle configuration. (11.6.0)

### Removed toggles and features in 12.0

Remove `alertingNoDataErrorExecution`, the Loki Alert State History toggles, `queryOverLive`, `live-service-web-worker`, `userStorageAPI`, and `traceQLStreaming`. Experimental dashboard restore behind `dashboardRestore` is removed. (12.0.0)

The external Metrics Drilldown app is the generally available implementation, its legacy paths are removed, and Traces Drilldown is preinstalled. (12.0.0)

### Removed configuration in later 12.x

Enterprise caching removes Memcached `reconnect_interval`. Loki removes `lokiQuerySplittingConfig` and experimental predefined operations. (12.1.0)

Remove `prometheusCodeModeMetricNamesSearch`, `HideAngularDeprec`, and the nested-folders flag. (12.2.0)

The deprecated experimental API-server toggle is removed. (12.3.0)

Remove `logRequestsInstrumentedAsUnknown`, `pinNavItems`, `unifiedHistory`, `individualCookiePreferences`, `permissionsFilterRemoveSubquery`, `logRowsPopoverMenu`, `logsInfiniteScrolling`, `exploreMetricsRelatedLogs`, and `postgresDSUsePGX`. Drilldown Investigations and CSV drag-and-drop snapshot queries are removed. (12.4.0)

### Grafana 13 toggle configuration

Feature toggles can be set through direct environment variables. `GF_FEATURE_TOGGLES_ENABLE` and `[feature_toggles] enable` are deprecated. `newFiltersUI` and `kubernetesAlertingRules` are removed. (13.0.0)

`alertRuleUseFiredAtForStartsAt`, `dashboardScene`, `publicDashboardsScene`, and `logsPanelControls` are removed. (13.1.0)

`AlertingCentralHistory` and `alertingSaveStateCompressed` are removed. Scripted dashboards are deprecated and disabled by default. (13.2.0)

## Removed or changed APIs

### Alertmanager and alert provisioning

Internal Alertmanager configuration writes and restore operations are removed. Later, legacy receiver-test and configuration delete endpoints are removed, while selected configuration-history reads and activation are admin-only. Move notification configuration to App Platform resources. (12.0.0, 13.0-upgrade)

Legacy notification actions and rule-provisioning endpoints are deprecated. Notification provisioning endpoints are also deprecated after Rules API v2 becomes available. (13.0.0, 13.1.0)

### Dashboard, star, and data-source APIs

Internal-ID star APIs are removed. Dashboard and data-source clients should use UIDs; `/api/dashboards/home` is deprecated, and numeric-ID data-source routes are disabled by default. (12.2.0, 12.4.0, 13.0-upgrade)

### Access-control APIs

Enterprise removes `/access-control/assignments/search` and `IncludeMapped` from user-role reads. Role writes no longer accept a client-controlled version. (13.0.0)

GroupAttributeSync routes and the dashboard-version metric are removed. (13.1.0)

## Runtime and container changes

The frontend build uses Node 22. (11.5.0)

Docker images use Grafana-provided glibc 2.40. (11.6.0)

Move from `grafana/grafana-oss` to `grafana/grafana`. (12.2.0)

Alpine-derived images move to Alpine 3.24.1 starting in 12.3.8. (12.3.0)

Plugin subprocesses stop inheriting the host environment by default. (12.4.0)

The Ubuntu base image moves from 22.04 to 24.04. (13.0.0)

## Metric and telemetry migrations

The Grafana HA Alertmanager cluster-metric prefix changes. Grafana HTTP metrics use native histograms by default; update selectors or opt back into classic histograms. (12.4.0)

Enterprise query caching removes duplicate `grafana_caching_items` and `grafana_caching_size`, and bundled Prometheus dashboards disappear. (13.0.0)

The dashboard-version metric is removed. (13.1.0)

## Deprecated surfaces

The OpsGenie alerting integration is deprecated. Internal-ID dashboards and data-source routes are removed or deprecated in favor of UIDs. (12.4.0)

`localeFormatPreference`, Datagrid, `GrafanaBootData.config.apps`, `GrafanaBootData.config.panels`, and `getFolderByUID` are deprecated. Use `folderFilterUIDs` instead of Library Elements `folderFilter`; Faro v2 removes `web_vitals_attribution_enabled`. (12.4.0)

The core Elasticsearch and Zipkin data sources are no longer bundled after their removals. Core Prometheus also removes Azure and SigV4 authentication and the `grafana-prometheus` package. (13.0.0, 13.1.0)

## Post-upgrade checks

1. Confirm startup completed all database and unified-storage migrations.
2. Verify dashboard and folder counts against the backup or Git repository.
3. Exercise UID-based dashboard, data-source, annotation, star, and home-dashboard calls.
4. Evaluate and deliver alerts through each authentication and contact-point path.
5. Validate custom roles, service accounts, SCIM lifecycle, and query permissions.
6. Load all plugins and test React, manifests, backend environment, renderer, and data-source hooks.
7. Reconcile metrics, labels, histogram types, and removed bundled dashboards with monitoring rules.
8. Confirm removed feature-toggle names are absent from configuration.
