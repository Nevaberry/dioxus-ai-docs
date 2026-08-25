# Upgrades and platform support

## Migrate stored APIs before replacing CRDs

Changing repository YAML is not sufficient when Kubernetes etcd still stores
objects under removed API versions. Run `flux migrate` while the old CRDs and
controllers are still available, verify the migration, and then upgrade Flux.

### Removed by the 2.7.0 CRDs

- `source.toolkit.fluxcd.io/v1beta1`
- `kustomize.toolkit.fluxcd.io/v1beta1`
- `helm.toolkit.fluxcd.io/v2beta1`
- `image.toolkit.fluxcd.io/v1beta1`
- `notification.toolkit.fluxcd.io/v1beta1`

### Removed by the 2.8.0 CRDs

- `source.toolkit.fluxcd.io/v1beta2`
- `kustomize.toolkit.fluxcd.io/v1beta2`
- `helm.toolkit.fluxcd.io/v2beta2`

### Removed by the 2.9.0 CRDs

- `image.toolkit.fluxcd.io/v1beta2`
- `notification.toolkit.fluxcd.io/v1beta2`

When migrating GCR Receivers for 2.9, also add `email` and `audience` to the
referenced Secret. These values are required in addition to the API migration.

## Migrate repository manifests

Since 2.9.4, `flux migrate -f` can migrate Flux manifests in a repository to
the 2.9 APIs. Use this for declarative files, while plain `flux migrate`
handles live stored resources.

## Upgrade CRDs with controllers

Do not upgrade a controller while leaving its CRD schema behind. Flux 2.9.4
changes both the `ArtifactGenerator` and `ImageUpdateAutomation` schemas;
apply the matching CRDs together with source-watcher and
image-automation-controller.

The same release marks Flux CRDs with
`kustomize.toolkit.fluxcd.io/substitute: disabled`. Keep that annotation so
post-build substitution cannot rewrite `${...}` text embedded in CRD schemas.

## Managed-field API versions

The kustomize-controller `MigrateAPIVersion` feature gate, added in 2.9.4,
migrates API versions recorded in managed-field entries. Enable it on the
controller when those entries must be updated:

```shell
--feature-gates=MigrateAPIVersion=true
```

This is separate from migrating object manifests and stored resource APIs.

## Platform support matrix

Flux supports the latest three Kubernetes minor versions. Match the Flux
release to a supported cluster version instead of assuming newer Kubernetes
minors are automatically covered.

| Flux release | Kubernetes | OpenShift | Newly end-of-life Flux line |
| --- | --- | --- | --- |
| 2.5.0 | 1.30–1.32 | 4.17 | 2.2 |
| 2.6.0 | 1.31–1.33 | 4.18 | 2.3 |
| 2.7.0 | 1.32–1.34 | 4.19 | 2.4 |
| 2.8.0 | 1.33–1.35 | 4.20 | 2.5 |
| 2.9.0 | 1.34–1.36 | 4.21 | 2.6 |
