# APIs and protocols

## Select the correct API surface

### Keep legacy V1 service contexts and routes distinct

The Auth API operates on the user identified by the access token's `sub`; Management targets `x-zitadel-orgid` or falls back to that user's organization; Admin manages one instance; and System manages multiple instances.

| Service | REST prefix | gRPC prefix |
|---|---|---|
| Auth | `/auth/v1/` | `/zitadel.auth.v1.AuthService/` |
| Management | `/management/v1/` | `/zitadel.management.v1.ManagementService/` |
| Admin | `/admin/v1/` | `/zitadel.admin.v1.AdminService/` |
| System | `/system/v1/` | `/zitadel.system.v1.SystemService/` |

Assets use `/assets/v1/`.

### Account for V1-to-V2 resource changes

Organization context moves from `x-zitadel-orgid` into each V2 request body:

```json
{"organization_id":"1234567890"}
```

V2 unifies human and service-account creation in `CreateUser`, creates users active rather than in an initial state, and lets callers send an email-verification code or receive it for custom delivery.

`ListProjects` returns both owned and granted projects, with filters to distinguish them. Application creation moves from `AddOIDCApp`, `AddSAMLApp`, and `AddAPIApp` to one `CreateApplication` request whose protocol settings are nested in an OIDC, SAML, or API object.

### Branch only on stable V2 error slugs

Stable V2 services can return `zitadel.error.v2.ErrorDetail`. Branch on its stable `slug`, such as `user.already_exists`, and use `message` only for diagnostics. Do not assume slugs on V1, v2beta, v3alpha, or a V2 endpoint whose logic is not backed by the relational-storage feature.

### Use ConnectRPC for new services

New V2 APIs use gRPC with ConnectRPC and do not add OpenAPI 2.0 endpoints. Earlier APIs retain their existing transports. ConnectRPC and gRPC-Web requests support CORS and participate in tracing when the tracing interceptor is enabled.

## Use the SCIM V2 preview safely

The preview API is organization-scoped at `/scim/v2/{orgId}` and uses service-account bearer authentication. Its documented surface is User CRUD, `GET /Users` or `POST /Users/.search`, `/Bulk`, and standard service-provider, schema, and resource-type discovery endpoints.

Queries support filtering, sorting, and paging, but return at most 100 users and limit filter strings to 1000 characters. Bulk requests allow 100 operations and a 1,000,000-byte payload. Patch and password changes are supported; ETags are not.

```http
GET /scim/v2/{orgId}/Users?filter=meta.created%20gt%20%222025-01-24T09:22:35Z%22&sortBy=meta.created&sortOrder=descending
```

SCIM errors extend the standard schema with `urn:ietf:params:scim:api:zitadel:messages:2.0:ErrorDetail`, which carries an untranslated message and error ID.

## Discover and configure OIDC

### Discover endpoints instead of constructing them

OIDC endpoints mix `/oauth/v2/` and `/oidc/v1/` paths:

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

There is no separate OAuth 2.0 metadata endpoint. Device authorization, implicit, and JWT bearer are supported. Resource Owner Password Credentials and the SAML 2.0 OAuth assertion profile are unsupported.

### Build application and service-account JWT assertions correctly

An application using `private_key_jwt` signs with its downloaded `type: application` key and sets `iss` and `sub` to its `clientId`. A service account using JWT bearer instead uses a `type: serviceaccount` key and sets both claims to its `userId`.

In both cases, `aud` must include `https://${CUSTOM_DOMAIN}`, `iat` must be no more than one hour old, and the RS256 header must carry the downloaded `keyId` as `kid`.

```text
header:  {"alg":"RS256","kid":"<keyId>"}
payload: {"iss":"<clientId-or-userId>","sub":"<same-value>","aud":"https://${CUSTOM_DOMAIN}","iat":<unix-time>,"exp":<unix-time>}
```

### Use reserved scopes deliberately

- `urn:zitadel:iam:org:id:{id}` enforces organization membership. `urn:zitadel:iam:org:domain:primary:{domain}` also requires a username suffixed by that domain.
- `urn:zitadel:iam:org:project:id:{projectid}:aud` adds a project to the access-token audience; use literal project ID `zitadel` to call core APIs.
- `urn:zitadel:iam:org:project:role:{rolekey}` requests current-project roles. `urn:zitadel:iam:org:projects:roles` emits per-project role claims for requested audience projects.
- Repeatable `urn:zitadel:iam:org:roles:id:{orgID}` scopes restrict role results to selected organizations; unknown IDs are ignored.
- `urn:zitadel:iam:user:metadata` includes Base64-encoded metadata. `urn:zitadel:iam:user:resourceowner` includes the user's organization ID, name, and primary domain.
- `urn:zitadel:iam:org:idp:id:{idp_id}` redirects directly to an identity provider; with a custom login policy, pair it with an organization-domain scope.

The authorization endpoint accepts `prompt=create` to open registration directly. It also supports `login_hint`; maintained releases correct the request-ID propagation and prevent auto-submit loops when it is combined with `prompt=login`.

### Understand token claims and lifecycle

When an authorization response includes an access token, the ID token omits `profile`, `email`, `phone`, and `address` scope claims unless the application enables `id_token_userinfo_assertion` (**User Info inside ID Token**). Otherwise, retrieve them from userinfo or introspection. Add OIDC custom claims with a complement-token Action and SAML custom attributes with a complement-SAML-response Action.

Introspection handles opaque and JWT access tokens, checks revocation, and returns `active: true` only when the requesting client is in the token audience. Revoking an access token affects only that token; revoking a refresh token also revokes its corresponding access token.

Authorization codes and refresh tokens are client-bound, and token exchange validates both the client and requested scopes. ID tokens from client credentials have a lifetime. Token V2 compares its subject to the user ID.

### Validate end-session redirects

`post_logout_redirect_uri` is validated against the client selected by the ID token's `azp` or by `client_id`; when both are supplied they must identify the same client. Without `id_token_hint` or `client_id`, the post-logout redirect is ignored. Invalid `id_token_hint` values are ignored by maintained releases rather than rejecting the flow, and `logout_hint` is supported.

### Use dynamic client registration when applicable

Version 4.17.0 implements RFC 7591 dynamic client registration and RFC 7592 dynamic client management, enabling standards-based OIDC client registration and subsequent management.

## Integrate SAML

SAML metadata, the standalone signing certificate, and SSO are exposed at `/saml/v2/metadata`, `/saml/v2/certificate`, and `/saml/v2/SSO`. SSO accepts HTTP-Redirect and HTTP-POST bindings. Protocol failures still use HTTP 200 and must be detected from the SAML `StatusCode` and message, not the HTTP status.

SAML service-provider POST handling avoids cookie-size limits. If an upstream response has no `NameID`, maintained releases use the transient mapping attribute. Identity-provider signatures support configurable `SignatureMethod`, and the service-provider certificate has a Common Name.

## Probe the service

Core readiness is `/debug/ready` and liveness is `/debug/healthz`. `/debug/metrics` exposes OpenTelemetry-format metrics and is enabled by default, but settings can disable it. Login has its own readiness endpoint; the separate Login container has stdout logs but no tracing or metrics surface.
