# Identity and Operations

## GitHub App authentication

### Create and use an App Secret (since 2.5.0)

Source-controller and image-automation-controller can authenticate to GitHub as
an App installation. Create the Secret with the CLI helper:

```shell
flux create secret githubapp github-auth \
  --app-id=1 \
  --app-installation-id=2 \
  --app-private-key=~/private-key.pem
```

Reference it through `.spec.secretRef.name` in a `GitRepository` or
`ImageUpdateAutomation`. `flux create source git --provider=github` also
supports this authentication mode.

GitHub App credentials can authenticate `github` and `githubdispatch`
notification Providers (since 2.6.0). GitRepository GitHub App authentication
can be combined with mutual TLS (since 2.7.0).

Since 2.8.0, supported flows can discover the installation ID from the
repository owner, so it does not always need to be supplied explicitly.

## Object-level Workload Identity

### Enable the feature gate (since 2.6.0)

`ObjectLevelWorkloadIdentity` is opt-in. It initially supports identities per
object and tenant for:

- Kustomization SOPS decryption through KMS services.
- OCIRepository and ImageRepository access to container registries.

### Expanded object support (since 2.7.0)

Object-level Kubernetes Workload Identity also supports:

- `Bucket.spec.serviceAccountName` for S3, Azure Blob Storage, and GCS.
- `GitRepository.spec.serviceAccountName` for Azure DevOps.
- `Provider.spec.serviceAccountName` for Azure DevOps, Azure Event Hub, and
  Google Pub/Sub.
- Azure DevOps access by image-automation-controller.

Kustomization and HelmRelease can authenticate to remote EKS, AKS, or GKE
clusters without a static kubeconfig Secret. Set
`spec.kubeConfig.configMapRef.name` to point at the configuration used to
obtain the remote identity.

Notification-controller can publish to Azure Event Hub with Azure Workload
Identity (since 2.6.0).

Static GCS authentication accepts service-account keys only (since 2.9.4).
Replace any other static credential form before upgrading; Workload Identity
remains the keyless option.

### Keyless Git and secret-service access (since 2.9.0)

GitRepository access and `flux bootstrap` support AWS CodeCommit through
Workload Identity, avoiding stored AWS access keys. Kustomize-controller can
authenticate to OpenBao or HashiCorp Vault with Kubernetes Workload Identity,
exchanging its ServiceAccount token instead of storing a long-lived Vault
token.

## SOPS key operations

Kustomize-controller supports centrally managed Age keys for global SOPS
decryption (since 2.7.0). It also supports SOPS secrets sealed with the Age
post-quantum cipher (since 2.9.0). Object-level identity can be used for KMS,
Vault, and OpenBao access as described above.

## Flux Operator UI

The Flux Operator Web UI provides cluster and GitOps-resource monitoring,
rollout inspection, delivery graphs, and RBAC-guarded actions (since 2.8.0).
It combines OIDC single sign-on with Kubernetes RBAC for multi-tenant clusters.

The UI adds a workload dashboard for Deployments, StatefulSets, DaemonSets,
and CronJobs plus a multi-pod, multi-container log viewer (since 2.9.0).
Workload actions and log access use Kubernetes RBAC through user impersonation.

## Flux CLI plugins

Since 2.9.0, the Flux CLI installs independently versioned plugins under
`~/fluxcd/plugins` and exposes them as `flux <plugin>`. The initial catalog
includes Mirror for declarative registry mirroring and Schema for JSON Schema
and CEL validation.

```shell
flux plugin search
flux plugin install schema@0.5.0
flux plugin list
flux plugin update schema
flux plugin uninstall schema
```

Pin a plugin version or immutable digest in reproducible automation.
