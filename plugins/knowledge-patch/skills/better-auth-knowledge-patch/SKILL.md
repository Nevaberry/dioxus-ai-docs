---
name: better-auth-knowledge-patch
description: Better Auth
license: MIT
version: 1.6.0
metadata:
  author: Nevaberry
---

# Better Auth Knowledge Patch

Use this skill when implementing, upgrading, debugging, or reviewing Better Auth applications. Start with the quick references below, then load the topic file that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [agent-auth.md](references/agent-auth.md) | Agent Auth discovery, JWT profiles, grants, approvals, execution, SDK, CLI, and hardening |
| [core-authentication.md](references/core-authentication.md) | Email/password, verification, account linking, social providers, usernames, and account deletion |
| [data-model-and-adapters.md](references/data-model-and-adapters.md) | IDs, schema generation, joins, hooks, official adapters, D1, Drizzle, Kysely, SQLite, and PostgreSQL |
| [framework-integrations.md](references/framework-integrations.md) | Convex, Electron, Encore, Expo, Express, Lynx, NestJS, Next.js, SvelteKit, TanStack Start, Waku, and Workers |
| [identity-and-utility-plugins.md](references/identity-and-utility-plugins.md) | Two-factor, passkeys, OTP, magic links, phone, API keys, anonymous, bearer, JWT, SIWE, captcha, One Tap, and utility plugins |
| [infrastructure-and-observability.md](references/infrastructure-and-observability.md) | Managed infrastructure, audit logs, Sentinel, email/SMS, OpenTelemetry, background tasks, and request-state diagnostics |
| [migration-guides.md](references/migration-guides.md) | Schema, package, endpoint, callback, hook, type, and plugin migrations |
| [oauth-oidc-and-mcp.md](references/oauth-oidc-and-mcp.md) | OAuth 2.1 provider, OIDC, generic OAuth, device authorization, resource servers, and MCP migration |
| [organizations-sso-and-scim.md](references/organizations-sso-and-scim.md) | Organizations, teams, dynamic roles, SSO, SAML, SCIM, provisioning, and domain trust |
| [payments.md](references/payments.md) | Autumn, Stripe, Polar, Creem, Dodo Payments, and Openfort |
| [plugin-development-and-testing.md](references/plugin-development-and-testing.md) | Middleware, plugin context, error codes, adapter predicates, lifecycle hooks, testing, and OpenAPI |
| [sessions-cookies-and-security.md](references/sessions-cookies-and-security.md) | Stateless auth, session placement, cookie cache, rate limits, CSRF/origin checks, secret rotation, and token storage |
| [upgrades-and-cli.md](references/upgrades-and-cli.md) | Standalone CLI, ESM, package alignment, release tracks, runtime compatibility, and removed exports |

## Breaking changes and migrations

### Use the standalone CLI

Run the standalone executable instead of the old package-scoped CLI:

```sh
npx auth init
npx auth migrate
npx auth generate --adapter prisma
npx auth upgrade
```

The distribution is ESM-only. Convert CommonJS loading before upgrading.

### Update extracted package imports

Several features now have dedicated packages:

```ts
import { sso } from "@better-auth/sso";
import { scim } from "@better-auth/scim";
import { passkey } from "@better-auth/passkey";
import { apiKey } from "@better-auth/api-key";
import { oauthProvider } from "@better-auth/oauth-provider";
```

Redis-backed secondary storage is installed from `@better-auth/redis-storage`.

Database adapters also have `@better-auth/*-adapter` packages. Direct adapter imports paired with `better-auth/minimal` reduce the imported distribution.

### Apply schema migrations before serving traffic

Important schema changes include:

- Replace organization member `teamId` with the `teamMembers` join table.
- Rename API-key `userId` to `referenceId` and add `configId`.
- Rename OIDC `redirectURLs` to `redirectUrls`.
- Migrate legacy OAuth-provider tables, secrets, and token values before switching providers.
- Generate tables for Agent Auth, dynamic organization roles, activity tracking, and persisted billing when those features are enabled.
- Rerun generation or migration after enabling database joins.

### Replace removed and renamed APIs

```ts
await authClient.requestPasswordReset({ email }); // not forgotPassword
await auth.api.accountInfo({ query });             // GET/query, not POST/body
```

Use `createAdapterFactory` instead of `createAdapter`, `afterEmailVerification` instead of `onEmailVerification`, and `permissions` instead of the organization model's `permission` field. See the migration reference for removed endpoint, type, export, and callback details.

### Treat post-transaction hooks correctly

Database `create.after`, `update.after`, and `delete.after` hooks run after commit. Put atomic follow-up writes in the adapter operation or transaction, not in an `after` hook.

## Sessions and security

### Database-free auth is explicit through omission

Omitting `database` enables stateless session management. Account data can be kept in a signed cookie, and token/account endpoints remain available:

