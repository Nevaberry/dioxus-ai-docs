---
name: grafana-knowledge-patch
description: Grafana
version: "13.1.0"
license: MIT
metadata:
  author: Nevaberry
---


# Grafana Compatibility and Operations Guide

Use this skill when upgrading, configuring, provisioning, extending, or operating
Grafana, especially when code or automation depends on an API, feature toggle,
plugin contract, alerting behavior, data-source integration, or storage detail.

## How to use this skill

1. Determine the deployed Grafana version and edition from the project manifest,
   image tag, package lock, or runtime configuration.
2. Identify the task area in the reference index below.
3. Apply only guidance relevant to the deployed version. Prefer manifests, code,
   tests, and observed behavior when they differ from compatibility notes.
4. For an upgrade, inspect every intermediate major-version migration and take a
   database backup before any irreversible schema or storage transition.
5. Audit feature toggles, deprecated endpoints, RBAC actions, plugin manifests,
   container assumptions, and provisioning workflows before rollout.
6. Validate the change in a staging environment with representative dashboards,
   alerts, plugins, authentication, rendering, and data-source queries.

## Reference index

| Reference | Topics |
| --- | --- |
| [Alerting](references/alerting.md) | Rules, recording, evaluation, state, Alertmanager, contact points, templates, imports, and alerting APIs |
| [Dashboards and visualizations](references/dashboards-and-visualizations.md) | Dashboard schema and layout, variables, panels, transformations, annotations, reporting, and rendering |
| [Data sources and observability](references/data-sources-and-observability.md) | Prometheus, Loki, Tempo, CloudWatch, Elasticsearch, SQL, traces, profiles, expressions, and query behavior |
| [Identity, access, and Enterprise](references/identity-access-and-enterprise.md) | Authentication, SSO, SCIM, RBAC, permissions, auditing, cloud migration, and Enterprise controls |
| [Plugins and frontend](references/plugins-and-frontend.md) | Plugin installation, manifests, runtime isolation, frontend APIs, UI components, and build dependencies |
| [Provisioning, storage, and APIs](references/provisioning-storage-and-apis.md) | Git Sync, file provisioning, Unified Storage, database migrations, HTTP APIs, webhooks, and resource identity |
| [Upgrades and runtime](references/upgrades-and-runtime.md) | Major-upgrade sequencing, removed settings and toggles, commands, containers, server defaults, and Grafana Live |

## Breaking changes and migration priorities

### Do not use Grafana 13.0.0 for affected Git Sync upgrades

Self-managed 12.x deployments using the Git Sync-related `provisioning`,
`kubernetesClientDashboardsFolders`, `kubernetesDashboards`, and
`grafanaAPIServerEnsureKubectlAccess` flags can lose or revert dashboards and
folders on 13.0.0. Upgrade directly to 13.0.1 or later. If local and Git-managed
content are mixed, restore the pre-upgrade database before proceeding.

### Treat unified-storage migration as one-way

The first 13.0 startup migrates folders and dashboards out of the legacy SQL
tables and records completion in `unifiedstorage_migration_log`. A downgrade
reads stale legacy tables, and a later re-upgrade does not replay post-downgrade
changes. Roll back by restoring the pre-upgrade database, not by downgrading the
binary against the migrated database.

### Budget space for the Grafana 12 annotation migration

An 11.x-to-12.x upgrade rewrites the full `annotation` table and its indexes to
populate `annotation.dashboard_uid`. Back up the database and reserve two to
three times the table size in free space. Reclaim space later in a low-traffic
window because `VACUUM FULL`, `OPTIMIZE TABLE`, and SQLite `VACUUM` lock work.

### Move automation from numeric IDs to UIDs

Malformed data-source UIDs are rejected by default from 12.0, including values
over 40 characters. Dashboard, annotation, analytics, star, home-dashboard,
data-source, and Usage Insights surfaces progressively remove or deprecate
numeric-ID and name-based contracts. Prefer stable UIDs throughout JSON,
provisioning, URLs, permissions, and alert queries.

### Migrate from legacy HTTP APIs

The legacy `/api` family is deprecated in Grafana 13 in favor of versioned
Kubernetes-style `/apis` resources. Numeric-ID data-source endpoints are disabled
by default, and multiple legacy Alertmanager configuration and notification
provisioning endpoints are removed or deprecated. Keep any temporary legacy flag
exception narrowly scoped and plan its removal.

### Update plugins before the React 19 upgrade

Before moving to Grafana 13, update the current Grafana release line to its latest
patch, update and validate every installed plugin, and only then perform the major
upgrade. Grafana 12 removes Angular support; Grafana 13 moves to React 19 and
removes or changes multiple `@grafana/ui` contracts.

### Replace plugin-mode image rendering

Grafana 13 removes plugin-mode Image Renderer support. Run rendering as a separate
service and configure the same nonempty, non-`-` `[rendering] renderer_token` in
Grafana and the renderer. JWT renderer authentication is enabled by default.

### Revisit bundled data-source assumptions

