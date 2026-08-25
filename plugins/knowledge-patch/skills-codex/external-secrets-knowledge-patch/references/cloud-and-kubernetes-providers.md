# Cloud and Kubernetes providers

Read this reference for cloud-provider and Kubernetes-provider authentication,
lookup, metadata, replication, existence checks, and write semantics.

## AWS

### Parameter Store and Secrets Manager configuration

- Parameter Store accepts a parameter-tier setting (since 0.13.0).
- Secrets Manager accepts `AWSProvider.prefix` for a provider-level secret-name
  prefix (since 0.16.0).
- AWS-backed workflows support tags (since 0.16.0). Secrets Manager can update,
  patch, and delete tags (since 0.19.0).
- When both name and tags are specified as Secrets Manager filters, both are
  applied (since 1.2.0).

### Credential resolution and STS context

The `ECRAuthorizationToken` generator resolves credentials through the AWS
credential chain (restored in 0.19.0) and can target custom ECR endpoints
(since 0.18.0).

When explicit AWS credentials are configured, resolution does not fall back to
the EC2 Instance Metadata Service (since 2.2.0). Kubernetes context is injected
into STS sessions as session tags (since 2.5.0); account for those tags in trust
policies, CloudTrail analysis, and session-policy limits.

### Tags and resource policies

Tag and resource-policy metadata is synchronized even when the secret value is
unchanged (since 2.2.0). Resource policies are converted to canonical, sorted
JSON before comparison (since 1.2.0), so JSON key order alone does not trigger a
change. Empty resource policies are handled during `PushSecret` operations
(since 2.3.0).

### Replicated Secrets Manager secrets

`replicationLocations` configures replicated secret locations (since 2.7.0).
Empty replica-region entries are omitted rather than sent to AWS (since 2.9.0).
Before deleting a replicated secret, the provider detaches replicated regions
so deletion can proceed (since 2.9.0). Test replica creation, update, detachment,
and cleanup as one lifecycle.

### AWS Certificate Manager

AWS Certificate Manager is available as a provider (since 2.8.0). Verify the
consumer's expected certificate, chain, and key fields rather than treating ACM
like a generic string-secret store.

## Google Cloud

### Workload identity

GCP workload-identity parameters are optional where they do not apply (since
0.16.0). The provider supports Workload Identity Federation (since 0.20.0),
including Kubernetes-service-account impersonation (since 2.3.0). The
service-account email is optional for WIF impersonation (since 2.5.0).

Vault authentication can also use GCP Workload Identity (since 1.1.0); that is
a Vault authentication path rather than direct GCP Secret Manager access.

### Project and regional secret detection

GCP Secret Manager can auto-detect `projectID` from the metadata server (since
2.2.0). When a store location is set, existence checks look for regional
secrets (since 1.2.0). Confirm the detected project and configured location in
multi-project or regional deployments.

### PushSecret replication and existence

GCP push handling applies location and replication settings correctly (since
0.17.0). Regional push operations omit replication settings (since 0.18.0),
while multi-location replication uses `replicationLocations` (since 2.4.0).
GCP push also verifies that a secret version exists before treating a target as
usable (since 1.1.0).

## Kubernetes provider

### Authentication and CA trust

The provider's `auth` field is optional (since 0.20.0). When no CA is configured,
the provider falls back to system CA roots (since 2.1.0). ConfigMap-backed
`CAProvider` access works correctly (since 2.4.0).

Provider TokenRequests use the URL namespace in the request body as well as the
request URL (since 2.6.0), which matters when the target namespace differs from
the caller's context. Restrict `serviceaccounts/token` permission to the exact
accounts used for referent authentication.

### Fetch and metadata behavior

Fetched secret metadata can include the remote namespace (since 0.20.0).
`SecretExists` is implemented (since 2.1.0), enabling policy-aware push logic to
check a target before writing.

### Delete and replace behavior

The provider can delete an entire Secret rather than deleting each key (since
1.1.0). Pushes replace the entire destination Secret instead of merging (since
2.7.0), so keys absent from the pushed object are removed.

### ClusterSecretStore access

Cross-namespace pushes through `ClusterSecretStore` work (since 2.1.0). On a
`ClusterSecretStore`, Volcengine credentials honor `secretRef.namespace` (since
2.7.0). Apply the same namespace-boundary scrutiny to every cluster-scoped
provider credential reference.

## Azure and IBM

### Azure Key Vault

Fetched Azure Key Vault secrets include expiration time (since 2.2.0).
Azure-backed `PushSecret` supports `contentType` (since 2.4.0). Treat expiration
and content type as provider metadata, and verify whether downstream templates
or consumers preserve it.

### IBM Cloud Secrets Manager

The IBM provider supports custom credentials (since 0.18.0) and can override
the IAM endpoint used for API-key authentication (since 1.1.0). Set endpoint
trust and network policy consistently when using a non-default IAM service.

## Other cloud providers

### Cloud.ru Secret Manager

Cloud.ru Secret Manager is supported (since 0.15.0), including path-based
addressing (since 2.2.0).

### Yandex

Yandex Lockbox and Certificate Manager can retrieve resources by name rather
than requiring only their other identifiers (since 0.20.0).

### Volcengine

Volcengine is supported (since 0.20.0). For cluster-scoped stores, credential
Secrets can be resolved from the namespace named by `secretRef.namespace`
(since 2.7.0).

### Barbican

Barbican is supported (since 1.2.0). It supports `property` and `extract`, and
`find.name.regexp` is interpreted as a regular expression rather than an exact
name (since 2.8.0).

### Nebius MysteryBox

Nebius MysteryBox is available as a provider (since 2.1.0).

## Provider capability checklist

Before selecting or upgrading a provider, verify these capabilities separately:

- authentication and namespaced referent behavior;
- store validation and retry support;
- exact-key retrieval, path lookup, find, and bulk retrieval;
- extraction, metadata fetch, and native-value handling;
- existence checks and `IfNotExists` behavior;
- push, overwrite, merge, whole-secret replacement, and property mapping;
- key deletion, whole-secret deletion, replication cleanup, and finalizers.

Provider maturity is not a substitute for this capability check.
