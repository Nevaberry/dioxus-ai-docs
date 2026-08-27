# Node SDK Migrations and Contracts

Use this reference when upgrading `@workos-inc/node` or depending on exact SDK
types, pagination, errors, events, or request behavior.

## v9 migration

- The minimum runtime is Node.js 22.11. Node.js 20 is no longer supported.
- The legacy FGA package, deprecated in v8.4, was removed. Replace it with
  authorization resources, organization roles, and role-assignment APIs.
- The Admin Portal namespace changed from `portal` to `adminPortal`.
- v9.1.1 restored the established Authorization method names after generated
  renames and corrected the endpoint for
  `listEffectivePermissionsByExternalId`.

## v10 migration

- `Group.createdAt` and `Group.updatedAt` deserialize to `Date`, not `string`.
- Construct webhook helpers with the WorkOS client:
  `new Webhooks(workos)`, not a `CryptoProvider`.
- `listResources` no longer accepts `search`.
- `vault.listObjects` is an auto-paginatable object-summary collection, not the
  earlier list-digest response. Generated Vault key and object response fields
  use camel-cased SDK names.

## Authorization and resource contracts

The SDK exposes environment and organization roles, authorization resources,
and resource-scoped custom roles. Permissions and roles expose
`resourceTypeSlug`; `createOrganizationRole` accepts `resource_type_slug`; and
`CreateAuthorizationResourceOptions` provides typed resource creation.

Resource and group role-assignment endpoints are available. Filter assignment
lists with `resource` and `role_slug`; inspect returned `source` to distinguish
direct assignments from group-derived assignments. Invitations accept
`role_slug`.

## Events and preserved payload data

Typed event contracts cover organization roles and permissions, feature flags,
Vault, groups, and domain-verification failures. In particular:

- handle `vault.byok_key.verification_completed`;
- read `resourceTypeSlug` on deserialized organization-role events;
- handle API-key deletion as `api_key.revoked`, replacing
  `api_key.deleted`;
- preserve SSO context on authentication events; and
- preserve `verification_prefix` on organization domains.

Webhook signature verification accepts raw request bytes. Supply the original
bytes rather than a decoded, normalized, or reserialized body. Webhook endpoint
CRUD is also available through the SDK.

## Users, sessions, identities, and errors

- Organization memberships expose `directoryManaged`.
- `Profile`, `User`, and `Actions` expose `name`.
- User Management values carry `signalsId`.
- `CookieSession` is exported from the package root.
- Server and authentication errors retain typed data.
- `isAuthenticationErrorData` recognizes every supported authentication-error
  shape.
- Exported `ConflictException` values include `code`.
- Identity deserialization returns `GitHubOAuth`, not `GithubOAuth`.

The SDK's `getAuthorizationUrl` accepts `claimNonce`, `invitationToken`, and
`max_age` for nonce-bound claims, invitation flows, and requested
authentication age.

## Pagination and request handling

- `listEvents` accepts `order`.
- Vault object listing forwards `order` and `before`.
- Authorization list endpoints use standardized pagination.
- Connect auto-pagination serializes its pagination options.
- Vault provides object-list filters, rekey support, and version checks when
  deleting objects.

## Additional SDK contracts (10.10.0)

- Action contexts expose the authentication method so handlers can inspect how
  the current authentication occurred.
- The Agents module adds `linkClaimAttemptToExternalUser`, methods for reading
  agent registrations and validating credentials, and the agent registration
  ID in API-key validation results.
- User API-key methods are available. `ApiKey.owner` includes the user variant
  and `organizationId`.
- `CookieSession.refresh()` distinguishes retryable transient failures from
  terminal refresh failures.
- `AuthenticationFactor.totp` is optional on values returned by list
  operations, matching the response contract.
- The HTTP client supports configurable automatic request retries.
- Pipes adds API-key installation plus Data Integration operations and models.
- DELETE requests retain parameters supplied through `{ query: ... }`.

## Product modules exposed by the SDK

- Groups endpoints and group events are available.
- Radar is available, including Radar fields on headless AuthKit methods,
  challenge completion, and typed challenge-error handling.
- Connect is available and supports pagination options during automatic
  pagination.
- Audit Log schemas can be listed with `auditlogs.listSchemas`.