Grafana 13 removes the core Elasticsearch data source. Grafana 13.1 removes core
Zipkin and removes Azure and SigV4 authentication from the core Prometheus
integration, together with the `grafana-prometheus` package. Install or redesign
integrations explicitly instead of assuming those capabilities remain bundled.

### Review plugin process environment access

From 12.4, plugin processes do not inherit host environment variables by default.
External AWS plugins retain AWS SDK credential-chain variables, and plugins get
`PLUGIN_UNIX_SOCKET_DIR` for restricted temporary-directory deployments. Pass
required configuration through supported plugin mechanisms.

## Alerting quick reference

### Identify rules by UID

Rule titles and library-panel names are not unique. Alert groups can also contain
position-matched duplicates or rules without a group. Use rule UIDs and explicit
resource identity in tooling rather than title or position alone.

### Account for state and evaluation defaults

Alert retry `max_attempts` defaults to 3, recording rules become enabled by
default in 12.1, compressed alert state becomes the default in 12.2, and the
compression toggle is removed in 13.2. Pending periods apply to NoData and Error
alerts from 12.4. Test state transitions, retries, recovery windows, and recording
destinations during upgrades.

### Use current provisioning resources

Prefer the App Platform notification resources under
`/apis/notifications.alerting.grafana.app/v1beta1/namespaces/{namespace}/` for
receivers, routing trees, template groups, time intervals, and inhibition rules.
Provisioning authorization now checks resource-specific permissions, protected
fields, provenance, and managed-route access.

### Update custom alerting roles

Alertmanager status requires `alert.notifications.system-status:read` in Grafana
13. Custom roles and automation must also account for dedicated template-testing,
enrichment, snapshot, and provisioning permissions where applicable.

## Provisioning and storage quick reference

### Treat Git Sync ownership as authoritative

Provisioning and Git Sync are enabled by default in 13.0. Repository-managed
resources reject ownership mutations, and unmanaged resources cannot be
overridden. Validate branch protection, write access, repository emptiness,
webhook tokens, signing, URL/branch/path identity, and folder metadata.

### Protect webhook and external URL configuration

Provisioning webhooks reject GET, rotate secrets, require a new token after URL
changes, and validate `ref`; GitHub handling adds replay protection. Configure
`public_root_url` for externally visible provisioning links and explicitly set
sync write timeouts when long writes require it.

### Check Unified Storage cleanup behavior

Unified Storage honors `GF_DATABASE_URL`, migration locking, PostgreSQL TLS, and
migration cache/Parquet controls. In 13.2, garbage collection defaults to real
cleanup because dry-run defaults to false. Make dry-run intent explicit before
enabling scheduled collection.

## Plugin and frontend quick reference

### Validate manifests and compatibility

Plugin installation honors `grafanaDependency` and offers no compatibility bypass
other than deliberate ZIP installation. Grafana can reject unsupported Angular
versions. Plugin manifests require `routes[].path` from 12.4 and `includes[].type`
from 13.0.

### Migrate changed UI contracts

Use `Combobox` instead of deprecated `Select`; account for `Combobox` grouping and
`isItemDisabled`. The `Gauge` visualization remains available although the
`Gauge` component is removed. Replace removed `Modal` props, Graph graveyard APIs,
`SeriesIcon.noMargin`, and synchronous `datasourceSrv` access. Review required
accessibility props on childless `ToolbarButton` and required `Slider.inputId`.

## Runtime quick reference

### Update executable names and images

Use `grafana cli` and `grafana server`; the old hyphenated commands are removed.
Move Docker references from deprecated `grafana/grafana-oss` to
`grafana/grafana`. Derived images must account for Grafana-provided glibc 2.40,
Alpine 3.24.1, and the Ubuntu base transition from 22.04 to 24.04.

### Make changed defaults explicit

`server.enable_gzip` defaults to true in 13.0. Short URLs default to never
expiring, Grafana HTTP metrics use native histograms by default, recording rules
are enabled by default, scripted dashboards are disabled by default in 13.2, and
Unified Storage garbage collection is no longer dry-run by default. Pin settings
when infrastructure depends on earlier behavior.

### Remove dead feature gates

Do not leave removed toggles in configuration or branch application behavior on
them. Feature lifecycles include promotion to defaults or general availability,
followed later by toggle removal. Consult the runtime reference before carrying a
feature-toggle list across releases.

## Verification checklist

- Back up the database and test both forward migration and restore procedures.
- Inventory dashboard, data-source, rule, folder, annotation, and role UIDs.
- Exercise alert evaluation, notification delivery, imports, templates, and HA.
- Verify SSO, JWT, SCIM, service-account, anonymous, and custom-role behavior.
- Run representative Prometheus, Loki, Tempo, SQL, CloudWatch, trace, and profile queries.
- Validate plugin installation, signatures, manifests, process configuration, and UI APIs.
- Confirm Git Sync ownership, webhook security, signing, folder metadata, and resync behavior.
- Check metrics, audit events, logs, reporting, image rendering, and container dependencies.
- Remove obsolete flags, endpoints, settings, executable names, and image repositories.
- Prefer a tested restore over an unsupported downgrade after one-way migration.
