# Sources, authentication, and artifacts

## Use the stable OCIRepository API

`OCIRepository` is GA at `source.toolkit.fluxcd.io/v1` since 2.6.0. It is
backward compatible with `v1beta2`, so a repository manifest migrates by
changing only `apiVersion`. Migrate live stored objects before installing CRDs
that remove the beta API.

The associated stable artifact media types are:

- `application/vnd.cncf.flux.config.v1+json`
- `application/vnd.cncf.flux.content.v1.tar+gzip`

The stable CLI surface includes `flux build artifact`, `push artifact`,
`pull artifact`, `tag artifact`, `diff artifact`, and `list artifacts`.

## Validate registry provider selection

Since 2.6.0, `OCIRepository` and `ImageRepository` reject a `spec.provider`
that does not match the repository URL. Use `aws`, `azure`, or `gcp` only for
a matching registry when automatic OIDC authentication is intended. For a
public registry or image-pull-secret authentication, omit `provider` or set it
to `generic`.

GCS static authentication accepts only service-account keys as of 2.9.4.
Other static GCS credential forms must be replaced. Source-controller and
image-reflector-controller in that release also understand GCP sovereign-cloud
artifact registry endpoints.

## Authenticate as a GitHub App

Since 2.5.0, source-controller and image-automation-controller can authenticate
to GitHub repositories as an App installation. Create the Secret with:

```shell
flux create secret githubapp github-auth \
  --app-id=1 \
  --app-installation-id=2 \
  --app-private-key=~/private-key.pem
```

Reference it through `spec.secretRef.name` on a `GitRepository`, or in the
Git configuration of `ImageUpdateAutomation`. `flux create source git
--provider=github` supports this mode too.

From 2.7.0, GitRepository GitHub App authentication can also use mutual TLS.
From 2.8.0, supported flows can discover the installation ID from the
repository owner, so the ID need not be supplied manually.

## Limit Git checkout and configure TLS

`GitRepository` v1 accepts `spec.sparseCheckout` since 2.6.0:

```yaml
spec:
  sparseCheckout:
    - apps
    - clusters/production
```

Only the listed directories are fetched. HTTPS Git repositories can also use
mutual-TLS client authentication.

ImageUpdateAutomation sparse checkout is a separate 2.7.0 controller feature;
enable it on image-automation-controller with
`--feature-gates=GitSparseCheckout=true`.

## Choose object-level Workload Identity

The 2.6.0 `ObjectLevelWorkloadIdentity` feature gate allows each object or
tenant to select an identity rather than sharing one controller identity. Its
initial uses include:

- Kustomization SOPS decryption through KMS services;
- OCIRepository and ImageRepository registry access.

The 2.7.0 expansion adds object-level identity through
`spec.serviceAccountName` for:

- Bucket access to S3, Azure Blob Storage, and GCS;
- GitRepository access to Azure DevOps;
- notification Provider access to Azure DevOps, Azure Event Hub, and Google
  Pub/Sub.

Image-automation-controller can also use Kubernetes Workload Identity for
Azure DevOps repositories.

For remote-cluster reconciliation without a static kubeconfig Secret, use
`Kustomization.spec.kubeConfig.configMapRef.name` or
`HelmRelease.spec.kubeConfig.configMapRef.name`. These flows support remote
EKS, AKS, and GKE authentication when the referenced ConfigMap and environment
are configured correctly.

## Use keyless Git providers

Since 2.9.0, `GitRepository` and `flux bootstrap` can authenticate to AWS
CodeCommit with Workload Identity. Prefer this to long-lived AWS Git
credentials when the cluster and repository trust are configured for it.

## Verify and sign source revisions

`GitRepository.spec.verify` supports SSH-signed commits in addition to GPG
signatures since 2.9.0. Image automation can SSH-sign pushed commits through
`ImageUpdateAutomation.spec.git.commit.signingKey`, and `flux bootstrap` can
SSH-sign the manifest commits that it pushes.

OCI artifacts and container images support Cosign v3 verification since
2.8.0. In 2.9.0, source-controller can load a custom Sigstore trusted root for
keyless verification. Use that trusted root for air-gapped environments with
self-hosted Rekor and Fulcio rather than assuming the public Sigstore trust
domain.

## Install source-watcher

`ArtifactGenerator` and `ExternalArtifact` are supplied by the optional
source-watcher component introduced in 2.7.0. Add it at bootstrap or install
time:

```shell
--components-extra=source-watcher
```

The 2.9.4 OCI `flux-manifests` artifact includes source-watcher, so that
distribution can be used to deploy ArtifactGenerator support. Upgrade its CRD
along with the component because the 2.9.4 schema changes.

## Combine sources into an ExternalArtifact

`ArtifactGenerator` can combine content from GitRepository, OCIRepository, and
Bucket sources. Copy strategies can overwrite or merge content into one
artifact:

```yaml
apiVersion: source.extensions.fluxcd.io/v1beta1
kind: ArtifactGenerator
metadata:
  name: podinfo
  namespace: apps
spec:
  sources:
    - alias: chart
      kind: OCIRepository
      name: podinfo-chart
    - alias: repo
      kind: GitRepository
      name: podinfo-values
  artifacts:
    - name: podinfo-composite
      originRevision: "@chart"
      copy:
        - from: "@chart/"
          to: "@artifact/"
        - from: "@repo/charts/podinfo/values.yaml"
          to: "@artifact/podinfo/values.yaml"
          strategy: Overwrite
        - from: "@repo/charts/podinfo/values-prod.yaml"
          to: "@artifact/podinfo/values.yaml"
          strategy: Merge
```

A HelmRelease consumes the result through `spec.chartRef`:

```yaml
spec:
  chartRef:
    kind: ExternalArtifact
    name: podinfo-composite
```

ArtifactGenerator can extract and modify Helm charts while generating outputs
since 2.8.0.

## Split and discover monorepo content

Multiple artifact entries with path-specific `copy.from` globs split a
monorepo into independently revised `ExternalArtifact` objects. A
Kustomization consumes one through `sourceRef.kind: ExternalArtifact`; only the
artifact whose selected paths changed triggers that deployment.

Since 2.9.0, `ArtifactGenerator.spec.pathPattern` discovers matching
directories. Named captures become variables in artifact names, labels, and
copy rules:

```yaml
spec:
  sources:
    - alias: monorepo
      kind: GitRepository
      name: my-monorepo
  pathPattern: "@monorepo/apps/{app}/envs/{env}"
  artifacts:
    - name: "{app}-{env}"
      copy:
        - from: "@monorepo/apps/{app}/envs/{env}/**"
          to: "@artifact/"
```

Use discovery when directory naming is regular; use explicit artifacts when
each output needs bespoke copy or merge rules.
