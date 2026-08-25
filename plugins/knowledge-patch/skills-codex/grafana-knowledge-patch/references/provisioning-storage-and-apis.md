# Provisioning, Storage, and HTTP APIs

Use this reference for data-source and dashboard provisioning, Git Sync, webhooks,
resource identity, Unified Storage, database migrations, and API transitions.

## Resource identity and HTTP API migration

### Validate data-source UIDs before Grafana 12 (12.0-upgrade)

`failWrongDSUID` is enabled by default, so REST and provisioning requests reject
malformed data-source UIDs. UIDs must use supported characters and be no longer
than 40 characters. Create replacements for invalid data sources and repoint
dashboard JSON and alert queries.

Add authentication to this local audit when required:

```bash
curl http://localhost:3000/api/datasources | jq '.[] | select((.uid | test("^[a-zA-Z0-9\\-_]+$") | not) or (.uid | length > 40)) | {id, uid, name, type}'
```

### Kubernetes dashboard authorization (since 12.0.0)

Dashboard endpoints under `/apis` perform fine-grained access-control checks.
`kubernetesClientDashboardsFolders` is enabled by default.

### Home and analytics identity (since 12.1.0)

Preferences use the dashboard UID for the home dashboard. Analytics integrations
should likewise use dashboard-UID endpoints rather than internal IDs.

### Kubernetes dashboards default (since 12.2.0)

`kubernetesDashboards` is enabled by default.

### Star endpoints removed (since 12.2.0)

Deprecated star APIs based on internal IDs are removed.

### PUT identity matching (since 12.3.0)

`PUT /api/datasources/uid/:uid` returns HTTP 400 if the payload UID differs from
the URL UID.

### Annotation persistence by UID (since 12.3.0)

Annotations saved through a dashboard UID do not contain the internal numeric
dashboard ID. Consumers must tolerate its absence.

### UID-first routes (since 12.4.0)

Deprecated internal-ID dashboard endpoints are removed, `/api/dashboards/home` is
deprecated, and data-source routes by name or internal ID are deprecated. Use
UID-based routes.

### Legacy `/api` and numeric data-source endpoints (13.0-upgrade)

The legacy `/api` family is deprecated but remains enabled pending a later major
removal. Migrate to versioned Kubernetes-style `/apis` resources. Numeric-ID
data-source endpoints are disabled by default; use UIDs. The
`datasourceLegacyIdApi` flag can temporarily restore them until the endpoints and
flag are removed.

### Dashboard and folder resource versions (since 13.0.0)

Dashboard and folder APIs graduate to `v1`; dashboard `v2` aligns
`TransformationKind` and Dashboard Preferences. API-server clients may set a
preferred resource version.

### Dashboard mutations and screenshots (since 13.1.0)

The Dashboard DTO removes `isStarred`, the mutation API adds annotation CRUD, and
a panel screenshot API is available.

## File and dashboard provisioning

### Experimental GitHub configuration (since 12.0.0)

The App Platform adds an experimental GitHub integration for dashboard
configuration management.

### Git repository modes (since 12.1.0)

App Platform provisioning adds a pure-Git repository type and experimental
`nanogit` mode for Git Sync.

### Inline secrets (since 12.2.0)

Git Sync provisioning moves to inline secrets. Treat this as a breaking
provisioning-configuration change.

### File change watches (since 12.3.0)

File provisioning watches the filesystem for changes rather than depending only
on the initial scan.

### Schema V2 and editable provisioned dashboards (since 12.4.0)

Dashboard provisioning accepts schema V2. Provisioned dashboards can be edited
through their JSON model.

### Git-synced alert folders (since 12.4.0)

Alert rules cannot be saved into Git-synced folders.

## Git Sync upgrades and repository ownership

### Avoid 13.0.0 for affected upgrades (13.0-upgrade)

Grafana 13.0.0 can lose or revert dashboards and folders when a self-managed 12.x
instance uses the `provisioning`, `kubernetesClientDashboardsFolders`,
`kubernetesDashboards`, and `grafanaAPIServerEnsureKubectlAccess` Git Sync flags.
The release was withdrawn; upgrade directly to 13.0.1 or later.

For mixed local and Git Sync content, or uncertain deployment mode, restore the
pre-upgrade database before upgrading to 13.0.1. A full-instance Git Sync
deployment can upgrade and resync from Git. Upgrading an affected 13.0.0 database
alone does not recover lost content.

### Git Sync defaults and repository checks (since 13.0.0)

Provisioning and Git Sync are enabled by default. Grafana checks repositories for
branch protection, write access, and emptiness; ignores Git submodules; no longer
requires `.git` on pure-Git repository URLs; and accepts a custom webhook base URL.

