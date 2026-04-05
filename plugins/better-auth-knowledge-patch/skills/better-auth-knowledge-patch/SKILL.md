---
name: better-auth-knowledge-patch
description: "Better Auth changes since training cutoff (latest: 1.5) — OAuth 2.1 provider, Agent Auth protocol, cookie cache strategies, organization hooks, MCP integration, Stripe billing, i18n, SSO/SAML SLO, Electron/Expo/Convex support. Load before working with Better Auth."
version: "1.5"
license: MIT
metadata:
  author: Nevaberry
---

# Better Auth 1.2+ Knowledge Patch

Claude's baseline knowledge covers Better Auth through ~1.1.x. This skill provides features from 1.2 onwards through 1.5.

## Quick Reference

### CLI

```bash
npx auth@latest generate                  # Generate ORM schema or SQL migration
npx auth@latest migrate                   # Apply migrations (Kysely adapter only)
npx auth@latest upgrade                   # Upgrade all better-auth packages
npx auth@latest generate --adapter prisma # Schema for specific adapter
```

### Core Imports

| Import | What |
|--------|------|
| `better-auth` | `betterAuth`, `createAuthMiddleware`, `createAuthEndpoint`, `sessionMiddleware`, `createAdapterFactory` |
| `better-auth/plugins` | `customSession`, `twoFactor`, `passkey`, `magicLink`, `emailOTP`, `username`, `anonymous`, `phoneNumber`, `multiSession`, `bearer`, `jwt`, `captcha`, `deviceAuthorization`, `testUtils`, `mcp`, `genericOAuth` |
| `better-auth/client/plugins` | Client counterparts (e.g. `twoFactorClient`, `passkeyClient`) |
| `better-auth/cookies` | `getSessionCookie`, `getCookieCache` |
| `better-auth/next-js` | `nextCookies` |
| `better-auth/svelte-kit` | `svelteKitHandler`, `sveltekitCookies` |
| `better-auth/node` | `fromNodeHeaders` |
| `better-auth/minimal` | `betterAuth` without bundled Kysely (for ORM adapters) |
| `better-auth/plugins/one-time-token` | `oneTimeToken` |
| `better-auth/plugins/access` | `createAccessControl` |
| `better-auth/plugins/organization/access` | `defaultStatements`, `adminAc` for org RBAC |
| `@better-auth/oauth-provider` | OAuth 2.1 provider (replaces `oidcProvider` + `mcp`) |
| `@better-auth/agent-auth` | Agent Auth Protocol server |
| `@auth/agent` | Agent Auth client SDK + AI framework tool adapters |
| `@better-auth/stripe` | Stripe billing integration |
| `@better-auth/api-key` | API key plugin (moved from `better-auth/plugins` in v1.5) |
| `@better-auth/i18n` | Type-safe error message translations |
| `@better-auth/sso` | SSO with SAML SLO support |
| `@better-auth/infra` | Managed dashboard, sentinel, email/SMS (paid) |
| `@better-auth/electron` | Electron integration (server + proxy + client) |

### Session & Cookie Cache

```ts
session: {
  cookieCache: {
    enabled: true,
    maxAge: 5 * 60,
    strategy: "compact", // "compact" | "jwt" | "jwe"
  },
}
// Bypass: authClient.getSession({ query: { disableCookieCache: true } })
```

See `references/sessions-and-hooks.md` for stateless sessions, cookie cache details, databaseHooks, and createAuthMiddleware hooks.

### Dynamic Base URL (Multi-Domain)

```ts
baseURL: {
  allowedHosts: ["myapp.com", "*.vercel.app", "localhost:3000"],
  fallback: "https://myapp.com",
  protocol: "auto",
}
```

### Server API Helpers

```ts
// Get headers from server-side calls
const { headers, response } = await auth.api.signUpEmail({ returnHeaders: true, body: { ... } });
// Get raw Response
const response = await auth.api.signInEmail({ asResponse: true, body: { ... } });
```

### ID Generation

```ts
advanced: { database: { generateId: false | "serial" | "uuid" | ((options) => string | false) } }
```

### Essential Config Options

| Option | Purpose |
|--------|---------|
| `disabledPaths: ["/sign-up/email"]` | Disable specific endpoints |
| `advanced.disableCSRFCheck` | Disable CSRF only |
| `advanced.disableOriginCheck` | Disable URL validation AND CSRF |
| `advanced.trustedProxyHeaders: true` | Derive baseURL from proxy headers |
| `trustedOrigins: ["chrome-extension://ID"]` | Browser extension support |
| `experimental.joins: true` | Reduce DB roundtrips (v1.4+) |
| `experimental.opentelemetry: true` | OpenTelemetry instrumentation |

See `references/configuration.md` for onAPIError, verification.storeIdentifier, rate limiting, error codes, and security options.

### Framework Handlers (Quick Patterns)

```ts
// Next.js — server action cookies (must be LAST plugin):
import { nextCookies } from "better-auth/next-js";
plugins: [nextCookies()]

// Next.js 16 — rename middleware.ts → proxy.ts, function middleware → proxy

// SvelteKit — handler requires `building` param:
import { svelteKitHandler } from "better-auth/svelte-kit";
import { building } from '$app/environment';
return svelteKitHandler({ event, resolve, auth, building });

// Express v5 — wildcard syntax changed:
app.all('/api/auth/{*any}', toNodeHandler(auth));

// Expo API route:
// app/api/auth/[...all]+api.ts
const handler = auth.handler;
export { handler as GET, handler as POST };

// Node.js headers → web Headers:
import { fromNodeHeaders } from "better-auth/node";
auth.api.getSession({ headers: fromNodeHeaders(req.headers) });
```

