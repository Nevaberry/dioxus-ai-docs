# Authentication, Identity, and Policy

## Privileged system operations

`sys/generate-root`,
`sys/replication/dr/secondary/generate-operation-token`, and `sys/rekey`
authenticate callers by default. A root token generated on the primary can
authenticate to a DR secondary. Restore legacy unauthenticated behavior only
for an explicitly selected operation. (`1.19-changelog`)

```hcl
enable_unauthenticated_access = ["generate-root", "generate-operation-token", "rekey"]
```

A root token can relock an Enterprise namespace. (`1.19-changelog`)

Cancelling a rekey operation requires its nonce, so automation must retain and
send the nonce. (`1.19`)

## Identity entities, aliases, and SCIM

### De-duplication and merges

The disabled-by-default `force_identity_deduplication` activation flag resolves
duplicate entities and groups by renaming them. Entity merges require `sudo`,
and wildcards are rejected in rendered identity templates.
(`1.19-changelog`)

`identity/entity/merge` rejects a request involving any SCIM-managed entity;
even privileged callers cannot move aliases, group memberships, or policies
across the SCIM ownership boundary. (`2.0.4`)

### Alias metadata and list metadata

Enterprise AppRole, AWS, certificate, GitHub, LDAP, Okta, RADIUS, SCEP, and
userpass configuration accepts `alias_metadata`, which populates alias custom
metadata. (`1.21-changelog`)

Identity list responses include entity status plus entity and alias timestamps
in `key_info`, avoiding a fetch for every entity when inspecting lifecycle
state. (`2.0.4`)

### SCIM provisioning and filtering

Enterprise beta SCIM 2.0 support provisions externally managed entities,
aliases, and groups. User PATCH can contain multiple changes, update metadata,
names, or active status, and use explicit paths. Group removal supports paths
such as `members[value eq "id"]`. (`2.0-changelog`)

`GET /scim/v2/Users` supports `userName eq`, `externalId eq`, `active eq`, and
`meta.lastModified` comparisons with `gt`, `ge`, `lt`, or `le`.
`GET /scim/v2/Groups` supports `displayName eq` and the same timestamp
comparisons. Unsupported filters return HTTP 400, `ServiceProviderConfig`
advertises filtering, and User resources expose a read-only `groups` field of
direct memberships managed by the requesting SCIM client. (`2.0.4`)

## ACL and request-policy behavior

### Canonical paths and list parameters

Vault began rejecting non-canonical paths in 1.19.16; 1.19.19 redirects paths
containing `/./`, `/../`, or `//` to their cleaned forms. A mount tuneable can
trim trailing slashes on POST. A trailing-slash LIST honors a more-specific deny
instead of falling through to a broader allow. (`1.19-changelog`)

`VAULT_NEW_PER_ELEMENT_MATCHING_ON_LIST` opted into contains-all matching for
list-valued `allowed_parameters` and `denied_parameters`.
(`1.19-changelog`)

Exact-match list comparison is retired in 1.21.x; policies must use the
per-element behavior. (`1.21`)

For a `policies` request-field constraint, Vault lowercases policy names before
evaluating `allowed_parameters` or `denied_parameters`; mixed case cannot evade
a lowercase constraint. (`2.0.4`)

### Rendered and resultant paths

`resultant-acl` merges segment-wildcard (`+`) paths into `glob_paths` alongside
prefix rules, giving callers a complete view of glob-style permissions.
(`1.21-changelog`)

Set the global `deny_slash_in_templated_path` option to reject identity-template
values containing `/` and prevent a rendered value from adding path segments.
The default is `false`. (`2.0.4`)

```hcl
deny_slash_in_templated_path = true
```

Enterprise soft-mandatory Sentinel policies honor an override flag and allow a
previously denied request when the override is set. (`1.21-changelog`)

The mounts API can unset `allowed_response_headers`. (`1.21-changelog`)

## Forwarded identity and certificate auth

### Trusted proxy headers

Vault removes Vault tokens from a plugin-bound `Authorization` header unless
`Authorization` is explicitly among passthrough request headers. Client IPs
read from `X-Forwarded-For` must parse as IPv4 or IPv6.
(`1.19-changelog`)

