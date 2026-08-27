---
name: flux-cd-knowledge-patch
description: Flux CD
version: "2.9.0"
license: MIT
metadata:
  author: Nevaberry
---


# Flux CD Knowledge Patch

Use this skill when changing Flux manifests, controller flags, authentication,
artifact pipelines, notification integrations, or upgrade procedures. Inspect
the installed Flux and Kubernetes versions before applying version-dependent
advice, and prefer the cluster's CRDs, manifests, and observed controller
behavior when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Helm releases](references/helm-releases.md) | Helm v4 behavior, retries, values, inventory, health checks, and chart processing |
| [Identity and operations](references/identity-and-operations.md) | GitHub Apps, Workload Identity, SOPS key services, UI operations, and CLI plugins |
| [Image automation](references/image-automation.md) | Stable image APIs, digest pinning, commit templates, signing, and refspec restrictions |
| [Kustomizations](references/kustomizations.md) | CEL health, deletion, reconciliation watches, SOPS, apply ordering, and ignored fields |
| [Notifications and Receivers](references/notifications-and-receivers.md) | Event metadata, commit status, pull-request comments, OTel, provider transport, and Receiver security |
| [Sources and artifacts](references/sources-and-artifacts.md) | OCI APIs, artifact commands, Git access, verification, ArtifactGenerator, and ExternalArtifact |
| [Upgrades and platforms](references/upgrades-and-platforms.md) | Required migrations, CRD coordination, supported platforms, and end-of-life windows |

## Start with upgrade blockers

### Migrate stored APIs before controller upgrades

Run `flux migrate` before an upgrade whose CRDs remove an API version. The key
removal boundaries are:

- Flux 2.7 removes the `v1beta1` source, Kustomize, Helm, image, and
  notification APIs listed in the upgrade reference.
- Flux 2.8 removes `source.toolkit.fluxcd.io/v1beta2`,
  `kustomize.toolkit.fluxcd.io/v1beta2`, and
  `helm.toolkit.fluxcd.io/v2beta2`.
- Flux 2.9 removes `image.toolkit.fluxcd.io/v1beta2` and
  `notification.toolkit.fluxcd.io/v1beta2`. GCR Receiver Secrets must also
  contain `email` and `audience`.

For Flux 2.9 repository manifests, use `flux migrate -f`. When deploying
Flux 2.9.4, update the `ArtifactGenerator` and `ImageUpdateAutomation` CRDs
together with their controllers. GCS static authentication accepts only
service-account keys, and `MigrateAPIVersion` is available to repair API
versions in managed-field entries.

### Account for Helm behavior changes

Flux 2.8 ships Helm v4. New releases use server-side apply; releases already
stored by Helm remain on client-side apply until explicitly opted in.
Kstatus-based health checks become the default for every HelmRelease. Enable
`UseHelm3Defaults` to retain the prior apply and health behavior.

Flux 2.9 changes the default post-render strategy from `nohooks` to `combined`,
which sends Helm hooks through post-rendering. Set the strategy to `nohooks`
before upgrading if a chart depends on the old behavior.

### Update image automation assumptions

The image APIs are stable at `image.toolkit.fluxcd.io/v1`. Before moving to
Flux 2.7, replace removed image-reflector `autologin` flags with
`ImageRepository.spec.provider`, and replace commit-template uses of `.Updated`
or `.Changed.ImageResult` with `.Changed.FileChanges`, `.Changed.Objects`, or
the flat `.Changed.Changes` list.

Flux 2.9.4 rejects `ImageUpdateAutomation` refspecs that force-update or delete
refs. Remove those operations before upgrading. Source-controller and
image-reflector-controller support GCP sovereign-cloud artifact registries.

## High-value Helm release controls

Use `RetryOnFailure` for install or upgrade retry behavior. If enabling
`CancelHealthCheckOnNewRevision` for helm-controller, also enable
`DefaultToRetryOnFailure`; otherwise a canceled health check can leave a
release stuck with the default no-retry configuration. A cancellation reports
`HealthCheckCanceled` on the `Ready` condition.

`HelmRelease.valuesFrom` supports literal mode: the full contents of a selected
ConfigMap or Secret key become one string, like `helm install --set-literal`,
without parsing types or expanding dotted names.

Use `.status.inventory` to inspect all objects managed by a HelmRelease. To see
the final merged values, run:

