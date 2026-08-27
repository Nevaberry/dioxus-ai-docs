# Namespaces and Helm

Use this reference when an upgrade changes namespace placement, when a
Kustomize tree contains children, or when Helm chart inflation differs across
Helm versions.

## Child kustomization namespace propagation

### Regression in 5.8.0

Kustomize 5.8.0 has a regression that prevents namespaces from propagating to
child kustomizations in workloads that rely on that behavior. Do not move such
workloads to 5.8.0. Wait for a fixed patch release or retain an unaffected
version.

This warning is specifically about child kustomizations. Do not generalize it
to every namespace transformation path.

### Restoration in 5.8.1

Kustomize 5.8.1 completes the namespace-propagation fix. Builds that need the
top-level namespace to reach child kustomizations can use 5.8.1 instead of
avoiding the entire 5.8 release line.

For an upgrade review:

1. Identify overlays that set `namespace` above one or more child
   kustomizations.
2. If the renderer is 5.8.0, treat missing child namespaces as the known
   regression.
3. Re-render with 5.8.1 and inspect the child resources that depend on
   propagation.

## Namespace propagation to Helm charts

Kustomize 5.8.0 passes a kustomization's top-level namespace to its
`helmCharts` entries. The namespace therefore does not need to be repeated in
each chart entry.

```yaml
namespace: any-namespace
helmCharts:
- name: minecraft
  repo: https://kubernetes-charts.storage.googleapis.com
  version: v1.2.0
  valuesFile: values.yaml
```

Keep this behavior separate from the 5.8.0 child-kustomization regression:

- the Helm change passes the namespace into chart processing;
- the regression affects propagation into child kustomizations;
- 5.8.1 restores the child path.

When a build combines charts and children, evaluate each path independently.

## Development chart versions

From 5.7.0, a `helmCharts` entry may use `devel` as its chart version alias.
Choose `devel` when development chart versions should be considered instead of
pinning the entry to a normal released chart version.

This is chart-version selection. It does not determine which Helm runtime
Kustomize can use for inflation.

## Helm runtime compatibility

Kustomize 5.8.1 accommodates the breaking changes introduced by Helm v4 while
retaining compatibility with Helm v3.

When chart inflation breaks around a Helm runtime migration:

1. Check whether the environment moved from Helm v3 to Helm v4.
2. Check whether Kustomize is at 5.8.1.
3. Update Kustomize compatibility before assuming the chart declaration itself
   must be rewritten.

The relevant Helm decisions are independent:

| Concern | Guidance |
| --- | --- |
| Include development chart versions | Use the `devel` version alias from 5.7.0 |
| Pass the top-level namespace to a chart | Use the namespace propagation behavior in 5.8.0 |
| Run chart inflation with Helm v3 or v4 | Use the compatibility provided in 5.8.1 |
| Propagate a namespace into children | Avoid 5.8.0; use the restored behavior in 5.8.1 |
