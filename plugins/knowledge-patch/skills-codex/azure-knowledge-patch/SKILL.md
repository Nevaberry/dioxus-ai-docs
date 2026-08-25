---
name: azure-knowledge-patch
description: Microsoft Azure
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Microsoft Azure compatibility guide

Use this skill when changing Azure infrastructure, automation, authentication,
or service configuration. Start with the quick-reference guidance below, then
open the topic reference that matches the resource or tool being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [Application platform](references/application-platform.md) | App Configuration, App Service, Functions, Container Apps, API Management, AI Foundry, Service Connector, Service Fabric, and HDInsight |
| [ARM, Bicep, and CLI](references/arm-bicep-and-cli.md) | Bicep language and tooling, deployment operations, cloud environments, API versions, and provider registration |
| [Compute and images](references/compute-and-images.md) | VMs, VM scale sets, disks, snapshots, restore points, images, galleries, and scheduled events |
| [Containers and Kubernetes](references/containers-and-kubernetes.md) | AKS, ACR, Azure Container Storage, Azure CNI, and Azure Red Hat OpenShift |
| [Data, storage, and backup](references/data-storage-and-backup.md) | Azure Storage and Files, Backup, NetApp Files, Cosmos DB, MySQL, PostgreSQL, SQL, and messaging services |
| [Identity and security](references/identity-and-security.md) | Azure Identity SDKs, Azure PowerShell, CLI sign-in, Entra, Microsoft Graph, MFA, RBAC, Key Vault, and managed identities |
| [Networking](references/networking.md) | Virtual networks, subnets, IPAM, gateways, VPN, load balancers, NAT, public IPs, Application Gateway, WAF, Private Link, and network appliances |
| [Service operations and retirements](references/service-operations-and-retirements.md) | Azure CLI runtime support, Batch, monitoring, output compatibility, retirements, and retirement inventory |
| [Terraform and AzAPI](references/terraform-and-azapi.md) | AzureRM 4 migration, AzAPI 2 migration, state moves, imports, preflight, sensitive data, and retry behavior |

## Working method

1. Identify the controlling client: AzureRM, AzAPI, Azure CLI, Azure
   PowerShell, a Bicep binary, an Identity SDK, or a direct ARM API.
2. Read the project's manifest and lockfile before choosing syntax. Keep a
   deliberately pinned API or client behavior unless the change requires a
   migration.
3. Confirm the Azure cloud, tenant, subscription, region, resource provider,
   and API version. Public-cloud assumptions do not always hold in sovereign
   clouds.
4. Make changed defaults explicit in reproducible automation. Treat JSON and
   table output as interfaces and test consumers against the current shape.
5. For stateful or networking migrations, inspect the service-specific
   transition rules before applying. Some changes require deallocation,
   replacement, downtime, or an explicit outbound path.

## Breaking changes and deprecations

### AzureRM 4 provider setup

- Every provider instance needs `subscription_id` or
  `ARM_SUBSCRIPTION_ID`; Azure CLI authentication no longer supplies the
  active subscription implicitly.
- Choose `resource_provider_registrations` from `core`, `extended`, `all`,
  `none`, or the transitional `legacy` set. Add an exact custom list through
  `resource_providers_to_register`.
- Migrate removed SQL resources to `azurerm_mssql_*`, MySQL Single Server to
  Flexible Server, and other removed services or resources to the replacements
  listed in the Terraform reference.
- Update renamed AKS, diagnostic-setting, Cosmos DB, Service Bus, networking,
  Container Registry, and VMSS fields before upgrading.
- Remove positional indexing where AzureRM changed lists to sets. Pin values
  that must not follow changed security, SKU, network, or upgrade defaults.

```hcl
provider "azurerm" {
  subscription_id                 = var.subscription_id
  resource_provider_registrations = "core"
  resource_providers_to_register  = ["Microsoft.ContainerService"]
  features {}
}
```

### AzAPI 2 provider behavior

- Use native HCL objects for `body` and consume `output` as an HCL object;
  remove surrounding `jsonencode` and `jsondecode` calls.
- Replace `ignore_body_changes` with a precise
  `lifecycle.ignore_changes` path. Build any former global naming prefix or
  suffix into each resource name.
- Managed identity is opt-in because `use_msi` defaults to `false`.
- Review state after the default-output change, or set
  `disable_default_output = true` when computed response output is unwanted.
- Remove deprecated `retry.multiplier`, `retry.randomization_factor`, and
  provider-level `maximum_busy_retry_attempts`; current retry defaults replace
  them.

### Authentication and authorization

- Do not use `az login --username` for a user-assigned managed identity. Pass
  `--client-id`, `--object-id`, or `--resource-id`.
- `az role assignment delete` no longer means delete everything when selection
  criteria are absent. Always specify the intended assignments.
- Azure Resource Manager enforces MFA server-side for affected user write
  operations. A claims challenge can follow a sign-in that is sufficient for
  reads; use challenge-capable clients or move unattended jobs to workload
  identities.
- Username/password authentication cannot satisfy mandatory MFA and is
  deprecated across Identity SDKs and MSAL clients.
- Azure AD Graph is retired. Use Microsoft Graph endpoints and the Microsoft
  Graph application-manifest shape.
