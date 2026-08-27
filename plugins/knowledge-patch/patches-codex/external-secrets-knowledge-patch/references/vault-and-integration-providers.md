# Vault and integration providers

Read this reference for Vault, OpenBao, 1Password, Infisical, Akeyless,
Passbolt, Delinea, BeyondTrust, GitHub, Grafana, Doppler, Keeper, Conjur,
Devolutions, Pulumi, and related integrations.

## Vault and OpenBao

### Dynamic secrets and request parameters

Vault dynamic secrets accept `allowEmptyResponse` when an empty response should
be treated as valid (since 0.13.0). `VaultDynamicSecret` GET requests can take
parameters from the resource spec, and GET uses its own parameters correctly
(since 2.4.0).

### Authentication

Vault supports Pod Identity authentication (since 0.20.0) and authentication
through GCP Workload Identity (since 1.1.0). TLS authentication accepts a
`VaultRole` attribute (since 2.3.0). Check that the identity mechanism, Vault
role, Kubernetes audience, namespace, and TLS material agree.

### Client and token caching

Vault clients are cached separately where namespaces require distinct access
(since 0.17.0). Token caching graduated from experimental status, and token
expiry participates in validation (since 2.3.0). Do not reuse assumptions from
one Vault namespace or token lifetime in another.

### Push and metadata

Vault implements the remote-existence check and set operations needed for
`PushSecret` (since 0.20.0). Vault v2 custom metadata exposes additional values
to External Secrets (since 2.8.0).

### Dedicated OpenBao provider

OpenBao was initially supported through Vault compatibility (0.17.0). A
dedicated OpenBao provider is available since 2.7.0, with custom trust through
`caBundle` or `caProvider`, `auth.userPass`, `auth.appRole`, and OpenBao
namespaces. Prefer the dedicated provider when its native configuration is
needed.

## 1Password

### Provider choices and addressing

The SDK-based 1Password provider was introduced in 0.17.0. It supports secret
maps and vault selection by UUID (since 0.18.0), native item IDs (since 2.2.0),
and 1Password Environments (since 2.9.0).

The SDK provider implements `GetAllSecrets` for bulk selection (since 2.7.0).
Each 1Password client receives a fresh provider instance (since 2.5.0), avoiding
a race in which operations could target the wrong vault.

### Push behavior

1Password Connect is recognized as read-write (since 0.18.0). The SDK provider
supports multi-field pushes and completes its push implementation (since
2.3.0). The provider honors `IfNotExists` (since 2.8.0). Verify whether a store
uses Connect or SDK and which addressing fields the chosen implementation
accepts.

### Authorization retries

Authorization failures are retried (since 0.20.0), allowing transient failures
to recover. Persistent authorization errors still require inspection of the
item, vault, service account, and SDK/Connect configuration.

## Infisical

### Errors, paths, and find

Missing-secret and authentication errors are surfaced rather than failing
silently (since 0.13.0). `data` references can address secrets within paths
(since 0.17.0). Since 2.2.0, `dataFrom.find.path` filters by secret path, not by
secret name.

### Authentication and scope

Authentication methods are configurable (since 0.19.0). Kubernetes
authentication can use a Client JWT as the Reviewer JWT token (since 0.20.0).
Secret scope may include an organization slug (since 2.7.0).

### Push and absence semantics

Infisical supports `PushSecret` (since 2.7.0). An HTTP 404 is returned as
`NoSecretErr`, so a genuinely missing remote secret follows normal absence
semantics rather than generic provider-failure behavior.

## Akeyless

The Akeyless provider is classified as read-write so pushes route to it (since
2.7.0). It supports `azure_ad` Workload Identity through `serviceAccountRef`
(since 2.8.0). Store configuration accepts `ignoreCache` to bypass the Akeyless
Gateway cache, and `dataFrom.extract.property` can select nested JSON (both
since 2.8.0).

Since 2.9.0, Akeyless API failures are no longer classified as missing items.
Handle absent secrets separately from authentication, transport, gateway, and
API failures.

## Passbolt

Passbolt honors `refreshInterval` correctly (since 0.14.0), supports its V5 API
(since 2.2.0), and accepts a custom CA bundle or CA provider (since 2.4.0).
`ExternalSecret` also supports the `v5-custom-fields` resource type (since
2.6.0).

## Delinea Secret Server

- Fetched values need not be JSON (since 0.18.0).
- Connections accept a domain and secrets can be looked up by path (since
  0.20.0).
- TLS is configured for provider connections (since 1.1.0).
- `PushSecret` is supported (since 2.3.0).
- Push content can be created with BeyondTrust API v3.2 only in the BeyondTrust
  provider; do not confuse these two integrations.
- Access-token authentication is supported (since 2.8.0).

## BeyondTrust

The provider accepts an API-version parameter (since 0.14.0). Get-secret calls
accept `decrypt` (since 1.3.0), and API v3.2 can create secrets (since 2.5.0).
BeyondTrust WorkloadCredentials is also available as a distinct provider (since
2.7.0). Select the provider and API version deliberately; their credential and
write capabilities differ.

## GitHub

GitHub provider errors are surfaced (since 0.17.0). `GithubProvider` accepts
`orgSecretVisibility` for organization-secret visibility (since 2.3.0).
Updating an organization secret preserves its selected repositories (since
2.7.0); visibility changes should not silently discard the repository set.

## Grafana

The Grafana service-account credential generator arrived in 0.14.0. In-cluster
Grafana integration and role pass-through improved in 0.15.0. `SecondsToLive`
is optional since 2.8.0, so an explicit token lifetime is no longer required.
Choose the service-account role and lifetime based on the consumer rather than
relying on an incidental generator default.

## Doppler and Pulumi

Doppler supports OIDC authentication (since 1.2.0), and its provider errors
include the HTTP status (since 2.7.0). Pulumi authentication supports OIDC
(since 2.5.0). Diagnose identity, audience, endpoint, and HTTP response before
treating an error as a missing secret.

## Keeper

Keeper can retrieve a secret by ID or name (since 2.4.0). It exposes the
`provider_api_calls_count` metric (since 2.6.0), which can reveal unexpected
polling or fan-out volume.

## Conjur

Conjur returns explicit errors for unimplemented `PushSecret` and
`DeleteSecret` operations (since 2.4.0). Certificate-based authentication is
supported (since 2.8.0). Certificate authentication does not add write support;
verify the operation separately.

## Devolutions Server

Devolutions Server is supported (since 1.3.0), and entries can be addressed by
name (since 2.4.0).

## Other integrations

- OVHcloud is available as a provider (since 2.3.0).
- The Secret Server, Kubernetes, and other provider names can describe
  different capability sets; compare the exact provider schema before copying
  authentication or path fields.
- Environment-aware group-variable selection has been supported since 0.18.0;
  include environment context when a provider or generator resolves grouped
  values.
