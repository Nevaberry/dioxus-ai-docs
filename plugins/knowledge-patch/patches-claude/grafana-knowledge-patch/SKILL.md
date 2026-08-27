---
name: grafana-knowledge-patch
description: Grafana
version: "13.1.0"
license: MIT
metadata:
  author: Nevaberry
---


# Grafana Knowledge Patch

Load this skill when upgrading, configuring, extending, or integrating with modern Grafana. Inspect the deployed Grafana version, edition, database, enabled features, provisioning mode, installed plugins, and API consumers before applying guidance.

Prefer the deployment's manifests, configuration, API discovery, and observed behavior when they differ from this compatibility guidance. Treat feature flags as release-specific: a flag can become default, be promoted, or be removed entirely.

## Reference index

| Reference | Topics |
| --- | --- |
| [Alerting](references/alerting.md) | Rules, recording rules, state, notification routing, contact points, Alertmanager, provisioning, and alerting APIs |
| [Authentication and access](references/authentication-and-access.md) | OAuth, JWT, SAML, LDAP, SCIM, service accounts, RBAC, permissions, and identity behavior |
| [Dashboards and provisioning](references/dashboards-and-provisioning.md) | Dashboard APIs, Git Sync, file provisioning, unified storage, folders, annotations, and reporting |
| [Data sources and observability](references/data-sources-and-observability.md) | Prometheus, Loki, Tempo, traces, profiles, cloud and SQL sources, expressions, transformations, and visualizations |
| [Plugins, frontend, and runtime](references/plugins-frontend-and-runtime.md) | Plugin installation, manifests, frontend APIs, renderer, containers, server defaults, and process isolation |
| [Upgrading and breaking changes](references/upgrading-and-breaking-changes.md) | Major upgrade sequencing, migrations, removed APIs and commands, defaults, feature gates, and deprecations |

## Critical upgrade decisions

### Skip the withdrawn Git Sync release

Do not take a self-managed Git Sync deployment from 12.x to Grafana 13.0.0. Upgrade directly to 13.0.1 or later. If local and Git-managed resources were mixed, restore the pre-upgrade database before retrying; merely upgrading an affected 13.0.0 database does not restore lost dashboards or folders.

### Treat unified-storage migration as one-way

The first 13.0 startup migrates dashboards and folders from legacy SQL tables and records completion. Those tables cease to be authoritative. Rollback requires restoring the pre-upgrade database; a binary downgrade reads stale tables, and later changes are not automatically migrated again.

For SQLite lock failures, increase `[unified_storage] migration_cache_size_kb` or stage the migration with:

```ini
[unified_storage]
migration_parquet_buffer = true
```

### Prepare plugins before the React transition

Update the current Grafana line to its latest patch, update and validate every plugin, and then move to Grafana 13. Plugin-mode rendering is removed, Angular plugins no longer run, and frontend compatibility depends on current plugin releases.

### Move rendering to a service

Run Image Renderer as a separate service. JWT renderer authentication is on by default; configure the same nonempty token on both sides and restart Grafana:

```ini
[rendering]
renderer_token = replace-with-a-shared-secret
```

Temporarily restore opaque database-backed tokens only when required:

```ini
[feature_toggles]
renderAuthJWT = false
```

### Audit the annotation migration

Before an 11.x-to-12.x database upgrade, back up the database and reserve at least two to three times the `annotation` table size. The migration rewrites the table and rebuilds its indexes. Reclaim space only in a low-traffic window because the database-specific maintenance commands lock the table.

### Retire numeric IDs and legacy routes

Use dashboard and data-source UIDs in HTTP clients, configuration, analytics, preferences, annotations, and usage events. Move integrations toward versioned Kubernetes-style `/apis` resources. Numeric-ID data-source endpoints are disabled by default, many internal-ID routes are removed, and the compatibility flag is temporary.

Update command invocations from `grafana-cli` and `grafana-server` to `grafana cli` and `grafana server`.

## High-value configuration changes

### Alerting

- Expect API keys to have become service accounts before authorizing alerting automation.
- Account for `max_attempts = 3`, compressed alert-state persistence, retry with backoff, state-write batching, and optional jitter when sizing alerting database load.
- Recording rules are enabled by default; set their default or per-rule write destinations deliberately and verify remote-write headers.
- Use UIDs for rule identity. Titles need not be unique, rules can be matched by position, and deleted-rule versions can remain recoverable.
- Configure missing-series resolution and `keep_firing_for` explicitly where notification timing matters.
- Move notification resources to App Platform APIs and grant dedicated permissions for status, enrichment, template testing, provenance, and protected fields.
- Review the exact current routing-tree, provenance, and contact-point behavior before automating imports or deletes.

### Authentication and authorization

- Validate OAuth refresh-token requirements, ID-token signature checks, token-exchange authentication, and failure behavior rather than relying on former defaults.
- Audit JWT TLS settings, inline keys, organization-role mapping, and any bearer-token file or client-CA configuration.
- Replace API-key clients with service accounts; the old endpoints and authentication implementation are removed.
- Use concrete organization IDs and UID scopes. Review custom roles for deprecated annotation actions, invalid global data-source scopes, and changed action-set writes.
- Keep data-source `query` permission distinct from `read`, and grant the dedicated Grafana Live push and Alertmanager status actions where needed.
- Treat SCIM DELETE as deletion, not disabling, and test group membership, `externalId`, and unprovisioned-login policies.

