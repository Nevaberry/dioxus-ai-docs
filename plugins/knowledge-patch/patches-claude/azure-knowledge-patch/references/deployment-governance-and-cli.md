# Deployment, governance, and Azure CLI

## Resource-provider registration and ARM metadata

### Regional registration (`arm-api-versions-and-registration`)

Registration completes independently by region. Do not block creation merely
because the provider's global state is `Registering`; a target region can be
ready. Register again when a provider adds a location the subscription needs.

```bash
az provider register --namespace Microsoft.Batch
az provider show --namespace Microsoft.Batch \
  --query registrationState --output tsv
```

Registration requires `<provider>/register/action`, included in Contributor
and Owner, and can add an Entra application for the provider through Windows
Azure Service Management API. Register only providers ready for use. A
provider cannot be unregistered while its resource types remain.

Portal creation normally registers a provider. ARM/Bicep deployments auto-
register providers for resource types explicitly present in a template, but
not providers used only by implicit monitoring/security support resources.

### Discover API versions and locations

Query each resource type in provider metadata. Do not assume one namespace-
wide version or region list. Listed locations describe provider support;
subscription restrictions can still make them unavailable.

```bash
az provider show --namespace Microsoft.Batch \
  --query "resourceTypes[?resourceType=='batchAccounts'].apiVersions | [0]" -o tsv
az provider show --namespace Microsoft.Batch \
  --query "resourceTypes[?resourceType=='batchAccounts'].locations | [0]" -o tsv
```

## Bicep language and CLI

### Extendable parameter files (`bicep-language-and-cli`)

Bicep CLI 0.44.1 adds `extends` and `base`. A derived `.bicepparam` extends one
base; chains are allowed and base/intermediate files use `using none`. A
derived assignment replaces inheritance unless an object/array is explicitly
spread from `base`.

```bicep
// base.bicepparam
using none
param tags = { owner: 'platform', environment: 'dev' }

// prod.bicepparam
using './main.bicep'
extends './base.bicepparam'
param tags = { ...base.tags, environment: 'prod' }
```

Only parameter assignments are inherited; variables, user-defined types, and
imported functions are unavailable to derived files.

### Secure output

Since 0.35.1, `@secure()` marks string/object outputs, including module
outputs. ARM omits values from deployment history, portal, logs, and CLI.
Wrap arrays/numbers in an object or serialize them when secret.

```bicep
@secure()
output returnedToken string = suppliedToken
```

### Module identity limitation

Bicep 0.36.1 parses user-assigned module identity, intended for service access
such as Key Vault, but backends do not yet deploy it. Do not depend on the
syntax in live deployments.

### Console and snapshots

Bicep 0.42.1 adds direct `bicep console`, a REPL supporting expressions,
variables, multiline input, types/functions, and launch-directory `load*()`.
It accepts pipes but has no Azure-context functions, persistence, completion,
or `az bicep` equivalent.

Bicep 0.41.2 adds direct `bicep snapshot` to normalize a `.bicepparam` and
validate later code offline. Supply subscription/resource group/location/
tenant/management-group context for environment functions.

```bash
bicep snapshot --mode overwrite main.bicepparam
bicep snapshot --mode validate main.bicepparam
```

### Azure CLI Bicep operations

- `2.81.0` `az bicep install --version` honors the requested version without
  requiring `bicep.use_binary_from_path=false`.
- `2.84.0` `az bicep decompile-params --force` overwrites output files.

## Deployment validation, what-if, and stacks

- `2.75.0` pretty deployment what-if output includes potential changes,
  warnings, and diagnostic messages.
- `2.76.0` group export accepts `--export-format`; deployment create, validate,
  and what-if expose `--validation-level` at all scopes.
- `2.84.0` deployment-stack create/validate at resource-group, subscription,
  and management-group scopes add validation level and
  `--resources-without-delete-support`; stack delete adds the latter.
- `2.89.0` adds `az stack-whatif group`, `sub`, and `mg` for stack what-if at
  all three scopes.

## RBAC and role-assignment automation

### Deletion and listing safety

- `2.68.0` role-assignment delete no longer deletes all assignments when no
  selection is supplied. Bulk deletion must provide explicit criteria.
- `2.71.0` role-assignment list includes management-group inherited entries and
  announces removal of classic-administrator inclusion.
- `2.73.0` removes `--include-classic-administrators`.

### Avoid expansion queries (`2.72.0`)

Use `role assignment list --fill-principal-name false` to omit principal names
and bypass Graph; use `--fill-role-definition-name false` to omit role names
and bypass the definition query. List/delete accept `--assignee-object-id`
instead of `--assignee` to avoid a Graph lookup.

## Output contracts and CLI automation

### Output shape changes

