# Ambient mesh and multicluster

Use this reference for ztunnel enrollment, waypoint behavior, ambient service
discovery, and remote-cluster routing. Roll out features only after all
participating ztunnels understand their xDS representation.

## DNS capture and ambient enrollment

- (`upgrade-1.25`) DNS proxying is enabled by default for newly created ambient
  workloads. Existing pods gain capture only after restart or CNI startup
  reconciliation. Set `ambient.istio.io/dns-capture=false` on a pod to opt out.
- (`upgrade-1.25`) Both TCP and UDP DNS honor pod exclusions such as
  `traffic.sidecar.istio.io/excludeOutboundIPRanges` and
  `traffic.sidecar.istio.io/excludeOutboundPorts`.
- (`1.25.0`) Ambient DNS proxying resolves Kubernetes `ExternalName` Services.
- (`upgrade-1.29`) Ambient pod iptables or nftables startup reconciliation is
  enabled by default; set `cni.ambient.reconcileIptablesOnStartup=false` to
  disable it.
- (`1.29.0`) Enable retry of transient ambient-enrollment detection failures
  with `ambient.enableAmbientDetectionRetry` in the istio-cni chart. It is off
  by default.
- (`upgrade-1.30`) The CNI agent honors `excludeNamespaces`: existing ambient
  pods in an excluded namespace are un-enrolled, and new labeled pods are not
  enrolled.

## Waypoint selection and policy

- (`1.25.0`) Attach default policies to the `istio-waypoint` `GatewayClass`.
- (`1.25.0`) Set `istio.io/ingress-use-waypoint` at namespace scope to select
  ingress waypoint behavior for that namespace.
- (`1.26.0`) Waypoint proxies process Gateway API `TCPRoute` resources.
- (`1.28.0`) Waypoints route traffic to remote networks in ambient multicluster
  meshes.
- (`1.28.0`) Waypoint Deployments now use the Kubernetes default 30-second
  termination grace period instead of two seconds.
- (`1.29.0`) `istioctl waypoint status --wait=false` returns current status
  without waiting for readiness; `--all-namespaces` lists every namespace.
- (`1.30.0`) Annotate a waypoint `Gateway` or `GatewayClass` with
  `ambient.istio.io/xfcc-include-client-identity: "true"` to replace inbound
  `x-forwarded-client-cert` with a value synthesized from the source workload's
  ztunnel-provided SPIFFE identity.
- (`1.30.0`) `WorkloadEntry` status includes `WaypointBound` to report a
  successful attachment or binding error.

## Service discovery in ambient mode

- (`1.25.0`) Addressless `ServiceEntry` resources receive auto-allocated IPs in
  `status.addresses` because `PILOT_ENABLE_IP_AUTOALLOCATE` defaults to `true`.
  Proxies use these addresses only with DNS proxying.
- (`1.27.0`) Set `PILOT_IP_AUTOALLOCATE_IPV4_PREFIX` and
  `PILOT_IP_AUTOALLOCATE_IPV6_PREFIX` to choose the CIDR prefixes used by the
  `ipallocate` controller.
- (`1.28.0`) ztunnel honors a `WorkloadEntry` port map when the associated
  Service port is referenced by name.
- (`1.29.0`) ztunnel uses a canonical Workload Discovery Service for name
  resolution unless a Service in the client's namespace overrides it. The
  canonical candidate is a Kubernetes Service or the oldest `ServiceEntry`
  specifying the hostname.
- (`1.30.0`) Ambient `ServiceEntry.spec.addresses` may contain CIDRs such as
  `10.0.0.0/24`; istiod sends them to ztunnel for longest-prefix-match routing.

## PASSTHROUGH and dynamic DNS

- (`upgrade-1.28`) A `ServiceEntry` with `resolution: NONE` becomes the new
  `PASSTHROUGH` service type. During a mixed-version rollout, an older ztunnel
  NACKs it. Existing configuration remains, but a new ServiceEntry behaves as
  absent until ztunnel advances, allowing pass-through without waypoint
  determination.
- (`1.28.0`) Wildcard hosts with `resolution: DYNAMIC_DNS` initially require
  ambient mode, an egress waypoint, and HTTP traffic.
- (`1.29.0`) Wildcard `DYNAMIC_DNS` hosts can route TLS by SNI without TLS
  termination when
  `ENABLE_WILDCARD_HOST_SERVICE_ENTRIES_FOR_TLS=true`. This alpha behavior is
  off by default. Enable it only for trusted clients because SNI selects the
  route.
