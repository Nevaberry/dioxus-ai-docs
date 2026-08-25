# Helm Charts

## Development chart versions

A `helmCharts` entry can use `devel` as its chart version alias. Use the alias
when development chart versions should be considered. (5.7.0)

## Top-level namespace propagation

The namespace transformer passes the kustomization's namespace to
`helmCharts` entries. The namespace therefore does not need to be repeated on
each chart. (5.8.0)

```yaml
namespace: any-namespace
helmCharts:
- name: minecraft
  repo: https://kubernetes-charts.storage.googleapis.com
  version: v1.2.0
  valuesFile: values.yaml
```

This behavior concerns chart entries. For the release-sensitive behavior of
namespaces passed to child kustomizations, see
[upgrade-and-namespaces.md](upgrade-and-namespaces.md).

## Helm executable compatibility

Helm chart inflation accommodates the breaking changes in Helm v4 and retains
support for Helm v3. (5.8.1)

Chart-inflation workflows can therefore operate with either Helm major
version.
