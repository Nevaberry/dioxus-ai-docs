# Identity, Brokering, and Organizations

## Identity Brokering API v2

Since 26.7.0, the disabled-by-default v2 API authorizes external-token retrieval per confidential client. Enable *Allow retrieve external tokens* and configure an identity-provider allow list. The API uses `POST` and OAuth-style JSON responses, replacing v1's per-user broker roles.

*Store token in session* gives up persistence across sessions in exchange for automatic expiry cleanup and faster access. V1 remains enabled by default but is deprecated.

## OID4VCI configuration and issuance

Experimental OID4VCI configuration is available in the admin UI with HAIP conformance, per-user credential management, and user-initiated issuance from the account console.

Use the dedicated `client-auth-abca` feature for attestation-based client authentication. The pre-authorized code grant moved to `oid4vc-vci-preauth-code`.

`vc.refresh_interval_in_seconds` controls credential refresh independently of credential lifetime. Its default is the smaller of seven days and the credential lifetime.

## SCIM API preview

Enable preview `scim-api` to manage realm users and groups with CRUD, PATCH, filtering, pagination, Enterprise User extensions, and schema discovery. It is disabled in the default feature profile.

As corrected in 26.7.2, the standard formatted-name field is `name.formatted`, not the misspelled `name.formated`.

```json
{"name":{"formatted":"Ada Lovelace"}}
```

## Shared Signals Framework transmitter

Enable experimental `ssf` to let a realm transmit signed Security Event Tokens using CAEP 1.0 or RISC 1.0 over push or poll delivery. Configure streams, subjects, and event types through the admin console or REST API.

Events pass through a durable outbox and cluster-aware retry processing, so delivery survives restarts.

## Delegated organization administration

Since 26.7.0, the realm roles `manage-organizations`, `view-organizations`, and `query-organizations` grant coarse-grained write, read, and search access. Viewing members additionally requires `view-users` or an equivalent fine-grained permission. `manage-realm` continues to grant full access.

Organizations are also resources under Fine-Grained Admin Permissions. Use those permissions to grant view or manage access to individual organizations and to filter member queries according to user-level visibility.

## Organization group role inheritance

Realm and client roles assigned to an organization group propagate to every member's `realm_access` and `resource_access` token claims.

Enable *Add group role mappings* on the OIDC or SAML *Organization Group Membership* mapper to also group these roles per organization inside the `organization` claim.

## Realm display-name search

Realm search matches both the technical realm name and the human-readable display name.

## Redirect URI wildcard safeguards

Valid redirect URIs match exactly and case-sensitively unless a trailing wildcard is configured. Even with such a wildcard, a requested URI containing userinfo or a `/../` parent-directory path is forced back to exact matching.

The full `*` pattern permits any HTTP or HTTPS redirect and must not be used in production.

## Adapter-mediated web origins

The client's *Web Origins* values are embedded in its access token so the application can decide whether to permit CORS requests. This behavior belongs to Keycloak client adapters; it is not portable OIDC client metadata.

## Consent-screen client item

When *Consent required* is off, *Display client on screen* decides whether a client-specific item appears next to configured client-scope consents. Custom client consent text is used only when both consent and that client item are enabled.

## Logout delivery fallback

A backchannel logout URL is used only while front-channel logout is disabled. Without a backchannel URL, Keycloak can fall back to the *Admin URL* through its nonstandard adapter protocol.

Those callbacks are supported only by the legacy Keycloak Java OIDC adapters and the Elytron WildFly OIDC adapter. No logout request is sent when neither URL is configured.

## Logout confirmation behavior

Enabling *Logout confirmation* shows a completion page after browser logout. If the client supplies a validated `post_logout_redirect_uri`, the page offers that URI as a continuation link or button rather than redirecting automatically.

## Identity-provider representation changes

In Keycloak 26, ordinary realm representations no longer embed identity providers; exports still do. API clients should query the dedicated identity-provider instances endpoint and use its filtering and pagination.

Since 26.7, an identity-provider alias is immutable after creation. Admin REST attempts to change it return HTTP 400.

## Organization REST response changes

Since 26.7, organization-member listing returns brief users by default. Pass `briefRepresentation=false` for full records.

Invitation filters `email`, `firstName`, and `lastName` are case-insensitive exact matches, while `search` remains a substring match. Organization-group representations return empty or populated `realmRoles` and `clientRoles` instead of `null`. General user-by-ID queries no longer return service accounts.
