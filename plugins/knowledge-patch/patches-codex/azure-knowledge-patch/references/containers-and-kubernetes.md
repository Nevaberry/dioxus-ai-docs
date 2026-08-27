# Containers and Kubernetes

Use this reference for current compatibility details and exact command or schema changes.

## Azure Container Registry

### ACR access and source-registry identity (2.73.0)

Registry create/update accepts `--role-assignment-mode` to enable or disable
ABAC, and `az acr check-health --repository` checks read, write, and delete
permissions for one repository. ACR task create/update, build, and run accept
`--source-acr-auth-id` to choose the managed identity used to authenticate to
the source registry.

### ACR content-trust and health-check breaking changes (2.83.0)

`az acr config content-trust update` announces that the `enabled` status will
stop being accepted. `az acr check-health` also announces removal of its
Notary client check, so automation must not depend on either behavior.

### ACR content-trust command deprecation (2.79.0)

`az acr config content-trust` and its `show` and `update` operations now emit
deprecation notices. Treat these interfaces as transitional in automation.

### ACR creation controls (2.88.0)

`az acr create` now accepts `--data-endpoint-enabled` for a dedicated data
endpoint used in client firewall configuration and `--endpoint-protocol` to
select the registry endpoint protocol during creation.

### ACR domain-name-label hash scope (2.72.0)

`az acr create` and `az acr check-name` accept `--dnl-scope` to select the
scope used for the registry's domain-name-label hash.

### ACR endpoint routing and cache identities (2.85.0)

`az acr replication create` and `update` gain
`--global-endpoint-routing`; `--region-endpoint-enabled` now redirects to
that option rather than being confused with registry-level
`--regional-endpoints`. Cache-rule create/update also accepts `--identity`
for a user-assigned managed identity.

### ACR exposed-token output (2.74.0)

`az acr login --expose-token` now adds `refreshToken` and `username` fields to
its output, so consumers with fixed output schemas must account for them.

### ACR Podman and regional-endpoint login (2.86.0)

`az acr login --name` now supports Podman. For registries with regional
endpoints enabled, `az acr show-endpoints` displays their host names,
`az acr login --endpoint` selects one for login, and `az acr import` accepts a
regional endpoint URI as its source.

### ACR token audience (2.82.0)

`az acr login` now enforces the ACR audience when acquiring its Microsoft
Entra token. Token acquisition policies or scripts that assumed another
audience must account for this change.

### ACR token audience and endpoint protocol (2.87.0)

`az acr login` can now customize the Microsoft Entra token audience used for
authentication. Registry updates also accept `--endpoint-protocol` to select
the registry endpoint protocol.

### AKS attach-ACR principal types (2.75.0)

When `az aks update` uses `--attach-acr`, the new
`--assignee-principal-type` option specifies the attached registry assignee's
principal type.

### Connected-registry garbage collection (2.73.0)

`az acr connected-registry create` and `update` accept `--gc-enabled` and
cron-based `--gc-schedule` to control garbage collection.

### Credentialless ACR cache rules (2.71.0)

`az acr create` can now create a cache rule without a credential set; that
previously failed even when the cache rule did not need credentials.

### Cross-cloud ACR use by Container Apps (2.86.0)

`az containerapp create` now supports Azure Container Registry references in
other Azure clouds rather than assuming the default cloud.

### Writable ACR cache repositories (2.89.0)

`az acr create` and `az acr update` accept `--writable-cache-repo` to enable
writable behavior for cache repositories in a registry.

## Azure Container Storage

### AKS Azure Container Storage v2 controls (2.83.0)

On a new cluster, `az aks create --enable-azure-container-storage` enables
ACStor v2 without selecting a storage option. On an existing cluster,
`az aks update --enable-azure-container-storage ephemeralDisk` enables
ephemeral-disk storage, `--disable-azure-container-storage elasticSan`
disables Elastic SAN storage, and the value-less disable flag disables ACStor
v2 entirely.

### Azure Container Storage lifecycle and AKS Automatic (2.77.0)

`az aks create` and `az aks update` can install the latest acstor release with
`--enable-azure-container-storage`; when enabling it,
`--container-storage-version` selects a specific release. `az aks update
--disable-azure-container-storage` can uninstall acstor regardless of its
installed version, and create/update also accept `--sku` for AKS Automatic.

## Azure Kubernetes Service

### AKS advanced networking controls (2.68.0)

`az aks create` and `az aks update` gain `--enable-acns`; when enabling it,
`--disable-acns-observability` and `--disable-acns-security` can omit the
corresponding ACNS features. `az aks update` also gains `--disable-acns`.

```bash
az aks update --resource-group "$RESOURCE_GROUP" --name "$CLUSTER" \
  --enable-acns --disable-acns-observability
```

### AKS application auto-instrumentation (2.86.0)

`az aks update --enable-azure-monitor-app-monitoring` enables Azure Monitor
Application Monitoring auto-instrumentation on a cluster.

