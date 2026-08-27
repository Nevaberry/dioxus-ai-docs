# Dashboards and provisioning

## Dashboard identity and HTTP APIs

### UID-first analytics and preferences

Enterprise Analytics Views deprecates `:dashboardID` routes for `uid/:dashboardUID`; Analytics Summaries deprecates `dashboard_id` routes for `dashboard_uid`. (11.5.0)

Preferences store the home dashboard by UID, not numeric dashboard ID. (12.1.0)

Deprecated internal-ID dashboard endpoints are removed, and `/api/dashboards/home` is deprecated. Use UID-based resource routes. (12.4.0)

Usage Insights events use UIDs rather than numeric data-source and dashboard IDs. (13.0.0)

### Stars, annotations, and mutations

The deprecated star endpoints based on internal IDs are removed. (12.2.0)

Annotations saved through a dashboard UID no longer populate the internal numeric dashboard ID; consumers must tolerate its absence. (12.3.0)

The Dashboard DTO removes `isStarred`. The mutation API provides annotation CRUD, and a panel screenshot API is available. (13.1.0)

## Dashboard schemas and authoring

### Validation, layouts, and limits

Dashboard schema validation is available. Panels can enforce a configurable series-count limit while allowing an explicit render-all choice. (12.0.0)

Repeated panels in new layouts work in full-screen and embedded solo-panel routes. Variables can render beneath a drop-down; repeating no longer uses clone keys. The Inspect drawer cannot be opened or linked by URL. (12.2.0)

Dashboards add a `Switch` variable type for on/off input. (12.3.0)

Dashboards support threshold interpolation, four levels of nesting, and tabs inside nested layouts. (13.2.0)

### Time controls

Models can define custom quick ranges, and users can manually add time-picker quick ranges. Plugin/frontend `WeekStart` is `WeekStart | undefined`, not an arbitrary string. (11.6.0)

Time regions accept cron expressions. (11.6.0)

Quick ranges can be configured server-wide. Schema V2 dashboards are transformed automatically when exported as `V1Resource`. (12.1.0)

Dashboard controls expose annotations. Time-comparison windows can be saved, and panel time-range settings can be changed from view mode. (12.3.0)

Variable regular expressions can transform displayed text, and time-series dashboards support per-panel filtering. (12.4.0)

### Resource versions and schema V2

Dashboard and folder resource APIs graduate to `v1`. Dashboard `v2` aligns `TransformationKind` and Dashboard Preferences, and API-server users can choose a preferred resource version. (13.0.0)

The As Code editor performs schema validation. Schema V2 imports can contain labels, and authors can select the default layout, add rows and tabs from the side pane, and define section-level variables. (13.0.0)

V1-to-V2 conversion preserves the timezone user preference and query-variable sorting. A file-defined V2 dashboard can serve as the home dashboard. (13.1.0)

## File and JSON provisioning

### File watches and editable provisioned dashboards

File provisioning watches the filesystem for changes rather than relying only on its startup scan. (12.3.0)

Provisioning supports schema V2. A provisioned dashboard can be edited through its JSON model. (12.4.0)

### Scripted dashboards

Scripted dashboards returned in 11.6 after their earlier removal. (11.6.0)

They are later deprecated and disabled by default. Deployments that still depend on scripts must explicitly verify their configuration and plan a replacement. (13.2.0)

### Git-synced folder restrictions

Alert rules cannot be saved into Git-synced folders. (12.4.0)

## Git-backed provisioning

### Repository modes and secrets

The App Platform initially adds experimental GitHub-backed dashboard configuration. (12.0.0)

Provisioning adds a pure-Git repository type and an experimental `nanogit` Git Sync mode. (12.1.0)

Git Sync configuration switches to inline secrets; update existing provisioning configuration for this breaking format change. (12.2.0)

### Defaults and repository validation

Provisioning and Git Sync are enabled by default. Repository validation checks branch protection, write access, and emptiness. Git submodules are ignored, pure-Git URLs no longer need a `.git` suffix, and specs can set a custom webhook base URL. (13.0.0)

Folder metadata is enabled by default. Exports generate fresh UIDs. An unmanaged resource cannot be overridden, and repository-managed folders reject changes to `ownerReferences` and manager properties. Starting in 13.0.3, creating or moving dashboards into new folders writes `_folder.json`. (13.0.0)

### Signing and repository identity

GPG, SSH, and S/MIME commit signing are configurable. Repository identity is the combination of URL, branch, and path. Write-workflow checks honor ruleset bypasses. (13.1.0)

