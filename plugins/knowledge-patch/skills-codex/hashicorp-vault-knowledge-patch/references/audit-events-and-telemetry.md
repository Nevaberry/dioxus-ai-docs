# Audit, Events, Reporting, and Telemetry

Use this reference for audit schemas, event delivery, activity and utilization
reporting, billing metrics, and observability.

## Audit records and files

### Audit request metadata (`1.19-changelog`)

Audit records include incoming `User-Agent` without HMAC by default. Configure
HMAC behavior at `/sys/config/auditing/request-headers/user-agent`.

### File audit-device permissions (`1.19-changelog`)

Executable file audit devices became an unseal blocker in 1.19.7. From
1.19.16, unseal warns about and clears existing executable bits; creation of a
new executable file audit device remains disallowed.

### Supplemental audit data (`2.0-changelog`)

Response audit entries may carry `supplemental_audit_data` in request and
response structures for non-JSON protocol details. The
`audit-non-hmac-request-keys` and `audit-non-hmac-response-keys` controls apply
to these values. PKI OCSP details use this area and are HMACed by default.

## Event delivery and subscriptions

### Enterprise event subscriptions (`1.19-changelog`)

Performance-standby subscriptions no longer redirect to the active node.
Events are forwarded only when a matching subscriber exists. Authorization
uses event metadata `path`, not a required `data_path`.

### Secret-deletion event subscriptions (`1.19`)

Enterprise notification subscriptions for secret deletion no longer require a
root token.

### Multiple event clients (`1.19`)

Enterprise deployments can miss events when multiple clients are connected.
The issue is unresolved in 1.19.x; use the documented workaround.

### Event-driven consistency (`1.20-changelog`)

Events with metadata `modified=true` include `vault_index`, allowing consumers
to use client-consistency controls for reads triggered by storage-changing
events.

### LDAP secrets-engine events (`1.21`)

The LDAP secrets engine emits events including rotation success and failure,
which can feed event-subscription monitoring.

### Enterprise lease events (`2.0-changelog`)

Enterprise notifications include lease events and can forward notifications
from primary to secondary clusters.

### Bounded event-notification queues (`2.0.4`)

`VAULT_EVENT_NOTIFICATIONS_BOUNDED_QUEUE_SIZE` selects a per-subscriber buffered
queue. Positive values enable buffering, capped at 1000; `0` keeps unbuffered
behavior. Buffering bounds resources with many subscribers but can drop events.

```shell
export VAULT_EVENT_NOTIFICATIONS_BOUNDED_QUEUE_SIZE=16
```

## Activity, utilization, and billing

### Product and activity reporting (`1.19-changelog`)

Product usage reporting adds anonymous numerical feature-usage information to
utilization reports. `sys/internal/counters/activity` responses include
`mount_type`.

### Activity-query billing boundaries (`1.20-changelog`)

`sys/internal/counters/activity` aligns requested start and end times to
billing periods and caps the end at the latest completed month. Enterprise
current-month queries return actual new-client values.

### Entity and collective rate-limit quotas (`1.20-changelog`)

The Enterprise rate-limit quota API supports `group_by` for entity-based and
collective grouping.

### Utilization reports (`1.20-changelog`)

Enterprise `/sys/utilization-report` returns a high-level utilization snapshot.
The HCL `development_cluster` field defaults to false and is included in the
report.

### Cluster-wide client telemetry (`1.20`)

Enterprise `vault.client.billing_period.activity` is a cluster-wide distinct
client count, refreshed every ten minutes for monitoring and alerting.

### Activity and utilization APIs (`1.21-changelog`)

Activity export renames `timestamp` to `token_creation_time` and adds the
client's first-use timestamp for the requested period. Enterprise also exposes
cumulative namespace counts at `sys/internal/counters/activity/cumulative`,
certificate counts at `sys/billing/certificates`, and namespace filters plus
finer Secret Sync details in `sys/utilization-report`.

### Client-level activity inspection (`1.21`)

The Enterprise client-count dashboard has a **Client list** tab showing the
individual clients represented in each aggregate.

### Consumption-billing APIs (`2.0-changelog`)

`sys/billing/overview` returns current- and previous-month metrics, accepts
`start_month` and `end_month`, and is available in the admin namespace.
Historical internal billing data defaults to 37 months; `sys/billing/config`
sets retention from 13 months through six years.

### Utilization-report schema (`2.0-changelog`)

`vault operator utilization` bundles use `snapshot_records` instead of
`snapshots`; each `decoded_snapshot` contains the former human-readable data.
Reports also include `issuer`, `edition`, `add_ons`, `license_start_time`,
`license_expiration_time`, and `license_termination_time`.

### License utilization telemetry (`2.0`)

`/sys/billing/overview` has a GUI dashboard and metrics with the prefixes
`gcp_kms_operation_count`, `normalized_oidc_tokens_issued`,
`normalized_spiffe_jwt_token_units`, `os_local_static_max_role_count`, and
`normalized_external_ca_cert_units`. Each has `.current_month_estimate` and
`.previous_month_complete` forms.

### Product usage telemetry (`2.0`)

Product metrics include `secret.engine.os.local.account.static.role.count`,
agent-registration counts, and OAuth resource-server configuration counts.
Agent and resource-server counts distinguish configurations with RAR enabled
and disabled.

## Logs and metrics

### Response status-code telemetry (`1.20-changelog`)

`vault.core.response_status_code` records handled response codes with `code`
and `type` labels.

### Credential-rotation attestation logs (`1.21`)

Server logs describe successful and failed automated root rotations and
database or LDAP static-role rotations for compliance evidence.
