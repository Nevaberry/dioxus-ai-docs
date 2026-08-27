# Audit, Events, Billing, and UI

## Audit records and operational evidence

### Request headers and supplemental data

Audit records include the incoming `User-Agent` without HMAC by default. Change
that behavior at `/sys/config/auditing/request-headers/user-agent` when the
header is sensitive. (`1.19-changelog`)

Response audit entries can include `supplemental_audit_data` in request and
response structures for non-JSON protocol details. The
`audit-non-hmac-request-keys` and `audit-non-hmac-response-keys` settings govern
these values; PKI OCSP supplemental details remain HMACed by default.
(`2.0-changelog`)

### Rotation and state-report evidence

Server logs report successful and failed automated root rotations and database
or LDAP static-role rotations, providing attestation evidence. (`1.21`)

The sudo-protected `sys/reporting/scan` endpoint writes Vault-state report files
under `reporting_scan_directory`; secure that directory as operationally
sensitive output. (`1.21-changelog`)

## Event subscriptions

### Forwarding and authorization

Enterprise performance standbys can serve event subscriptions without
redirecting to the active node. Events are forwarded only when a matching
subscriber exists, and subscription authorization uses the event metadata
`path` rather than requiring `data_path`. (`1.19-changelog`)

Secret-deletion event subscriptions no longer require a root token. (`1.19`)

When event metadata has `modified=true`, it also carries `vault_index`, so a
consumer can apply client-consistency controls before reading the changed
state. (`1.20-changelog`)

Enterprise lease events can be published as notifications, including
forwarding from primary to secondary clusters. (`2.0-changelog`)

The LDAP secrets engine emits rotation-success and rotation-failure events for
monitoring credential rotation. (`1.21`)

### Multiple clients and bounded queues

Enterprise 1.19 can miss events when multiple event clients are connected; use
the documented workaround for that release line. (`1.19`)

`VAULT_EVENT_NOTIFICATIONS_BOUNDED_QUEUE_SIZE` configures a per-subscriber
buffer. `0` keeps unbuffered behavior; a positive value enables buffering up to
the maximum of 1000. Buffering bounds resources with many subscribers but can
cause missed events when a queue fills. (`2.0.4`)

```shell
export VAULT_EVENT_NOTIFICATIONS_BOUNDED_QUEUE_SIZE=16
```

## Leases, retries, and quotas

`vault lease renew --fail-if-not-fulfilled` exits unsuccessfully when the
requested renewal cannot be fully granted. The default API client honors
`Retry-After`, and rate-limit waits round up to whole seconds.
(`1.19-changelog`)

Enterprise `remove_irrevocable_lease_after` removes irrevocable leases after
the configured duration beyond expiry. A nonzero value must be at least two
days. (`1.20-changelog`)

Enterprise rate-limit quotas accept `group_by` for entity-based and collective
grouping modes. (`1.20-changelog`)

## Activity, billing, and utilization

### Activity boundaries and dimensions

`sys/internal/counters/activity` includes `mount_type`. Product usage reports
also contain anonymous numerical feature-usage data. (`1.19-changelog`)

Activity queries align supplied start and end times to billing periods and cap
the end at the last completed month. Enterprise current-month queries return
actual new-client values. (`1.20-changelog`)

The activity export schema uses `token_creation_time` instead of `timestamp`
and includes the client's first-use timestamp for the requested period.
Enterprise adds cumulative namespace counts at
`sys/internal/counters/activity/cumulative`, issued-certificate counts at
`sys/billing/certificates`, and namespace filtering plus finer Secret Sync
detail in `sys/utilization-report`. (`1.21-changelog`)

### Utilization reports and billing APIs

Enterprise `/sys/utilization-report` returns a high-level utilization snapshot.
The HCL `development_cluster` setting defaults to `false` and is represented in
the report. (`1.20-changelog`)

`sys/billing/overview` returns current- and previous-month metrics, accepts
`start_month` and `end_month`, and is available in the admin namespace.
Historical internal billing data defaults to 37 months; `sys/billing/config`
allows retention from 13 months through six years. (`2.0-changelog`)

Manual `vault operator utilization` bundles use `snapshot_records` instead of
`snapshots`; `decoded_snapshot` holds the former human-readable data. Reports
also include `issuer`, `edition`, `add_ons`, `license_start_time`,
`license_expiration_time`, and `license_termination_time`. (`2.0-changelog`)

### Live client and license telemetry

Enterprise `vault.client.billing_period.activity` is a cluster-wide distinct
client count refreshed every ten minutes. (`1.20`)

The Enterprise client-count dashboard includes a **Client list** tab for
inspecting clients represented by aggregate counts. (`1.21`)

The billing overview GUI and API expose GCP KMS operation counts, normalized
OIDC token counts, normalized SPIFFE JWT token units, OS local static-role
high-water marks, and normalized External CA certificate units. Their prefixes
are `gcp_kms_operation_count`, `normalized_oidc_tokens_issued`,
`normalized_spiffe_jwt_token_units`, `os_local_static_max_role_count`, and
`normalized_external_ca_cert_units`; each has `.current_month_estimate` and
`.previous_month_complete` values. (`2.0`)

Product metrics include `secret.engine.os.local.account.static.role.count`,
agent-registration counts, and OAuth resource-server configuration counts. The
agent and resource-server metrics distinguish configurations with Rich
Authorization Requests enabled or disabled. (`2.0`)

## Response telemetry

The `vault.core.response_status_code` metric records handled HTTP statuses with
`code` and `type` labels. (`1.20-changelog`)

`/sys/internal/counters/tokens` is deprecated and responds with HTTP 403
`unsupported path`; remove callers rather than treating the response as an
authorization problem. (`1.20-changelog`)

## UI behavior

### Authentication and navigation

Enterprise can configure default and backup auth methods for the login form.
`/vault/auth?with=` refers only to an auth mount path and displays a simplified
form; choosing another method does not rewrite it. (`1.20-changelog`)

The Enterprise GUI can configure workload identity federation for AWS, Azure,
and GCP integrations. (`1.19`)

The namespace picker can search, filter, and navigate to namespaces without
reauthentication. Community Edition can list and add TOTP accounts, reveal
codes hidden by default, and show expiry timers. (`1.20`)

The GUI can generate ACL policy snippets with a visual editor, and Enterprise
can create a namespace through a guided questionnaire before continuing setup
through GUI, CLI, or Terraform. (`2.0`)

### Secrets-engine routes and known UI issues

Secrets-engine UI URLs use `/secrets-engines` rather than `/secrets`, and the
list view no longer supports bulk deletion. TLS certificate authentication is
available on the login screen. (`2.0-changelog`)

In 1.21 and 2.0, changing **Items per page** away from the first Secrets Engines
page can show an empty or incomplete table. Return to page 1 before changing
page size, or refresh and retry from page 1. (`upgrade-safety`)

An open Enterprise 2.0 issue can block root-token GUI access to a child
namespace protected by an Endpoint Governing Policy when the GUI calls
`sys/internal/ui/mounts`. CLI and API access still work; use them or allow that
endpoint in the EGP. (`upgrade-safety`)
