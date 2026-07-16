# API and protocols

## Legacy v1 service contexts and routes

The Auth API operates on the user identified by the access token's `sub`; Management targets `x-zitadel-orgid` or falls back to that user's organization; Admin manages one instance; and System manages multiple instances. Their REST and gRPC prefixes are respectively `/auth/v1/` and `/zitadel.auth.v1.AuthService/`, `/management/v1/` and `/zitadel.management.v1.ManagementService/`, `/admin/v1/` and `/zitadel.admin.v1.AdminService/`, and `/system/v1/` and `/zitadel.system.v1.SystemService/`; assets use `/assets/v1/`.

## v1-to-v2 request and resource changes

Organization context moves from the V1 `x-zitadel-orgid` header into each V2 request body as `{"organization_id":"1234567890"}`. V2 unifies human and service-account creation in `CreateUser`, creates users active rather than in an initial state, and lets callers send an email verification code or receive it for custom delivery.

`ListProjects` now returns both owned and granted projects, with filters to distinguish them. Application creation likewise moves from `AddOIDCApp`, `AddSAMLApp`, and `AddAPIApp` to one `CreateApplication` request whose protocol-specific settings are nested in an OIDC, SAML, or API object.

## Stable v2 error slugs

Stable V2 services can return `zitadel.error.v2.ErrorDetail`; branch on its stable `slug`, such as `user.already_exists`, and use `message` only for diagnostics. Do not assume slugs on V1, V2 beta, V3 alpha, or a V2 endpoint whose logic is not backed by the relational-storage feature.

## SCIM v2 preview surface and limits

The preview SCIM API is organization-scoped at `/scim/v2/{orgId}` and uses service-account bearer authentication. Its documented resource operations are User CRUD, `GET /Users` or `POST /Users/.search` queries, and `/Bulk`, plus the standard service-provider, schema, and resource-type discovery endpoints.

User queries support filtering, sorting, and paging but return at most 100 users, and filter strings are limited to 1000 characters. Bulk requests allow 100 operations and a 1,000,000-byte payload; patch and password changes are supported, while ETags are not.

```http
GET /scim/v2/{orgId}/Users?filter=meta.created%20gt%20%222025-01-24T09:22:35Z%22&sortBy=meta.created&sortOrder=descending
```

SCIM errors extend the standard error schema with `urn:ietf:params:scim:api:zitadel:messages:2.0:ErrorDetail`, which carries an untranslated message and error ID.

## OIDC endpoint and grant surface

The protocol endpoints mix `/oauth/v2/` and `/oidc/v1/` paths, so take them from discovery rather than constructing them from one common prefix.

```text
discovery   /.well-known/openid-configuration
authorize   /oauth/v2/authorize
token       /oauth/v2/token
introspect  /oauth/v2/introspect
revoke      /oauth/v2/revoke
userinfo    /oidc/v1/userinfo
logout      /oidc/v1/end_session
JWKS        /oauth/v2/keys
```

There is no separate OAuth 2.0 metadata endpoint. Device authorization, implicit, and the JWT bearer profile are supported, but Resource Owner Password Credentials and the SAML 2.0 OAuth assertion profile are not.

## Application and service-account JWT assertions

An application using `private_key_jwt` signs with its downloaded `type: application` key and sets both `iss` and `sub` to its `clientId`. A service account using the JWT bearer grant instead uses a `type: serviceaccount` key and sets both claims to its `userId`; in both cases `aud` must include `https://${CUSTOM_DOMAIN}`, `iat` must be no more than one hour old, and the RS256 header must carry the downloaded `keyId` as `kid`.

```text
header:  {"alg":"RS256","kid":"<keyId>"}
payload: {"iss":"<clientId-or-userId>","sub":"<same-value>","aud":"https://${CUSTOM_DOMAIN}","iat":<unix-time>,"exp":<unix-time>}
```

## ZITADEL-specific OIDC scopes and routing

Reserved scopes change both login routing and token contents:

- `urn:zitadel:iam:org:id:{id}` enforces organization membership; `urn:zitadel:iam:org:domain:primary:{domain}` also requires a username suffixed by that domain.
- `urn:zitadel:iam:org:project:id:{projectid}:aud` adds a project to the access-token audience; use the literal project ID `zitadel` to call the core APIs.
- `urn:zitadel:iam:org:project:role:{rolekey}` requests current-project roles, while `urn:zitadel:iam:org:projects:roles` emits per-project role claims for requested audience projects.
- Repeatable `urn:zitadel:iam:org:roles:id:{orgID}` scopes restrict role results to selected organizations; unknown IDs are ignored.
- `urn:zitadel:iam:user:metadata` includes Base64-encoded metadata, and `urn:zitadel:iam:user:resourceowner` includes the user's organization ID, name, and primary domain.
- `urn:zitadel:iam:org:idp:id:{idp_id}` redirects directly to an identity provider; with a custom login policy it must be paired with an organization-domain scope.

The authorization endpoint also accepts `prompt=create` to open registration directly.

## Token claims and lifecycle behavior

When an authorization response includes an access token, the ID token omits the `profile`, `email`, `phone`, and `address` scope claims unless the application enables `id_token_userinfo_assertion` (**User Info inside ID Token**); otherwise retrieve them from userinfo or introspection. Add OIDC custom claims with a complement-token Action and SAML custom attributes with a complement-SAML-response Action.

Introspection handles opaque and JWT access tokens, checks revocation, and reports `active: true` only when the requesting client is in the token audience. Revoking an access token affects only that token, while revoking a refresh token also revokes its corresponding access token.

## End-session redirect validation

`post_logout_redirect_uri` is validated against the client selected by the ID token's `azp` or by `client_id`; when both are supplied they must identify the same client. Without either `id_token_hint` or `client_id`, the post-logout redirect is ignored.

## SAML endpoints and error transport

SAML metadata, the standalone signing certificate, and SSO are exposed at `/saml/v2/metadata`, `/saml/v2/certificate`, and `/saml/v2/SSO`. SSO accepts HTTP-Redirect and HTTP-POST bindings; protocol failures still use HTTP 200 and must be detected from the SAML `StatusCode` and message rather than the HTTP status.

## Readiness, liveness, and metrics endpoints

Core process probes are `/debug/ready` for readiness and `/debug/healthz` for liveness. `/debug/metrics` exposes OpenTelemetry-format metrics and is enabled by default, but can be disabled in settings.
