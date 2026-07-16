# OAuth, OIDC, Device Authorization, and MCP

## OAuth Provider

`@better-auth/oauth-provider` turns an auth instance into an OAuth 2.1 and OIDC provider. It replaces the deprecated OIDC Provider plugin and supports:

- Authorization-code, refresh-token, and client-credentials grants.
- Dynamic client registration and consent, including `prompt=none`.
- JWT/JWKS, introspection, revocation, and scope narrowing.
- Per-client PKCE requirements and endpoint-specific rate limits.

Non-local redirect URIs require HTTPS.

```ts
import { oauthProvider } from "@better-auth/oauth-provider";
import { jwt } from "better-auth/plugins";

plugins: [
  jwt(),
  oauthProvider({ loginPage: "/sign-in", consentPage: "/consent" }),
]
```

Legacy OAuth clients may be permitted to run without PKCE, but new public clients should use it.

## Metadata routes

The plugin does not automatically solve framework placement of well-known handlers. OIDC metadata appends an issuer path before `/.well-known/openid-configuration`; RFC 8414 metadata inserts the path after `/.well-known/oauth-authorization-server`. A separate resource server also needs protected-resource metadata at its API resource path.

```ts
export const GET = oauthProviderOpenIdConfigMetadata(auth);
```

At the RFC 8414 route:

```ts
export const GET = oauthProviderAuthServerMetadata(auth);
```

## Redirect continuations

OAuth redirect parameters are stored in signed `oauth_query`. `oauthProviderClient` forwards it automatically; a custom sign-in endpoint must pass the signed value unchanged.

Resume signup, account selection, and post-login screens through `oauth2Continue({ created: true })`, `{ selected: true }`, or `{ postLogin: true }`. Complete consent through `oauth2.consent`.

## Client administration

Ordinary CRUD cannot set restricted `skip_consent`, `enable_end_session`, `client_secret_expires_at`, or private `metadata`. Use server-only admin create/update APIs.

Public and confidential client types cannot be switched after creation. Secret rotation invalidates the old secret immediately. Clients listed in `cachedTrustedClients` cannot be changed through CRUD endpoints.

### Organization-owned clients

`clientReference` fixes ownership at registration. Organization ownership normally resolves the session's active organization. CRUD defaults to matching the user or reference owner; use `clientPrivileges` when membership or roles decide each action.

```ts
oauthProvider({
  clientReference: ({ session }) =>
    session?.activeOrganizationId as string | undefined,
  clientPrivileges: async ({ action, headers }) =>
    await canManageOAuthClients(action, headers),
})
```

## Token verification and revocation

Resource servers can use `verifyAccessToken` or `oauthProviderResourceClient` to check JWT signature, issuer, audience, expiry, and scopes. Opaque tokens require `/oauth2/introspect`.

Revoking an opaque access token deletes only that token. Revoking a refresh token also deletes its descendant access tokens. Every successful refresh rotates and replaces the refresh token.

## Pairwise subjects

A permanent `pairwiseSecret` lets clients choose `subject_type: "pairwise"`. The subject derives from the first redirect URI's host and user ID. Different hosts receive unlinkable IDs, and all redirect URIs for one pairwise client must share a host. JWT access tokens still expose the real user ID in `sub`.

```ts
oauthProvider({ pairwiseSecret: process.env.PAIRWISE_SECRET! })
```

The secret must be at least 32 characters.

## Migration from the legacy OIDC provider

The replacement makes `consentPage` required, sets default ID-token and refresh-token lifetimes to 10 hours and 30 days, changes default registration scopes to an array, removes global PKCE opt-out, and hashes client secrets by default.

Database migration renames `oauthApplication` to `oauthClient`, splits refresh tokens into a separate table, and requires hashing legacy plain secrets and stored token values. MCP routes move from `/mcp/*` to `/oauth2/*`.

## Generic OAuth

Generic OAuth supports extra token-URL parameters and token-encryption options. OAuth 2 token responses include `refresh_token_expires_in`. OIDC `offline_access` no longer requires `prompt=consent`.

Preconfigured provider factories are imported separately and passed in `config`; Keycloak is one preset.

```ts
import { genericOAuth } from "better-auth/plugins";
import { keycloak } from "better-auth/plugins/generic-oauth";

plugins: [genericOAuth({
  config: [keycloak({ clientId, clientSecret, issuer })],
})]
```

## Custom OAuth state

Social sign-in accepts `additionalData`. It survives redirects and is available to hooks, middleware, and endpoints through `getOAuthState`.

```ts
await authClient.signIn.social({
  provider: "google",
  additionalData: { referralCode: "ABC123", source: "landing-page" },
});

const state = await getOAuthState<{
  referralCode: string;
  source: string;
}>();
```

## OIDC and legacy MCP authorization-server capabilities

The older OIDC Provider and MCP authorization-server plugins support refresh tokens in discovery and token endpoints, JWKS and PKCE for public clients, trusted clients, and encrypted and hashed client secrets. OIDC also supports RP-initiated logout.

## Device Authorization Grant

The device-authorization plugin implements OAuth device authorization for input-constrained clients.

```ts
import { deviceAuthorization } from "better-auth/plugins";

plugins: [deviceAuthorization()]
```

The flow exposes code issuance, token polling, verification, and authenticated approve/deny operations. Production deployments should provide `validateClient` rather than accept arbitrary client IDs.

Codes last 30 minutes and default polling is no faster than every five seconds. Continue on `authorization_pending`, add five seconds to the interval on `slow_down`, and stop on denial or expiry.

## Remote MCP resource servers

The framework-independent MCP client verifies Better Auth tokens and wraps handlers on a separate resource server. Hono and Express-like middleware adapters are available.

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

The older MCP plugin can send unauthenticated users to an application login page:

```ts
plugins: [mcp({ loginPage: "/login" })]
```

The built-in MCP plugin is deprecated and scheduled for removal in 1.7. Move its authorization-server role to `@better-auth/oauth-provider`; keep `createMcpAuthClient` only for resource-server token validation and handler integration.