See `references/framework-integrations.md` for Elysia, NestJS, Encore, Convex, Electron, Lynx, Waku, TanStack Start.

### OAuth 2.1 Provider (Replaces oidcProvider + mcp)

```ts
import { oauthProvider } from "@better-auth/oauth-provider";
// MUST disable JWT /token endpoint to avoid conflict:
betterAuth({
  disabledPaths: ["/token"],
  plugins: [
    jwt(),
    oauthProvider({
      loginPage: "/sign-in",
      consentPage: "/consent", // required (new in OAuth provider)
      scopes: ["openid", "profile", "email", "offline_access"],
      allowDynamicClientRegistration: true, // for MCP clients
    }),
  ],
});
```

Key differences from old OIDC Provider: PKCE required by default, `consentPage` required, pairwise subject identifiers, client credentials grant, token revocation/introspection. See `references/oauth-provider.md`.

### Secondary Storage (Redis)

```ts
import { redisStorage } from "@better-auth/redis-storage";
secondaryStorage: redisStorage({ client: new Redis(), keyPrefix: "better-auth:" })
```

### Rate Limiting

```ts
rateLimit: {
  storage: "database", // or "secondary-storage" or default in-memory
  customRules: {
    "/sign-in/email": { window: 10, max: 3 },
    "/get-session": false, // disable for this path
  },
}
```

### v1.5 Breaking Changes (Critical)

| Before | After |
|--------|-------|
| `import { apiKey } from "better-auth/plugins"` | `import { apiKey } from "@better-auth/api-key"` |
| `createAdapter` | `createAdapterFactory` |
| `advanced.database.useNumberId` | `advanced.database.generateId: "serial"` |
| `InferUser<O>` / `InferSession<O>` | `User<...>` / `Session<...>` from `"better-auth"` |
| `better-auth/adapters/test` | `@better-auth/test-utils/adapter` |

See `references/breaking-changes.md` for full list.

### Dual Module Hazard Fix

If `No request state found` error appears: Next.js → add `serverExternalPackages: ['better-auth']` to config. Cloudflare → enable `nodejs_compat`. Always install in `dependencies`, not `devDependencies`.

### Plugin Creation

```ts
const myPlugin = (opts) => ({
  id: "my-plugin",
  endpoints: { getHello: createAuthEndpoint("/my-plugin/hello", { method: "GET", use: [sessionMiddleware] }, async (ctx) => ctx.json({ ... })) },
  schema: { myTable: { fields: { name: { type: "string" } } } },
  hooks: { before: [{ matcher: (c) => c.path === "/sign-up/email", handler: createAuthMiddleware(async (ctx) => { ... }) }] },
}) satisfies BetterAuthPlugin;
```

See `references/plugin-creation.md` for client plugins, schema extensions, middleware, rate limits, and v1.5 plugin type system.

## Reference Files

- **`references/sessions-and-hooks.md`** — Cookie cache strategies, stateless sessions, customSession, createAuthMiddleware hooks, databaseHooks, background tasks
- **`references/authentication.md`** — Email enumeration protection, generic OAuth, magic link, email OTP, username, anonymous, phone number, multi-session, account linking, change email, delete user
- **`references/core-plugins.md`** — 2FA (passwordless, server-side, OTP storage), passkey (pre-auth, WebAuthn), bearer tokens, JWT (JWKS, key rotation, custom signing), captcha, device authorization, test utils, one-time token
- **`references/oauth-provider.md`** — OAuth 2.1 provider plugin (replaces oidcProvider + mcp), PKCE, pairwise subjects, client credentials, token management, MCP handler, migration from OIDC
- **`references/agent-auth.md`** — Agent Auth Protocol server + client SDK + CLI + AI framework adapters, capability constraints, approval flows, streaming execution
- **`references/organization.md`** — Organization hooks, dynamic access control, teams, additional fields, default AC import path
- **`references/api-keys-and-billing.md`** — API key plugin (multiple configs, org-owned, permissions, storage, rate limits), Stripe billing (subscriptions, org billing, seat pricing, webhooks)
- **`references/framework-integrations.md`** — Next.js (nextCookies, proxy), SvelteKit, Expo, Express v5, TanStack Start, Elysia, NestJS, Encore, Convex, Electron, Lynx, Waku
- **`references/database-adapters.md`** — Drizzle, Prisma, MongoDB, MS SQL, PostgreSQL non-default schema, SQLite, custom adapter factory, adapter testing, recommended indexes
- **`references/infrastructure.md`** — Better Auth Infrastructure (paid): dash plugin, audit logs, sentinel security, email/SMS services
- **`references/breaking-changes.md`** — v1.5 breaking changes: API key moved to `@better-auth/api-key`, deprecated API removals, plugin type system changes, SSO improvements, i18n plugin
- **`references/configuration.md`** — onAPIError, trustedProxyHeaders, disabledPaths, CSRF vs origin check, verification storage, rate limiting, dual module hazard fix, secret rotation
