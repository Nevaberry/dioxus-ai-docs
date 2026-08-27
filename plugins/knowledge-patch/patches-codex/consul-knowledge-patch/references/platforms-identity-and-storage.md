# Platforms, Identity, and Storage

## Enterprise support designations

Consul 1.21 is an Enterprise LTS release with two years of support (1.21.0).
This permits operators to remain on that line while receiving patches and
fixes. Consul 2.0.0 introduced Enterprise support options for longer contract
periods; earlier Enterprise releases continue under their existing LTS
contracts.

## Kubernetes Pod Security Admission

Since 1.21.0, Consul can be deployed with Kubernetes Pod Security Admission
controls applied per namespace. Pod Security Admission replaces
PodSecurityPolicy as the mechanism for enforcing minimum pod security
requirements.

## OpenShift compatibility and migration

### Supported 1.21 platform versions

Consul 1.21.0 supports OpenShift Container Platform 4.16, 4.17, and 4.18.

### Gateway resources for OpenShift 4.19 and later

Since 2.0.0, new Kubernetes resource types in the `consul.hashicorp.com` API
group support OpenShift 4.19 and later. Earlier Kubernetes Gateway API
`v1alpha` resources are incompatible there. Migrate existing gateway resources
to the newer types as part of the OpenShift upgrade.

## UI OIDC authentication

Since 1.22.0, PKCE is enabled by default for Consul UI OIDC login. OIDC
providers can also authenticate the client with a JWT assertion instead of a
client secret. Validate provider support and redirect flows when migrating from
secret-based authentication.

## Azure snapshot identity

Since 1.22.0, the Enterprise snapshot agent supports Azure Managed Service
Identity for Azure Blob Storage. This avoids embedding static storage
credentials in snapshot configuration.

## KV key-name validation

Since 1.22.0, the key/value endpoint validates key names. This is a breaking
security change for callers that previously sent invalid names.
`DisableKVKeyValidation` controls whether validation is disabled. Audit clients
and keys before rollout; use the switch only as a temporary compatibility
measure.
