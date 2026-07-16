# Go Backend SDK

## Install v2

The v2 SDK requires Go 1.24 or newer. Its module path includes the major version.

```bash
go get -u github.com/clerk/clerk-sdk-go/v2
```

Import packages beneath `github.com/clerk/clerk-sdk-go/v2`; do not use the unversioned v1 path for v2 code.

## Global and per-key clients

For a single secret key, set it globally and use package-level resource functions:

```go
clerk.SetKey("sk_live_XXX")
usr, err := user.Get(ctx, userID)
```

For multiple keys, construct resource clients with the shared `clerk.ClientConfig` type:

```go
config := &clerk.ClientConfig{}
config.Key = "sk_live_YYY"
users := user.NewClient(config)
usr, err := users.Get(ctx, userID)
```

## Raw responses and errors

Successful resources carry a `Response` containing raw headers, status, body, and trace information. Failed operations may return `*clerk.APIErrorResponse`, which exposes the API error list, `TraceID`, and the same raw response data.

## Authorization middleware

`WithHeaderAuthorization` parses a bearer token and places valid `SessionClaims` in request context, but does not require authentication. `RequireHeaderAuthorization` performs the same parsing and returns HTTP 403 when valid claims are absent.

```go
protected := clerkhttp.RequireHeaderAuthorization()(handler)
claims, ok := clerk.SessionClaimsFromContext(r.Context())
```

Do not assume the optional middleware rejects signed-out requests; branch on the returned `ok` value.

## Update metadata deprecations

In v2.7.0, user and Organization update-parameter metadata fields are deprecated. Existing callers still compile, but treat these inputs as migration-only rather than stable update surfaces.

## User list filters

Since v2.6.0, user `List` parameters accept `LastSignInAtBefore` and `LastSignInAtAfter` for server-side last-sign-in timestamp filtering.

## Billing and membership-limit provenance

Billing endpoints arrived in v2.4.2. Version 2.5.0 moved to Backend API `2025-04-10` and changed corresponding Billing resource schemas. Since v2.6.0, Organization responses include `membership_limit_set_by`, identifying what established the membership limit.

## API-key resources

Version 2.5.1 includes API Keys endpoints in the v2 module, including `Get` and `Delete` on the `apikey` client. Typed API-key management no longer requires a raw Backend API request.

## Organization roles, permissions, and role sets

Version 2.5.1 adds v2 clients for custom Organization Roles and Permissions. The `roleset` resource supports CRUD and Role management. Organizations expose `RoleSetKey`, and Role Set types distinguish built-in `initial` sets from user-created `custom` sets.

## User and enterprise-account fields

The v2 user resource includes:

- Passkeys.
- `CreatedAt` and `UpdatedAt`.
- `MFAEnabledAt` and `MFADisabledAt`.
- `LegalAcceptedAt`.
- `EnterpriseAccounts`, covering SAML and OAuth connections.

Related additions include:

- `EmailAddress.MatchesSSOConnection`.
- Shared `Verification` and `LinkedIdentification` types.
- `Verification.Message`.
- `OrganizationMembershipPublicUserData.Username`.
- Exported enterprise-connection and SAML-connection types.
- `ExternalAccount.PhoneNumber`.

Preserve these fields when mapping SDK resources into application types.

## Machines and M2M resources

The v2 SDK includes machine and M2M endpoints, including:

- Machine scopes during creation.
- Secret-key and default-TTL data.
- Secret retrieval and rotation.
- Nullable M2M claims.
- Ordering for M2M queries.

M2M values were renamed from `secret` to `token`. The scoped-machine input was removed from machine updates. Code written against beta-era fields needs an explicit migration.

## OAuth application flags

OAuth application resources expose `consent_screen_enabled` and `dynamically_registered`. `consent_screen_enabled` can be set during creation and changed afterward.

## Session-token and password operations

Version 2.4.0 adds typed session-token creation and user-password verification operations. Direct Backend API calls are not required for either operation.

## JWT verification and claims

When no JSON web key is supplied, `jwt.Verify` can fetch one from `GET /v1/jwks`. Callers may provide a `jwks.Client`; cache fetched keys when requests reuse them.

The public claims API separates `RegisteredClaims`, Clerk `Claims`, and `SessionClaims`. `jwt.Decode` exposes the token key ID. Version 2 Organization claims are populated only when an Organization exists, so an absent Organization no longer yields a false Organization Role.

## Session reverification

The SDK provides factor-age helpers and HTTP middleware for testing session freshness and triggering reverification. Use these instead of manually interpreting timestamps when protecting sensitive operations.

## Authentication, invitation, and SAML fields

The v2 resources include:

- `LastAuthenticationStrategy` on clients.
- `URL` on Organization invitations.
- `force_authn` handling on SAML connections.

## Instance and domain settings

Instance Organization settings accept `force_organization_selection`. Instance settings expose `ignore_dots_for_gmail_addresses`.

Domain updates accept `is_secondary`. When `true` and supported by the application, Clerk retains the complete supplied hostname, including subdomains, instead of reducing it to eTLD+1.

## Invitation and template variants

The invitation API supports multiple invitation templates. Custom templates can set a reply-to email name and expose `flagged_as_suspicious`. Preserve both fields when storing or transforming templates and invitations.