`x_forwarded_for_client_cert_header` accepts RFC 9440 colon-wrapped Base64
certificates. `enable_metadata_on_failures` can include client-certificate
metadata in failed-login responses and audit records. (`1.19-changelog`)

Certificate auth accepts forwarded client-certificate headers when Vault
listener TLS is disabled, including headers from AWS Application Load
Balancers. This permits proxy TLS termination while retaining certificate
login; configure the trust boundary carefully. (`2.0.4`)

### Certificate role matching

Certificate-auth roles accept `allowed_organizations`. Non-CA matching compares
certificate equality, renewal requires the certificate attached to the
session, and role-based quotas apply to certificate auth.
(`1.21-changelog`)

Enterprise SPIFFE authentication verifies the full peer certificate chain, so
chain material provided by the peer participates in validation. (`2.0.4`)

## Directory, cloud, and user authentication

### LDAP and RADIUS

LDAP login errors when a user-DN search returns multiple entries and always
rejects an empty password. An option permits `sAMAccountName` login while
`upndomain` is configured. (`1.19-changelog`)

RADIUS `case_insensitive_names` prevents case-only username collisions and
enables case-insensitive lookup. (`1.19-changelog`)

LDAP auth can use a separate URL for root-credential rotation. MFA/TOTP is
enforced when `username_as_alias` is enabled. (`1.21-changelog`)

The deprecated LDAP `deny_null_bind` option no longer affects behavior because
empty passwords are always denied; remove it before the option disappears.
(`upgrade-safety`)

### Azure, Kubernetes, and SAML

Azure login requires configured `resource_group_name`, `vm_name`, and
`vmss_name` values to match token claims. (`1.19-changelog`)

Azure auth requires a bound group or service-principal ID. Existing
configurations without either binding must be updated. (`1.20`)

Values stored at `auth/azure/config` take precedence over `AZURE_*` environment
variables. Move intended overrides into stored plugin configuration.
(`upgrade-safety`)

Kubernetes auth warns about role audiences; review audience settings when
creating or updating roles. (`1.20`)

`VAULT_SAML_DENY_INTERNAL_URLS` prevents SAML `idp_metadata_url`, `idp_sso_url`,
and `acs_urls` values from resolving to internal IP addresses.
(`1.21-changelog`)

The Azure OIDC provider can retrieve groups through the Azure Graph API.
(`2.0`)

### Other auth-method behavior

Local LDAP, AWS, GCP, or Azure auth-mount writes can ignore a mount's `local`
flag in 1.19.x; no workaround is listed. (`1.19`)

The Cloud Foundry plugin initializes its client only for a config write or
login. Set `force_new_client` to create a new client for every login rather than
reuse the shared cached client. (`2.0`)

Centrify authentication is no longer officially supported; migrate to another
auth method. (`upgrade-safety`)

## MFA, SPIFFE, and workload identity

Enterprise users can self-enroll in login MFA TOTP from a QR code and secret
generated during login. Enable it on the TOTP login-MFA method with
`enable_self_enrollment`. (`1.21-changelog`)

Enterprise SPIFFE auth accepts JWT- and X.509-based SPIFFE IDs.
(`1.21-changelog`)

Authenticated workloads can request JWT-SVIDs from Vault, allowing Vault to
issue SPIFFE identities in addition to authenticating them. (`2.0`)

## Agent authorization and OAuth resource server

Enterprise beta support introduced an Agent Registry and an OAuth resource
server for registered agent entities. Once configured, OAuth 2.0 JWTs authorize
Vault requests without a Vault token. (`2.0-changelog`)

By 2.0.3, native agent support is a public beta available to all customers,
rather than only an Enterprise beta. (`2.0`)

Read a resource-server profile by configuration ID at
`sys/config/oauth-resource-server/id/:config_id`. A resource-server JWT may omit
`typ`; when present it must be `at+jwt`, `application/at+jwt`, or `JWT`. An empty
`authorization_details` array counts as absent when details are optional.
(`2.0.4`)

Rich Authorization Requests can carry `allowed_parameters`,
`denied_parameters`, and `required_parameters` in `authorization_details`.
These values support identity templates such as `{{identity.entity.id}}` for
identity-dependent authorization. (`2.0.4`)
