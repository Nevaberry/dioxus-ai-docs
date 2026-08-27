---
name: flux-cd-knowledge-patch
description: Flux CD
version: "2.9.0"
license: MIT
metadata:
  author: Nevaberry
---


# Flux CD Knowledge Patch

Use this skill when writing, reviewing, migrating, or troubleshooting Flux
manifests, controller flags, CLI workflows, source authentication, image
automation, notification delivery, or Flux Operator installations.

Prefer the project's installed CRDs, controller versions, manifests, and live
behavior when they disagree with this guidance. Flux controllers and CRDs are
upgraded as a coordinated set, and feature gates must be enabled on the
controller that implements the feature.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI and Operator](references/cli-and-operator.md) | Debug commands, artifact commands, plugins, migrations, Operator UI |
| [Image automation](references/image-automation.md) | Stable APIs, digest pinning, cloud auth, commit templates, refspec safety |
| [Kustomizations and Helm](references/kustomizations-and-helm.md) | Health, apply, deletion, SOPS, values, dependencies, retries, inventory |
| [Notifications and Receivers](references/notifications-and-receivers.md) | Event metadata, commit statuses, comments, transports, traces, webhook auth |
| [Sources, auth, and artifacts](references/sources-auth-and-artifacts.md) | Git and OCI sources, Workload Identity, verification, ArtifactGenerator |
| [Upgrades and platforms](references/upgrades-and-platforms.md) | Required migrations, removed APIs, CRD coordination, support windows |

## Upgrade safety first

Before upgrading, inspect stored API versions and run:

```shell
flux migrate
```

The 2.7, 2.8, and 2.9 CRDs remove successive beta APIs. A manifest's current
`apiVersion` does not prove that the object stored in etcd has been migrated.
Read [upgrades and platforms](references/upgrades-and-platforms.md) for the
exact removed versions.

Upgrade CRDs with their controllers. This is especially important when using
`ArtifactGenerator` or `ImageUpdateAutomation`, whose schemas changed in a
2.9 maintenance release. Repository manifests can be migrated with
`flux migrate -f` where supported.

### Breaking Helm post-render behavior

The HelmRelease post-render default is `combined`, so hooks pass through
post-rendering. A chart that requires the former behavior must explicitly use
`nohooks` before the controller upgrade.

### Image automation refspec restrictions

Remove force-update and ref-deletion operations from
`ImageUpdateAutomation` refspecs. They are rejected by current controllers.

### Registry provider validation

For `OCIRepository` and `ImageRepository`, set `spec.provider` to `aws`,
`azure`, or `gcp` only when the registry URL matches and automatic OIDC is
intended. For public registries and pull-secret authentication, omit it or use
`generic`.

## Kustomization health and ownership

Use `spec.healthCheckExprs` to teach Flux readiness semantics for custom
resources. Select the API version and kind, then define CEL `failed` and
`current` expressions. With `wait: true`, dependents wait until resources are
current.

```yaml
spec:
  wait: true
  healthCheckExprs:
    - apiVersion: cluster.x-k8s.io/v1beta1
      kind: Cluster
      failed: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'False')"
      current: "status.conditions.filter(e, e.type == 'Ready').all(e, e.status == 'True')"
```

For an API-group-wide rule, omit `kind`. Dependency entries in
`Kustomization.spec.dependsOn` and `HelmRelease.spec.dependsOn` can also use
CEL readiness expressions.

Use `Kustomization.spec.ignore` when another controller owns selected fields:

```yaml
spec:
  ignore:
    - target:
        kind: Deployment
      paths:
        - /spec/replicas
```

This keeps fields such as HPA-managed replicas out of drift detection and
apply. See [Kustomizations and Helm](references/kustomizations-and-helm.md) for
deletion policies, apply staging, decryption, and feature-gate interactions.

## Helm reconciliation defaults

New Helm releases use Helm v4 server-side apply and kstatus health checks.
Existing stored releases continue with client-side apply until opted in. Use
the `UseHelm3Defaults` feature gate only when the previous apply and health
behavior is required.

For quicker recovery, enable `CancelHealthCheckOnNewRevision` on
helm-controller together with `DefaultToRetryOnFailure`. Cancellation can be
caused by source or spec changes, watched ConfigMaps or Secrets, manual
reconciliation, or Receiver triggers, and reports `HealthCheckCanceled`.

