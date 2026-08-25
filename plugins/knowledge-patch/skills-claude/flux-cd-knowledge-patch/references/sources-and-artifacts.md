# Sources and Artifacts

## OCIRepository and artifact commands

`OCIRepository` is GA at `source.toolkit.fluxcd.io/v1` (since 2.6.0). The API
is backward compatible with `v1beta2`, so update a manifest by changing only
its `apiVersion`.

These artifact commands are stable:

- `flux build artifact`
- `flux push artifact`
- `flux pull artifact`
- `flux tag artifact`
- `flux diff artifact`
- `flux list artifacts`

The Flux config media type
`application/vnd.cncf.flux.config.v1+json` and content media type
`application/vnd.cncf.flux.content.v1.tar+gzip` are stable as well.

## Registry provider validation

Since 2.6.0, OCIRepository and ImageRepository reject `.spec.provider` values
that do not match the repository URL. Use `aws`, `azure`, or `gcp` only with a
matching cloud registry and automatic OIDC authentication. For public access
or image-pull-Secret authentication, omit the provider or set it to `generic`.

## GitRepository checkout and transport

`GitRepository` v1 accepts a directory list in `.spec.sparseCheckout` to fetch
only selected paths (since 2.6.0):

```yaml
spec:
  sparseCheckout:
    - apps
    - clusters/production
```

HTTPS GitRepository connections support mutual TLS (since 2.6.0). GitHub App
authentication can also use mTLS (since 2.7.0).

## Git identity and verification

`GitRepository.spec.verify` can verify SSH-signed commits in addition to GPG
signatures (since 2.9.0). GitRepository access and `flux bootstrap` can use AWS
CodeCommit Workload Identity for keyless AWS authentication.

## OCI and image verification

OCI artifact and container-image verification supports Cosign v3 (since
2.8.0).

Source-controller accepts a custom Sigstore trusted root for keyless
verification of OCI artifacts and images (since 2.9.0). Use it to point an
air-gapped installation at self-hosted Rekor and Fulcio trust infrastructure.

## Registry compatibility

OCIRepository supports Helm's encoding of SemVer build metadata in OCI tags
(since 2.9.4). Source-controller supports GCP sovereign-cloud artifact
registries in the same release.

## ArtifactGenerator and ExternalArtifact

### Enable source-watcher (since 2.7.0)

Install the optional source-watcher component with:

```shell
flux bootstrap ... --components-extra=source-watcher
```

`ArtifactGenerator` can combine GitRepository, OCIRepository, and Bucket
content into an `ExternalArtifact`, or split a monorepo into artifacts with
independent revisions.

Since 2.9.4, the OCI `flux-manifests` artifact includes source-watcher, so an
ArtifactGenerator deployment can use that distribution.

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

A HelmRelease consumes a generated artifact through `spec.chartRef` with
`kind: ExternalArtifact`. For monorepo decomposition, use multiple artifact
entries with path-specific `copy.from` globs. Kustomizations can consume each
result with `sourceRef.kind: ExternalArtifact`, so only the artifact whose
paths changed triggers its deployment.

### Helm chart processing (since 2.8.0)

ArtifactGenerator can extract and modify Helm charts while creating an
artifact.

### Directory discovery (since 2.9.0)

`ArtifactGenerator.spec.pathPattern` discovers matching monorepo directories
and emits one ExternalArtifact for each match. Named captures become template
variables for artifact names, labels, and copy rules:

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

Flux 2.9.4 changes the ArtifactGenerator CRD schema. Upgrade the CRD and
source-watcher controller together.
