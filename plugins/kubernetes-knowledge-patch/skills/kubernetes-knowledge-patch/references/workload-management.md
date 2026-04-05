# Workload Management

## HPA Configurable Tolerance (beta 1.35)

Custom tolerance per metric in HPA behavior field. Default was hardcoded 10%.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  behavior:
    scaleUp:
      tolerance: 0.05 # 5% — more sensitive scaling
```

## StatefulSet maxUnavailable (beta 1.35)

Rolling updates can now update multiple Pods at once.

```yaml
spec:
  podManagementPolicy: Parallel
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 3 # or "10%"
```

## Deployment terminatingReplicas (beta 1.35)

`.status.terminatingReplicas` field shows count of Pods with deletion timestamp but not yet removed.

## Job managedBy (GA 1.35)

`.spec.managedBy` field delegates Job status sync to an external controller (e.g., MultiKueue). Built-in Job controller skips Jobs with this field set.

## Job podReplacementPolicy (GA 1.34)

`.spec.podReplacementPolicy: Failed` — only create replacement Pod after original fully terminates, avoiding resource contention and simultaneous execution.

## VolumeAttributesClass (GA 1.34)

Modify volume parameters (e.g. provisioned IOPS) on-line. Requires CSI driver support for `ModifyVolume`.

## Node Topology Labels via Downward API (beta 1.35)

Access zone/region labels directly in Pods without API server queries:

```yaml
env:
  - name: ZONE
    valueFrom:
      fieldRef:
        fieldPath: metadata.labels['topology.kubernetes.io/zone']
```

Kubelet injects topology labels into every Pod automatically.
