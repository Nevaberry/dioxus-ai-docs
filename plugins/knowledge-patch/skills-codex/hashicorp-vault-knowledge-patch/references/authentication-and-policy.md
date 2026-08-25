# Authentication, Identity, and Policy

Use this reference for auth methods, identities, SCIM, OAuth resource-server
authorization, ACL behavior, and policy templates.

## Authentication behavior and configuration

### Forwarded request headers (`1.19-changelog`)

Vault strips Vault tokens from a plugin-bound `Authorization` header unless
`Authorization` is explicitly configured as a passthrough request header.
Addresses derived from `X-Forwarded-For` must parse as valid IPv4 or IPv6.

### Certificate auth behind proxies (`1.19-changelog`)

`x_forwarded_for_client_cert_header` accepts RFC 9440 colon-wrapped Base64
certificates. `enable_metadata_on_failures` can include client-certificate
metadata in failed-login responses and audit records.

### LDAP authentication changes (`1.19-changelog`)

LDAP login fails if a user-DN search returns multiple entries and always
rejects empty passwords. An option permits `sAMAccountName` login with
`upndomain` configured.

### Azure authentication claim binding (`1.19-changelog`)

Configured `resource_group_name`, `vm_name`, and `vmss_name` values must match
the Azure token claims.

### RADIUS name matching (`1.19-changelog`)

Set `case_insensitive_names` to prevent case-only username collisions and use
case-insensitive matching.

### Auto-auth credential reloads (`1.19-changelog`)

`enable_reauth_on_new_credentials` makes supported auto-auth methods log in
again when credentials change. Certificate auto-auth then watches its
certificate and key files.

### Azure authentication binding requirement (`1.20`)

Azure auth requires a bound group or service-principal ID. Update any method
configuration that lacks both.

### Kubernetes role audience warnings (`1.20`)

Kubernetes authentication roles emit audience warnings; review the audience
when creating or updating a role.

### Login MFA TOTP self-enrollment (`1.21-changelog`)

Enterprise users can enroll in login-MFA TOTP from the QR code and secret
generated during login. Enable `enable_self_enrollment` on the TOTP login-MFA
method.

### SPIFFE authentication (`1.21-changelog`)

The Enterprise SPIFFE auth plugin accepts JWT- and X.509-based SPIFFE IDs.

### SPIFFE JWT-SVID issuance (`2.0`)

Authenticated workloads can request JWT-SVIDs from Vault, allowing Vault to
issue SPIFFE workload identities as well as authenticate existing ones.

### Certificate-auth matching (`1.21-changelog`)

Certificate roles support `allowed_organizations`. Non-CA login matching uses
certificate equality, renewal requires the session certificate, and
role-based quotas apply to certificate auth.

### SAML internal-URL protection (`1.21-changelog`)

`VAULT_SAML_DENY_INTERNAL_URLS` prevents SAML `idp_metadata_url`, `idp_sso_url`,
and `acs_urls` from resolving to internal IP addresses.

### LDAP rotation URL (`1.21-changelog`)

LDAP auth can use a separate URL for root-credential rotation. MFA/TOTP is
enforced when `username_as_alias` is enabled.

### Cloud Foundry auth client handling (`2.0`)

The Cloud Foundry plugin initializes its CF client only for configuration writes
or login. `force_new_client` creates a new client per login instead of reusing
the shared cache.

### Azure OIDC group retrieval (`2.0`)

The Azure OIDC provider can retrieve groups through the Azure Graph API.

### Azure authentication precedence (`upgrade-safety`)

From 2.0, stored `auth/azure/config` values take precedence over `AZURE_*`
environment variables. Move intended overrides into stored configuration.

### LDAP null-bind setting (`upgrade-safety`)

`deny_null_bind` is deprecated and ineffective because empty-password LDAP
logins are always denied. Remove it before upgrading to a release that drops
the field.

### Centrify authentication support (`upgrade-safety`)

The Centrify authentication plugin is no longer officially supported. Migrate
to another authentication method before upgrading.

### Forwarded certificate authentication without listener TLS (`2.0.4`)

Certificate auth accepts forwarded client-certificate headers even when the
Vault listener has TLS disabled, including AWS Application Load Balancer
headers. This permits proxy TLS termination with certificate login.

### SPIFFE peer-chain verification (`2.0.4`)

Enterprise SPIFFE auth validates against the full certificate chain supplied
by the peer.

## Identity, aliases, and provisioning

### Identity de-duplication and merge controls (`1.19-changelog`)