### Webhook hardening and public URLs

The webhook connector rejects GET. Changing the provisioning URL requires a new token, and webhook secrets rotate. GitHub webhooks have replay protection; files and history endpoints validate the `ref` query parameter. (13.1.0)

`public_root_url` controls externally visible provisioning URLs. Starting in 13.1.1, the per-resource sync write timeout is configurable. (13.1.0)

### Provider integrations and commit attribution

GitHub Enterprise is enabled by default and supports previews and webhooks. Enterprise provisioning adds OAuth app connections and webhooks for GitLab and Bitbucket. (13.2.0)

Public-preview Git Sync conventions and user attribution are enabled by default. Commits can override the author or use the signer as author, while repository jobs record author and origin. (13.2.0)

### Sync and migration controls

Pull-request previews compare against the merge base. Operators can force a full pull, disable repository or connection webhooks, permit root-level saves and new folders in folderless mode, and migrate to a chosen branch. Migrate to GitOps includes playlists; SLO-managed dashboards are excluded from export. (13.2.0)

## Major storage migrations

### Annotation table migration

An 11.x-to-12.x upgrade fills `annotation.dashboard_uid` by rewriting the entire `annotation` table and rebuilding indexes. Back up first and reserve at least two to three times the table size in free space; insufficient room can prevent Grafana from starting. (12.0-upgrade)

After success, reclaim disk during a low-traffic window because the commands lock the table:

```sql
-- PostgreSQL
VACUUM FULL annotation;

-- MySQL
OPTIMIZE TABLE annotation;

-- SQLite
VACUUM;
```

### Unified-storage migration

The first 13.0 startup migrates dashboards and folders out of legacy SQL tables and records the migration in `unifiedstorage_migration_log`. Afterward, `dashboard`, `dashboard_acl`, `dashboard_provisioning`, `dashboard_version`, `dashboard_tag`, `library_element_connection`, and `folder` are deprecated and non-authoritative. (13.0-upgrade)

Downgrading reads stale legacy tables. Restore the pre-upgrade database to roll back; changes made against those tables after a binary downgrade are not picked up on the next upgrade because the one-time migration is recorded. (13.0-upgrade)

SQLite automatically retries lock failures using a Parquet buffer. For persistent `database is locked` errors, raise `[unified_storage] migration_cache_size_kb` above its `1000000` default or explicitly configure: (13.0-upgrade)

```ini
[unified_storage]
migration_parquet_buffer = true
```

Unified Storage honors the `GF_DATABASE_URL` override, and storage migration respects `migration_locking`. (12.1.0)

Garbage collection later defaults `dry-run` to false. Once configured, collection performs real cleanup unless dry-run is explicitly restored. (13.2.0)

## Git Sync upgrade hazard

Grafana 13.0.0 was withdrawn because a self-managed 12.x deployment using `provisioning`, `kubernetesClientDashboardsFolders`, `kubernetesDashboards`, and `grafanaAPIServerEnsureKubectlAccess` could lose or revert dashboards and folders. Upgrade directly to 13.0.1 or later. (13.0-upgrade)

For mixed local and Git-managed content—or uncertain deployment mode—restore the pre-upgrade database before moving to 13.0.1. A full-instance Git Sync deployment can upgrade and resync from Git, but upgrading the damaged 13.0.0 database alone does not recover resources. (13.0-upgrade)

## Kubernetes dashboard APIs

`kubernetesDashboards` is enabled by default. (12.2.0)

The deprecated experimental API-server toggle is removed; delete it from feature-toggle configuration. (12.3.0)

## Library panels

Library panels no longer require unique names. Use a stable identifier rather than assuming one name resolves to one panel. (12.3.0)

Library Elements deprecates `folderFilter` in favor of `folderFilterUIDs`. (12.4.0)

## Enterprise reporting

Reporting can restrict recipient domains, uses the API server by default, and deprecates internal IDs. (11.5.0)

Report emails can have a custom subject. (11.6.0)

Schema V2 dashboards are supported in reports. (12.3.0)

Retries are productized, the stable PDF renderer no longer needs `newPDFRendering`, and schema-V2 report forms allow template-variable editing. (12.4.0)

PDF reports gain header toggles, configurable footers, and a readiness observer. (13.0.0)

Backend URL-based rendering is supported, and report-email recipients can be restricted to organization members. (13.1.0)

Report template variables are no longer restricted by a type allowlist. (13.2.0)

## Dashboard recovery

The Restore dashboards feature is enabled by default. (13.0.0)
