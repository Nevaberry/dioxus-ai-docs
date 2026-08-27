# Image Automation

## Stable APIs and migration

`ImageRepository`, `ImagePolicy`, and `ImageUpdateAutomation` are stable at
`image.toolkit.fluxcd.io/v1` (since 2.7.0).

Before upgrading existing automation:

- Remove image-reflector-controller `autologin` flags; they no longer exist.
  Set `ImageRepository.spec.provider` for cloud registries instead.
- Replace commit-template `.Updated` and `.Changed.ImageResult` fields with
  `.Changed.FileChanges`, `.Changed.Objects`, or the flat
  `.Changed.Changes` list.
- Run `flux migrate` before a Flux 2.9 upgrade because that release removes
  `image.toolkit.fluxcd.io/v1beta2`.

## Registry authentication and validation

Since 2.6.0, `ImageRepository.spec.provider` is validated against its
repository URL. Select `aws`, `azure`, or `gcp` only for a matching registry
when using automatic OIDC authentication. For a public repository or
image-pull Secret, omit the provider or set it to `generic`.

Image-reflector-controller supports GCP sovereign-cloud artifact registries
(since 2.9.4).

The `ObjectLevelWorkloadIdentity` gate permits per-object registry identities
for ImageRepository (since 2.6.0). Image-automation-controller can use
Kubernetes Workload Identity for Azure DevOps repositories (since 2.7.0).

## Digest-pinned updates

Set `ImagePolicy.spec.digestReflectionPolicy` to `Always` to track the newest
digest (since 2.6.0). ImageUpdateAutomation then writes an image reference as
`<registry>/<name>:<tag>@<digest>`.

Use the `:digest` marker when repository, tag, and digest are stored in separate
custom-resource fields:

```yaml
spec:
  values:
    image:
      repository: docker.io/my-org/my-app # {"$imagepolicy": "flux-system:my-app:name"}
      tag: latest # {"$imagepolicy": "flux-system:my-app:tag"}
      digest: sha256:ec0119... # {"$imagepolicy": "flux-system:my-app:digest"}
```

`ImagePolicy.spec.suspend` pauses policy evaluation (since 2.7.0).

## Sparse checkout

Git sparse checkout for ImageUpdateAutomation is available behind the
image-automation-controller flag
`--feature-gates=GitSparseCheckout=true` (since 2.7.0). Use it when automation
needs only selected paths from a large repository.

## Commit authentication and signatures

ImageUpdateAutomation can authenticate to GitHub with an App Secret referenced
by `.spec.secretRef.name` (since 2.5.0).

Since 2.9.0, set `ImageUpdateAutomation.spec.git.commit.signingKey` to sign
pushed commits with an SSH key. `flux bootstrap` can SSH-sign its manifest
commits as well.

## Verification

OCI artifact and container-image verification supports Cosign v3 (since
2.8.0). Source-controller can use a custom Sigstore trusted root for keyless
verification (since 2.9.0), including self-hosted Rekor and Fulcio services in
air-gapped installations.

## Refspec safety and schema coordination

Since 2.9.4, ImageUpdateAutomation rejects refspecs that force-update or delete
refs. Remove those operations before upgrading.

Flux 2.9.4 also changes the ImageUpdateAutomation CRD schema. Update that CRD
together with image-automation-controller rather than deploying either side
alone.
