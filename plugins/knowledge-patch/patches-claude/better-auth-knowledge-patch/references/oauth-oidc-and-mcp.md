# OAuth, OIDC, Device Authorization, and MCP

## OAuth Provider

`@better-auth/oauth-provider` turns an auth instance into an OAuth 2.1/OIDC server and replaces the deprecated OIDC Provider plugin (since 1.5-guide). It supports authorization-code, refresh-token, and client-credentials grants; discovery; dynamic registration; JWT/JWKS; consent; `prompt=none`; scope narrowing; introspection; revocation; per-client PKCE; and endpoint-specific rate limits. Non-local redirect URIs require HTTPS.

```ts
plugins: [
  jwt(),
  oauthProvider({ loginPage: "/sign-in", consentPage: "/consent" }),
]
```

The earlier stable OIDC/MCP plugins gained discovery refresh tokens, JWKs, PKCE for public clients, trusted clients, encrypted/hashed secrets, login-page redirects, and RP-initiated logout beginning in 1.3.0. Use the new provider for authorization-server work.

## Metadata route placement

Mount both well-known metadata handlers at the issuer. OIDC metadata appends an issuer path before `/.well-known/openid-configuration`; RFC 8414 inserts the path after `/.well-known/oauth-authorization-server`. Separate resource servers also publish protected-resource metadata at the API resource path.

```ts
export const GET = oauthProviderOpenIdConfigMetadata(auth);
```

Use `oauthProviderAuthServerMetadata(auth)` at the RFC 8414 route.

## Login, consent, and continuation

Redirect parameters travel in signed `oauth_query`. `oauthProviderClient` forwards it; custom sign-in routes must pass it unchanged. Resume signup, account choice, and post-login screens with `oauth2Continue({ created: true })`, `{ selected: true }`, or `{ postLogin: true }`; finish consent with `oauth2.consent`.

## Client administration

Normal CRUD cannot set `skip_consent`, `enable_end_session`, `client_secret_expires_at`, or private `metadata`; use server-only admin APIs. Client type cannot switch between public/confidential. Secret rotation invalidates the old secret immediately. `cachedTrustedClients` entries cannot be changed through CRUD.

`clientReference` fixes ownership at registration. Organization ownership typically reads the active organization; override CRUD decisions through `clientPrivileges`.

```ts
oauthProvider({
  clientReference: ({ session }) =>
    session?.activeOrganizationId as string | undefined,
  clientPrivileges: async ({ action, headers }) =>
    await canManageOAuthClients(action, headers),
})
```

## Resource-server validation

Use `verifyAccessToken` or `oauthProviderResourceClient` to validate JWT signature, issuer, audience, expiry, and scopes. Opaque tokens require introspection. Revoking an opaque access token removes only that token; revoking a refresh token also removes descendants. Every refresh rotates the refresh token.

Missing scopes return HTTP 403 with an RFC 6750 `insufficient_scope` `WWW-Authenticate` challenge listing all missing scopes (since 1.7.1), allowing MCP clients to request the complete set in one escalation.

## Pairwise subjects

A permanent `pairwiseSecret` of at least 32 characters lets clients request `subject_type: "pairwise"`. Subjects derive from the first redirect URI host and user ID; clients on different hosts receive unlinkable IDs, and all redirects for one client must share a host. JWT access-token `sub` still contains the real user ID.

## Generic OAuth

Generic OAuth supports extra token-URL parameters, token encryption controls, `refresh_token_expires_in`, and OIDC `offline_access` without requiring `prompt=consent` (since 1.3.0). Provider presets are imported separately and passed through `config`; Keycloak is one:

```ts
import { keycloak } from "better-auth/plugins/generic-oauth";
genericOAuth({ config: [keycloak({ clientId, clientSecret, issuer })] })
```

Legacy OAuth clients may be allowed without PKCE.

## Device authorization

The built-in device plugin implements OAuth Device Authorization (since 1.4.0). It exposes issuance, polling, verification, and authenticated approve/deny operations. Production must provide `validateClient` rather than accept arbitrary IDs. Codes last 30 minutes and default polling is no faster than five seconds. Continue on `authorization_pending`, add five seconds after `slow_down`, and stop on denial/expiry.

## MCP resource servers

The built-in `mcp` authorization server is deprecated as of 1.6.0 and was scheduled for removal in 1.7. Move authorization to `@better-auth/oauth-provider`.

Independent resources can use `createMcpAuthClient` to verify Better Auth tokens or wrap handlers. It is framework-neutral and includes Hono and Express-like adapters.

```ts
const mcpAuth = createMcpAuthClient({
  authURL: "https://app.example/api/auth",
});
const handler = mcpAuth.handler(async (_request, session) =>
  Response.json({ userId: session.userId }),
);
```

## Legacy provider migration

The replacement requires `consentPage`, uses 10-hour ID tokens and 30-day refresh tokens by default, makes registration scopes an array, removes global PKCE opt-out, and hashes client secrets. Migrate `oauthApplication` to `oauthClient`, split refresh tokens into their own table, hash old secrets/token values, and move MCP endpoints from `/mcp/*` to `/oauth2/*`.