```ts
const auth = betterAuth({
  socialProviders: { google: { clientId, clientSecret } },
  account: { storeAccountCookie: true },
});
```

When secondary storage is configured, sessions move there by default. Opt into database persistence with `storeSessionInDatabase`; use `preserveSessionInDatabase` to retain rows after revocation.

### Do not extend freshness by refreshing

Session `freshAge` is measured from `createdAt`, not `updatedAt`. Refreshing cannot keep a session fresh indefinitely. Stateless cookie-cache `maxAge` is bounded by session `expiresIn`.

### Rotate secrets without invalidating all data

Put the newest key first and retain older keys for decryption:

```ts
secrets: [
  { version: 2, value: process.env.AUTH_SECRET_V2! },
  { version: 1, value: process.env.AUTH_SECRET_V1! },
]
```

### Separate CSRF and origin decisions

CSRF and origin validation are independent controls. `disableCSRFCheck` disables only CSRF defense; `disableOriginCheck` also disables callback/redirect validation and retains broader legacy disabling behavior. Never trust forwarded host/protocol headers unless a front proxy strips attacker-supplied values.

### Encrypt provider tokens when required

Provider access and refresh tokens are plain by default. Prefer the built-in option:

```ts
account: { encryptOAuthTokens: true }
```

## OAuth, OIDC, SSO, and SCIM

### Build new authorization servers with OAuth Provider

`@better-auth/oauth-provider` implements OAuth 2.1 and OIDC authorization-code, refresh-token, and client-credentials flows, plus discovery, dynamic registration, consent, introspection, revocation, JWT/JWKS, PKCE policy, and rate limits.

```ts
plugins: [
  jwt(),
  oauthProvider({ loginPage: "/sign-in", consentPage: "/consent" }),
]
```

Mount both well-known metadata handlers at the issuer. A separate API also needs protected-resource metadata and should validate access tokens with `verifyAccessToken`, a resource client, or introspection for opaque tokens.

### Retire the legacy MCP authorization server

Move authorization-server duties from the legacy built-in MCP plugin to `@better-auth/oauth-provider`. Separate MCP resource servers can verify tokens with `createMcpAuthClient`.

### Harden SSO and provisioning

- Allowlist the OIDC discovery URL and every resolved endpoint.
- Keep SAML assertion replay protection and response-correlation validation enabled.
- Export all five SCIM methods: `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.
- Authorize SCIM token issuance and choose hashed, encrypted, or custom token storage.

## Hooks and background work

### Use unified middleware

```ts
hooks: {
  before: createAuthMiddleware(async (ctx) => inspect(ctx.path)),
  after: createAuthMiddleware(async (ctx) => inspect(ctx.context.returned)),
}
```

Plugin hooks remain matcher/handler entries. A plugin `init()` receives the live mutable auth context and may return context keys for other plugins.

### Choose fire-and-forget versus required completion

`runInBackground()` schedules work after the response. `runInBackgroundOrAwait()` uses the configured background handler, but awaits when none exists. Connect serverless lifetime primitives through `advanced.backgroundTasks.handler`; expect eventual consistency when database writes are deferred.

## Framework integration checks

- Mount Express auth routes before `express.json()`; Express 5 needs a named wildcard.
- Put `nextCookies()` last when Server Actions call `auth.api` directly, and validate full sessions for protected Next.js routes.
- Keep Electron auth state and cookies in the main process and align protocol, callback path, client ID, and trusted origin across server, web, and desktop clients.
- Pair Expo server/client plugins with secure storage; send `getCookie()` manually for non-client requests.
- Enable Workers AsyncLocalStorage compatibility before constructing auth.
- Follow the custom Set-Cookie bridge for Waku Server Actions.

## Agent Auth essentials

Agent Auth separates persistent hosts from runtime agents. Each agent has an Ed25519 key, an immutable delegated/autonomous mode, scoped grants, and short-lived single-use Agent JWTs. Discovery starts at `/.well-known/agent-configuration`; unsupported major protocol versions must stop the client.

Use `@better-auth/agent-auth` for registration, approval, grant enforcement, and execution. Run its migration, keep automatic default grants low-risk, use durable secondary storage for replay/JWKS caches in multi-instance deployments, and require fresh sessions or WebAuthn proof of presence for sensitive approvals.

## Adapter and plugin reminders

- `advanced.database.generateId` may delegate selected models to the database by returning `false` or `undefined`.
- Adapter predicates support per-clause `mode: "insensitive"`.
- Custom session fields are recomputed on every fetch and bypass cookie/secondary caches.
- Passkey registration can run without a session only when the supplied context is securely validated.
- API-key validation consumes limits and budgets; avoid verifying twice before `getSession`.
- Defining custom admin/user roles replaces built-in grants unless their statements are merged.
- Payment plugins differ sharply in owner/reference semantics, persistence, cancellation, and entitlement lookup; load the payment reference before implementation.
