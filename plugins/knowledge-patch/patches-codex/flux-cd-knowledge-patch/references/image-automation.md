# Image automation

## Pin mutable tags to digests

Since 2.6.0, set `ImagePolicy.spec.digestReflectionPolicy` to `Always` to track
the newest digest behind a tag. `ImageUpdateAutomation` can then write a full
reference in the form `<registry>/<name>:<tag>@<digest>`.

Use component markers when a custom resource stores the image parts in
separate fields:

```yaml
spec:
  values:
    image:
      repository: docker.io/my-org/my-app # {"$imagepolicy": "flux-system:my-app:name"}
      tag: latest # {"$imagepolicy": "flux-system:my-app:tag"}
      digest: sha256:ec0119... # {"$imagepolicy": "flux-system:my-app:digest"}
```

The `:digest` marker is specifically responsible for updating the digest
field; retain `:name` and `:tag` markers for the other fields.

## Migrate to stable image APIs

The following resources are stable at `image.toolkit.fluxcd.io/v1` since
2.7.0:

- `ImageRepository`
- `ImagePolicy`
- `ImageUpdateAutomation`

Run `flux migrate` before installing CRDs that remove beta storage versions.
Upgrade the `ImageUpdateAutomation` CRD together with its controller when
moving to 2.9.4 because that maintenance release changes its schema.

## Replace removed controller flags and template fields

The image-reflector-controller `autologin` flags were removed in 2.7.0. Set
`ImageRepository.spec.provider` to the appropriate cloud provider instead.

Update commit-message templates that use the removed `.Updated` or
`.Changed.ImageResult` fields. Use one of:

- `.Changed.FileChanges` for changed files;
- `.Changed.Objects` for changed Kubernetes objects;
- the flat `.Changed.Changes` list for a consolidated view.

## Suspend and scope automation

Set `ImagePolicy.spec.suspend` to pause policy evaluation without deleting the
policy. To use sparse checkout in `ImageUpdateAutomation`, enable the 2.7.0
feature on image-automation-controller:

```shell
--feature-gates=GitSparseCheckout=true
```

The controller can use Kubernetes Workload Identity for Azure DevOps
repositories, avoiding a static Git credential when the environment is
configured for federated identity.

## Authenticate and sign Git writes

Image automation can authenticate to GitHub as an App installation by
referencing a GitHub App Secret through
`ImageUpdateAutomation.spec.git` configuration. Since 2.9.0, pushed commits
can be SSH-signed with `ImageUpdateAutomation.spec.git.commit.signingKey`.

Use a signing key Secret appropriate for SSH commit signing; this is distinct
from transport authentication to the repository.

## Remove unsafe refspec operations

As of 2.9.4, `ImageUpdateAutomation` rejects refspecs that force-update or
delete refs. Remove those operations before upgrading. Keep automation writes
as normal non-forced updates to the intended branch.
