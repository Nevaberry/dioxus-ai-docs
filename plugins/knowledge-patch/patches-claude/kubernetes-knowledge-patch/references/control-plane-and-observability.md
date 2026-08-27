# Control Plane and Observability

Use this reference for API-server request handling, feature gates, metrics,
diagnostic endpoints, mixed-version control planes, leader election, and audit.

## Watches, lists, and API Priority and Fairness

### Follow the WatchList default transition (1.33.0, 1.34-guide)

The beta server `WatchList` feature was disabled by default in 1.33 while
streaming JSON and protobuf collection encoding replaced the old initial-list
path. In 1.34, kube-apiserver and kube-controller-manager use WatchList by
default. Test memory, latency, and client compatibility before overriding the
current behavior.

`WatchFromStorageWithoutResourceVersion` can no longer be enabled.
`StorageNamespaceIndex` and `SeparateCacheWatchRPC` are deprecated and default
off. Kube-controller-manager no longer opts into `WatchListClient` separately.

### Charge large LIST requests by memory (1.34.0)

Default-on `SizeBasedListCostEstimate` charges one APF seat per 100 KB loaded
into memory, up to 100 seats. Capacity planning and priority-level limits must
account for large initial lists.

## Feature-gate and API cleanup

### Remove obsolete API versions (1.33.0)

`apidiscovery.k8s.io/v2beta1` is disabled by default. The `v1alpha1`
`ValidatingAdmissionPolicy` and `ValidatingAdmissionPolicyBinding` APIs are no
longer served.

### Remove graduated gate names (1.33.0, 1.34.0)

Do not name `CPUManager`, `PDBUnhealthyPodEvictionPolicy`,
`PersistentVolumeLastPhaseTransitionTime`, `AppArmor`, `AppArmorFields`,
`KubeProxyDrainingTerminatingNodes`, `JobPodFailurePolicy`,
`DevicePluginCDIDevices`, or `PodDisruptionConditions` in component
configuration. Kubeadm also removes `EtcdLearnerMode`.

### Remove later switches (1.35.0)

Delete `StrictCostEnforcementForVAP`, `StrictCostEnforcementForWebhooks`,
`SizeMemoryBackedVolumes`, `ComponentSLIs`,
`UserNamespacesPodSecurityStandards`, and kubeadm
`WaitForAllControlPlaneComponents`. `KUBECTL_OPENAPIV3_PATCH` is removed.

### Satisfy feature dependencies (1.35.0)

Components reject an enabled feature whose dependency is disabled.
`AllAlpha=true` can require `AllBeta=true` or explicit enablement of particular
default-off beta dependencies.

### Remove cloud-provider flags (1.33.0)

Kube-apiserver no longer accepts `--cloud-provider` or `--cloud-config`. The
`DisableCloudProviders` and `DisableKubeletCloudCredentialProviders` gates are
also gone; use external cloud integration.

## Leader election and mixed-version control planes

### Coordinate leader candidates (1.33.0)

Beta `CoordinatedLeaderElection` introduces the
`coordination.k8s.io/v1beta1` `LeaseCandidate` API for participants in a
coordinated election.

### Use Lease locks (1.34.0)

The default APF configuration no longer includes `endpoint-controller` and
`workload-leader-election` FlowSchemas. Migrate lock types from
`configmapsleases` and `endpointsleases` to `leases`.

### Configure peer trust for version-skew proxying (1.36-guide, 1.36.0)

The beta mixed-version proxy uses peer-aggregated discovery to route an unknown
group/version/resource request to a peer that serves it. Even though
`UnknownVersionInteroperabilityProxy` is enabled by default, proxying activates
only when kube-apiserver has `--peer-ca-file`. Monitor rerouted-request metrics.

## Metrics and diagnostics

### Migrate scheduler metrics (1.33.0)

Replace `pod_scheduling_duration_seconds` with
`pod_scheduling_sli_duration_seconds`. Replace deprecated
`scheduler_scheduler_cache_size` with `scheduler_cache_size`.

### Separate API groups from resource labels (1.34.0)

Update queries and alerts for these label changes:

- Cache LIST metrics replace `resource_prefix` with `group` and `resource`.
- Etcd request metrics replace `type` with `group` and `resource`.
- Watch metrics replace `kind` with `resource`.
- Storage and watch-cache metrics move API groups out of `resource`.
- Replace deprecated `apiserver_storage_objects` with
  `apiserver_resource_objects`.
- Replace the separate encryption reload success and failure counters with
  `apiserver_encryption_config_controller_automatic_reloads_total`.

### Use structured flag and status endpoints (1.35-guide, 1.36-guide)

Authorized clients can negotiate machine-readable `/flagz` and `/statusz`.
They are beta and default-on across core control-plane and node components,
authorize `system:monitoring`, and return `config.k8s.io/v1beta1` JSON, YAML,
or CBOR as well as text. `/flagz` retains human-readable text.

### Consider native histograms (1.36-guide)

Alpha native-histogram support lets components export sparse histograms with
adaptive resolution. Validate backend and query compatibility before replacing
classic fixed buckets.

### Apply the latest metric removals (1.36.0)

Rename `volume_operation_total_errors` to `volume_operation_errors_total` and
`etcd_bookmark_counts` to `etcd_bookmark_total`. Remove cAdvisor queries for the
always-zero `container_cpu_load_average_10s`,
`container_cpu_load_d_average_10s`, and `cpu_tasks_state` metrics.

## Audit retention

### Update matching and rotation semantics (1.36.0)

Audit resource rules may use `group: "*"` to match every API group.
`--audit-log-maxsize=0` disables rotation. Defaults are
`--audit-log-maxage=366` and `--audit-log-maxbackup=100`; explicitly set both
pruning controls to `0` to retain every rotated log.
