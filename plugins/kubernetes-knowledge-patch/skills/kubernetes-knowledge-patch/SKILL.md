---
name: kubernetes-knowledge-patch
description: "Kubernetes features from v1.33-1.35 including In-Place Pod Resize GA, Dynamic Resource Allocation GA, MutatingAdmissionPolicy, Pod-Level Resources, Image Volumes, Gateway API v1.3-1.4, and key deprecations. Use when writing Kubernetes manifests, Helm charts, or controller code targeting recent cluster versions."
license: MIT
metadata:
  author: Nevaberry
  version: "1.35.0"
---

# Kubernetes Knowledge Patch

Post-training knowledge for Kubernetes 1.33-1.35 and Gateway API v1.3-1.4.
Assumes familiarity with Kubernetes through 1.32 including core workloads, Services,
Ingress, RBAC, HPA/VPA, CRDs, Helm, NetworkPolicy, PodSecurityAdmission,
ValidatingAdmissionPolicy GA (1.30), sidecar containers beta, Gateway API v1.0-v1.2.

## References

- [Pod Resources & Lifecycle](references/pod-resources-lifecycle.md) — In-Place Pod Resize GA, Pod-Level Resources, Container Restart Rules, Image Volumes, Pod Generation
- [Dynamic Resource Allocation](references/dynamic-resource-allocation.md) — DRA GA (`resource.k8s.io/v1`), ResourceClaim, DeviceClass, firstAvailable
- [Admission Policies](references/admission-policies.md) — MutatingAdmissionPolicy (CEL-based declarative mutations)
- [Networking & Gateway API](references/networking-gateway-api.md) — Traffic Distribution GA, Gateway API v1.3-1.4, BackendTLSPolicy, Endpoints API deprecated
- [Workload Management](references/workload-management.md) — HPA configurable tolerance, StatefulSet maxUnavailable, Job managedBy/podReplacementPolicy, VolumeAttributesClass, Node Topology Labels
- [Deprecations & Removals](references/deprecations-removals.md) — cgroup v1 removed, Ingress NGINX retired, ipvs deprecated, containerd 1.x EOL

## Quick Reference — What's GA in 1.35

| Feature | API/Field | Since |
|---|---|---|
| In-Place Pod Resize | `kubectl patch pod --subresource=resize` | beta 1.33 → GA 1.35 |
| Dynamic Resource Allocation | `resource.k8s.io/v1` | GA 1.35 |
| Traffic Distribution | `svc.spec.trafficDistribution: PreferSameZone` | GA 1.35 |
| Pod Generation | `metadata.generation` / `status.observedGeneration` on Pods | GA 1.35 |
| Job managedBy | `.spec.managedBy` | GA 1.35 |
| Job podReplacementPolicy | `.spec.podReplacementPolicy: Failed` | GA 1.34 |
| VolumeAttributesClass | Modify volume params (IOPS) on-line via CSI | GA 1.34 |
| SupplementalGroupsPolicy | `Strict` mode ignores image `/etc/group` | GA 1.35 |
| Node Topology Labels | Downward API: `metadata.labels['topology.kubernetes.io/zone']` | beta 1.35 |
| HPA Configurable Tolerance | `behavior.scaleUp.tolerance` | beta 1.35 |
| StatefulSet maxUnavailable | `rollingUpdate.maxUnavailable` | beta 1.35 |
| Image Volumes | `volumes[].image` | on-by-default 1.35 |
| Container Restart Rules | per-container `restartPolicyRules` | beta 1.35 |

## Quick Reference — Key API Changes

### In-Place Pod Resize (GA 1.35)

CPU/memory requests and limits are mutable on running Pods via the resize subresource.
Memory limit decreases allowed since 1.35. Actual resources in `status.containerStatuses[*].resources`.

```yaml
# Resize via kubectl:
kubectl patch pod mypod --subresource=resize -p \
'{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"500m"},"limits":{"cpu":"1"}}}]}}'
```

### DRA — Request Hardware Devices (GA 1.35)

```yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: gpu-claim
spec:
  spec:
    devices:
      requests:
        - name: gpu
          deviceClassName: gpu.example.com
          selectors:
            - cel:
                expression: device.attributes["gpu.example.com"].memory.compareTo(quantity("16Gi")) >= 0
---
# In Pod spec:
# spec.resourceClaims:
# - name: gpu
#   resourceClaimTemplateName: gpu-claim
# spec.containers[*].resources.claims:
# - name: gpu
```

### MutatingAdmissionPolicy (beta 1.34)

CEL-based declarative mutations replacing mutating webhooks. Requires feature gate.

```yaml
apiVersion: admissionregistration.k8s.io/v1beta1
kind: MutatingAdmissionPolicy
metadata:
  name: add-team-label
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        operations: ["CREATE"]
        resources: ["deployments"]
  mutations:
    - patchType: ApplyConfiguration
      applyConfiguration:
        expression: >
          Object{
            metadata: Object.metadata{
              labels: {"team": "platform"}
            }
          }
```

### Pod-Level Resources (beta 1.34)

Shared resource budget across all containers in a Pod:

```yaml
spec:
  resources:
    requests:
      cpu: "2"
      memory: 4Gi
    limits:
      cpu: "4"
      memory: 8Gi
  containers:
    - name: app
      image: myapp
    - name: sidecar
      image: proxy
```

### Image Volumes (on-by-default 1.35)

Mount OCI images as readonly volumes. Requires containerd v2.1+.

```yaml
spec:
  volumes:
    - name: model
      image:
        reference: registry.example.com/ml-model:v2
        pullPolicy: IfNotPresent
  containers:
    - name: app
      volumeMounts:
        - name: model
          mountPath: /models
          subPath: weights # subPath supported since 1.33
```

### Container Restart Rules (beta 1.35)

```yaml
spec:
  restartPolicy: Never # Pod-level
  containers:
    - name: trainer
      restartPolicy: OnFailure # Container-level override
      restartPolicyRules:
        - exitCodes: [137, 139] # Restart only on specific exit codes
          action: Restart
```

### Traffic Distribution (GA 1.35)

`PreferClose` renamed to `PreferSameZone`. New `PreferSameNode` option.

```yaml
spec:
  trafficDistribution: PreferSameNode # or PreferSameZone
```

### Gateway API — Percentage Mirroring (v1.3)

```yaml
filters:
  - type: RequestMirror
    requestMirror:
      backendRef: { name: canary, port: 8080 }
      percent: 10
```

### HPA Configurable Tolerance (beta 1.35)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  behavior:
    scaleUp:
      tolerance: 0.05 # 5% — more sensitive scaling (default was 10%)
```

### EndpointSlice Migration (1.33+)

```bash
# Old (deprecated, returns warnings in 1.33+)
kubectl get endpoints myservice
# New — look up by label (one Service → multiple EndpointSlices)
kubectl get endpointslice -l kubernetes.io/service-name=myservice
```

### Node Topology Labels via Downward API (beta 1.35)

```yaml
env:
  - name: ZONE
    valueFrom:
      fieldRef:
        fieldPath: metadata.labels['topology.kubernetes.io/zone']
# Kubelet injects topology labels into every Pod automatically
```

### Key Deprecations (1.33–1.35)

- **cgroup v1 removed** — kubelet won't start on cgroup v1 nodes
- **Ingress NGINX retired** — best-effort until March 2026, migrate to Gateway API
- **ipvs kube-proxy deprecated** — migrate to `nftables` mode
- **containerd 1.x** — last supported in 1.35, upgrade to 2.0+
- **Endpoints API deprecated** (1.33) — use `EndpointSlice` instead
