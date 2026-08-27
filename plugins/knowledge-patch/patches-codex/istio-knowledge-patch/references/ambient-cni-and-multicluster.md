# Ambient, CNI, and Multicluster

Use this reference for ambient enrollment and capture, ztunnel behavior,
waypoints, CNI repair, and multicluster traffic.

## Contents

- [Enrollment, capture, and reconciliation](#enrollment-capture-and-reconciliation)
- [Packet redirection and CNI ownership](#packet-redirection-and-cni-ownership)
- [Ambient service discovery and waypoint behavior](#ambient-service-discovery-and-waypoint-behavior)
- [Multicluster and remote networks](#multicluster-and-remote-networks)
- [Mixed-version rollout caveats](#mixed-version-rollout-caveats)

## Enrollment, capture, and reconciliation

### Ambient pod iptables reconciliation on istio-cni startup (upgrade-1.25)

An istio-cni DaemonSet pod can inspect previously enrolled ambient pods at
startup and update in-pod iptables rules when they differ. This is disabled by
default in 1.25.0. Enable it with
`helm install cni --set ambient.reconcileIptablesOnStartup=true` or
`istioctl install --set values.cni.ambient.reconcileIptablesOnStartup=true`.

### Ambient DNS capture is enabled by default (upgrade-1.25)

DNS proxying is enabled by default for newly created ambient workloads. Existing
pods do not gain DNS capture until restarted or reconciled during an istio-cni
upgrade with `--set cni.ambient.reconcileIptablesOnStartup=true`. Opt a pod out
with `ambient.istio.io/dns-capture=false`.

### DNS traffic honors pod traffic exclusions (upgrade-1.25)

TCP and UDP DNS traffic respects pod annotations including
`traffic.sidecar.istio.io/excludeOutboundIPRanges` and
`traffic.sidecar.istio.io/excludeOutboundPorts`. UDP/DNS previously ignored
these exclusions; the behavior entered the 1.23 series despite being absent
from that release's notes.

### Ambient iptables reconciliation enabled by default (upgrade-1.29)

Startup reconciliation of ambient pod iptables or nftables rules is enabled by
default. Disable it with
`--set cni.ambient.reconcileIptablesOnStartup=false`.

### Retrying ambient enrollment detection (1.29.0)

Set `ambient.enableAmbientDetectionRetry` in the istio-cni chart to retry
transient failures while determining whether a pod is ambient-enabled. The
retry is disabled by default; enabling it reduces the risk of mesh bypass.

### CNI agent honors excluded namespaces (upgrade-1.30)

The CNI agent applies `excludeNamespaces` as well as the CNI plugin. Existing
ambient-enrolled pods in an excluded namespace are un-enrolled, and new
ambient-labeled pods there are not enrolled.

## Packet redirection and CNI ownership

### Native nftables redirection in sidecar mode (1.27.0)

Sidecar-mode installations can use native nftables instead of iptables for pod
and service redirection. Enable it at installation with
`--set values.global.nativeNftables=true`.

### Istio-owned ambient CNI configuration (1.27.0)

Set `cni.istioOwnedCNIConfig=true` in the istio-cni chart to create an
Istio-owned conflist containing both the primary CNI configuration and Istio's
plugin. This prevents mesh bypass when the Istio CNI DaemonSet is unavailable
during node startup. The default filename is `02-istio-cni.conflist`; a custom
`cni.istioOwnedCNIConfigFilename` must have higher lexicographical priority than
the primary CNI file. Both ambient and chained CNI must be enabled.

### Native nftables in ambient mode (1.28.0)

Ambient installations can use native nftables redirection by setting
`values.global.nativeNftables=true`.

### Forced iptables binary (1.28.0)

`FORCE_IPTABLES_BINARY` overrides iptables backend detection and selects a
specific binary.

## Ambient service discovery and waypoint behavior

### Ambient ExternalName resolution (1.25.0)

Ambient mode with DNS proxying can resolve Kubernetes `ExternalName` services.

### Ambient port-level STRICT mTLS enforcement (1.25.0)

Multiple port-level `STRICT` rules in an ambient `PeerAuthentication` policy
enforce strict mTLS. Previously, their evaluation could make the effective
policy permissive.

### TCPRoute support in waypoints (1.26.0)

Waypoint proxies can process Gateway API `TCPRoute` resources.

### Wildcard DYNAMIC_DNS ServiceEntries (1.28.0)

`ServiceEntry` resources using `DYNAMIC_DNS` resolution can use wildcard hosts.
This requires ambient mode, an egress waypoint, and HTTP traffic.

### WorkloadEntry port maps in ztunnel (1.28.0)

ztunnel honors a `WorkloadEntry` port map when the corresponding `Service` port
is referenced by name.

### Waypoint termination grace period (1.28.0)

Waypoint deployments use Kubernetes' default `terminationGracePeriodSeconds`
of 30 seconds instead of hard-coding 2 seconds.

### Safe ambient dry-run policy upgrades (upgrade-1.29)

Enable experimental dry-run `AuthorizationPolicy` support for ztunnel with
`AMBIENT_ENABLE_DRY_RUN_AUTHORIZATION_POLICY=true` on istiod. Enable it only
after every connected ztunnel is at least 1.29: older ztunnels do not understand
the new xDS field and fully enforce policies intended only for dry-run.

### Canonical WDS service selection (1.29.0)

ztunnel uses a canonical Workload Discovery Service for name resolution unless
a service in the client's namespace overrides it. The canonical service is
selected from a Kubernetes `Service` or the oldest `ServiceEntry` that specifies
the hostname.

### Ambient CIDR ServiceEntries (1.30.0)

Ambient `ServiceEntry` addresses may be CIDRs such as `10.0.0.0/24`; istiod
propagates them to ztunnel for longest-prefix-match routing.

### Ambient XFCC synthesis (1.30.0)

Annotate a waypoint `Gateway` or its `GatewayClass` with
`ambient.istio.io/xfcc-include-client-identity: "true"` to replace any inbound
`x-forwarded-client-cert` with a value populated from the source workload's
ztunnel-provided SPIFFE identity.

## Multicluster and remote networks

### Ambient multicluster service scoping (1.27.0)

The alpha `MeshConfig.serviceScopeConfigs` API can select services or namespaces
as local or global. Local services are discoverable only within their cluster;
global services are mesh-wide. Its selectors also determine shared workloads
and the cluster and listener configuration generated for waypoints, including
east-west gateways.

### Local sidecar injector in a remote cluster (1.27.0)

With `profile=remote`, set
`.Values.istiodRemote.enabledLocalInjectorIstiod=true` and
`.Values.global.remotePilotAddress="${DISCOVERY_ADDRESS}"` to install a local
istiod for sidecar injection while continuing to obtain xDS from the remote
primary cluster.

### Remote-network routing through waypoints (1.28.0)

Waypoints in an ambient multicluster mesh can route traffic to remote networks.

### Ambient multicluster ingress opt-in (1.29.0)

Ingress gateways can route to exposed remote backends in ambient multicluster
deployments when `AMBIENT_ENABLE_MULTI_NETWORK_INGRESS=true`; the flag defaults
to `false`.

### Filesystem-backed multicluster registrations (1.30.0)

Set `PILOT_MULTICLUSTER_KUBECONFIG_PATH` to a mounted directory to have istiod
watch `.yaml` and `.yml` keys and dynamically update remote-cluster
registrations. This takes precedence over `LOCAL_CLUSTER_SECRET_WATCHER`.

### East-west gateway TLS passthrough (1.30.0)

With `AMBIENT_ENABLE_MULTI_NETWORK` enabled, east-west gateways can expose
non-HBONE TLS passthrough ports through Gateway API resources.

## Mixed-version rollout caveats

### Ambient PASSTHROUGH ServiceEntry rollout behavior (upgrade-1.28)

ServiceEntries with `resolution: NONE` use a new `PASSTHROUGH` service type that
older ztunnel images NACK during a mixed-version upgrade. Existing configuration
then remains unchanged. A newly added ServiceEntry is treated as absent, so
traffic passes through without ztunnel determining whether a waypoint is
required until ztunnel is upgraded.