- `Get-AzAccessToken` returns a `SecureString` token. PowerShell scripts must
  not assume plaintext output.

### Azure CLI output and defaults

- Re-test parsers for disk, snapshot, gallery application, resource-list,
  access-restriction, ACR token, Key Vault key, and consumption output.
- `az webapp list-runtimes` returns structured objects rather than flat
  strings; filter with `--runtime` and `--support`.
- AKS creation now follows `--no-ssh-key` behavior by default.
- VM and VMSS creation defaults to `Standard_D2s_v5` when no size is supplied.
- Linux App Service plans default to `P0V3`, and App Service plan creation
  defaults to Linux unless Windows is selected explicitly.
- The core CLI no longer supplies CDN commands; install and manage the CDN
  extension where automation depends on them.

### Network and service retirements

- Basic Load Balancer and Basic public IP are retired and unsupported. Plan a
  resource-specific migration to matching Standard SKUs, including NSG and
  explicit outbound requirements.
- New virtual networks created with the newer API default subnets to private
  outbound behavior. Configure NAT Gateway, a Standard load-balancer outbound
  rule, a Standard public IP, or firewall/NVA routing as appropriate.
- Deallocate existing VMs after changing a subnet's default-outbound setting
  so the NIC configuration receives the change.
- API Management's direct management API and ADAL-based developer-portal
  identity providers are retired. Use ARM-based management and MSAL with
  authorization code plus PKCE.
- Key Vault control-plane APIs older than `2026-02-01` retire on February 27,
  2027. New vaults created through the current stable API default to RBAC
  unless `enableRbacAuthorization` is explicitly false.
- Azure SQL Database control-plane API `2014-04-01` retires on June 30, 2027;
  some old operation groups require workflow redesign rather than an API-version
  substitution.

## Common workflows

### Build and parse Azure resource IDs

With Terraform 1.8 or later, prefer provider functions over string assembly.
AzureRM supplies `normalise_resource_id` and `parse_resource_id`; AzAPI adds
scope-specific builders and an API-type-aware parser. Preserve caller-owned
name casing when normalizing Azure-controlled ID segments.

### Validate AzAPI before deployment

Set `enable_preflight = true` to validate supported resource properties during
planning. Use `ignore_not_found` plus `exists` for absence-aware reads, and use
`sensitive_body` or `sensitive_response_export_values` for secret payloads.
For list reconciliation, identify entries with `list_unique_id_property`
before allowing unmanaged remote items.

### Register resource providers deliberately

Registration completes independently by region. A provider may remain
globally `Registering` while a target region is usable. Register only required
providers, and query each resource type's metadata for API versions and
locations instead of assuming a provider-wide value.

```bash
az provider show --namespace Microsoft.Batch \
  --query "resourceTypes[?resourceType=='batchAccounts'].apiVersions | [0]" \
  --output tsv
```

### Author and test Bicep

- Layer parameter files with `extends`; only parameter assignments inherit,
  and object or array values require explicit spread-based merging.
- Mark string or object outputs with `@secure()` to keep values out of
  deployment history and command output.
- Use direct `bicep snapshot` for deterministic local deployment snapshots and
  `bicep console` for expression experiments. Neither feature is an
  `az bicep` substitute.
- Module identity syntax is recognized but is not yet deployable by the
  backend service.

### Keep AKS and ACR automation explicit

- Pin node VM size, OS SKU, outbound type, storage mode, SSH-key behavior, and
  upgrade availability when those choices affect cluster invariants.
- Treat ACNS, deployment safeguards, managed namespaces, Automatic clusters,
  Managed Gateway API, artifact streaming, control-plane metrics, and rollback
  as separate opt-in workflows with their documented command flags.
- ACR token audience, endpoint protocol, content-trust deprecation, regional
  endpoint login, cache identity, and writable cache settings can affect login
  and repository automation.

### Choose a credential chain intentionally

Set `AZURE_TOKEN_CREDENTIALS=dev`, `prod`, or a credential class name to
constrain `DefaultAzureCredential`. Account for the managed-identity IMDS retry
window when sizing startup timeouts. Claims-challenge support differs among
Azure CLI, Azure PowerShell, Azure Developer CLI, and language credentials;
do not assume one tool-backed credential can substitute for another.

### Stabilize data-service provisioning

- Pass MySQL version, IOPS scaling, storage redundancy, backup interval, and
  maintenance choices explicitly where supported; remove options that later
  commands have dropped.
- For PostgreSQL, verify engine capability, compute tier, storage type, network
  mode, HA terminology, and mirroring restrictions for the operation being
  performed.
- Treat Azure Files OAuth, NFS, encryption-in-transit, user-delegation SAS,
  and provisioned-share controls as distinct authorization and protocol paths.
- Review SQL, Cosmos DB, Backup, and NetApp Files references before changing
  retention, restore, replication, encryption, or network behavior.

### Inventory retirements

Use Azure Advisor retirement metadata and impacted-resource APIs for public
Azure, then query the Resource Graph `advisorresources` table for affected
resource IDs and dates. Filter out upgrade-only recommendations that have no
retiring feature. Advisor coverage is incomplete, so use the retirement
analyzer for sovereign and national-partner clouds.