### Provisioned ownership and folder metadata (since 13.0.0)

Folder metadata is enabled by default. Exports create new UIDs. Unmanaged
resources cannot be overridden, and repository-managed folders reject
`ownerReferences` and manager-property changes. From 13.0.3, creating or moving
dashboards into new folders writes `_folder.json`.

### Signing and repository identity (since 13.1.0)

Git-backed provisioning exposes GPG, SSH, and S/MIME commit-signing settings.
Repository uniqueness is the combination of URL, branch, and path. Write-workflow
validation honors ruleset bypasses.

### Webhook hardening (since 13.1.0)

The webhook connector rejects GET. A provisioning URL change requires a new token,
and webhook secrets rotate periodically. GitHub webhooks add replay protection;
files and history endpoints validate the `ref` query parameter.

### External URLs and write timeout (since 13.1.0)

`public_root_url` controls externally visible provisioning URLs. From 13.1.1, the
per-resource sync write timeout is configurable.

### Provider integrations (since 13.2.0)

The GitHub Enterprise provider is enabled by default and adds dashboard previews
and webhooks. Enterprise provisioning adds OAuth app connections and webhooks for
GitLab and Bitbucket.

### Commit identity and attribution (since 13.2.0)

Public-preview Git Sync conventions and user attribution are enabled by default.
Commits can override the author or use the signer as author. Repository jobs
record author and origin.

### Preview, pull, folderless, and migration controls (since 13.2.0)

Pull-request previews diff against the merge base. Operators can force a full
pull, disable repository or connection webhooks, allow root-level saves and new
folders in folderless mode, and migrate to a selected branch. Migrate to GitOps
supports playlists; SLO-managed dashboards are excluded from export.

## Database and annotation migrations

### Annotation table disk requirement (12.0-upgrade)

An 11.x-to-12.x upgrade populates `annotation.dashboard_uid` by rewriting the
whole `annotation` table and rebuilding indexes. Back up the database and reserve
two to three times the table's current size in free space; insufficient space can
fail migration and prevent startup.

After successful migration, reclaim space during a low-traffic window because
these commands lock the table:

```sql
-- PostgreSQL
VACUUM FULL annotation;

-- MySQL
OPTIMIZE TABLE annotation;

-- SQLite
VACUUM;
```

### PostgreSQL TLS for Unified Storage (since 11.5.0)

Unified Storage supports PostgreSQL `verify-full` and prefers TLS when Grafana's
database connection uses SSL.

### Migration locking and database URL (since 12.1.0)

Storage honors `migration_locking`. Unified Storage respects `GF_DATABASE_URL`.

## One-way unified-storage migration

### First Grafana 13 startup (13.0-upgrade)

Grafana migrates folders and dashboards from legacy SQL tables to Unified Storage
and records completion in `unifiedstorage_migration_log`. The `dashboard`,
`dashboard_acl`, `dashboard_provisioning`, `dashboard_version`, `dashboard_tag`,
`library_element_connection`, and `folder` tables are then deprecated and no
longer authoritative.

A downgrade reads stale legacy tables. Restore the pre-upgrade database to roll
back. Changes made after a downgrade are not picked up by another upgrade because
the one-time migration remains recorded.

### SQLite retry and Parquet staging (13.0-upgrade)

SQLite migration retries with a Parquet buffer after lock errors. If `database is
locked` persists, increase `[unified_storage] migration_cache_size_kb` above its
`1000000` default or stage through Parquet:

```ini
[unified_storage]
migration_parquet_buffer = true
```

### Garbage collection is live by default (since 13.2.0)

Unified Storage garbage collection now defaults `dry-run` to false. Configured
collection performs real cleanup unless dry-run is explicitly selected.

### SQLite journal restoration (since 13.2.0)

When WAL is disabled, Grafana restores SQLite's journal mode rather than leaving
the database in WAL mode.

## Alertmanager and notification resources

### Internal configuration writes removed (since 12.0.0)

Settings no longer allow manual editing or restoration of the internal
Alertmanager configuration, and its internal POST endpoint is removed.

### Legacy endpoints and App Platform resources (13.0-upgrade)

Legacy Alertmanager configuration write endpoints are removed and selected read
or history endpoints become admin-only. Move automation under
`/apis/notifications.alerting.grafana.app/v1beta1/namespaces/{namespace}/` with
`receivers`, `routingtrees`, `templategroups`, `timeintervals`, and
`inhibitionrules`.

## Frontend API clients

### Packaged clients (since 12.3.0)

Grafana's frontend API clients cover all endpoints, expose regular and lazy hooks,
and automatically set PATCH headers.
