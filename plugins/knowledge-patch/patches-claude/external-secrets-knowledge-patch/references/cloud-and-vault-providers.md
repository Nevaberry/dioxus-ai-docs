# Cloud, Vault, and Kubernetes Providers

Provider capabilities evolve independently. Confirm the store type and controller
version before using authentication, metadata, lookup, existence, or write
features described here.

## AWS

### Configuration and credentials

- Parameter Store can configure its parameter tier from 0.13.0.
- Secrets Manager accepts `AWSProvider.prefix` from 0.16.0 for a common remote
  secret-name prefix.
- AWS provider workflows can use AWS tag metadata from 0.16.0.
- ECR authorization-token generation accepts custom endpoints from 0.18.0.
- The `ECRAuthorizationToken` generator again resolves through the AWS credential
  chain from 0.19.0.
- When explicit credentials are supplied, resolution no longer falls back to EC2
  Instance Metadata Service from 2.2.0.
- Kubernetes context is injected into STS sessions as session tags from 2.5.0.

### Secrets Manager filters and metadata

- Tag update, patch, and delete operations are supported from 0.19.0.
- When both name and tags are configured as filters, both criteria apply from
  1.2.0.
- Resource policies are canonicalized to sorted JSON before comparison from
  1.2.0, so ordering-only differences do not cause updates.
- Tags and resource policies synchronize even when the value is unchanged from
  2.2.0.
- An empty resource policy is handled during `PushSecret` operations from 2.3.0.

### Replication and deletion

- Secrets Manager accepts `replicationLocations` from 2.7.0.
- Empty replica-region entries are omitted instead of sent to AWS from 2.9.0.
- Before deleting a replicated secret, the provider detaches replica regions from
  2.9.0 so deletion can proceed.

### AWS Certificate Manager

AWS Certificate Manager is available as a provider from 2.8.0.

## Google Cloud

### Workload Identity and project selection

- GCP Workload Identity parameters became optional in 0.16.0; omit inapplicable
  fields instead of providing placeholders.
- Workload Identity Federation is supported from 0.20.0.
- Federation through a Kubernetes ServiceAccount can impersonate a service account
  from 2.3.0.
- The service-account email is no longer mandatory for WIF impersonation from
  2.5.0.
- Secret Manager can auto-detect `projectID` from the GCP metadata server from
  2.2.0.

### Secret Manager regional behavior

- GCP `PushSecret` applies location and replication settings correctly from
  0.17.0.
- Regional push operations omit replication settings from 0.18.0.
- When a store location is configured, existence checks look for regional secrets
  from 1.2.0.
- GCP push checks that a secret version exists from 1.1.0, rather than treating a
  versionless secret as a usable target.
- Multiple `replicationLocations` are supported for GCP pushes from 2.4.0.

## Azure Key Vault

- Fetched Azure Key Vault secrets include expiration time from 2.2.0.
- Azure `PushSecret` accepts `contentType` from 2.4.0.

## Kubernetes provider

### Authentication and trust

- `auth` is optional from 0.20.0; omit it instead of adding an empty block.
- With no configured CA, the provider falls back to system CA roots from 2.1.0.
- Provider TokenRequests use the URL namespace in the request body from 2.6.0,
  fixing calls where the target namespace differs from caller context.

### Read and metadata behavior

- Remote namespace information can be added to fetched Secret metadata from
  0.20.0.
- `SecretExists` is implemented from 2.1.0.

### Write and deletion behavior

- Whole-Secret deletion is supported from 1.1.0; deletion no longer needs to be
  decomposed key by key.
- Push operations replace the entire remote Secret from 2.7.0. Existing keys that
  are absent from the pushed source are removed instead of merged through.

## HashiCorp Vault

### Dynamic secrets and caching

- `allowEmptyResponse` allows an empty Vault dynamic-secret response from 0.13.0.
- Vault clients are cached per namespace when required from 0.17.0, preventing
  namespace-specific access from sharing the wrong client.
- Token caching graduated from experimental status in 2.3.0, and validation now
  includes token expiry.
- `VaultDynamicSecret` GET requests can take parameters from the resource spec from
  2.4.0; GET uses its own parameter.

### Authentication and trust

- Pod Identity authentication is supported from 0.20.0.
- Vault authentication supports GCP Workload Identity from 1.1.0.
- TLS authentication accepts `VaultRole` from 2.3.0.

### Push and metadata

- Vault implements the existence and set operations needed for `PushSecret` from
  0.20.0.
- Vault v2 custom metadata exposes additional values to ESO from 2.8.0.

## OpenBao

OpenBao could be used through the Vault provider from 0.17.0. A dedicated OpenBao
provider arrived in 2.7.0 and supports `caBundle` or `caProvider`,
`auth.userPass`, `auth.appRole`, and OpenBao namespaces.

## IBM Cloud Secrets Manager

- Custom credentials are supported from 0.18.0.
- API-key authentication can override the IAM endpoint from 1.1.0.

## Cloud.ru Secret Manager

Cloud.ru Secret Manager became a provider in 0.15.0 and gained path support in
2.2.0.

## Volcengine

The Volcengine provider arrived in 0.20.0. From 2.7.0, it honors
`secretRef.namespace` on a `ClusterSecretStore`, resolving credentials from the
configured namespace.

## Yandex

From 0.20.0, Yandex Lockbox and Certificate Manager can fetch secrets and
certificates by name rather than requiring only other identifiers.

## Barbican

Barbican became a provider in 1.2.0. From 2.8.0 it supports `property` and
`extract`, and treats `find.name.regexp` as a regular expression rather than an
exact name.

## Other cloud providers

- Nebius MysteryBox became a provider in 2.1.0.
- OVHcloud became a provider in 2.3.0.
- Alibaba and Device42 were removed in 2.0.0 because they were unsupported and
  unmaintained; migrate before upgrading.
