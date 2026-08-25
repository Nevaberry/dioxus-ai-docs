# Service operations and retirements

Use this reference for current compatibility details and exact command or schema changes.

## Azure Batch

### Batch pool argument removals (2.80.0)

`az batch pool create` no longer accepts `--target-communication` or
`--resource-tags`; pool `reset` and `set` also drop
`--target-communication`.

### Expanded Batch task and JSON configuration (2.69.0)

Batch job creation gains `--job-manager-task-application-package-references`
and `--on-all-tasks-complete`. Job-schedule creation gains that application
package option plus `--job-metadata` and
`--job-manager-task-environment-settings`; schedule set/reset gains
`--job-max-task-retry-count` and `--job-max-wall-clock-time`.

`--json-file` is now accepted by job disable, node reboot, node scheduling
disable, and pool autoscale evaluate. Pool creation gains
`--start-task-environment-settings` and `--start-task-max-task-retry-count`,
while pool reset gains `--start-task-resource-files` and
`--target-node-communication-mode`.

### Removed Batch commands and options (2.69.0)

The deprecated `az batch certificate create/list/show/delete`,
`az batch node reimage`, and `az batch node remote-desktop` commands are
removed. Batch pool creation also removes `--application-licenses`,
`--certificate-references`, `--os-family`, and `--os-version`; pool set/reset
removes `--certificate-references`.

## Azure CLI platform support

### Azure Linux 2.0 packaging support removed (2.75.0)

Azure CLI packages no longer support Azure Linux (Mariner) 2.0; installations
on that release must move to a supported platform.

### CLI platform support (2.73.0)

Azure CLI packages on RHEL and CentOS Stream now use Python 3.12, and Ubuntu
20.04 is no longer supported.

### Preview macOS installation methods (2.85.0)

Azure CLI adds additional preview installation methods on macOS.

### Python 3.13 packaging (2.77.0)

Azure CLI now supports Python 3.13, and packaged builds embed Python 3.13.7.

### Python 3.14 packaging (2.88.0)

Azure CLI now supports Python 3.14 and ships Python 3.14.5 as its embedded
runtime; extensions that depend on the embedded interpreter must be
compatible with that version.

### Python 3.9 support removed (2.80.0)

Azure CLI no longer supports Python 3.9.

## Monitoring and diagnostics

### Action-group incident receivers and identities (2.74.0)

`az monitor action-group` now supports `--incident-receivers`,
`--mi-user-assigned`, and `--mi-system-assigned`.

### Grafana-backed dashboards (2.82.0)

`az monitor dashboard` now supports dashboards with Grafana.

## Retirement discovery and deadlines

### Advisor retirement metadata and impacted-resource APIs (service-retirement-calendar)

Azure Advisor classifies upgrade and retirement recommendations under API
category `HighAvailability` and subcategory `ServiceUpgradeAndRetirement`.
Use the provider-level metadata endpoint to list recommendation metadata and
the subscription endpoint to list recommendations with impacted resources;
`recommendationControl` is a legacy filter property planned for deprecation.

```http
GET https://management.azure.com/providers/Microsoft.Advisor/metadata?api-version=2025-01-01&$filter=recommendationCategory%20eq%20'HighAvailability'%20and%20recommendationSubCategory%20eq%20'ServiceUpgradeAndRetirement'&$expand=ibiza

GET https://management.azure.com/subscriptions/<subscription-id>/providers/Microsoft.Advisor/recommendations?api-version=2025-01-01&$filter=Category%20eq%20'HighAvailability'%20and%20SubCategory%20eq%20'ServiceUpgradeAndRetirement'&$expand=ibiza,details
```

The expanded responses include links, recommendation details, and recommended
actions. Advisor retirement recommendations currently cover only public Azure,
and both service coverage and impacted-resource coverage are incomplete;
sovereign and national-partner clouds require the Azure Retirement Impact
Analyzer.

### Resource Graph retirement inventory (service-retirement-calendar)

The `advisorresources` table exposes the affected resource ID, retiring
feature, and retirement date. Upgrade-only recommendations share this
subcategory but have no retiring feature, so filter them out when building a
retirement inventory.

```kusto
advisorresources
| where type == "microsoft.advisor/recommendations"
| where properties.category == "HighAvailability"
| where properties.extendedProperties.recommendationSubCategory == "ServiceUpgradeAndRetirement"
| extend retirementFeatureName = properties.extendedProperties.retirementFeatureName
| extend retirementDate = properties.extendedProperties.retirementDate
| extend resourceId = properties.resourceMetadata.resourceId
| where retirementFeatureName != ''
| project retirementFeatureName, retirementDate, resourceId
```

### SQL Database 2014-04-01 control-plane retirement (service-retirement-calendar)

Azure SQL Database control-plane API version `2014-04-01` now retires on
June 30, 2027, rather than June 30, 2026. The deadline covers every operation,
including servers, databases, elastic pools, managed instances, and related
SQL resources; the primary stable migration target is `2021-11-01`.

| `2014-04-01` operation group | `2021-11-01` replacement |
| --- | --- |
| Database table auditing policies | Database blob auditing policies |
| Database threat detection policies | Database advanced threat protection settings |
| Disaster recovery configurations | Failover groups |
| Extensions | Database extensions |
| Restorable dropped databases | Restorable dropped managed databases |
| Service objectives | Capabilities |
| Transparent data encryption activities/configurations | Transparent data encryptions |

Database connection policies, elastic-pool activities, elastic-pool database
activities, queries, query statistics, query texts, recommended elastic pools,
and service-tier advisors have no newer stable equivalent; workflows using
them must be redesigned rather than only changing the `api-version`.

## Service operations

### Bleu known-cloud support (2.85.0)

Bleu is now included in the CLI's Known Clouds list.

### CDN moves out of the core CLI (2.88.0)

The entire CDN module is now supplied through `azure-cli-extensions`, so
automation and offline installations that use CDN commands must make the
extension available.

### Consumption usage null values (2.75.0)

`az consumption usage list` now emits a JSON null for missing values instead
of the literal string `None`, which changes parsing for affected output.

### Resource-list table output (2.79.0)

`az resource list --output table` now includes `provisioningState`, changing
the table schema for consumers that parse its columns.

### RHEL 10 and CentOS Stream 10 packages (2.76.0)

Azure CLI packaging now supports RHEL 10 and CentOS Stream 10.
