# Kubernetes Operator

Use this reference for Operator-managed ingress and egress, ProxyGroups, the
Kubernetes API proxy, Recorder, DNSConfig, multi-tailnet access, and deployment
customization.

## Proxy configuration and lifecycle

### Dynamic reload and monitoring labels (since 1.80.0)

Operator-created proxy `ServiceMonitor` objects can carry user-specified
labels. Proxies dynamically reload changed `tailscaled` configuration;
hostnames can take up to a minute to propagate. Restarting egress `ProxyGroup`
replicas no longer interrupts cluster workloads accessing tailnet targets.

### HA, multiplexing, and cross-cluster failover (since 1.84.0)

Operator-managed Ingresses and Tailscale Kubernetes Services can use a
`ProxyGroup` for multiple active proxy replicas and multiplex multiple
applications over those replicas. Both resource types can expose applications
across clusters. The Operator watches `EndpointSlice` objects cluster-wide and
can fail over when a cluster has no healthy backends.

### Container state and direct endpoints (since 1.86.0)

Container image 1.86.2 clears pod-specific state whenever it starts in
Kubernetes. It improves direct connectivity to `ProxyGroup` Pods by using
external node IP addresses as static endpoints.

## Ingress

### Let's Encrypt staging certificates (since 1.82.0)

Operator 1.82 can issue Ingress TLS certificates from Let's Encrypt's staging
environment through the ProxyClass APIs. Use staging during initial setup to
avoid production rate limits.

### Path and class behavior (since 1.84.0 and 1.86.0)

An unset path on an Operator-managed Ingress defaults to `/`. The Operator also
supports custom Ingress class names.

### HTTP-to-HTTPS redirects (since 1.92.1)

Apply `tailscale.com/http-redirect` to an Ingress to enable HTTP-to-HTTPS
redirects.

## Kubernetes API proxy

### Session recording (since 1.82.0 and 1.86.0)

The API server proxy can record `kubectl exec` session content; support later
extends to `kubectl attach` and `kubectl debug`. This recording capability is
beta.

### Highly available proxy (since 1.86.0)

Operator 1.86.2 introduces the Tailscale Kubernetes proxy and the
`kube-apiserver` `ProxyGroup` type for running its API server proxy in HA mode.

### Audit events (since 1.94.1)

Operator 1.94.1 adds beta audit logging for events passing through its API
server proxy. Log events in addition to, or instead of, full session
recordings.

### ACL configuration replaces the environment flag (since 1.96.2)

Operator 1.96.5 removes `TS_EXPERIMENTAL_KUBE_API_EVENTS`. Configure the
capability through Tailscale ACLs instead.

## Recorder

### AWS IRSA identity (since 1.84.0)

Recorder pods can use AWS IRSA instead of static S3 credentials. Configure the
generated `ServiceAccount` name and annotations.

### High availability (since 1.92.1)

Recorder resources can specify multiple replicas. A multi-replica deployment
must use an S3 storage backend.

### Deployment default (since 1.96.2)

The `Recorder` CRD defaults to a single-replica `StatefulSet` with filesystem
storage.

## Configuration and validation

### ProxyClass annotations and resource validation (since 1.86.0)

`ProxyClass` can use recommended annotations and still accepts labels. The
Operator validates ACL tags from `tailscale.com/tags` and requires that only
one Tailscale Kubernetes Service in a cluster refer to a given Tailscale
Service.

### DNSConfig nameservers (since 1.86.0 and 1.92.1)

`DNSConfig` nameservers can have a static cluster IP. The Operator later
defaults nameservers deployed through `DNSConfig` to the stable image.

### Argo CD values (since 1.92.1)

Both boolean and string values are accepted for `apiServerProxyConfig.mode` and
`apiServerProxyConfig.allowImpersonation`.

## Workload identity and Helm

### Provider-native identity (since 1.92.1)

Operator 1.92.3 can authenticate with provider-native identity tokens.
Operator 1.92.4 fixes Helm rendering when no OAuth client secret is set.

### Tailnet-scoped identity (since 1.102.2)

Workload identity federation configuration can be supplied through a `Tailnet`
custom resource.

## Multi-tailnet and namespace controls

### Tailnet and ProxyGroupPolicy CRDs (since 1.96.2)

Operator 1.96.5 adds `Tailnet` for multi-tailnet access and
`ProxyGroupPolicy` for controlling ProxyGroup creation by namespace. Ingress
and egress ProxyGroup pods can request a new auth key when needed.

### Reused hostnames (since 1.102.2)

ProxyGroup Services can use the same hostname in different tailnets without
reconciliation failing.

## Networking and deployment

### In-cluster Peer Relays (since 1.102.2)

The Operator can deploy Peer Relays in a cluster through a custom resource.

### Deployment annotations (since 1.102.2)

The Helm chart can apply annotations to the Operator's Deployment.

### Dual-stack egress (since 1.102.2)

Connector and egress-proxy resources support 4via6 when egressing from a
dual-stack cluster. Egress `ProxyGroup` resources support IPv6.