### AKS artifact streaming (2.87.0)

AKS add and update operations accept `--enable-artifact-streaming` and
`--disable-artifact-streaming`, allowing artifact streaming to be toggled
through the CLI.

### AKS Automatic clusters on a bring-your-own VNet (2.86.0)

`az aks create` can combine `--enable-hosted-system`,
`--system-node-subnet-id`, and `--node-subnet-id` to place an Automatic
Managed System Pool cluster on a caller-supplied virtual network.

### AKS bootstrap artifacts and outbound type (2.71.0)

`az aks create` and `az aks update` accept `--bootstrap-artifact-source` and
`--bootstrap-container-registry-resource-id` for selecting the cluster's
bootstrap artifact source and registry. Their `--outbound-type` option also
accepts `none`.

```bash
az aks update --resource-group "$RESOURCE_GROUP" --name "$CLUSTER" \
  --bootstrap-artifact-source "$ARTIFACT_SOURCE" \
  --bootstrap-container-registry-resource-id "$REGISTRY_ID" \
  --outbound-type none
```

### AKS container-network logs and cloud workspaces (2.84.0)

`az aks create` gains `--enable-container-network-logs`; `az aks update` can
toggle the feature with `--enable-container-network-logs` and
`--disable-container-network-logs`. `az aks enable-addons` can now create a
default workspace in the Bleu and Delos clouds.

### AKS control-plane metrics (2.88.0)

AKS create can enable Azure Monitor managed Prometheus control-plane metrics
with `--enable-control-plane-metrics` or `--enable-cp-metrics`; update can
also disable them with `--disable-control-plane-metrics` or
`--disable-cp-metrics`.

### AKS custom-CA removal and advanced network policies (2.79.0)

`az aks update` can remove existing custom CA certificates by passing an empty
file to `--custom-ca-trust-certificates`. AKS create and update also accept
`--acns-advanced-networkpolicies` with `None`, `L7`, or `FQDN`.

### AKS deployment safeguards and run-command policy (2.76.0)

The new `az aks safeguards` group manages deployment safeguards. Creation can
disable run command with `--disable-run-command`, while update can toggle it
with `--disable-run-command` or `--enable-run-command`.

### AKS device-code kubeconfigs (2.78.0)

`az aks get-credentials` converts device-code-mode kubeconfigs to Azure CLI
token format so that conditional-access login does not block them.

### AKS downloads and node-pool choices (2.82.0)

`az aks install-cli` accepts `--gh-token` to authenticate the GitHub download
of `kubelogin`. `az aks nodepool add` and `update` accept `Ubuntu2404` for
`--os-sku`, and node-pool update now accepts `--gpu-driver install` or
`--gpu-driver none`.

### AKS identity bindings (2.89.0)

The new `az aks identity-binding` command group manages identity bindings,
also described as the trust domain, for a managed cluster.

### AKS isolation and node networking (2.80.0)

Cluster and node-pool creation accept `KataVmIsolation` for
`--workload-runtime`; node-pool add and update accept `--localdns-config`.
Service Mesh egress gateways can be managed with
`az aks mesh enable-egress-gateway` and
`az aks mesh disable-egress-gateway`.

### AKS Istio CNI and managed gateways (2.86.0)

`az aks mesh enable` and `az aks mesh proxy-redirection-mechanism` add Istio
CNI management. AKS create/update can toggle Managed Gateway API with
`--enable-gateway-api` or `--disable-gateway-api`, and the App Routing Istio
gateway implementation with `--enable-app-routing-istio` or
`--disable-app-routing-istio`.

### AKS load-balancer SKU migration (2.76.0)

`az aks update` can now migrate a cluster load balancer from Basic to Standard
SKU.

### AKS maintenance-window format (2.88.0)

`az aks maintenanceconfiguration add` and `update` now accept the
`maintenanceWindow` format for the default maintenance configuration.

### AKS managed namespaces (2.80.0)

The new `az aks namespace` group supports `add`, `update`, `show`, `list`,
`delete`, and `get-credentials` operations for managed namespaces.

### AKS message of the day (2.70.0)

`az aks create` and `az aks nodepool add` accept `--message-of-the-day`, so a
message can be configured with either the cluster or a newly added node pool.

### AKS network-family updates and node-resource-group lockdown (2.68.0)

`az aks update` can now change the cluster network with `--ip-families`.
Both create and update accept `--nrg-lockdown-restriction-level` to set the
managed node resource group's restriction level.

### AKS network-integration behavior (2.73.0)

AKS create/update now supports API-server VNet integration. Cluster creation
and app routing also apply a default NIC configuration for app routing.

### AKS networking and high-volume logging (2.85.0)

AKS create/update accepts `--acns-transit-encryption-type` with `WireGuard`
or `None` for pod-to-pod encryption and adds ACNS performance support.
`az aks update` also gains `--enable-http-proxy`, `--disable-http-proxy`, and
`--enable-high-log-scale-mode` for proxy and Container Logs configuration.

