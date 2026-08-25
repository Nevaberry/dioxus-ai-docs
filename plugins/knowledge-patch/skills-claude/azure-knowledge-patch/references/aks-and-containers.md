# AKS and containers

## AKS networking and cluster topology

### Network controls and outbound behavior

- In Azure CLI `2.68.0`, create/update add `--enable-acns`; pair it with
  `--disable-acns-observability` or `--disable-acns-security` to omit those
  ACNS features, and use update `--disable-acns` to turn ACNS off. Update can
  change `--ip-families`; create/update set node-resource-group restrictions
  with `--nrg-lockdown-restriction-level`.
- In `2.71.0`, create/update accept `--bootstrap-artifact-source` and
  `--bootstrap-container-registry-resource-id`; `--outbound-type none` is
  valid.
- In `2.73.0`, create/update support API-server VNet integration, and cluster
  creation/app routing apply a default NIC configuration for app routing.
- In `2.75.0`, create/update add `--enable-static-egress-gateway`; add the
  gateway pool with node-pool `--mode Gateway --gateway-prefix-size ...`.
  Create and node-pool add support Azure CNI Static Block Allocation through
  `--pod-ip-allocation-mode`.
- In `2.85.0`, create/update accept `--acns-transit-encryption-type WireGuard`
  or `None` and add ACNS performance support. Update can toggle HTTP proxy with
  `--enable-http-proxy`/`--disable-http-proxy`.
- In `2.86.0`, Automatic Managed System Pool clusters can use a caller VNet by
  combining `--enable-hosted-system`, `--system-node-subnet-id`, and
  `--node-subnet-id`.
- In `2.89.0`, update no longer requires `--vnet-subnet-id` to be repeated for
  `userDefinedRouting` or `userAssignedNATGateway` on BYO-VNet clusters;
  managed-VNet clusters get a clear validation error for these outbound types.

## Node pools, machines, and operating systems

### Pool types and provisioning

- `2.73.0` changes the `--node-vm-size` default on cluster create and node-pool
  add to an empty string. Pass a size when it must be stable.
- `2.76.0` adds Virtual Machines node pools and permits update migration from
  VMAS to VMS. `az aks machine show/list` table output adds zones. Create/update
  also add `--node-provisioning-mode` and `--node-provisioning-default-pools`.
- `2.89.0` cluster upgrades skip Machines-mode pools during both node-image and
  Kubernetes-version upgrades; operate on those pools separately.

### OS, CA, GPU, DNS, and runtime choices

- `2.72.0`: node-pool add/update accept `Ubuntu2204`; cluster create and pool
  add accept `--custom-ca-trust-certificates`; pool add accepts
  `--gpu-driver install|none`.
- `2.78.0`: node-pool add/update accept `AzureLinux3`. Cluster creation with
  v1 container storage fails when the VM SKU is empty.
- `2.79.0`: update removes custom CA certificates when
  `--custom-ca-trust-certificates` points to an empty file.
- `2.80.0`: cluster/pool creation accept `KataVmIsolation` as
  `--workload-runtime`; pool add/update accept `--localdns-config`.
- `2.82.0`: pool add/update accept `Ubuntu2404`; update also accepts
  `--gpu-driver install|none`. `az aks install-cli --gh-token` authenticates
  the GitHub `kubelogin` download.
- `2.86.0`: create and pool add/update accept `AzureContainerLinux`; pool add
  also accepts `Windows2025`.

## Upgrades, disruption, and recovery

### Concurrency and disruption controls

- `2.69.0` cluster create/update/delete support `--if-match` and
  `--if-none-match` for ETag-guarded operations.
- `2.70.0` node-pool delete accepts `--ignore-pod-disruption-budget`; upgrade
  accepts `--node-soak-duration 0` for no soak.
- `2.74.0` node-pool add/update/upgrade add
  `--undrainable-node-behavior` and number-or-percentage `--max-unavailable`.
- `2.88.0` node-pool upgrade no longer ignores `--max-unavailable`. New
  `get-rollback-versions` and `rollback` commands list rollback choices and
  restore the pool's most recently used configuration.

### Load balancer and maintenance migrations

In `2.76.0`, `az aks update` migrates a Basic cluster load balancer to
Standard. In `2.88.0`, maintenance-configuration add/update accept the
`maintenanceWindow` format for the default maintenance configuration.

## Security, policy, and identity

### Run command and safeguards

`2.76.0` adds the `az aks safeguards` group. Cluster creation can set
`--disable-run-command`; update can disable or enable it. `2.81.0` safeguards
adds `--pss-level` for Pod Security Standards, and create rejects duplicate
safeguard resources during CLI validation.

### SSH and conditional access

`2.78.0` announces the coming `--no-ssh-key` default; `2.80.0` enacts it, so
cluster create now behaves as if no SSH key were requested unless configured
otherwise. In `2.78.0`, `az aks get-credentials` converts device-code
kubeconfigs to Azure CLI token format so Conditional Access does not block
them.

### Identity and registry attachment

`2.75.0` adds `--assignee-principal-type` when update uses `--attach-acr`.
`2.89.0` adds `az aks identity-binding` to manage cluster identity bindings,
also called the trust domain.

### Advanced network policy

In `2.79.0`, create/update accept
`--acns-advanced-networkpolicies None|L7|FQDN`.

## Observability, add-ons, and cluster features

