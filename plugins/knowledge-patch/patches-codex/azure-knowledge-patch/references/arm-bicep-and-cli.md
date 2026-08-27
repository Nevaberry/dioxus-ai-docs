# ARM, Bicep, and CLI

Use this reference for current compatibility details and exact command or schema changes.

## Bicep language and tooling

### Bicep overwrite and deployment-stack controls (2.84.0)

`az bicep decompile-params --force` can overwrite existing output files.
Deployment-stack create and validate commands at resource-group,
subscription, and management-group scope gain `--validation-level` and
`--resources-without-delete-support`; stack deletion also gains the latter
option for resources that cannot be deleted when no longer managed.

### Extendable parameter files (bicep-language-and-cli)

Bicep CLI 0.44.1 adds `extends` and `base` for layering parameter
assignments. A derived file can extend one base, chains are allowed, and
base/intermediate files use `using none`; a derived assignment replaces the
inherited value unless an object or array is explicitly merged with spreads
from `base`.

```bicep
// base.bicepparam
using none
param location = 'westus'
param tags = {
  owner: 'platform'
  environment: 'dev'
}

// prod.bicepparam
using './main.bicep'
extends './base.bicepparam'
param tags = {
  ...base.tags
  environment: 'prod'
}
```

Only parameter assignments are inherited. Variables, user-defined types, and
imported functions in a base file aren't exposed to derived files.

### Interactive expression console (bicep-language-and-cli)

Bicep CLI 0.42.1 adds `bicep console`, a REPL for expressions, variables,
multi-line input, user-defined types and functions, and `load*()` calls
resolved from the launch directory. It also accepts piped or redirected input,
but has no Azure-context functions such as `resourceGroup()`, session
persistence, completions, or `az bicep` equivalent.

```bash
bicep console
echo "parseCidr('10.144.0.0/20')" | bicep console
```

### Local deterministic deployment snapshots (bicep-language-and-cli)

Bicep CLI 0.41.2 adds `snapshot` for producing a normalized representation
from a `.bicepparam` file and validating later code against it without
deploying or consulting live Azure state. Use direct `bicep`, not `az bicep`;
offline evaluation can be supplied with `--subscription-id`,
`--resource-group`, `--location`, `--tenant-id`, and `--management-group`
context when environment functions need concrete values.

```bash
bicep snapshot --mode overwrite main.bicepparam
bicep snapshot --mode validate main.bicepparam
```

### Module identity is not yet deployable (bicep-language-and-cli)

Bicep 0.36.1 recognizes a user-assigned managed identity on a module, intended
to let the module access services such as Key Vault. Backend services don't
yet support the capability, so code using this syntax can't currently rely on
it at deployment time.

```bicep
param identityId string

module workload './workload.bicep' = {
  name: 'workload'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identityId}': {}
    }
  }
}
```

### Secure outputs (bicep-language-and-cli)

Since Bicep 0.35.1, `@secure()` can mark string or object outputs, including
outputs returned through modules. ARM then omits their values from deployment
history, portal views, logs, and command-line output; wrap arrays or numbers
in an object or serialize them to a string when they must remain secret.

```bicep
@secure()
param suppliedToken string

@secure()
output returnedToken string = suppliedToken
```

### Version-pinned Bicep installation (2.81.0)

`az bicep install --version` now installs the requested version without
requiring `bicep.use_binary_from_path` to be explicitly set to `false`;
previously the installation could be skipped without that setting.

## Cloud environment configuration

### Custom-cloud endpoint controls (2.75.0)

`az cloud register` and `az cloud update` accept
`--endpoint-microsoft-graph-resource-id` for the Microsoft Graph endpoint and
`--skip-endpoint-discovery` to suppress automatic endpoint discovery.

### Custom-cloud endpoint discovery (2.73.0)

With `az cloud register` or `update --endpoint-resource-manager`, endpoint
discovery now finds data-plane endpoints automatically and no longer returns
a `gallery` endpoint. Consumers of the discovered endpoint set must tolerate
that field being absent.

## Deployment operations

### ARM export format and deployment validation (2.76.0)

`az group export --export-format` selects the exported template format.
Deployment `create`, `validate`, and `what-if` expose `--validation-level` at
every scope.

### Deployment what-if diagnostics (2.75.0)

The pretty-printed result from `az deployment what-if` now includes potential
changes, warnings, and diagnostic messages.

### Deployment-stack what-if commands (2.89.0)

The new `az stack-whatif group`, `az stack-whatif sub`, and
`az stack-whatif mg` command groups provide deployment-stack what-if support
at resource-group, subscription, and management-group scope.

## Resource-provider registration and API metadata

### ARM and Bicep auto-registration has an explicit-resource boundary (arm-api-versions-and-registration)

Portal resource creation typically registers its provider, and ARM template or
Bicep deployments automatically register providers for resource types defined
in the template. Providers needed only by implicit supporting resources, such
as monitoring or security integrations not present in the template, must be
registered separately.

### Discover API versions and locations from provider metadata (arm-api-versions-and-registration)

Query a provider's `resourceTypes` metadata instead of assuming that every
resource type uses the same API versions or regions. Returned locations
describe provider support, but subscription restrictions can still make a
listed region unavailable.

```bash
az provider show --namespace Microsoft.Batch \
  --query "resourceTypes[?resourceType=='batchAccounts'].apiVersions | [0]" \
  --output tsv
az provider show --namespace Microsoft.Batch \
  --query "resourceTypes[?resourceType=='batchAccounts'].locations | [0]" \
  --output tsv
```

### Least-privilege provider registration (arm-api-versions-and-registration)

Registration requires the provider's `/register/action` permission, which
Contributor and Owner include, and it can add an application for the provider
to the Microsoft Entra tenant, typically through the Windows Azure Service
Management API. Register only providers that are ready for use; a provider
cannot be unregistered while its resource types still exist in the
subscription.

### Regional registration completion and new locations (arm-api-versions-and-registration)

Registration runs separately for every supported region. Do not block resource
creation merely because the provider remains in `Registering`; creation can
proceed in a target region once registration has completed there; run the
registration operation again when a provider adds a location that the
subscription needs.

```bash
az provider register --namespace Microsoft.Batch
az provider show --namespace Microsoft.Batch \
  --query registrationState --output tsv
```