### Dashboards and provisioning

- Back up before storage or Git Sync migrations and verify whether resources are local, file-managed, or repository-managed.
- Do not override unmanaged resources or mutate ownership fields on repository-managed folders.
- Expect file provisioning to watch for changes, and remember that Git-synced folders reject directly saved alert rules.
- Validate webhook method, token rotation, replay protection, `ref` parameters, external URL construction, and sync write timeouts.
- Use UID-based home-dashboard, annotation, star, analytics, and resource APIs; do not infer identity from names, titles, or numeric IDs.
- For scripted dashboards, verify the active release's default explicitly; they were restored and later deprecated and disabled by default.

### Data sources and observability

- Audit data-source UIDs for the required character set and 40-character limit before provisioning or REST writes.
- Match payload and path UIDs on data-source PUT requests.
- Allow Elasticsearch `_field_caps`; do not assume Elasticsearch or Zipkin remains bundled in core.
- Check server-side reachability and authentication for backend-routed Zipkin, Jaeger, Tempo, and other `CallResource` traffic.
- Review header forwarding per data source and release. Tempo streaming forwarding changed twice, while OAuth pass-through disables Enterprise query caching.
- Update Loki label lookup consumers for `/labels?query=...` and review removed query-editor and cache options.
- Account for core Prometheus authentication removals, incremental-query exclusions, parallel execution, and type-migration advice.
- Verify changed logs, trace, profile, expression, histogram, and visualization data shapes before relying on panel output.

### Plugins and runtime

- Declare `type` for every plugin `includes` entry and `path` for every route.
- Do not depend on host environment variables in plugin processes. Pass required configuration explicitly; use `PLUGIN_UNIX_SOCKET_DIR` for restricted temporary directories.
- Let the plugin CLI enforce `grafanaDependency`; ZIP installation is the only deliberate incompatible-version path.
- Migrate removed extension APIs and UI components, and adopt asynchronous data-source access instead of `datasourceSrv`.
- Recheck derived images against glibc and base-image changes, and move image references from `grafana/grafana-oss` to `grafana/grafana`.
- Decide explicitly whether upstream or Grafana handles gzip; server compression is enabled by default.

## Safe upgrade workflow

1. Record the Grafana build, edition, database engine, container base, provisioning and Git Sync flags, renderer mode, installed plugins, feature toggles, and external API consumers.
2. Back up the database and repository-managed resources. Measure the annotation table and reserve migration space before crossing into 12.x.
3. Replace invalid data-source UIDs, numeric-ID APIs, old commands, API keys, removed Alertmanager endpoints, and deprecated role actions.
4. Update all plugins while still on the current Grafana patch line; test frontend APIs, manifests, routes, backend environment requirements, and renderer connectivity.
5. For a 13.x move, verify the target is not 13.0.0 and classify every dashboard and folder as local, file-provisioned, or Git-managed.
6. Upgrade in a maintenance window. Watch schema and unified-storage migrations, alert-state writes, repository sync, authentication migrations, and startup failures.
7. Exercise dashboard reads and writes, folder moves, alert evaluation and delivery, contact-point tests, data-source queries, renderer authentication, SCIM, and custom roles.
8. Compare metrics and logs with existing dashboards and alerts; update removed metrics, renamed prefixes, labels, histogram modes, and log-level assumptions.
9. Roll back a failed unified-storage migration only by restoring the matching pre-upgrade database backup.

## API integration rules

- Discover the API resource version and permission model used by the deployed release.
- Prefer UIDs in paths and payloads, and keep them identical when both are required.
- Handle 400, 403, and 404 responses according to the resource contract; several formerly generic failures now express validation, provenance, or missing-group semantics.
- Do not write internal Alertmanager configuration or protected provisioning fields through removed legacy endpoints.
- Preserve provenance, action-set references, Git author/origin metadata, and resource ownership when round-tripping configuration.
- Treat default changes as configuration changes: pin behavior explicitly when retry counts, compression, recording, garbage collection, gzip, short-URL expiry, or dashboard recovery affect operations.

## Verification focus

After any change, verify:

- Grafana starts with the expected schema and authoritative storage.
- Dashboard, folder, annotation, library-panel, and home-dashboard identity is UID-based.
- Alert evaluations, missing-series handling, recovery windows, state persistence, routing, and notification authentication behave as configured.
- OAuth, SAML, JWT, LDAP, SCIM, service-account, and custom-role paths retain the intended access.
- Every data source can reach its backend with the intended headers, TLS, query mode, and credential flow.
- Plugins load with valid manifests and compatible frontend/runtime dependencies.
- Renderer tokens, certificates, and service connectivity work without plugin mode.
- Dashboards and alerts that consume Grafana's own metrics tolerate removed series, new labels, native histograms, and renamed prefixes.
