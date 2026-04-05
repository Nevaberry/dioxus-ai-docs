# Deprecations & Removals

## Kubernetes 1.35

- **cgroup v1 removed**: kubelet won't start on cgroup v1 nodes. Requires cgroup v2.
- **ipvs kube-proxy mode deprecated**: migrate to `nftables` mode.
- **containerd 1.x**: last supported in 1.35. Upgrade to containerd 2.0+.
- **SupplementalGroupsPolicy: Strict** (GA 1.35): only applies explicitly specified groups, ignores `/etc/group` from container image.

## Endpoints API Deprecated (1.33)

`v1/Endpoints` is officially deprecated. Use `discovery.k8s.io/v1/EndpointSlice`. See [Networking & Gateway API](networking-gateway-api.md) for details.

## Ingress NGINX Retired

Best-effort support until March 2026, then archived. Migrate to Gateway API. See [Networking & Gateway API](networking-gateway-api.md) for Gateway API v1.3-1.4 details.
