# Node SDK Migrations and Contracts

## Runtime and breaking migrations

### Node SDK v9

- Node.js 22.11 or newer is required; Node.js 20 support was removed.
- The legacy FGA package, deprecated in v8.4, was removed. Use authorization
  resources and organization-role APIs instead.
- The Admin Portal client namespace changed from `portal` to `adminPortal`.
- v9.1.1 restored the established Authorization method names after generated
  renames and corrected the endpoint used by
  `listEffectivePermissionsByExternalId`.

### Node SDK v10

- `Group.createdAt` and `Group.updatedAt` deserialize as `Date` objects.
- Construct `Webhooks` with the WorkOS client: `new Webhooks(workos)`; do not
  pass a `CryptoProvider`.
- `listResources` no longer accepts `search`.
- `vault.listObjects` is an auto-paginatable collection of object summaries,
  not the earlier list-digest response. Generated key and object fields use
  camel-cased SDK names.

## Roles, resources, and groups

The SDK exposes environment and organization roles, authorization resources,
resource-scoped custom roles, Groups endpoints, and group event types.
Permissions and roles expose `resourceTypeSlug`. Pass `resource_type_slug` to
`createOrganizationRole`; `CreateAuthorizationResourceOptions` types resource
creation, and invitations accept `role_slug`.

Resource and group assignment endpoints are available. Filter assignment lists
by `resource` or `role_slug`, and inspect returned `source` to tell direct grants
from group-derived grants.

## Events

Use `api_key.revoked` for API-key deletion; `api_key.deleted` is obsolete.
Typed events cover organization roles and permissions, feature flags, Vault,
groups, and domain-verification failures. Handle
`vault.byok_key.verification_completed`, dedicated organization-role event
types, and `resourceTypeSlug` on deserialized role events.

## User, membership, and authentication types

- Organization memberships expose `directoryManaged`.
- `Profile`, `User`, and `Actions` expose `name`.
- User Management calls carry `signalsId`.
- `CookieSession` is exported from the package root.
- Authentication event deserialization preserves SSO context.
- Organization-domain deserialization preserves `verification_prefix`.
- Server and authentication errors retain typed data.
- `isAuthenticationErrorData` recognizes every supported error shape.
- Exported `ConflictException` instances expose `code`.
- Identity providers normalize to `GitHubOAuth`, not `GithubOAuth`.

## Authorization URLs

`getAuthorizationUrl` accepts `claimNonce` for nonce-bound claims,
`invitationToken` for invitation flows, and `max_age` for requested
authentication age.

## Pagination and list behavior

- `listEvents` accepts `order`.
- Vault object listing forwards `order` and `before`.
- Authorization list endpoints use standardized pagination.
- Connect auto-pagination serializes its pagination options.

## Webhooks

Webhook endpoint create, read, update, and delete operations are available.
Verify signatures from raw request bytes so decoding or reserialization cannot
alter the signed payload.

## Vault

Alongside the v10 list shape and camel-cased fields, Vault supports rekeying,
object-list filters, and version checks when deleting objects.

## Radar and headless AuthKit

The SDK exposes Radar, including Radar fields on headless AuthKit calls. AuthKit
can complete Radar challenges and returns typed challenge-error handling.

## Connect and Audit Logs

The Connect module supports pagination options during automatic pagination.
List Audit Log schemas with `auditlogs.listSchemas`.

## Action, Agents, API keys, sessions, and HTTP behavior

The following contracts are identified by batch `10.10.0`:

- Action contexts expose the authentication method to action handlers.
- Agents adds `linkClaimAttemptToExternalUser`, operations to read agent
  registrations and validate credentials, and the agent registration ID in
  API-key validation results.
- User API-key methods are available. `ApiKey.owner` includes the user variant
  and `organizationId`.
- `CookieSession.refresh()` distinguishes transient, retryable failures from
  terminal failures.
- `totp` is optional on `AuthenticationFactor` objects returned by list calls.
- The HTTP client supports configurable automatic request retries.
- Pipes adds API-key installation plus Data Integration operations and models.
- DELETE requests retain query parameters provided through `{ query: ... }`.
