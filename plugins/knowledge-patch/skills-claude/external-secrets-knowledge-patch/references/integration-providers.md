# Integration Providers

Use this reference for provider-specific authentication, lookup, diagnostic, and
write behavior outside the major cloud, Kubernetes, Vault, and OpenBao providers.
Feature parity is not implied by provider maturity.

## 1Password

### SDK provider

- The SDK-based provider arrived in 0.17.0.
- `GetSecretMap` reached parity with 1Password Connect in 0.18.0.
- A vault can be selected by UUID from 0.18.0.
- Native item IDs are supported from 2.2.0.
- Multi-field `PushSecret` is supported from 2.3.0, completing its push
  implementation.
- A fresh provider instance is created per client from 2.5.0, preventing a race
  that could route operations to the wrong vault.
- `GetAllSecrets` is implemented from 2.7.0 for bulk selection workflows.
- `PushSecret` honors `IfNotExists` from 2.8.0.
- 1Password Environments are supported from 2.9.0.

### Connect and shared behavior

- 1Password Connect is classified read-write from 0.18.0.
- Authorization failures are retried from 0.20.0 so transient failures can
  recover.

## Akeyless

- Akeyless is classified read-write from 2.7.0, so `PushSecret` operations route
  to it.
- `azure_ad` Workload Identity through `serviceAccountRef` is supported from
  2.8.0.
- `SecretStore` accepts `ignoreCache` from 2.8.0 to bypass the Akeyless Gateway
  cache.
- `dataFrom.extract.property` can extract nested JSON from 2.8.0.
- API failures are no longer misclassified as a missing item from 2.9.0, allowing
  operational failures to be distinguished from actual absence.

## BeyondTrust

- An API-version parameter is supported from 0.14.0.
- Get-secret calls accept `decrypt` from 1.3.0.
- Secret creation through API v3.2 is supported from 2.5.0.
- BeyondTrust WorkloadCredentials became a provider in 2.7.0.

## Conjur

- From 2.4.0, unimplemented `PushSecret` and `DeleteSecret` operations return an
  explicit error rather than appearing to work.
- Certificate authentication is supported from 2.8.0.

## Delinea Secret Server

- Fetched non-JSON secrets are supported from 0.18.0.
- Domain selection and lookup by path are supported from 0.20.0.
- TLS connection configuration is applied correctly from 1.1.0.
- `PushSecret` is supported from 2.3.0.
- Access-token authentication is supported from 2.8.0.

## Devolutions Server

Devolutions Server became a provider in 1.3.0 and can address entries by name from
2.4.0.

## Doppler

- OIDC authentication is supported from 1.2.0.
- Provider errors include their HTTP status from 2.7.0.

## GitHub

- GitHub provider failures are surfaced from 0.17.0.
- `GithubProvider.orgSecretVisibility` configures organization-secret visibility
  from 2.3.0.
- Updating an organization secret preserves selected repositories from 2.7.0.

## Infisical

- Missing-secret and incorrect-authentication errors are reported from 0.13.0
  rather than failing silently.
- `data` references can address secrets within paths from 0.17.0.
- Authentication methods are configurable from 0.19.0.
- Kubernetes authentication can use a Client JWT as its Reviewer JWT token from
  0.20.0.
- From 2.2.0, `dataFrom.find.path` filters by secret path rather than secret name.
- `PushSecret` is supported from 2.7.0, and a 404 becomes `NoSecretErr` so missing
  items follow absence semantics.
- Secret scopes can include an organization slug from 2.7.0.

## Passbolt

- Configured `refreshInterval` is honored correctly from 0.14.0.
- Passbolt V5 API is supported from 2.2.0.
- Custom trust can use a CA bundle or CA provider from 2.4.0.
- The `v5-custom-fields` resource type is supported in `ExternalSecret` from
  2.6.0.

## Keeper

- Secrets can be retrieved by ID or name from 2.4.0.
- `provider_api_calls_count` is exposed from 2.6.0.

## Pulumi

Pulumi authentication supports OIDC from 2.5.0.

## Grafana integration

Service-account generation is described in the templates and generators
reference. For in-cluster Grafana, role propagation and optional token lifetime
must match the target Grafana API.
