# Dynamic Resource Allocation (DRA)

## GA (1.34-1.35)

`resource.k8s.io/v1` APIs are stable. Use ResourceClaim/ResourceClaimTemplate to request GPUs, TPUs, NICs via DeviceClass with CEL selectors. Always enabled in 1.35.

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

## firstAvailable (beta 1.34)

Ordered list of alternative device requests — scheduler picks first satisfiable option. Useful for heterogeneous clusters where workloads can run on different device types.