- `2.70.0` create and node-pool add accept `--message-of-the-day`.
- `2.74.0` removes preview status from `--enable-high-log-scale-mode` on
  cluster create and add-on enablement.
- `2.76.0` create/update add `--enable-ai-toolchain-operator` for Kaito;
  creation can configure Azure Monitor metrics and logs.
- `2.77.0` create/update accept `--sku` for AKS Automatic.
- `2.80.0` adds `az aks namespace add/update/show/list/delete/get-credentials`
  for managed namespaces. Mesh egress gateways use
  `az aks mesh enable-egress-gateway` and `disable-egress-gateway`.
- `2.84.0` create enables container-network logs; update enables or disables
  them. Add-on enablement can create a default workspace in Bleu and Delos.
- `2.85.0` update adds `--enable-high-log-scale-mode` for Container Logs.
- `2.86.0` update `--enable-azure-monitor-app-monitoring` enables application
  auto-instrumentation. `az aks mesh enable` and
  `mesh proxy-redirection-mechanism` manage Istio CNI. Create/update toggle
  Managed Gateway API and App Routing's Istio gateway with the corresponding
  `--enable-*` and `--disable-*` switches.
- `2.87.0` add/update toggle artifact streaming with
  `--enable-artifact-streaming` and `--disable-artifact-streaming`.
- `2.88.0` create enables managed Prometheus control-plane metrics with
  `--enable-control-plane-metrics` or `--enable-cp-metrics`; update can also
  disable them with either long or short form.

## Azure Container Storage

`2.77.0` create/update can install the latest acstor with
`--enable-azure-container-storage`; `--container-storage-version` pins a
release, and update `--disable-azure-container-storage` removes it regardless
of installed version.

`2.83.0` defines ACStor v2 behavior: value-less enable on a new cluster enables
v2 without a storage option; on an existing cluster, enable with
`ephemeralDisk`, disable with `elasticSan`, or use value-less disable to remove
v2 entirely.

## Azure Container Registry

### Registry creation, endpoints, and login

- `2.72.0` registry create/check-name accept `--dnl-scope` for domain-label
  hash scope.
- `2.74.0` `az acr login --expose-token` output adds `refreshToken` and
  `username`; update fixed-schema consumers.
- `2.82.0` ACR login enforces the ACR audience for its Entra token.
- `2.85.0` replication create/update add `--global-endpoint-routing`;
  `--region-endpoint-enabled` redirects to it and is distinct from registry
  `--regional-endpoints`.
- `2.86.0` login supports Podman. `show-endpoints` displays regional endpoint
  hosts; `login --endpoint` selects one, and import accepts a regional endpoint
  URI.
- `2.87.0` login can customize its Entra token audience; registry update adds
  `--endpoint-protocol`.
- `2.88.0` registry create adds `--data-endpoint-enabled` for a dedicated data
  endpoint and can select `--endpoint-protocol` at creation.
- `2.89.0` registry create/update add `--writable-cache-repo`.

### Cache, connected registries, ABAC, and tasks

`2.71.0` allows a credentialless cache rule. In `2.73.0`, connected-registry
create/update add `--gc-enabled` and cron `--gc-schedule`; registry
create/update add `--role-assignment-mode` for ABAC; `check-health
--repository` tests one repository's read/write/delete permissions; ACR task
create/update/build/run add `--source-acr-auth-id` for source authentication.
In `2.85.0`, cache-rule create/update accepts a user-assigned `--identity`.

### Content trust transition

`2.79.0` deprecates `az acr config content-trust` show/update. `2.83.0`
announces that content-trust update will stop accepting status `enabled`, and
that `az acr check-health` will remove its Notary client check. Do not create
new automation dependencies on either behavior.

## Container Apps and jobs

### Environments and ingress

- `2.79.0` adds environment `http-route-config` and `premium-ingress` groups.
- `2.80.0` premium-ingress operations remove `--min-replicas` and
  `--max-replicas`.
- `2.82.0` environment create accepts `--infrastructure-resource-group`.
- `2.85.0` workload-profile add supplies a default profile name if omitted;
  pass one explicitly for deterministic naming.

### Apps, Compose, and registries

`2.69.0` Compose create splits environment assignments only at the first `=`,
so values may contain equals signs. In `2.79.0`, registry show handles apps
without a registry server. In `2.86.0`, app creation supports ACR references
from another Azure cloud instead of assuming the default cloud.

### Jobs and defaults

`2.77.0` job list is no longer capped at 20 items; job update accepts `0` for
both minimum and maximum executions. `2.84.0` job create supplies defaults for
parallelism and replica completion count; pass both explicitly if those
defaults must not drift.

## Container Instances and Service Fabric

### Container group defaults

In `2.76.0`, `az container create` stops injecting the old container-group
defaults to permit standby-pool reuse. Supply required values explicitly.

### Service Fabric

- `2.76.0` managed-cluster NSG rules accept source/destination address prefixes
  and port ranges; managed-node-type update can change VM size and tags.
- `2.77.0` cluster create honors `cluster_name` from a parameter file.
- `2.80.0` removes several managed-application update options:
  `--service-type-policy`, `--upgrade-replica-set-check-timeout`, and the four
  misspelled `--max-porcent-unhealthy-*` options. Application update removes
  service-type policy, upgrade timeout, instance-close duration,
  warning-as-error, and its unhealthy partitions/replicas/deployed-applications
  percentage options.