- (`1.30.0`) Sidecars also support wildcard `DYNAMIC_DNS` ServiceEntries for
  `MESH_INTERNAL` and `MESH_EXTERNAL`, using HTTP Host or TLS SNI routing. The
  same client-spoofing warning applies.

## Service scope and traffic distribution

- (`1.25.0`) Kubernetes `Service.spec.trafficDistribution` and the
  `networking.istio.io/traffic-distribution` annotation apply across all data
  planes, not only ztunnel.
- (`1.27.0`) `PreferSameNode` and `PreferSameZone` are supported. `PreferClose`
  ignores subzone when choosing nearby endpoints.
- (`1.27.0`) Alpha `MeshConfig.serviceScopeConfigs` selectors mark services or
  namespaces local or global. Local services are discoverable only within the
  cluster; global services are mesh-wide. The same selectors decide which
  workloads are shared and drive waypoint cluster/listener configuration,
  including east-west gateways.
- (`1.30.0`) Set `networking.istio.io/traffic-distribution` on a namespace to
  provide a default inherited by Services without their own distribution
  setting.

## Cross-network and remote-cluster routing

- (`1.27.0`) A remote-cluster installation can run a local injector while
  receiving xDS from the primary. With `profile=remote`, set
  `.Values.istiodRemote.enabledLocalInjectorIstiod=true` and
  `.Values.global.remotePilotAddress="${DISCOVERY_ADDRESS}"`.
- (`1.28.0`) The istiod chart creates `EndpointSlice` rather than `Endpoints`
  for remote-istiod installations.
- (`1.29.0`) Ambient ingress gateways can reach exposed remote backends when
  `AMBIENT_ENABLE_MULTI_NETWORK_INGRESS=true`; the flag defaults to `false`.
- (`1.30.0`) With `AMBIENT_ENABLE_MULTI_NETWORK`, east-west gateways expose
  non-HBONE TLS passthrough ports through Gateway API resources.
- (`1.30.0`) Set `PILOT_MULTICLUSTER_KUBECONFIG_PATH` to a mounted directory for
  filesystem-backed cluster registrations. istiod watches `.yaml` and `.yml`
  keys and updates registrations dynamically; this takes precedence over
  `LOCAL_CLUSTER_SECRET_WATCHER`.
- (`1.29.0`) Monitor `istiod_remote_cluster_sync_status`, a Pilot gauge for
  remote-cluster synchronization.
- (`1.30.0`) `global.enableReaderRBAC` controls the reader service account,
  `ClusterRole`, and `ClusterRoleBinding` used by the remote-secret workflow.
  It defaults to `true`; set it to `false` on both base and istiod charts to
  disable all split resources.

## Cross-network telemetry

- (`1.29.0`) Set `AMBIENT_ENABLE_BAGGAGE=true` on Pilot to enable
  waypoint-generated baggage for cross-network source and destination labels.
  Waypoint support is off by default. ztunnel baggage is on by default and is
  controlled by ztunnel `ENABLE_RESPONSE_BAGGAGE`.
- (`1.29.0`) Waypoint spans expose source and destination workload and namespace
  tags, including `istio.source_workload`, `istio.source_namespace`,
  `istio.destination_workload`, `istio.destination_namespace`, and the
  `istio.downstream.*` and `istio.upstream.*` workload/namespace pairs.
- (`1.30.0`) Baggage peer-metadata discovery is disabled on TLS or PROXY
  traffic-policy routes so it cannot interfere with those policies. Peer
  metadata can therefore be incomplete for multicluster telemetry on those
  routes.

## Ambient security behavior

- (`1.25.0`) Multiple port-level `STRICT` rules in ambient
  `PeerAuthentication` enforce strict mTLS; their combined evaluation no longer
  becomes permissive.
- (`upgrade-1.29`) Do not enable
  `AMBIENT_ENABLE_DRY_RUN_AUTHORIZATION_POLICY=true` until all ztunnels are at
  least 1.29. Older instances fully enforce intended dry-run policies.
- (`1.30.0`) On EKS branch-ENI pods, enabled-by-default
  `AMBIENT_ENABLE_AWS_BRANCH_ENI_PROBE` sends kubelet probes through the veth
  pair instead of the VPC fabric.

