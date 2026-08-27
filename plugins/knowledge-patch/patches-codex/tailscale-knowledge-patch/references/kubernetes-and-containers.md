# Kubernetes and Containers

## Container image behavior

### HTTP-only Serve configuration (since 1.80.0)

The container image can load `TS_SERVE_CONFIG` when HTTPS is disabled for the
tailnet, provided the configuration contains no HTTPS endpoint.

### Kubernetes startup state (since 1.86.2)

The container clears pod-specific state whenever it starts in Kubernetes. It
also improves direct connectivity to `ProxyGroup` pods by using external node
IP addresses as static endpoints.

### Auth key files and firewall fallback (since 1.92.1)

`tsrecorder` 1.92.3 reads its auth key from the file named by
`TS_AUTHKEY_FILE`:

```console
export TS_AUTHKEY_FILE=/run/secrets/tailscale-auth-key
```

Container image 1.92.3 also restores `iptables` operation on hosts without
`nftables` support.

### OAuth and workload identity (since 1.94.1)

Container image 1.94.1 supports both OAuth and workload identity federation
authentication.

### Automatic Service advertisement (since 1.96.2)

Services are advertised automatically at startup. Disable this behavior when
advertisement is managed elsewhere:

```text
TS_EXPERIMENTAL_SERVICE_AUTO_ADVERTISEMENT=false
```

## Proxy resources and high availability

### Proxy reload and egress continuity (since 1.80.0)

Operator-created proxy `ServiceMonitor` objects accept user-specified labels.
Proxies dynamically reload changed `tailscaled` configuration; hostname
changes may take up to one minute to propagate. Restarting egress
`ProxyGroup` replicas no longer interrupts cluster workloads accessing
tailnet targets.

### Ingress and Service ProxyGroups (since 1.84.0)

Operator-managed Ingresses and Tailscale Kubernetes Services can use a
`ProxyGroup` for multiple active replicas and multiplex multiple applications
over those replicas. Both resource types can expose applications across
clusters. The Operator watches `EndpointSlice` objects cluster-wide so it can
fail over when one cluster has no healthy backends.

### Proxy configuration and validation (since 1.86.0)

- `ProxyClass` supports recommended annotations and continues to accept
  labels.
- The Operator supports custom Ingress class names.
- A `DNSConfig` nameserver can have a static cluster IP.
- ACL tags supplied through `tailscale.com/tags` are validated.
- Only one Tailscale Kubernetes Service in a cluster may refer to a given
  Tailscale Service.

### Multi-tailnet and namespace controls (since 1.96.2)

Operator 1.96.5 adds a `Tailnet` custom resource for multiple-tailnet access
and a `ProxyGroupPolicy` custom resource for controlling ProxyGroup creation
by namespace. Ingress and egress ProxyGroup pods can request a new auth key
when required.

### In-cluster Peer Relays (since 1.102.2)

The Operator can deploy Peer Relays in a cluster through a custom resource.

### Deployment and Tailnet identity (since 1.102.2)

The Operator Helm chart can add annotations to the Operator Deployment.
Workload identity federation configuration can be supplied through a
`Tailnet` custom resource.

### Dual-stack egress (since 1.102.2)

Connector and egress-proxy resources support 4via6 when egressing from a
dual-stack cluster. Egress `ProxyGroup` resources also support IPv6.

### Hostname reuse across tailnets (since 1.102.2)

ProxyGroup Services may use the same hostname in different tailnets without
reconciliation failure. Keep hostname uniqueness checks scoped to one
tailnet.

## Kubernetes API proxy, recording, and audit

### Exec recording beta (since 1.82.0)

The Operator can record the contents of `kubectl exec` sessions made through
its Kubernetes API server proxy; this capability is beta.

### Highly available API proxy (since 1.86.2)

Operator 1.86.2 introduces the Tailscale Kubernetes proxy and a `ProxyGroup`
type of `kube-apiserver` for running the API server proxy in high-availability
mode. Session recording covers `kubectl attach` and `kubectl debug` in
addition to `kubectl exec`.

### Audit logging (since 1.94.1)

Operator 1.94.1 adds beta audit logging for events passing through its
Kubernetes API server proxy. Audit events can be recorded in addition to, or
instead of, full session recordings.

### Event configuration (since 1.96.2)

Operator 1.96.5 removes `TS_EXPERIMENTAL_KUBE_API_EVENTS`. Configure the
capability through Tailscale ACLs instead.

## Ingress certificates and redirects

### Staging certificates (since 1.82.0)

Operator 1.82 can issue Ingress TLS certificates through Let's Encrypt's
staging environment. Configure this with ProxyClass APIs to avoid production
rate limits during initial setup.

### Default path and HTTP redirects

An unset Operator-managed Ingress path defaults to `/` (since 1.84.0). Apply
the `tailscale.com/http-redirect` annotation to an Ingress to enable
HTTP-to-HTTPS redirects (since 1.92.1).

## Recorder resources

### AWS IRSA identity (since 1.84.0)

Recorder pods can use AWS IRSA instead of static S3 credentials. Configure
the generated `ServiceAccount` name and annotations.

### Highly available Recorders (since 1.92.1)

Recorder resources can request multiple replicas. A multi-replica deployment
must use an S3 storage backend.

### Default deployment (since 1.96.2)

The `Recorder` CRD defaults to a single-replica `StatefulSet` using filesystem
storage.

## Operator authentication and chart compatibility

### Provider-native federation (since 1.92.1)

Operator 1.92.3 authenticates to a tailnet with provider-native identity
tokens. Operator 1.92.4 fixes Helm rendering when no OAuth client secret is
set.

### DNSConfig image default (since 1.92.1)

Nameservers deployed through a `DNSConfig` resource default to the stable
image.

### Argo CD values (since 1.92.1)

The Operator accepts boolean or string values for
`apiServerProxyConfig.mode` and
`apiServerProxyConfig.allowImpersonation`, avoiding type conflicts in Argo CD
rendering.

### Service VIP egress (since 1.94.1)

Operator egress proxies can send traffic to generally available Tailscale
Service virtual IPs.
