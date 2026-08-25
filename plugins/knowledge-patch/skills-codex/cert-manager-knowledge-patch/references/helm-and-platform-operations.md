# Helm and Platform Operations

## Installation and chart composition

### OperatorHub distribution ended `(1.17)`

Red Hat OpenShift and community OperatorHub catalogs stop at cert-manager 1.16.5. Installations from those catalogs need another distribution method to move to 1.17 or later.

### Dependency toggle `(1.17)`

The chart accepts `enabled`, allowing a parent chart to turn its cert-manager dependency on or off.

### ServiceAccount-independent pull secrets `(1.17)`

Configured image pull secrets reach Deployments even when the chart does not create ServiceAccounts.

### Namespace-scoped operation `(1.18)`

Running the controller with `--namespace=<namespace>` restricts cert-manager to that namespace and disables cluster-scoped controllers.

## Scheduling and availability

### Percentage PodDisruptionBudgets `(1.17)`

`podDisruptionBudget.minAvailable` and `podDisruptionBudget.maxAvailable` accept percentages:

```yaml
podDisruptionBudget:
  minAvailable: "50%"
```

### Global node selector `(1.19)`

`global.nodeSelector` applies a common selector to all chart components. Use 1.19.2 or later so it merges correctly with component-level settings.

```yaml
global:
  nodeSelector:
    kubernetes.io/os: linux
```

### Runtime classes `(1.21)`

Runtime classes can be set for cert-manager components and ACME HTTP-01 solver Pods. The solver chart value is:

```yaml
acmesolver:
  runtimeClassName: gvisor
```

## Pod identity and security context

### Templated ServiceAccount annotations `(1.17)`

The chart evaluates ServiceAccount annotation keys and values through Helm `tpl`, allowing workload-identity annotations to derive from other chart values.

### Kubernetes user namespaces `(1.19)`

On Kubernetes 1.33 or later, experimental `global.hostUsers: false` makes chart-managed Pods use Kubernetes user namespaces. It is unset by default to preserve compatibility with older Kubernetes releases.

```yaml
global:
  hostUsers: false
```

### Container identity defaults `(1.20)`

The default container UID changed from `1000` to `65532`, and the default GID changed from `0` to `65532`. Update admission policy, file ownership, and volume permissions that depend on the old IDs.

### Controller token-creation RBAC `(upgrade-1.21)`

The chart no longer creates the Role and RoleBinding that let the controller mint tokens for its own ServiceAccount. If an Issuer's `serviceAccountRef.name` selects that account—for example for Vault Kubernetes auth or Route53—create explicit RBAC or migrate to a dedicated ServiceAccount with its own RBAC before upgrading.

## Network policy

### IPv6 defaults `(1.19)`

The chart's default network policy includes IPv6 rules, so dual-stack and IPv6-only clusters do not need a custom patch for cert-manager traffic.

### Chart-managed NetworkPolicies `(1.20)`

The chart can create NetworkPolicy resources for every cert-manager Deployment, providing network isolation for all deployed components.

## Chart validation and rendering

### HTTP challenge RBAC value withdrawn `(1.18)`

`global.rbac.disableHTTPChallengesRole` appeared in 1.18.0 but was removed in 1.18.2 because of a bug. It is unavailable for the rest of the 1.18 line.

### Webhook config plus volumes `(1.20)`

Before 1.20.2, setting both `webhook.config` and `webhook.volumes` can render invalid YAML. Use 1.20.2 or later for that combination.

### Prometheus monitor overrides removed `(upgrade-1.21)`

Remove `prometheus.servicemonitor.targetPort`, `prometheus.servicemonitor.path`, and `prometheus.podmonitor.path` before upgrade or chart schema validation fails. Metrics use fixed path `/metrics` and port name `http-metrics`; custom scrapers must replace the former `tcp-prometheus-servicemonitor` Service port name.

## Labels and cleanup

### Common labels on solver resources `(1.21)`

The controller flag `--acme-http01-solver-extra-labels` allows Helm `global.commonLabels` to reach dynamic HTTP-01 Pods, Services, Ingresses, and Gateway API HTTPRoutes.

### Startup API check cleanup `(1.21)`

Set the opt-in value `startupapicheck.ttlSecondsAfterFinished` so the Kubernetes TTL-after-finished controller removes the completed startup API check Job.

## OpenShift correction `(1.20)`

Version 1.20.0 omitted issuer-finalizer RBAC needed by the Order controller and regressed OpenShift installations. Use 1.20.1 or later.
