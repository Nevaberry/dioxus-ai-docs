# Pod Resources & Lifecycle

## In-Place Pod Resize (beta 1.33 → GA 1.35)

CPU and memory requests/limits are now mutable on running Pods. Use the `resize` subresource to trigger changes. Actual resources reflected in `status.containerStatuses[*].resources`. Memory limit decreases now allowed (1.35). Deferred resizes are prioritized by PriorityClass → QoS → age.

```yaml
# Resize via kubectl (uses the resize subresource):
kubectl patch pod mypod --subresource=resize -p \
'{"spec":{"containers":[{"name":"app","resources":{"requests":{"cpu":"500m"},"limits":{"cpu":"1"}}}]}}'
```

## Pod-Level Resources (beta 1.34)

Set resource requests/limits at the Pod level instead of per-container. Shared budget among all containers.

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

## Container Restart Rules (alpha 1.34 → beta 1.35)

Per-container `restartPolicy` and `restartPolicyRules` based on exit codes, independent of Pod-level policy.

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

## Image Volumes (beta 1.33 → on-by-default 1.35)

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
          subPath: weights # subPath supported since 1.33 beta
```

## Pod Generation (GA 1.35)

Pods now have `metadata.generation` (incremented on spec changes) and `status.observedGeneration` (what kubelet has processed). Pod conditions also include `observedGeneration`. Useful for controllers tracking in-place resize completion.