Use `RetryOnFailure` for install and upgrade retries. Inspect
`HelmRelease.status.inventory` to see the managed object set.

`HelmRelease.valuesFrom` literal mode treats the entire referenced key as one
string, matching `helm install --set-literal`; it does not parse types or
expand dotted property names.

## Source and identity choices

Use the stable `source.toolkit.fluxcd.io/v1` API for `OCIRepository`; migration
from `v1beta2` requires only an `apiVersion` change. Git repositories support
directory-based sparse checkout, HTTPS mutual TLS, GitHub App authentication,
and several object-level Workload Identity paths.

Create GitHub App credentials with:

```shell
flux create secret githubapp github-auth \
  --app-id=1 \
  --app-installation-id=2 \
  --app-private-key=~/private-key.pem
```

Reference the Secret through `spec.secretRef.name`. Supported flows can look
up the installation ID from the repository owner, so it need not always be
provided. Read [sources, auth, and artifacts](references/sources-auth-and-artifacts.md)
before choosing static credentials, controller identity, or object identity.

## ArtifactGenerator workflows

Install the optional source-watcher component with:

```shell
flux bootstrap ... --components-extra=source-watcher
```

`ArtifactGenerator` can combine Git, OCI, and Bucket content, split a monorepo
into independently revised `ExternalArtifact` objects, and extract or modify
Helm charts. `spec.pathPattern` discovers matching directories; named captures
become variables in artifact names, labels, and copy rules.

Point a `Kustomization` source or a `HelmRelease.spec.chartRef` at an
`ExternalArtifact`. Path-specific outputs prevent unrelated monorepo changes
from triggering every deployment.

## Image digest pinning

Set `ImagePolicy.spec.digestReflectionPolicy: Always` to track the latest
digest. Image automation can then write
`<registry>/<name>:<tag>@<digest>`. For resources that split image fields, use
the `:name`, `:tag`, and `:digest` markers:

```yaml
image:
  repository: docker.io/my-org/my-app # {"$imagepolicy": "flux-system:my-app:name"}
  tag: latest # {"$imagepolicy": "flux-system:my-app:tag"}
  digest: sha256:ec0119... # {"$imagepolicy": "flux-system:my-app:digest"}
```

The image APIs are stable at `image.toolkit.fluxcd.io/v1`. Update old commit
templates away from removed `.Updated` and `.Changed.ImageResult` fields.
Details are in [image automation](references/image-automation.md).

## Reactive configuration

To reconcile immediately when a referenced ConfigMap or Secret changes, label
that object:

```yaml
metadata:
  labels:
    reconcile.fluxcd.io/watch: Enabled
```

Alternatively, configure the relevant controller with
`--watch-configs-label-selector=owner!=helm`. This applies to supported
Kustomization, HelmRelease, and Receiver references; consult the detailed
reference for the exact fields.

## Notifications, status, and Receivers

Flux object annotations can enrich notification events. Use
`event.toolkit.fluxcd.io/commit` for commit status providers and
`event.toolkit.fluxcd.io/change_request` for pull or merge request comment
providers. Comment providers update a deduplicated deployment-status comment
without an intermediary CI workflow.

`Provider.spec.commitStatusExpr` can derive per-cluster or per-tenant status
identifiers with CEL. `proxySecretRef` and `certSecretRef` supply proxy and
mutual-TLS material. A Provider of type `otel` converts reconciliation events
into related source-rooted traces.

Receivers can filter resources with CEL. Generic Receivers can validate an
OIDC ID token instead of an HMAC shared secret and can be invoked with:

```shell
flux trigger receiver
```

See [notifications and Receivers](references/notifications-and-receivers.md)
for provider types, GitHub App and cloud authentication, GCR requirements, and
event metadata behavior.

## Debugging and operational tooling

Inspect fully merged configuration with:

```shell
flux debug kustomization --show-vars
flux debug helmrelease --show-values
```

These commands print referenced Secret values in clear text. Treat terminal
output, logs, and captured transcripts as sensitive.

The CLI supports independently versioned plugins under `~/fluxcd/plugins`.
Pin versions or immutable digests in reproducible automation. The Flux
Operator UI provides GitOps rollout views, workload dashboards, multi-pod and
multi-container logs, and RBAC-guarded actions using user impersonation.

Read [CLI and Operator](references/cli-and-operator.md) for stable artifact
commands, plugin lifecycle commands, and UI authentication details.
