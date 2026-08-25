# Helm, Operations, and Security

## Chart composition and templating

Both ServiceAccount annotation keys and values are evaluated through Helm
`tpl`, so workload-identity annotations can derive values from the rest of the
chart (`1.17`).

When cert-manager is a dependency, the chart-level `enabled` value lets a
parent chart toggle it. Configured image pull Secrets are added to Deployments
even when the chart does not create ServiceAccounts.

PodDisruptionBudget values accept percentages for both `minAvailable` and
`maxAvailable`:

```yaml
podDisruptionBudget:
  minAvailable: "50%"
```

## Scheduling and runtime isolation

### Common node selection

`global.nodeSelector` applies to all cert-manager chart components (`1.19`).
Use 1.19.2 or later because it correctly merges the global selector with each
component's selector.

```yaml
global:
  nodeSelector:
    kubernetes.io/os: linux
```

### User namespaces and runtime classes

On Kubernetes 1.33 or later, experimental `global.hostUsers: false` runs all
chart-managed cert-manager Pods in Kubernetes user namespaces. It is unset by
default for compatibility with older Kubernetes releases.

Runtime classes are configurable for components and HTTP-01 solver Pods in
1.21. The solver chart value is:

```yaml
acmesolver:
  runtimeClassName: gvisor
```

### Container identities

From 1.20, default container UID and GID are both `65532`, replacing UID `1000`
and GID `0`. Adjust admission policies and volume permissions that encode the
old identities.

## NetworkPolicy

The default chart network policy includes IPv6 rules from 1.19, supporting
dual-stack and IPv6-only clusters without a patched cert-manager policy. From
1.20, the chart can create NetworkPolicy resources for every cert-manager
Deployment to apply isolation across all deployed components.

## RBAC and controller scope

### Namespace-scoped operation

`--namespace=<namespace>` restricts cert-manager to that namespace and disables
cluster-scoped controllers (`1.18`). Account for the unavailable cluster-wide
reconcilers when choosing this mode.

### Withdrawn HTTP challenge value

`global.rbac.disableHTTPChallengesRole` appeared in 1.18.0 but was removed in
1.18.2 because of a bug. Do not use it elsewhere in the 1.18 line.

### ServiceAccount token permissions

The 1.21 chart no longer creates controller-ServiceAccount token `Role` and
`RoleBinding` resources. An issuer whose `serviceAccountRef.name` points to
that account needs explicit RBAC or a dedicated ServiceAccount with its own
permissions.

From 1.19.6, aggregate `cert-manager-edit` permissions also exclude creating
Challenges and creating, updating, or patching Orders. Direct internal-resource
automation needs separate RBAC.

## Component and Job cleanup

Set the opt-in `startupapicheck.ttlSecondsAfterFinished` value to let
Kubernetes' TTL-after-finished controller clean up the completed startup API
check Job (`1.21`).

The `--acme-http01-solver-extra-labels` controller flag lets Helm
`global.commonLabels` propagate to dynamically created solver Pods, Services,
Ingresses, and Gateway API HTTPRoutes.

## Version-specific chart hazards

- On OpenShift, use 1.20.1 or later. Version 1.20.0 lacks issuer-finalizer RBAC
  required by the Order controller.
- Use 1.20.2 or later when both `webhook.config` and `webhook.volumes` are set;
  prior releases can render invalid YAML.
- Remove `prometheus.servicemonitor.targetPort`,
  `prometheus.servicemonitor.path`, and `prometheus.podmonitor.path` before a
  1.21 upgrade. Their fixed replacements are `/metrics` and `http-metrics`.