### AKS node operating-system choices (2.86.0)

`AzureContainerLinux` is now accepted by `az aks create` and by node-pool
`add` and `update` through `--os-sku`. Node-pool `add` also accepts
`Windows2025`.

### AKS node OS and container-storage validation (2.78.0)

`az aks nodepool add` and `update` accept `AzureLinux3` for `--os-sku`.
Creating a cluster with v1 container storage now fails when the VM SKU is empty.

### AKS node VM-size default (2.73.0)

The `--node-vm-size` default is now an empty string for `az aks create` and
`az aks nodepool add`; pass a value explicitly when provisioning must use a
specific VM size.

### AKS node-pool disruption and soak controls (2.70.0)

`az aks nodepool delete` accepts `--ignore-pod-disruption-budget` when a
deletion must proceed despite PodDisruptionBudgets. An upgrade can now set
`--node-soak-duration` to `0` when no soak interval is wanted.

### AKS node-pool OS, CA trust, and GPU driver controls (2.72.0)

`az aks nodepool add` and `az aks nodepool update` accept `Ubuntu2204` for
`--os-sku`. Cluster creation and node-pool addition gain
`--custom-ca-trust-certificates`, while node-pool addition can explicitly use
`--gpu-driver install` or `--gpu-driver none`.

### AKS node-pool upgrade and rollback (2.88.0)

`az aks nodepool upgrade` no longer silently ignores `--max-unavailable`.
The new `az aks nodepool get-rollback-versions` and `rollback` commands list
rollback versions and restore an agent pool to its most recently used
configuration.

### AKS outbound-type validation (2.89.0)

For `az aks update`, the `userDefinedRouting` and `userAssignedNATGateway`
outbound types no longer require a bring-your-own-VNet cluster to repeat
`--vnet-subnet-id`. Managed-VNet clusters now receive a clear validation
error for these configurations.

### AKS provisioning and observability add-ons (2.76.0)

AKS create/update gains `--node-provisioning-mode`,
`--node-provisioning-default-pools`, and `--enable-ai-toolchain-operator` for
the Kaito add-on. Cluster creation can also configure the Azure Monitor
metrics and logs add-on.

### AKS SSH-key default (2.80.0)

`az aks create` now uses `--no-ssh-key` behavior by default, enacting the
breaking change announced in 2.78.0.

### AKS SSH-key default warning (2.78.0)

This release pre-announces a breaking change to the default behavior of
`az aks create --no-ssh-key`; automation should not rely on its implicit default.

### AKS static egress gateways (2.75.0)

`az aks create` and `az aks update` accept
`--enable-static-egress-gateway`. To add the corresponding gateway node pool,
`az aks nodepool add` accepts `Gateway` for `--mode` together with
`--gateway-prefix-size`.

### AKS upgrade availability controls (2.74.0)

`az aks nodepool add`, `update`, and `upgrade` accept
`--undrainable-node-behavior` to control whether nodes can be cordoned during
an upgrade and `--max-unavailable` to cap simultaneously unavailable nodes by
number or percentage. The preview designation is also removed from
`--enable-high-log-scale-mode` on `az aks create` and `enable-addons`.

### AKS virtual-machine pools and migration (2.76.0)

AKS commands now support Virtual Machines node pools, and `az aks update` can
migrate an agent pool from VMAS to VMS. `az aks machine show/list` also adds
zones to table output.

### App Configuration import from AKS ConfigMaps (2.77.0)

`az appconfig kv import` can now import key-values from an AKS ConfigMap.

### Azure CNI static block allocation (2.75.0)

`az aks create` and `az aks nodepool add` accept
`--pod-ip-allocation-mode` to configure Azure CNI Static Block Allocation.

### ETag-guarded AKS operations (2.69.0)

`az aks create`, `az aks update`, and `az aks delete` accept `--if-match` and
`--if-none-match`, allowing callers to make cluster changes conditional on an
ETag instead of racing concurrent updates.

### Machines-mode agent pools during AKS upgrades (2.89.0)

`az aks upgrade` skips Machines-mode agent pools during both node-image and
Kubernetes-version upgrades.

### Pod Security Standards for AKS safeguards (2.81.0)

`az aks safeguards` adds `--pss-level` for configuring Pod Security Standards.
`az aks safeguards create` also rejects duplicate resource creation during
CLI validation.

## Azure Red Hat OpenShift

### ARO VM SKU selection (2.71.0)

`az aro create` uses an updated VM SKU selection aligned with current best
practices; automation that depends on a particular SKU should choose it
explicitly.

## Container instances and tooling

### Container-group defaults removed (2.76.0)

`az container create` no longer injects its former container-group defaults,
allowing standby-pool reuse. Automation that depended on those CLI defaults
must now pass the required values explicitly.