The disabled-by-default `force_identity_deduplication` activation flag resolves
duplicate entities and groups by renaming them. Entity merges require `sudo`,
and rendered identity templates reject wildcards.

### Managed keys and namespace operations (`1.19-changelog`)

Enterprise GCP managed keys support workload identity federation credentials.
A root token can relock a namespace.

### Auth alias custom metadata (`1.21-changelog`)

Enterprise AppRole, AWS, certificate, GitHub, LDAP, Okta, RADIUS, SCEP, and
userpass configuration accepts `alias_metadata`, which populates alias custom
metadata.

### SCIM 2.0 provisioning (`2.0-changelog`)

Enterprise beta can act as a SCIM 2.0 server for externally managed entities,
aliases, and groups. User PATCH accepts multiple changes, explicit paths, and
updates to metadata, names, or active status. Remove a group member with a path
such as `members[value eq "id"]`.

### SCIM-managed entity merge boundary (`2.0.4`)

`identity/entity/merge` rejects requests involving a SCIM-managed entity, even
for privileged callers; aliases, memberships, and policies cannot cross the
SCIM ownership boundary through a merge.

### SCIM filtering and direct group memberships (`2.0.4`)

`GET /scim/v2/Users` filters on `userName eq`, `externalId eq`, `active eq`, and
`meta.lastModified` with `gt`, `ge`, `lt`, or `le`. `GET /scim/v2/Groups`
supports `displayName eq` and the same time comparisons. Unsupported
expressions return 400; `ServiceProviderConfig` advertises filtering. User
`groups` is a read-only list of direct memberships managed by the requesting
SCIM client.

### Identity list response metadata (`2.0.4`)

Identity list `key_info` includes entity status and entity/alias timestamps, so
clients need not fetch every entity to inspect lifecycle state.

## ACL and policy semantics

### List-valued policy parameters (`1.19-changelog`)

`VAULT_NEW_PER_ELEMENT_MATCHING_ON_LIST` opts into contains-all, per-element
matching for `allowed_parameters` and `denied_parameters` on releases where the
old behavior still exists.

### Resultant ACL glob paths (`1.21-changelog`)

`resultant-acl` merges segment-wildcard (`+`) rules with prefix rules in
`glob_paths`, giving clients the complete glob-style permission view.

### Sentinel policy overrides (`1.21-changelog`)

Enterprise soft-mandatory Sentinel policy denials can be overridden when the
request's policy override flag is set.

### Exact-match list-policy retirement (`1.21`)

Exact-match list comparison is retired. Policies must use per-element matching
for `allowed_parameters` and `denied_parameters`.

### AI-agent authorization (`2.0-changelog`)

Enterprise beta adds an Agent Registry and an OAuth resource server for
registered agent entities. Configured OAuth 2.0 JWTs can authorize Vault
requests directly without a Vault token.

### AI-agent support availability (`2.0`)

By 2.0.3, native agent support is a public beta available to all customers.

### Visual ACL policy generation (`2.0`)

The GUI visual policy editor can generate ACL policy snippets.

### Case-normalized ACL policy constraints (`2.0.4`)

For `allowed_parameters` or `denied_parameters` constraints on the `policies`
request field, Vault lowercases policy names before evaluation. Mixed case
cannot bypass a lowercase constraint.

### OAuth resource-server lookup and token compatibility (`2.0.4`)

Read an Enterprise resource-server profile by configuration ID at
`sys/config/oauth-resource-server/id/:config_id`. JWT `typ` may be omitted; if
present it must be `at+jwt`, `application/at+jwt`, or `JWT`. An empty
`authorization_details` array counts as absent when details are optional.

### Rich Authorization Request policy controls (`2.0.4`)

OAuth Resource Server RAR `authorization_details` supports
`allowed_parameters`, `denied_parameters`, and `required_parameters`, plus
identity templates such as `{{identity.entity.id}}`.

### Slash rejection in rendered policy paths (`2.0.4`)

Set the global option below to reject identity-template expansions containing
`/`, preventing an expansion from adding policy path segments. The default is
`false`.

```hcl
deny_slash_in_templated_path = true
```

## GUI access related to auth and policy

### TOTP in the GUI (`1.20`)

The Community GUI lists and adds TOTP accounts, reveals codes hidden by
default, and displays expiry timers.

### Root-token GUI access under EGP (`upgrade-safety`)

An open Enterprise 2.0 issue can deny root-token GUI access to an EGP-protected
child namespace when the GUI calls `sys/internal/ui/mounts`. Use CLI/API access
or explicitly permit that endpoint in the EGP.
