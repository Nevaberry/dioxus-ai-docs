# Security, Identity, and RBAC

## Authorization defaults

### Grant log access explicitly

Log access enforces RBAC by default as of 3.0.0. During an upgrade, enumerate
roles that need pod logs, grant explicit permissions, and verify access through
both the CLI and API.

### Review fine-grained inheritance

Fine-grained RBAC inheritance is disabled by default in 3.0.0. Rework policies
that depended on an Application permission automatically flowing to its
resources.

### Repair invalid policy references

User-defined roles and policies receive referential-integrity checks in 3.0.0.
Fix missing or dangling role and policy references rather than expecting
permissive configuration loading.

## Tokens and sessions

### Use bearer authentication deliberately

Bearer-token authentication is supported as of 3.0.0. Scope tokens to the
minimum RBAC policy, protect them in transit and at rest, and exercise rotation
and revocation paths.

### Clean up expired project-role tokens

Since 3.1.0, the UI can delete all expired tokens for a project role in one
operation. Review the affected role before bulk deletion and confirm that only
expired credentials are selected.

### Identify Entra tokens without `jti`

For Microsoft Entra ID tokens that omit `jti`, Argo CD uses the `uti` claim as
the token ID as of 3.4.6. Token auditing and revocation logic should accept that
identifier fallback.

### Renew OIDC sessions

As of 3.4.6, an available OIDC refresh token renews an expired session rather
than forcing a fresh login. Align refresh-token lifetime, revocation, and
storage with the desired session policy.

## SSO and identity providers

### Configure the callback host

OAuth2 login accepts `--sso-host` in 3.2.0 to select the SSO callback host.
Match it to externally reachable routing and the identity provider's registered
redirect URI.

### Use Azure workload identity for Entra SSO

Microsoft Entra SSO supports Azure workload identity as of 3.0.0. Prefer
short-lived workload credentials and grant only the identity-provider access
needed by Argo CD.

### Resolve group-claim overflow

In 3.5.0, Microsoft Entra ID group-claim overflow can be resolved through a
Microsoft Graph API lookup. Scope Graph permissions to the required group
read, and account for lookup failure or throttling in authorization tests.

### Set a custom UserInfo endpoint

The OIDC UserInfo URL can be customized in 3.5.0 rather than being fixed by
provider discovery. Validate TLS, issuer alignment, returned subject, and claim
mapping when overriding discovery behavior.

### Preserve Dex environment substitution

The regression that broke environment-variable substitution in Dex
configuration is fixed in 3.3.13. Remove workarounds that hard-code substituted
values and verify that missing variables fail according to deployment policy.

## Server-operation impersonation

Impersonation is beta in 3.5.0 and applies to server operations including logs
and deletes. Test the effective Kubernetes identity and audit trail for each
operation. Strict enforcement can be disabled for compatibility, but doing so
weakens the intended identity boundary and should be time-bounded.

## Secret and static-content protection

### Keep Secret values masked in diff

In 3.3.13, server-side diff prevents CLI Secret-mask spoofing and hides Secret
data in the `last-applied-configuration` annotation. Do not re-expose that
annotation through custom diff formatting or diagnostic logs.

### Retain static asset hardening

The static-assets endpoint is protected against symlink traversal as of 3.1.0.
Avoid custom asset-serving wrappers that resolve symlinks outside the intended
static root.