```shell
flux debug helmrelease --show-values
```

The command prints referenced Secret values in clear text. Treat its output as
sensitive.

## High-value Kustomization controls

### Teach readiness with CEL

Use `Kustomization.spec.healthCheckExprs` when a custom resource does not
follow standard Kubernetes readiness conventions:

```yaml
spec:
  wait: true
  healthCheckExprs:
    - apiVersion: cluster.x-k8s.io/v1beta1
      kind: Cluster
      failed: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'False')"
      current: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'True')"
```

Health expressions for Kustomizations and HelmReleases can leave `kind` empty
to apply one expression across every kind in an API group. Dependency entries
in both resources can also use CEL to extend normal Ready-condition checks.

### Control deletion and field ownership

`Kustomization.spec.deletionPolicy` controls garbage collection. Select
`WaitForTermination` when deletion of the Kustomization must wait for all
managed resources to disappear.

Use `Kustomization.spec.ignore` to keep selected managed fields out of both
drift detection and apply, for example when an HPA owns replicas:

```yaml
spec:
  ignore:
    - target:
        kind: Deployment
      paths:
        - /spec/replicas
```

### Reconcile watched inputs immediately

Opt a referenced ConfigMap or Secret into immediate reconciliation with:

```yaml
metadata:
  labels:
    reconcile.fluxcd.io/watch: Enabled
```

The controller-wide alternative is
`--watch-configs-label-selector=owner!=helm`. The supported Kustomization,
HelmRelease, and Receiver reference fields are listed in their topic files.

## Sources and generated artifacts

`OCIRepository` is stable at `source.toolkit.fluxcd.io/v1` and is backward
compatible with `v1beta2`, so that migration only requires changing
`apiVersion`. Artifact build, push, pull, tag, diff, and list commands and the
Flux config/content media types are stable.

For `OCIRepository` and `ImageRepository`, use `aws`, `azure`, or `gcp` as
`.spec.provider` only when the repository URL matches that cloud registry and
automatic OIDC authentication is intended. For public repositories or
image-pull Secrets, omit the provider or set it to `generic`.

Enable source-watcher with `--components-extra=source-watcher` to use
`ArtifactGenerator` and `ExternalArtifact`. Generators can compose sources,
split monorepos, process Helm charts, and discover directories through
`spec.pathPattern`; only changed path-specific artifacts need to trigger their
consumers.

## Authentication quick reference

Create a GitHub App Secret with:

```shell
flux create secret githubapp github-auth \
  --app-id=1 \
  --app-installation-id=2 \
  --app-private-key=~/private-key.pem
```

Reference it through `.spec.secretRef.name` on a `GitRepository` or
`ImageUpdateAutomation`. `flux create source git --provider=github` supports
the same mode. Later authentication flows can look up the installation ID from
the repository owner, and GitRepository GitHub App authentication can use
mutual TLS.

Enable `ObjectLevelWorkloadIdentity` before assigning per-object identities.
It supports Kustomization SOPS/KMS decryption and registry access by
OCIRepository or ImageRepository, with broader Bucket, GitRepository,
notification Provider, remote-cluster, Vault, and OpenBao cases detailed in
the operations reference.

## Notifications and Receivers

Use `event.toolkit.fluxcd.io/image`, `change_request`, and `commit` annotations
to add the image reference or change identifier needed by downstream
providers. CEL can filter Receiver targets, derive custom commit-status IDs,
and distinguish clusters in monorepos.

Generic Receivers can validate an OIDC ID token instead of an HMAC secret. Use
`flux trigger receiver` to invoke one without manually constructing a webhook
request.

An `otel` Provider translates source events into root spans and consuming
Kustomization or HelmRelease events into child spans. Pull- and merge-request
comment providers publish deduplicated deployment-status comments directly;
commit-status reporting accepts events from any Flux API.

## Operational checks

- Use `flux debug kustomization --show-vars` to inspect merged substitutions;
  its referenced Secret values are clear text and must be protected.
- Pin Flux CLI plugin versions or immutable digests in reproducible workflows.
  Manage plugins with `flux plugin search`, `install`, `list`, `update`, and
  `uninstall`.
- Check the Kubernetes and OpenShift support matrix before an upgrade. Flux
  supports only the latest three Kubernetes minor versions.
- Verify CRDs and controllers were deployed as one coordinated change when a
  release changes schemas.
