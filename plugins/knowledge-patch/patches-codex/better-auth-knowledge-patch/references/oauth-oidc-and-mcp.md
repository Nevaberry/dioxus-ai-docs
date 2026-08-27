# OAuth, OIDC, Device Authorization, and MCP

## OAuth 2.1 authorization server

Use `@better-auth/oauth-provider` for new OAuth 2.1 and OIDC authorization servers. It supports authorization-code, refresh-token, and client-credentials grants; discovery; dynamic registration; JWT/JWKS; consent and `prompt=none`; scope narrowing; introspection; revocation; per-client PKCE policy; and endpoint-specific rate limits. Non-local redirect URIs require HTTPS.

```ts
import { oauthProvider } from "@better-auth/oauth-provider";
import { jwt } from "better-auth/plugins";

plugins: [
  jwt(),
  oauthProvider({
    loginPage: "/sign-in",
    consentPage: "/consent",
  }),
]
```

## Metadata routes

Mount the well-known handlers at the issuer. OIDC discovery appends an issuer path before `/.well-known/openid-configuration`; RFC 8414 inserts the path after `/.well-known/oauth-authorization-server`. A separate resource server also needs protected-resource metadata at its API resource path.

```ts
export const GET = oauthProviderOpenIdConfigMetadata(auth);
```

At the RFC 8414 route:

```ts
export const GET = oauthProviderAuthServerMetadata(auth);
```

## Redirect continuations and consent

OAuth redirect state travels in signed `oauth_query`. `oauthProviderClient` forwards it automatically; custom sign-in handlers must pass it through unchanged. Resume signup, account selection, and post-login screens with `oauth2Continue({ created: true })`, `{ selected: true }`, or `{ postLogin: true }`; complete consent with `oauth2.consent`.

## Client administration

Normal client CRUD cannot set `skip_consent`, `enable_end_session`, `client_secret_expires_at`, or private `metadata`; use server-only admin create/update APIs. A client cannot switch between public and confidential after creation. Secret rotation immediately invalidates the old secret. Entries in `cachedTrustedClients` are immutable through CRUD endpoints.

`clientReference` fixes ownership at registration. For organization ownership it usually resolves `session.activeOrganizationId`; `clientPrivileges` can replace default matching-user/reference checks with membership or role policy.

```ts
oauthProvider({
  clientReference: ({ session }) =>
    session?.activeOrganizationId as string | undefined,
  clientPrivileges: async ({ action, headers }) =>
    await canManageOAuthClients(action, headers),
})
```

## Token validation and revocation

Resource servers can use `verifyAccessToken` or `oauthProviderResourceClient` to check JWT signature, issuer, audience, expiration, and scopes. Opaque tokens require `/oauth2/introspect`. Revoking an opaque access token deletes that token only; revoking a refresh token also deletes descendant access tokens. Each refresh issues a replacement refresh token.

When scopes are missing, the provider returns HTTP 403 and an RFC 6750 `insufficient_scope` `WWW-Authenticate` challenge containing the complete missing-scope list. MCP clients can use that one response to request the necessary scope set (1.7.1).

## Pairwise subjects

A permanent `pairwiseSecret` allows clients to select `subject_type: "pairwise"`. The subject derives from the first redirect URI host and user ID. Clients on distinct hosts receive unlinkable subjects, and every redirect URI for one pairwise client must share a host. JWT access tokens still use the real user ID in `sub`.

```ts
oauthProvider({
  pairwiseSecret: process.env.PAIRWISE_SECRET!, // at least 32 characters
})
```

## Generic OAuth clients

Generic OAuth accepts additional token-URL parameters and token-encryption controls. Token responses expose `refresh_token_expires_in`; OIDC `offline_access` no longer requires `prompt=consent`.

Provider presets are imported separately and passed under `config`:

```ts
import { genericOAuth } from "better-auth/plugins";
import { keycloak } from "better-auth/plugins/generic-oauth";

plugins: [genericOAuth({
  config: [keycloak({ clientId, clientSecret, issuer })],
})]
```

Social sign-in accepts `additionalData`; it survives the OAuth round trip and is available to hooks, middleware, or endpoints through `getOAuthState`.

```ts
await authClient.signIn.social({
  provider: "google",
  additionalData: {
    referralCode: "ABC123",
    source: "landing-page",
  },
});

const state = await getOAuthState<{
  referralCode: string;
  source: string;
}>();
```

## Device authorization

The device-authorization plugin implements the OAuth 2.0 Device Authorization Grant.

```ts
import { deviceAuthorization } from "better-auth/plugins";

plugins: [deviceAuthorization()]
```

It provides code issuance, token polling, code verification, and authenticated approve/deny operations. Production deployments should define `validateClient` rather than accept arbitrary client IDs. Codes default to 30 minutes and polling no faster than five seconds. Continue on `authorization_pending`, add five seconds for `slow_down`, and stop on denial or expiry.

## MCP resource servers

Use the framework-independent client for a separate MCP resource server. It can verify Better Auth tokens or wrap handlers, and supplies Hono and Express-like middleware adapters.

```ts
import { createMcpAuthClient } from "better-auth/plugins/mcp/client";

const mcpAuth = createMcpAuthClient({
  authURL: "https://app.example/api/auth",
});
const handler = mcpAuth.handler(async (_request, session) =>
  Response.json({ userId: session.userId }),
);
const session = await mcpAuth.verifyToken(token);
```

## Legacy provider and MCP migration

The older OIDC/MCP plugins added refresh-token discovery and token endpoints, JWKS, PKCE for public clients, trusted clients, encrypted/hashed client secrets, and a configurable MCP login page. They are no longer the path for a new authorization server. Move MCP authorization duties and the deprecated OIDC-provider plugin to `@better-auth/oauth-provider`; keep `createMcpAuthClient` at separate resource servers.

```ts
// Legacy shape, retained only while migrating.
plugins: [mcp({ loginPage: "/login" })]
```

The OAuth-provider migration makes `consentPage` required; changes default ID-token and refresh-token lifetimes to 10 hours and 30 days; changes registration scopes to an array; removes global PKCE opt-out; and hashes client secrets by default.

Database migration renames `oauthApplication` to `oauthClient`, moves refresh tokens to a separate table, and requires legacy plain client secrets and stored token values to be hashed. Legacy MCP endpoints move from `/mcp/*` to `/oauth2/*`. Also rename OIDC `redirectURLs` to `redirectUrls` and migrate the column.

OIDC supports RP-initiated logout. Legacy OAuth clients can be allowed to work without PKCE during a controlled migration, but new clients should use the current PKCE policy.
