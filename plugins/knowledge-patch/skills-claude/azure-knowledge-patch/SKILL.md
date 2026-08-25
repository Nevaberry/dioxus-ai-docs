---
name: azure-knowledge-patch
description: Microsoft Azure
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Microsoft Azure Knowledge Patch

Use this skill for Azure infrastructure, Azure CLI, Azure PowerShell,
Terraform AzureRM or AzAPI, Bicep, identity SDK, Microsoft Entra, networking,
compute, containers, data services, storage, Key Vault, governance, and service
lifecycle work.

Azure is a rolling multi-product platform. Inspect the project's pinned
provider, CLI, module, API version, SDK, and resource SKU before applying
version-dependent advice. Prefer manifests, state, schemas, live API metadata,
command help, plans, and tests when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Terraform providers](references/terraform-providers.md) | AzureRM 4.x and AzAPI 2.x migrations, HCL bodies, import, preflight, actions, state, and authentication |
| [AKS and containers](references/aks-and-containers.md) | AKS, Azure Container Registry, Container Apps, Container Instances, Service Fabric, and container storage |
| [Compute and application platform](references/compute-and-app-platform.md) | VMs, VMSS, disks, images, App Service, Functions, App Configuration, Batch, AI, and application services |
| [Data, storage, and Key Vault](references/data-and-storage.md) | PostgreSQL, MySQL, SQL, Cosmos DB, Storage, Azure Files, NetApp Files, Backup, and Key Vault |
| [Deployment, governance, and CLI](references/deployment-governance-and-cli.md) | ARM, Bicep, provider registration, deployments, RBAC, monitoring, CLI packaging, API Management, and retirements |
| [Identity, authentication, and Graph](references/identity-authentication-and-graph.md) | Entra and Microsoft Graph, mandatory MFA, Azure Identity SDKs, Azure CLI, PowerShell, managed identity, and federation |
| [Networking](references/networking.md) | Private VNets, outbound access, load balancers, public IPs, gateways, private endpoints, Application Gateway, and network appliances |

## First-pass migration triage

1. Identify every client surface: Azure CLI version, Az PowerShell modules,
   Terraform providers, Bicep CLI, SDK packages, and explicit ARM API versions.
2. Resolve authentication type. Prefer workload identity, managed identity, or
   a service principal for automation; user-password flows cannot satisfy MFA.
3. Run `terraform plan`, deployment validation or what-if, and representative
   CLI queries without mutating production resources.
4. Check defaults that affect network exposure, egress, operating system,
   compute size, database version, storage redundancy, and access control.
5. Validate JSON and table-output consumers against the installed CLI because
   several commands changed casing, fields, null representation, and shape.
6. Query provider metadata for supported API versions and locations instead of
   copying one API version across a namespace.
7. Inventory retirements separately; an interface can remain operational after
   retirement while losing support and SLA coverage.

## Highest-impact breaking changes

### AzureRM 4.x requires a subscription

Every provider instance needs `subscription_id` or `ARM_SUBSCRIPTION_ID`.
Azure CLI authentication no longer supplies the active subscription
implicitly. Choose `resource_provider_registrations` deliberately and use
`resource_providers_to_register` for exact additions.

```hcl
provider "azurerm" {
  subscription_id                 = var.subscription_id
  resource_provider_registrations = "core"
  resource_providers_to_register  = ["Microsoft.ContainerService"]
  features {}
}
```

AzureRM 4.x also removes broad families of retired resources and renames many
AKS, networking, storage, diagnostic, and service-bus fields. Read the
Terraform reference before changing state; several migrations require a new
resource type or dedicated child resource rather than a spelling change.

### AzAPI 2.x uses native HCL

Set `body` as an HCL object and consume `output` as an HCL object. Remove
surrounding `jsonencode` and `jsondecode`. Replace `ignore_body_changes` with
a precise `lifecycle.ignore_changes` path.

```hcl
resource "azapi_resource" "example" {
  type      = "Microsoft.Example/widgets@2026-01-01"
  parent_id = var.parent_id
  name      = var.name
  body = { properties = { enabled = true } }
}
```

Custom retry fields `multiplier` and `randomization_factor`, and provider
`maximum_busy_retry_attempts`, are deprecated in later AzAPI 2.x. Do not copy
the early 2.0 retry shape into new configurations.

### Azure CLI defaults are not provisioning contracts

Pass values explicitly when repeatability matters. Recent changes include AKS
creation defaulting to no SSH key, VM and VMSS size defaulting to
`Standard_D2s_v5`, Linux App Service plans defaulting to `P0V3`, App Service
plans defaulting to Linux unless Windows is requested, and changing MySQL and
PostgreSQL creation defaults.

