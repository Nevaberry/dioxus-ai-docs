# Go Backend SDK

## Install v2 with the current Go floor

The v2 SDK requires Go 1.24 or newer. Its major version is part of the module
path:

```text
go get -u github.com/clerk/clerk-sdk-go/v2
```

Import packages from `github.com/clerk/clerk-sdk-go/v2/...`.

## Choose global or per-key resource clients

For one secret key, call `clerk.SetKey` and use package-level resource
functions. For multiple keys, construct each resource client with the shared
`clerk.ClientConfig` type.

```go
clerk.SetKey("sk_live_XXX")
usr, err := user.Get(ctx, userID)

config := &clerk.ClientConfig{}
config.Key = "sk_live_YYY"
users := user.NewClient(config)
usr, err = users.Get(ctx, userID)
```

## Inspect responses and API errors

Successful resources contain a `Response` with raw headers, status, body, and
trace information. A failed operation can return `*clerk.APIErrorResponse`,
which exposes its error list, `TraceID`, and the same raw response data.

## Select optional or required bearer middleware

`WithHeaderAuthorization` parses a bearer token and stores valid
`SessionClaims` in the request context, but does not require authentication.
`RequireHeaderAuthorization` does the same and responds with HTTP 403 when
valid claims are missing. Read claims with `clerk.SessionClaimsFromContext`.

```go
protected := clerkhttp.RequireHeaderAuthorization()(handler)
claims, ok := clerk.SessionClaimsFromContext(r.Context())
```

## Migrate metadata updates

Go SDK v2.7.0 deprecates metadata fields on user and Organization update
parameters. Existing code still compiles, but do not treat those fields as
stable update inputs.

## Filter users by last sign-in

Go SDK v2.6.0 adds `LastSignInAtBefore` and `LastSignInAtAfter` to user list
parameters for server-side last-sign-in filtering.

## Track Billing API schema and Organization limit provenance

Billing endpoints arrived in v2.4.2. v2.5.0 moved the SDK to Backend API
version `2025-04-10` and changed Billing models accordingly. Organization
responses in v2.6.0 add `membership_limit_set_by`, identifying what established
the membership cap.

## Manage API keys through v2

Go SDK v2.5.1 backports API Keys endpoints to v2, including `Get` and `Delete`
on the `apikey` client. Typed API-key management no longer needs raw Backend API
requests.

## Manage Organization roles, permissions, and Role Sets

Go SDK v2.5.1 adds clients for custom Organization Roles and Permissions. The
`roleset` resource supports CRUD and Role management, Organizations expose
`RoleSetKey`, and Role Set types distinguish `initial` sets from user-created
`custom` sets.

## Preserve expanded user and enterprise fields

The v2 user type now includes passkeys, `CreatedAt`, `UpdatedAt`,
`MFAEnabledAt`, `MFADisabledAt`, `LegalAcceptedAt`, and `EnterpriseAccounts`.
Enterprise accounts represent SAML and OAuth connections.

Related additions are:

- `EmailAddress.MatchesSSOConnection`
- shared `Verification` and `LinkedIdentification` types
- `Verification.Message`
- `OrganizationMembershipPublicUserData.Username`
- exported enterprise/SAML connection types
- `ExternalAccount.PhoneNumber`

Do not drop these fields when mapping SDK resources into application types.

## Migrate machine and M2M resources

The v2 SDK adds machine and M2M endpoints, machine scopes at creation,
secret-key/default-TTL data, secret retrieval and rotation, nullable M2M claims,
and M2M query ordering. M2M values were renamed from `secret` to `token`, and
scoped-machine input was removed from machine updates. Migrate beta-era callers
at the field level.

## Configure OAuth application flags

OAuth application resources expose `consent_screen_enabled` and
`dynamically_registered`. `consent_screen_enabled` is accepted on create and
update, so callers need not use raw requests to manage consent behavior.

## Create session tokens and verify passwords

Go SDK v2.4.0 adds typed session-token creation and user-password verification
operations.

## Verify JWTs and decode claims correctly

Without a supplied JSON web key, `jwt.Verify` can fetch one from
`GET /v1/jwks`. A caller may provide a `jwks.Client`; cache fetched keys when
reusing them.

The public types separate `RegisteredClaims`, Clerk `Claims`, and
`SessionClaims`. `jwt.Decode` exposes the token key ID. v2 Organization claims
are populated only when an Organization exists, preventing a false
Organization Role.

## Require session reverification

The SDK supplies Go helpers and HTTP middleware for checking factor ages and
triggering session reverification. Use these instead of recreating factor-age
parsing in application middleware.

## Preserve authentication, invitation, and SAML fields

The v2 types add `LastAuthenticationStrategy` to clients, `URL` to Organization
invitations, and `force_authn` on SAML connections.

## Configure instance and domain settings

Instance Organization-setting updates accept `force_organization_selection`.
Instance settings expose `ignore_dots_for_gmail_addresses`.

Domain updates accept `is_secondary`. When true and supported by the
application, Clerk retains the entire supplied hostname, including subdomains,
instead of reducing it to eTLD+1.

## Support invitation and template variants

The invitation API supports multiple invitation templates. Custom templates
can set a reply-to email name and expose `flagged_as_suspicious`; retain these
fields when mapping templates and invitations.
