# Security, Identity, and RBAC

## Log access authorization

RBAC enforcement for logs is enabled by default since 3.0.0. Roles that could
previously view logs without an explicit permission may lose access. Exercise
log access with representative users after an upgrade and grant only the
required project and resource scope.

## Fine-grained Application RBAC

Fine-grained RBAC inheritance is disabled by default since 3.0.0. Policies
that depended on an Application permission being inherited by its resources
need review. Express required child-resource permissions directly instead of
assuming the older inheritance behavior remains implicit.

Argo CD also checks user-defined roles and policies for referential integrity
since 3.0.0. Resolve references to missing or renamed roles and policies as a
configuration error rather than expecting them to be accepted silently.

## Authentication and SSO

- Bearer-token authentication is supported since 3.0.0. Apply the same token
  lifetime, storage, transport, and redaction controls used for other API
  credentials.
- Microsoft Entra SSO can use Azure workload identity since 3.0.0, avoiding a
  long-lived client secret in supported Azure deployments.
- OAuth2 login configuration accepts `--sso-host` since 3.2.0. Set it when the
  externally visible SSO callback host differs from the server's ordinary host,
  and keep redirect registration and proxy routing aligned with that value.

## Project-role token cleanup

Since 3.1.0, the UI can delete all expired tokens for a project role in one
operation. Use bulk removal to reduce stale credential records, while treating
the operation as cleanup rather than revocation of tokens that remain valid.

## Static asset boundary

The static-assets endpoint is hardened against symlink traversal since 3.1.0.
Do not build an extension or packaging flow that relies on following symlinks
outside the intended static-assets tree. Keep the patched behavior in place
rather than weakening path validation to restore such access.
