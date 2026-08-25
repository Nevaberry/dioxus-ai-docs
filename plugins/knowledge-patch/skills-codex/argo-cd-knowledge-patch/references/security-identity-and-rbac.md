# Security, Identity, and RBAC

## Log access and fine-grained RBAC

RBAC enforcement for logs is enabled by default in 3.0.0. Grant explicit log
permissions to every role that needs pod-log access, then test CLI and API
paths with representative identities.

Fine-grained RBAC inheritance is disabled by default in 3.0.0. Review policies
that expected an Application permission to flow to its resources and replace
implicit access with explicit rules where necessary.

User-defined roles and policies receive referential-integrity checks in 3.0.0.
Fix dangling references before upgrade rather than relying on permissive
loading.

## Tokens and bearer authentication

Bearer-token authentication is supported (3.0.0). Apply the same transport,
storage, expiration, and scope controls used for other reusable credentials.

The UI can delete every expired token for a project role in one operation
(3.1.0). Use the bulk cleanup while preserving audit evidence required by the
deployment.

## Microsoft Entra ID

Microsoft Entra SSO can use Azure workload identity (3.0.0). For Entra ID
tokens without `jti`, Argo CD uses `uti` as the token ID (3.4.6), so token
handling must not require `jti` unconditionally.

Microsoft Entra ID group-claim overflow can be resolved through a Microsoft
Graph API lookup (3.5.0). Provision that lookup's identity and permissions when
group membership can exceed the token claim capacity.

## OAuth2 and OIDC sessions

OAuth2 login accepts `--sso-host` for choosing the callback host (3.2.0).
Align it with externally reachable routing and registered redirect URLs.

OIDC refresh tokens can renew expired sessions instead of forcing a new login
(3.4.6). Configure session expectations around refresh-token availability and
lifetime.

The OIDC UserInfo endpoint URL can be customized rather than relying only on
provider discovery (3.5.0). Use the override when discovery does not identify
the endpoint the deployment must call.

## Dex configuration

Environment-variable substitution in Dex configuration works again in 3.3.13
after a regression. Revalidate substituted values during upgrade, especially
where a previous workaround materialized values before Dex read the config.

## Server-operation impersonation

Impersonation is beta and applies to server operations such as logs and
deletes in 3.5.0. Strict impersonation enforcement can be disabled for
compatibility. Treat disabling it as a deliberate security exception and test
authorization for each affected operation.

## Destination and cluster credentials

Global projects support `destinationServiceAccounts` (3.5.0), extending
destination service-account policy beyond individually defined projects.
Review global precedence and intended destination access before rollout.

Cluster `ExecProviderConfig` has `ProvideClusterInfo` and `Config` fields
(3.5.0). These allow exec credential providers to receive cluster information
and provider-specific configuration; pass only what the provider needs.

## Server cache namespace filtering

Objects from namespaces that are not allowed are removed before entering the
server cache (3.5.0). Security tests should verify cache-backed retrieval and
not only final response filtering.

## Static assets and Secret diff output

The static-assets endpoint is hardened against symlink traversal (3.1.0).
Keep external static content and custom extensions compatible with the
protected path behavior rather than weakening the endpoint.

Server-side diff prevents CLI Secret-mask spoofing and masks Secret content in
the last-applied-configuration annotation (3.3.13). Avoid logging or persisting
older unmasked diff output during migration.
