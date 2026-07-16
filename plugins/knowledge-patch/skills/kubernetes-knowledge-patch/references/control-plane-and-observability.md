# Control Plane and Observability

Use this reference for control-plane configuration, watch and cache behavior, metrics, diagnostics, feature gates, and upgrade-time component changes.

Entries are grouped by task; the parenthetical identifier is the source batch.

## API-server metrics split API groups from resources (1.34.0)

Update dashboards and alerts: cache LIST metrics replace `resource_prefix` with `group` and `resource`, etcd request metrics replace `type` with those labels, watch metrics replace `kind` with `resource`, and many storage and watch-cache metrics now move the API group out of `resource`. `apiserver_storage_objects` is deprecated for `apiserver_resource_objects`, while the separate encryption-config reload success and failure counters are removed for `apiserver_encryption_config_controller_automatic_reloads_total`.

## API-server watch and cache gates change defaults (1.33.0)

`WatchFromStorageWithoutResourceVersion` can no longer be enabled, while `StorageNamespaceIndex` and `SeparateCacheWatchRPC` are deprecated and default off. The beta `WatchList` server feature is also disabled by default in favor of streaming JSON and Protobuf collection encoding, and kube-controller-manager no longer opts into `WatchListClient`.

## Cloud-provider flags are removed from kube-apiserver (1.33.0)

The deprecated `--cloud-provider` and `--cloud-config` flags are gone, along with the `DisableCloudProviders` and `DisableKubeletCloudCredentialProviders` feature gates.

## Component diagnostics can return JSON (1.35-guide)

Authorized clients can use HTTP content negotiation to obtain versioned, machine-readable JSON from the alpha `/flagz` and `/statusz` endpoints; `/flagz` retains its plain-text form for people.

## Component flag and status endpoints are beta and default-on (1.36-guide)

`/flagz` and `/statusz` are enabled across core control-plane components and node agents, authorize the `system:monitoring` group, and offer structured `config.k8s.io/v1beta1` output in JSON, YAML, or CBOR as well as text.

## Coordinated leader election is beta (1.33.0)

The beta `CoordinatedLeaderElection` feature introduces the `coordination.k8s.io/v1beta1` `LeaseCandidate` API for participants in coordinated elections.

## Core component metrics can use native histograms (1.36-guide)

Alpha native-histogram support lets Kubernetes components export sparse histograms whose resolution adjusts dynamically, avoiding the fixed bucket layout of classic Prometheus histograms for latency distributions.

## Core components use WatchList by default (1.34-guide)

After being disabled by default in 1.33, the beta streaming informer mechanism is used by both kube-apiserver and kube-controller-manager by default in 1.34, reducing memory spikes during large initial lists.

## Feature-gate dependencies are validated at startup (1.35.0)

A component now rejects an enabled feature whose dependency is disabled. In particular, `AllAlpha=true` may also require `AllBeta=true` or explicit enablement of the disabled-by-default beta dependencies.

## Graduated feature-gate names are removed (1.33.0)

Configurations must stop naming `CPUManager`, `PDBUnhealthyPodEvictionPolicy`, `PersistentVolumeLastPhaseTransitionTime`, `AppArmor`, `AppArmorFields`, `KubeProxyDrainingTerminatingNodes`, and `JobPodFailurePolicy`; kubeadm also removes `EtcdLearnerMode`.

## Graduated feature-gate names are removed (1.34.0)

Component configurations must stop naming `DevicePluginCDIDevices` and `PodDisruptionConditions` because those GA feature gates no longer exist.

## Large LIST requests consume APF seats by size (1.34.0)

The default-on `SizeBasedListCostEstimate` gate charges one API Priority and Fairness seat per 100 KB loaded into memory by a LIST request, and the maximum LIST seat count rises to 100.

## Mixed-version API servers can proxy unknown resources (1.36-guide)

The beta mixed-version proxy uses peer-aggregated discovery to route a request to an API server that serves its requested group, version, and resource, reducing version-skew failures during control-plane upgrades and exposing metrics for rerouted traffic.

## Monitoring configurations need metric updates (1.36.0)

Rename `volume_operation_total_errors` to `volume_operation_errors_total` and `etcd_bookmark_counts` to `etcd_bookmark_total` in dashboards and alerts. cAdvisor also stops reporting the always-zero `container_cpu_load_average_10s`, `container_cpu_load_d_average_10s`, and `cpu_tasks_state` metrics.

## Namespace deletion removes Pods first (1.33.0)

The alpha `OrderedNamespaceDeletion` gate is enabled by default and deletes Pods before other namespaced resources, changing cleanup ordering for finalizers and dependent resources.

## Old leader-election locks lose their APF defaults (1.34.0)

The default APF configuration no longer includes the `endpoint-controller` and `workload-leader-election` FlowSchemas. Workloads should migrate leader-election lock types from `configmapsleases` or `endpointsleases` to `leases`.

## Removed switches require configuration cleanup (1.35.0)

Remove the `StrictCostEnforcementForVAP`, `StrictCostEnforcementForWebhooks`, `SizeMemoryBackedVolumes`, `ComponentSLIs`, `UserNamespacesPodSecurityStandards`, and kubeadm `WaitForAllControlPlaneComponents` feature gates. The `KUBECTL_OPENAPIV3_PATCH` environment switch is also removed.

## Scheduler metrics require migration (1.33.0)

`pod_scheduling_duration_seconds` is removed in favor of `pod_scheduling_sli_duration_seconds`, and `scheduler_scheduler_cache_size` is deprecated for removal in 1.34 in favor of `scheduler_cache_size`.

## The mixed-version proxy still needs peer trust (1.36.0)

Although `UnknownVersionInteroperabilityProxy` is beta and enabled by default, kube-apiserver activates peer proxying only when `--peer-ca-file` is configured.

