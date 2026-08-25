# Control Plane and Observability

## API-server behavior and flow control

### API-server watch and cache gates change defaults (1.33.0)

`WatchFromStorageWithoutResourceVersion` cannot be enabled.
`StorageNamespaceIndex` and `SeparateCacheWatchRPC` are deprecated and default
off. The server-side `WatchList` feature is disabled by default in this release
in favor of streaming JSON and Protobuf collection encoding, and
kube-controller-manager no longer opts into `WatchListClient`.

### Core components use WatchList by default (1.34-guide)

The beta streaming informer mechanism is used by kube-apiserver and
kube-controller-manager by default, reducing large initial-list memory spikes.
This is the later transition from the 1.33 defaults above.

### Large LIST requests consume APF seats by size (1.34.0)

Default-on `SizeBasedListCostEstimate` charges one API Priority and Fairness seat
per 100 KB loaded into memory by a LIST request; the maximum LIST seat count is
100.

### Mixed-version API servers can proxy unknown resources (1.36-guide)

The beta proxy uses peer-aggregated discovery to route a request to a peer that
serves the requested group, version, and resource. This reduces version-skew
failures during control-plane upgrades and exposes reroute metrics.

### The mixed-version proxy still needs peer trust (1.36.0)

Although `UnknownVersionInteroperabilityProxy` is beta and enabled by default,
peer proxying activates only when kube-apiserver has `--peer-ca-file`.

## Configuration and lifecycle

### Cloud-provider flags are removed from kube-apiserver (1.33.0)

Remove `--cloud-provider` and `--cloud-config`; the `DisableCloudProviders` and
`DisableKubeletCloudCredentialProviders` gates are also gone.

### Graduated feature-gate names are removed (1.33.0)

Stop naming `CPUManager`, `PDBUnhealthyPodEvictionPolicy`,
`PersistentVolumeLastPhaseTransitionTime`, `AppArmor`, `AppArmorFields`,
`KubeProxyDrainingTerminatingNodes`, and `JobPodFailurePolicy`. Kubeadm also
removes `EtcdLearnerMode`.

### Graduated feature-gate names are removed (1.34.0)

Stop naming `DevicePluginCDIDevices` and `PodDisruptionConditions`.

### Removed switches require configuration cleanup (1.35.0)

Remove `StrictCostEnforcementForVAP`, `StrictCostEnforcementForWebhooks`,
`SizeMemoryBackedVolumes`, `ComponentSLIs`, `UserNamespacesPodSecurityStandards`,
and kubeadm `WaitForAllControlPlaneComponents`. The
`KUBECTL_OPENAPIV3_PATCH` environment switch is removed too.

### Feature-gate dependencies are validated at startup (1.35.0)

Components reject enabled features whose dependencies are disabled.
`AllAlpha=true` can therefore require `AllBeta=true` or explicit enabling of
disabled-by-default beta dependencies.

### Old leader-election locks lose their APF defaults (1.34.0)

The default APF configuration drops the `endpoint-controller` and
`workload-leader-election` FlowSchemas. Migrate lock types from
`configmapsleases` or `endpointsleases` to `leases`.

### Coordinated leader election is beta (1.33.0)

`CoordinatedLeaderElection` introduces the `coordination.k8s.io/v1beta1`
`LeaseCandidate` API for coordinated-election participants.

## Metrics, logs, and diagnostics

### Scheduler metrics require migration (1.33.0)

Replace `pod_scheduling_duration_seconds` with
`pod_scheduling_sli_duration_seconds`, and replace the deprecated
`scheduler_scheduler_cache_size` with `scheduler_cache_size`.

### API-server metrics split API groups from resources (1.34.0)

Cache LIST metrics replace `resource_prefix` with `group` and `resource`; etcd
request metrics replace `type` with those labels; watch metrics replace `kind`
with `resource`; and storage/watch-cache metrics move the API group out of
`resource`. Replace deprecated `apiserver_storage_objects` with
`apiserver_resource_objects`. The encryption reload success/failure counters are
replaced by `apiserver_encryption_config_controller_automatic_reloads_total`.

### Component diagnostics can return JSON (1.35-guide)

Authorized clients can negotiate versioned, machine-readable JSON from alpha
`/flagz` and `/statusz`; `/flagz` retains plain text for people.

### Component flag and status endpoints are beta and default-on (1.36-guide)

`/flagz` and `/statusz` are available across core control-plane components and
node agents, authorize `system:monitoring`, and emit structured
`config.k8s.io/v1beta1` JSON, YAML, or CBOR as well as text.

### Core component metrics can use native histograms (1.36-guide)

Alpha native-histogram support exports sparse, dynamically resolved histograms
instead of fixed Prometheus buckets for latency distributions.

### Monitoring configurations need metric updates (1.36.0)

Rename `volume_operation_total_errors` to `volume_operation_errors_total` and
`etcd_bookmark_counts` to `etcd_bookmark_total`. cAdvisor stops reporting the
always-zero `container_cpu_load_average_10s`,
`container_cpu_load_d_average_10s`, and `cpu_tasks_state` metrics.

### Node log queries require an explicit kubelet option (1.36-guide)

`NodeLogQuery` is GA and its gate is on, but kubelet must set
`enableSystemLogQuery: true`; queried services must write below `/var/log`.

### Kubelet exports cgroup v2 pressure metrics (1.36-guide)

Stable PSI metrics report CPU, memory, and I/O contention, distinguishing
ordinary utilization from actively stalled workloads.

## Operational policy

### Audit policy and retention semantics changed (1.36.0)

Audit resource rules may use `group: "*"`. `--audit-log-maxsize=0` disables
rotation. Defaults are `--audit-log-maxage=366` and
`--audit-log-maxbackup=100`; set both pruning controls explicitly to `0` to
retain every rotated log.

### Admission control can use a unified manifest (1.36-guide)

Alpha manifest-based admission configuration places plugins and settings in one
structured, versioned manifest instead of distributing them among flags and
separate plugin files.