The CLI also removes or relocates commands. Single Server PostgreSQL commands,
legacy Batch certificate and node commands, and several old options are gone;
CDN and IoT device-stream commands moved to extensions. Pin and install needed
extensions in offline or controlled environments.

### Mandatory ARM MFA rejects password automation

Azure Resource Manager write operations can return claims challenges for user
identities even when Conditional Access exclusions exist. ROPC and username-
password credentials cannot satisfy MFA. Move unattended work to managed
identity, workload identity, or service principals, and use clients that can
handle claims challenges for interactive users.

### New networks and vaults have safer defaults

New VNets created with the newer API default subnet
`defaultOutboundAccess` to `false`; supply NAT gateway, Standard Load Balancer
outbound rules, Standard public IP, or firewall/NVA routing when egress is
required. Changing subnet privacy requires deallocating existing VMs before
their NICs receive the setting.

New Key Vaults created with control-plane API `2026-02-01` or later default to
RBAC when `enableRbacAuthorization` is omitted. Set it to `false` explicitly
only when access policies are intentional, and ensure the operator can create
role assignments before switching access models.

### Basic network SKUs are retired

Basic Load Balancer and Basic Public IP are retired and unsupported, although
existing instances can continue operating. Their migrations are resource-
specific and may require downtime. Do not mix Basic and Standard IP/LB SKUs;
preserve static public addresses before disassociation and configure NSG and
outbound behavior explicitly.

## Common workflows

### Safely update an AKS cluster

1. Query the cluster and node-pool modes, network plugin, outbound type,
   storage add-on, OS SKU, and current upgrade availability.
2. Treat preview-only AzureRM fields separately; editing the same AKS resource
   through both AzureRM and AzAPI can cause perpetual diffs or recreation.
3. Use ETags where concurrent updates are possible.
4. Set disruption, soak, undrainable-node, and maximum-unavailable controls
   explicitly for node-pool upgrades.
5. Account for Machines-mode pools being skipped by cluster upgrade and use
   node-pool rollback commands when recovery is needed.

### Choose an authentication chain

Set `AZURE_TOKEN_CREDENTIALS=prod`, `dev`, or a credential class name to
constrain `DefaultAzureCredential` in current .NET, Go, Java, JavaScript, and
Python Azure Identity libraries. Use the language-specific required-variable
option where silent fallback is unsafe. Allow roughly 70 seconds for IMDS
retry behavior when managed identity is selected directly.

Tool-backed credentials do not uniformly support claims challenges. Validate
the exact language implementation before relying on Azure CLI, PowerShell, or
Azure Developer CLI credentials for challenged sign-in.

### Author an ARM or Bicep deployment

Query `resourceTypes` provider metadata for the precise resource type, API
versions, and locations. Explicit resource types in ARM/Bicep deployments are
automatically registered, but implicit supporting providers may still need
manual registration.

Use secure Bicep outputs for secret strings or objects. Parameter files can
extend one base and merge objects or arrays with `base`, while local snapshots
can validate deterministic deployment expansion without contacting Azure.
Module identity syntax is recognized but is not yet deployable.

### Handle output safely

Prefer JSON plus explicit JMESPath queries over parsing table columns. Treat
new fields as additive, tolerate JSON null, preserve exact property casing,
and add contract tests for scripts that consume disk, snapshot, gallery,
resource-list, Web App runtime, Key Vault key, or network outputs.

### Plan database operations

Pass engine version, SKU, storage type, redundancy, network mode, and public
access explicitly. PostgreSQL and MySQL CLI options have changed repeatedly;
check current `--help` before upgrades, restores, replica creation, or backup
automation. Use validation-only PostgreSQL upgrades where available.

### Inventory service retirement

Use Azure Advisor metadata/recommendations and Resource Graph retirement data,
then supplement them for sovereign clouds and incomplete service coverage.
Retired APIs and SKUs can demand redesign, not only a new version string; for
example, some SQL `2014-04-01` operation groups have no stable replacement.

## Validation habits

- Pin provider and module constraints, CLI/extension versions, Bicep versions,
  and SDK lockfiles in reproducible automation.
- Test authentication in the target cloud and tenant; endpoint discovery,
  audiences, claims handling, and sovereign-cloud support differ.
- Use `az deployment ... validate`, `what-if`, deployment-stack what-if, AzAPI
  preflight, and Terraform plan before writes.
- Preserve state backups before Terraform provider upgrades and verify import
  IDs, resource moves, set/list semantics, and replacements.
- Query current resource state after CLI updates before depending on defaults.
- Deallocate VMs when subnet privacy changes and schedule downtime for Basic
  network SKU migrations.
- Treat previews, deprecated flags, and announced removals as transitional;
  avoid adding new dependencies on them.
- Read the relevant topic reference for exact flags, resource names, output
  changes, limitations, and version attribution.