- `2.79.0` `az resource list --output table` adds `provisioningState`.
- `2.75.0` missing consumption usage fields become JSON null, not `None`.
- Disk/snapshot, gallery application, Web App runtime, Key Vault key, and VNet
  output changes are detailed in their topic references.

Prefer JSON plus explicit `--query`; do not treat table column positions or
additive fields as stable APIs.

### Custom clouds and endpoint discovery

- `2.73.0` cloud register/update resource-manager endpoint discovery also
  discovers data-plane endpoints and no longer returns `gallery`.
- `2.75.0` cloud register/update adds Graph resource ID and
  `--skip-endpoint-discovery`.
- `2.85.0` adds Bleu to Known Clouds.

## Azure CLI runtime, packaging, and extension lifecycle

### Supported platforms and Python

- `2.73.0`: RHEL/CentOS Stream packages use Python 3.12; Ubuntu 20.04 support
  ends.
- `2.75.0`: Azure Linux/Mariner 2.0 packages are unsupported.
- `2.76.0`: packages support RHEL 10 and CentOS Stream 10.
- `2.77.0`: CLI supports Python 3.13 and embeds 3.13.7.
- `2.80.0`: Python 3.9 support is removed.
- `2.85.0`: additional preview macOS installation methods appear.
- `2.88.0`: CLI supports Python 3.14 and embeds 3.14.5; extensions using the
  embedded interpreter must be compatible.

### Commands moved to extensions

`2.77.0` moves IoT Hub device streams to `azure-iot`. `2.88.0` moves the full
CDN module to `azure-cli-extensions`. Install/pin extensions in offline and
reproducible environments.

## Monitoring and operational tooling

- `2.74.0` Monitor action groups add incident receivers and system/user-
  assigned identities.
- `2.82.0` `az monitor dashboard` supports Grafana-backed dashboards.
- `2.75.0` Network Watcher ring-buffer captures and other network diagnostics
  are described in the networking reference.

## API Management lifecycle

### Retired developer-portal identity (`api-management-retirements`)

On September 30, 2025, the provided developer portal stopped supporting ADAL-
based Entra and Azure AD B2C providers. Change the app redirect URI to the SPA
platform, select MSAL as the provider client library, update configuration, and
republish. The replacement uses authorization code plus PKCE.

### Retired direct management API

The optional direct API at
`https://<service-name>.management.azure-api.net` retired March 15, 2025.
Replace callers with ARM-based API Management REST operations and disable the
direct API. The APIM instance itself is unaffected.

### Current CLI surface

`2.85.0` adds `az apim backend` for backend services.

## Retirement inventory (`service-retirement-calendar`)

### Advisor metadata and impacted resources

Advisor classifies retirement under category `HighAvailability` and
subcategory `ServiceUpgradeAndRetirement`. Query provider metadata and
subscription recommendations with API `2025-01-01`, filtering those values and
expanding `ibiza`/details. `recommendationControl` is legacy and planned for
deprecation.

```http
GET https://management.azure.com/providers/Microsoft.Advisor/metadata?api-version=2025-01-01&$filter=recommendationCategory%20eq%20'HighAvailability'%20and%20recommendationSubCategory%20eq%20'ServiceUpgradeAndRetirement'&$expand=ibiza

GET https://management.azure.com/subscriptions/<subscription-id>/providers/Microsoft.Advisor/recommendations?api-version=2025-01-01&$filter=Category%20eq%20'HighAvailability'%20and%20SubCategory%20eq%20'ServiceUpgradeAndRetirement'&$expand=ibiza,details
```

Expanded responses include links, recommendation detail, and recommended
actions.

Advisor recommendations cover public Azure only and have incomplete service
and impacted-resource coverage. Use Azure Retirement Impact Analyzer for
sovereign and national-partner clouds.

### Resource Graph inventory

`advisorresources` contains affected ID, retiring feature, and date. Upgrade-
only entries share the subcategory but have no retirement feature; exclude
empty `retirementFeatureName`.

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

### SQL Database API `2014-04-01`

The control-plane API retires June 30, 2027 and covers all operations,
including servers, databases, elastic pools, managed instances, and related
resources. Primary stable target is `2021-11-01`.

| Old operation group | Replacement |
| --- | --- |
| database table auditing policies | database blob auditing policies |
| database threat detection | advanced threat protection settings |
| disaster recovery configurations | failover groups |
| extensions | database extensions |
| restorable dropped databases | restorable dropped managed databases |
| service objectives | capabilities |
| TDE activities/configurations | transparent data encryptions |

Connection policies, elastic-pool activities, elastic-pool DB activities,
queries/statistics/texts, recommended elastic pools, and service-tier advisors
have no newer stable equivalent; redesign those workflows.
