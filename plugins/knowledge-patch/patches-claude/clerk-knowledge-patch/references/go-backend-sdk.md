# Go Backend SDK

## Install v2 and choose a client style

The v2 SDK requires Go 1.24 or newer and uses the major-version module path:

```sh
go get -u github.com/clerk/clerk-sdk-go/v2
```

For one key, call `clerk.SetKey` and use package-level resource functions. For
multiple keys, instantiate resource clients with the shared
`clerk.ClientConfig` type.

```go
clerk.SetKey("sk_live_XXX")
usr, err := user.Get(ctx, userID)

config := &clerk.ClientConfig{}
config.Key = "sk_live_YYY"
users := user.NewClient(config)
usr, err = users.Get(ctx, userID)
```

## Responses, errors, and middleware

Successful resources carry a `Response` containing raw headers, status, body,
and trace data. Failures may be `*clerk.APIErrorResponse`, which exposes its
error list, `TraceID`, and the same response data.

`WithHeaderAuthorization` parses a bearer token and stores valid
`SessionClaims` in the request context, but does not require authentication.
`RequireHeaderAuthorization` returns HTTP 403 when valid claims are absent.
Read claims with `clerk.SessionClaimsFromContext`.

```go
protected := clerkhttp.RequireHeaderAuthorization()(handler)
claims, ok := clerk.SessionClaimsFromContext(r.Context())
```

## User and organization changes

- v2.7.0 deprecates metadata fields on user and organization update
  parameters. They still compile but are migration surfaces.
- v2.6.0 adds `LastSignInAtBefore` and `LastSignInAtAfter` to user list
  parameters.
- Organization responses gained `membership_limit_set_by` in v2.6.0 so callers
  can identify the source of a membership cap.
- The user model now includes passkeys, `CreatedAt`, `UpdatedAt`, `MFAEnabledAt`,
  `MFADisabledAt`, `LegalAcceptedAt`, and `EnterpriseAccounts` for SAML and OAuth.
- Related models add `EmailAddress.MatchesSSOConnection`, shared `Verification`
  and `LinkedIdentification`, `Verification.Message`, membership public
  `Username`, exported enterprise/SAML connection types, and
  `ExternalAccount.PhoneNumber`.

## Billing and API keys

Billing endpoints arrived in v2.4.2. v2.5.0 moved to Backend API version
`2025-04-10` and changed the Billing models accordingly. v2.5.1 backports API
Keys to v2, including `Get` and `Delete` on the `apikey` client, eliminating the
need for raw Backend API calls.

## Organization roles, permissions, and role sets

v2.5.1 adds clients for custom organization Roles and Permissions. The
`roleset` resource supports CRUD and Role management. Organizations expose
`RoleSetKey`, and Role Set types distinguish `initial` sets from user-created
`custom` sets.

## Machines and M2M

The typed SDK includes machine and M2M endpoints, scopes at machine creation,
secret-key/default-TTL data, secret retrieval and rotation, nullable M2M claims,
and M2M ordering. M2M values were renamed from `secret` to `token`; the scoped-
machine input was removed from machine updates. Migrate beta-era field names.

## OAuth application flags

OAuth application models expose `consent_screen_enabled` and
`dynamically_registered`. `consent_screen_enabled` is accepted on creation and
update, so consent behavior no longer needs a raw request.

## Session and password operations

v2.4.0 adds typed session-token creation and user-password verification
operations.

## JWT verification and claims

Without a supplied JSON web key, `jwt.Verify` fetches one from `GET /v1/jwks`.
Callers may provide a `jwks.Client`; cache fetched keys for reuse. The public
claim model separates `RegisteredClaims`, Clerk `Claims`, and `SessionClaims`.
`jwt.Decode` exposes the token key ID. Version 2 organization claims are
populated only when an Organization exists, avoiding a false Role.

## Reverification

Go helpers and HTTP middleware can check factor ages and trigger session
reverification.

## Expanded resource fields

- Client models expose `LastAuthenticationStrategy`.
- Organization invitations expose `URL`.
- SAML connections support `force_authn`.
- Instance organization-settings updates accept `force_organization_selection`.
- Instance settings expose `ignore_dots_for_gmail_addresses`.
- Domain updates accept `is_secondary`; when supported and true, Clerk keeps
  the complete hostname, including subdomains, rather than reducing to eTLD+1.
- The invitation API supports multiple templates. Custom templates have a
  reply-to email name and `flagged_as_suspicious`; preserve these fields.
