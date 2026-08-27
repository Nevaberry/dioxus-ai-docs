# Upgrades and Supported Platforms

## Stored-resource migration

Run `flux migrate` before installing CRDs that remove versions still stored in
Kubernetes etcd.

### Flux 2.7 API removals

Flux 2.7 removes these APIs (2.7.0):

- `source.toolkit.fluxcd.io/v1beta1`
- `kustomize.toolkit.fluxcd.io/v1beta1`
- `helm.toolkit.fluxcd.io/v2beta1`
- `image.toolkit.fluxcd.io/v1beta1`
- `notification.toolkit.fluxcd.io/v1beta1`

Run `flux migrate` before upgrading so stored resources use their latest API
versions.

### Flux 2.8 API removals

Flux 2.8 removes these APIs (2.8.0):

- `source.toolkit.fluxcd.io/v1beta2`
- `kustomize.toolkit.fluxcd.io/v1beta2`
- `helm.toolkit.fluxcd.io/v2beta2`

Run `flux migrate` before the upgrade.

### Flux 2.9 API and Receiver migration

Flux 2.9 removes `image.toolkit.fluxcd.io/v1beta2` and
`notification.toolkit.fluxcd.io/v1beta2` (2.9.0). Run `flux migrate` before
upgrading. A GCR Receiver must also have `email` and `audience` fields in its
referenced Secret.

For manifests stored in a repository, `flux migrate -f` supports migration to
Flux 2.9 (2.9.4).

## Coordinated CRD and controller deployment

Flux 2.9.4 changes both the `ArtifactGenerator` and `ImageUpdateAutomation` CRD
schemas. Deploy the new CRDs together with their corresponding controllers.
Running a new controller against an old schema, or the reverse, leaves the
installation inconsistent.

The same release stops accepting ImageUpdateAutomation refspecs that
force-update or delete refs. Remove such refspec operations before upgrading.

Static GCS authentication accepts only service-account keys in 2.9.4. Flux
CRDs opt out of post-build substitution to protect schema `${...}` text, and
the kustomize-controller `MigrateAPIVersion` gate can migrate API versions in
managed-field entries.

## Helm compatibility checks

Flux 2.8.0 introduces Helm v4 defaults: new releases use server-side apply and
all HelmReleases use kstatus health checking, while releases already stored by
Helm remain on client-side apply until opted in. Enable `UseHelm3Defaults` to
retain previous behavior temporarily.

Flux 2.9.0 changes the HelmRelease post-render strategy default from `nohooks`
to `combined`. Explicitly select `nohooks` before upgrading charts whose hooks
must bypass post-rendering.

## Image automation compatibility checks

Before Flux 2.7.0, migrate image resources to
`image.toolkit.fluxcd.io/v1`, remove the image-reflector `autologin` flags, and
update commit templates that use `.Updated` or `.Changed.ImageResult`.

Before Flux 2.9.4, remove force-update and delete operations from
ImageUpdateAutomation refspecs and deploy its changed CRD with the controller.

## Platform support matrix

Flux supports only the latest three Kubernetes minor versions. Use the row for
the Flux release being installed rather than assuming a newer controller still
supports an older cluster.

| Flux release | Kubernetes | OpenShift | End-of-life Flux line |
| --- | --- | --- | --- |
| 2.5.0 | 1.30–1.32 | 4.17 | 2.2 |
| 2.6.0 | 1.31–1.33 | 4.18 | 2.3 |
| 2.7.0 | 1.32–1.34 | 4.19 | 2.4 |
| 2.8.0 | 1.33–1.35 | 4.20 | 2.5 |
| 2.9.0 | 1.34–1.36 | 4.21 | 2.6 |
