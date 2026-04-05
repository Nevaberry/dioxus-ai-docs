# Networking & Gateway API

## Traffic Distribution (GA 1.35)

`PreferClose` renamed to `PreferSameZone`. New `PreferSameNode` option added.

```yaml
apiVersion: v1
kind: Service
spec:
  trafficDistribution: PreferSameNode # or PreferSameZone (was PreferClose)
```

## Endpoints API Deprecated (1.33)

`v1/Endpoints` is officially deprecated. Use `discovery.k8s.io/v1/EndpointSlice`:

```bash
# Old (returns deprecation warnings in 1.33+)
kubectl get endpoints myservice
# New — look up by label, not name (one Service → multiple EndpointSlices)
kubectl get endpointslice -l kubernetes.io/service-name=myservice
```

A Service may have multiple EndpointSlices (dual-stack, >100 endpoints, mixed port updates).

## Gateway API v1.3-1.4

**v1.3** (Apr 2025): Percentage-based request mirroring (Standard). **v1.4** (Oct 2025): BackendTLSPolicy GA, named rules for Routes, Mesh resource (experimental).

```yaml
# Percentage mirroring (v1.3):
filters:
  - type: RequestMirror
    requestMirror:
      backendRef: { name: canary, port: 8080 }
      percent: 10
```

```yaml
# BackendTLSPolicy (v1.4 Standard):
apiVersion: gateway.networking.k8s.io/v1
kind: BackendTLSPolicy
metadata:
  name: tls-backend
spec:
  targetRefs:
    - kind: Service
      name: backend
      group: ""
  validation:
    caCertificateRefs:
      - kind: ConfigMap
        name: backend-ca
    subjectAltNames:
      - type: Hostname
        hostname: backend.example.com
```
