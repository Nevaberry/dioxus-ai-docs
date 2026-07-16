# Node SDK Migrations and Contracts

Use this reference when upgrading `@workos-inc/node` or depending on recently
added SDK surfaces.

## Contents

- [Runtime and namespace migrations](#runtime-and-namespace-migrations)
- [Authorization compatibility](#authorization-compatibility)
- [Type and constructor migrations](#type-and-constructor-migrations)
- [Events](#events)
- [User, membership, session, and identity values](#user-membership-session-and-identity-values)
- [Errors](#errors)
- [Authorization URL options](#authorization-url-options)
- [Pagination](#pagination)
- [Groups](#groups)
- [Webhooks](#webhooks)
- [Vault](#vault)
- [Radar and headless AuthKit](#radar-and-headless-authkit)
- [Connect and Audit Logs](#connect-and-audit-logs)

## Runtime and namespace migrations

Node SDK v9 requires Node.js 22.11 or newer and no longer supports Node.js 20.
It also renames the client namespace `portal` to `adminPortal`.

## Authorization compatibility

Replace the legacy FGA package, deprecated in v8.4 and removed in v9, with
authorization-resource and role APIs.

As of v9.1.1, `listEffectivePermissionsByExternalId` calls the corrected
endpoint. The same release reverted generated Authorization method renames, so
keep using the earlier public method names.

Node SDK v10 removes the `search` option from `listResources`.

## Type and constructor migrations

In Node SDK v10:

- Read `Group.createdAt` and `Group.updatedAt` as `Date` objects rather than
  strings.
- Construct `Webhooks` with the `WorkOS` client:
  `new Webhooks(workos)`. Do not pass a `CryptoProvider`.
- Consume `vault.listObjects` as an auto-paginatable object-summary collection,
  not the earlier list-digest shape.
- Read generated Vault key and object responses through camel-cased SDK fields.

## Events

Use `api_key.revoked` for API-key deletion; it replaces
`api_key.deleted`.

Typed events cover:

- organization roles and permissions, including dedicated organization-role
  event types and `resourceTypeSlug` on deserialized role events;
- feature flags;
- Vault, including `vault.byok_key.verification_completed`;
- groups; and
- domain-verification failures.

## User, membership, session, and identity values

- Read `directoryManaged` on organization memberships.
- Read `name` on `Profile`, `User`, and `Actions`.
- Pass and read `signalsId` through user-management APIs.
- Import `CookieSession` from the package root.
- Expect identity deserialization to normalize the provider to `GitHubOAuth`,
  not `GithubOAuth`.

Authentication-event deserialization retains SSO context, and organization-domain
deserialization retains `verification_prefix`. Do not add compatibility code
that discards either field.

## Errors

Server and authentication exceptions retain typed error data.
`isAuthenticationErrorData` recognizes every supported authentication-error
shape, and exported `ConflictException` instances expose `code`.

## Authorization URL options

`getAuthorizationUrl` accepts:

- `claimNonce` for nonce-bound claims;
- `invitationToken` for invitation flows; and
- `max_age` for the requested authentication age.

## Pagination

- Pass `order` to `listEvents`.
- Pass `order` and `before` through Vault object listing.
- Use standardized pagination on authorization list endpoints.
- Expect Connect automatic pagination to serialize and forward its pagination
  options.

## Groups

The SDK exposes Groups endpoints and typed group events. Account for the v10
timestamp conversion described above when serializing or comparing groups.

## Webhooks

Verify signatures against raw request bytes. Decoding or reserializing a request
can change the byte sequence and invalidate verification.

Webhook endpoint CRUD is available directly in the SDK. Apply the v10
constructor migration before instantiating the `Webhooks` helper.

## Vault

In addition to the v10 list and casing changes, Vault supports:

- object rekeying;
- object-list filters; and
- version checks when deleting objects.

## Radar and headless AuthKit

The SDK exposes Radar fields on headless AuthKit methods, supports completing
Radar challenges, and returns typed challenge-error handling.

## Connect and Audit Logs

The SDK includes a Connect module with pagination-aware automatic pagination.
List Audit Log schemas with `auditlogs.listSchemas`.
