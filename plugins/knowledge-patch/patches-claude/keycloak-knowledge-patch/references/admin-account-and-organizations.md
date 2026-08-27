# Admin, Account, and Organization APIs

## Client Admin API v2

Enable experimental `client-admin-api:v2` for strictly validated, declarative
OIDC and SAML client management through REST, Java, generated JavaScript, CLI,
or the `KeycloakOIDCClient` and `KeycloakSAMLClient` Operator custom resources.
Its OpenAPI specification is available on the management interface. (26.7.0)

`GET /admin/api/{realmName}/clients/v2` accepts a `q` expression using the SCIM
subset `eq`, `ne`, `co`, `sw`, `ew`, and `pr`, combined with `and`, `or`, `not`,
and parentheses. Strings are case-sensitive and double-quoted; booleans are
unquoted. Malformed filters, unknown fields, and `gt`, `ge`, `lt`, or `le`
return HTTP 400.

```bash
curl -G -H "Authorization: Bearer $TOKEN" \
  --data-urlencode 'q=protocol eq "openid-connect" and enabled eq true' \
  --data-urlencode 'fields=clientId,displayName' \
  https://keycloak.example/admin/api/myrealm/clients/v2
```

For collection fields such as `roles` and `redirectUris`, `eq`, `co`, `sw`, and
`ew` match when any element matches; `ne` means no element equals the value.
Repeat a condition with `and` to require multiple values. Protocol-specific
fields are actually null for the other client type and can be selected with
`eq null` or `not ... pr`. Apply `fields` projection after filtering the full
representation.

## Account REST feature boundaries

When `ACCOUNT_API` is disabled, sessions, credentials, UMA resources,
organizations, verifiable-credential resources, applications, and
application-consent operations return 404. The profile root,
`supportedLocales`, `linked-accounts`, and groups are not guarded by that check.

Profile GET requires `manage-account` or `view-profile` and includes user-profile
metadata unless `userProfileMetadata=false`. Profile POST requires
`manage-account`, validates in the `ACCOUNT` user-profile context, and returns
204 on success.

## Account application discovery

`GET /applications?name=` requires `manage-account` or `view-applications`. It
returns the union of clients used by online sessions, offline sessions,
existing consents, and clients configured to always appear in the account
console. Bearer-only clients are excluded. `name` is a case-insensitive
substring match on the configured client name, not the client ID.

## Account consent CRUD

At `/applications/{clientId}/consent`, GET accepts `briefRepresentation`
(default `true`) and returns 204 when no consent exists; DELETE also returns
204. POST and PUT are both upserts rather than separate create and replace
operations.

Granted-scope IDs must resolve to realm client scopes, or to the client itself
when its consent is required. Parameterized client scopes are rejected with
HTTP 400. Reading consent requires `manage-account`, `view-consent`, or
`manage-consent`; changing or deleting it requires `manage-account` or
`manage-consent`.

## SCIM provisioning

Enable preview `scim-api`; it is disabled by the default profile. The API
manages realm users and groups with CRUD, PATCH, filtering, pagination,
Enterprise User extensions, and schema discovery. (26.7.0)

SCIM uses the standard `name.formatted` field, not the misspelled
`name.formated` spelling fixed in 26.7.2.

```json
{"name":{"formatted":"Ada Lovelace"}}
```

## Delegated organization administration

Use `manage-organizations`, `view-organizations`, and `query-organizations` for
coarse-grained write, read, and search access. `manage-realm` retains full
access. Viewing members also requires `view-users` or an equivalent
fine-grained permission. Organizations can themselves be fine-grained
admin-permission resources, permitting view or manage access to selected
organizations and filtering member queries by user-level visibility. (26.7.0)

Fine-Grained Admin Permissions protect the Role Groups endpoint and prevent
group-hierarchy searches from exposing hidden parent groups. The parameterized
`UserPropertyMapper` also checks permission before exposing a target user's
attributes. (26.7.2)

## Organization group roles in tokens

Realm and client roles assigned to an organization group propagate to every
member's `realm_access` and `resource_access` claims. Enable *Add group role
mappings* on the OIDC or SAML *Organization Group Membership* mapper to group
those roles per organization in the `organization` claim. (26.7.0)

## Organization response compatibility

Organization-member listings return brief users by default from 26.7; request
`briefRepresentation=false` for full records. Invitation `email`, `firstName`,
and `lastName` filters are case-insensitive exact matches, while `search`
remains a substring match. Organization-group representations return empty or
populated `realmRoles` and `clientRoles` instead of null, and general user-by-ID
queries no longer return service accounts.

Adding an organization member works with `stateless:v1` enabled after the fix
in 26.7.2.

## Realm and role administration

Realm search matches both the technical realm name and human-readable display
name. Account for either field when interpreting search results. (26.7.0)

Non-master realms can update a custom realm-level role named exactly `admin`;
26.7.2 fixes the regression that blocked such updates.
