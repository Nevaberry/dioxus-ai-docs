# OAuth 2.1 Provider Plugin (`@better-auth/oauth-provider`)

New standalone package replacing both `oidcProvider` and `mcp` plugins. Full OAuth 2.1 provider with OIDC compatibility.

## Setup

```ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { oauthProvider } from "@better-auth/oauth-provider";

const auth = betterAuth({
  disabledPaths: ["/token"], // avoid conflict with JWT plugin's /token
  plugins: [
    jwt(),
    oauthProvider({
      loginPage: "/sign-in",
      consentPage: "/consent",
      scopes: ["openid", "profile", "email", "offline_access", "read:post"],
      validAudiences: ["https://api.example.com"],
      allowDynamicClientRegistration: true,
      allowUnauthenticatedClientRegistration: true, // public clients (MCP agents)
    }),
  ],
});
```

## Client Plugins

Two types:

```ts
// OAuth Client (web/mobile app connecting as OAuth client)
import { oauthProviderClient } from "@better-auth/oauth-provider/client";
const authClient = createAuthClient({ plugins: [oauthProviderClient()] });

// Resource Server Client (API server verifying tokens)
import { oauthProviderResourceClient } from "@better-auth/oauth-provider/resource-client";
const serverClient = createAuthClient({ plugins: [oauthProviderResourceClient(auth)] });
```

## Well-Known Endpoints

Must expose manually:

```ts
// /.well-known/oauth-authorization-server/[issuer-path]/route.ts
export const GET = oauthProviderAuthServerMetadata(auth);
// [issuer-path]/.well-known/openid-configuration/route.ts (if using openid scope)
export const GET = oauthProviderOpenIdConfigMetadata(auth);
```

## Key Features (Not in Old OIDC Provider)

- **PKCE required by default** (OAuth 2.1), per-client opt-out via `require_pkce: false`
- **Pairwise subject identifiers**: `oauthProvider({ pairwiseSecret: "256-bit-secret" })` — each client gets unique unlinkable `sub`
- **Scope-based token expiration**: `scopeExpirations: { "write:payments": "5m" }`
- **Client credentials grant** (M2M tokens)
- **RP-initiated logout** (`/oauth2/end-session`) for clients with `enable_end_session: true`
- **Token revocation** (`/oauth2/revoke`) — RFC 7009 compliant
- **Token introspection** (`/oauth2/introspect`) — RFC 7662 compliant
- **Admin client CRUD**: `auth.api.adminCreateOAuthClient` / `adminUpdateOAuthClient`
- **Client secret rotation**: `authClient.oauth2.rotateClientSecret({ client_id })`
- **Consent management**: get/list/update/delete user consents
- **Custom claims** on id_token, access_token, and userinfo separately
- **Redirect screens**: configurable login, consent, sign-up, select-account, and post-login pages
- **Organization integration**: `clientReference: ({ session }) => session?.activeOrganizationId`
- **Advertised metadata**: control which scopes/claims appear in discovery vs. actually supported
- **Per-endpoint rate limiting**

## Token Verification on Resource Servers

```ts
import { verifyAccessToken } from "better-auth/oauth2";
const payload = await verifyAccessToken(accessToken, {
  verifyOptions: { issuer: "https://auth.example.com", audience: "https://api.example.com" },
  scopes: ["read:post"],
});
```

## MCP Handler Helper

```ts
import { mcpHandler } from "@better-auth/oauth-provider";
const handler = mcpHandler({
  jwksUrl: "https://auth.example.com/api/auth/jwks",
  verifyOptions: { issuer: "https://auth.example.com", audience: "https://api.example.com" },
}, (req, jwt) => {
  return createMcpHandler(/* ... */)(req);
});
```

## MCP Plugin (Being Deprecated → Use OAuth Provider)

Lets the app act as an OAuth provider for MCP clients:

```ts
import { mcp } from "better-auth/plugins";
export const auth = betterAuth({ plugins: [mcp({ loginPage: "/sign-in" })] });
```

Session handling in same-process MCP server:

```ts
import { withMcpAuth } from "better-auth/plugins/mcp";
const handler = withMcpAuth(auth, (req, session) => {
  // session.userId, session.scopes, session.clientId
  return createMcpHandler(/* ... */)(req);
});
```

**Remote MCP Client** for separate-process MCP servers:

```ts
import { createMcpAuthClient } from "better-auth/plugins/mcp/client";
const mcpAuth = createMcpAuthClient({ authURL: "http://localhost:3000/api/auth" });
const handler = mcpAuth.handler(async (req, session) => { /* ... */ });
const discovery = mcpAuth.discoveryHandler();
const protectedResource = mcpAuth.protectedResourceHandler("http://localhost:4000");
```

Framework adapters: `mcpAuthHono`, `mcpAuthOfficial` (MCP SDK), `mcpAuthMcpUse`:

```ts
import { mcpAuthHono } from "better-auth/plugins/mcp/client/adapters";
const { middleware, discoveryRoutes } = mcpAuthHono({ authURL: "http://localhost:3000/api/auth" });
discoveryRoutes(app, "http://localhost:4000");
app.use("/mcp/*", middleware);
// Access session: c.get("mcpSession")
```

## Migration from OIDC Provider

- PKCE now required by default
- `consentPage` required
- `storeClientSecret` defaults to `hashed`
- `redirectURLs` → `redirectUris`
- `oauthApplication` table → `oauthClient`
- Separate `oauthRefreshToken` table
- `type` field replaced by `public: boolean`
