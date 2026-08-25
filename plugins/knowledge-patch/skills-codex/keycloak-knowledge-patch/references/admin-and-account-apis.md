# Admin and Account APIs

## Client Admin API v2

Since 26.7.0, enable experimental `client-admin-api:v2` for strictly validated, declarative OIDC and SAML client management. It is available through REST, Java, generated JavaScript, and CLI clients. Its OpenAPI specification is exposed on the management interface.

The Operator uses this API for `KeycloakOIDCClient` and `KeycloakSAMLClient` custom resources.

## Client filtering and field projection

`GET /admin/api/{realmName}/clients/v2` accepts `q` with the SCIM operators `eq`, `ne`, `co`, `sw`, `ew`, and `pr`, boolean `and`, `or`, and `not`, and parentheses. Comparisons are case-sensitive. Quote strings with double quotes, but leave booleans unquoted. Malformed filters, unknown fields, and the unsupported ordering operators `gt`, `ge`, `lt`, and `le` produce HTTP 400.

```bash
curl -G -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'q=protocol eq "openid-connect" and enabled eq true' \
  --data-urlencode 'fields=clientId,displayName' \
  https://keycloak.example/admin/api/myrealm/clients/v2
```

For collections such as `roles` and `redirectUris`, `eq`, `co`, `sw`, and `ew` match when any element matches. `ne` means that no element equals the value. Repeat conditions with `and` when multiple values must all be present.

Protocol-specific fields are truly `null` on the other client type. Select these with `eq null` or `not ... pr`. The `fields` parameter projects the result only after the full representation has been filtered.

## Account REST feature boundaries

The `ACCOUNT_API` feature gate protects sessions, credentials, UMA resources, organizations, verifiable-credential resources, applications, and application-consent operations; those return HTTP 404 while the feature is unavailable. In this service the profile root, `supportedLocales`, `linked-accounts`, and groups are not guarded by that check.

Profile GET requires `manage-account` or `view-profile` and includes user-profile metadata unless `userProfileMetadata=false`. Profile POST requires `manage-account`, validates using the `ACCOUNT` user-profile context, and returns HTTP 204 on success.

## Account application discovery

`GET /applications?name=` requires `manage-account` or `view-applications`. It returns the union of clients found in online sessions, offline sessions, existing consents, and clients configured to always display in the account console. Bearer-only clients are excluded.

The `name` filter is a case-insensitive substring match against the configured client name, not the client ID.

## Account consent operations

At `/applications/{clientId}/consent`:

- GET accepts `briefRepresentation`, defaulting to `true`, and returns HTTP 204 when no consent exists.
- DELETE returns HTTP 204.
- POST and PUT are both upserts; they are not separate create and replace operations.
- Granted-scope IDs must resolve to realm client scopes, or to the client itself when its consent is required.
- Parameterized client scopes are rejected with HTTP 400.

Reading consent requires `manage-account`, `view-consent`, or `manage-consent`. Creating, updating, or deleting consent requires `manage-account` or `manage-consent`.

## Fine-grained permission enforcement

The 26.7.2 fixes make Fine-Grained Admin Permissions protect the Role Groups endpoint. Group-hierarchy searches no longer disclose hidden parent groups, and the parameterized `UserPropertyMapper` checks permissions before returning a target user's attributes.

## Custom realm role named `admin`

In 26.7.2, non-master realms can again update a custom realm-level role whose name is exactly `admin`. This fixes the regression introduced in 26.7.0; do not treat that role name as inherently immutable outside the master realm.
