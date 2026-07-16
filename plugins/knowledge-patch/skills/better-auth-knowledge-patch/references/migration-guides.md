# Migration Guides

## Package and executable moves

The distribution is ESM-only (since `1.4.0`). Convert CommonJS imports and loaders before upgrading.

The standalone `npx auth` executable replaces `@better-auth/cli` (documented in `1.5-guide`). Existing migration and generation commands use the new executable; `init` scaffolds auth, adapter, and framework integration, while `generate --adapter` can run without a complete auth config.

```sh
npx auth init
npx auth migrate
npx auth generate --adapter prisma
npx auth upgrade
```

Move direct imports to the extracted packages where applicable:

| Feature | Package |
| --- | --- |
| SSO | `@better-auth/sso` |
| SCIM | `@better-auth/scim` |
| OAuth Provider | `@better-auth/oauth-provider` |
| Passkey | `@better-auth/passkey` |
| API key server/client | `@better-auth/api-key`, `@better-auth/api-key/client` |
| Redis secondary storage | `@better-auth/redis-storage` |
| Drizzle, Prisma, Kysely, MongoDB, memory | Matching `@better-auth/*-adapter` package |

The main package still re-exports database adapters. Direct imports can be paired with `better-auth/minimal`.

## Organization and API-key schemas

Organization members may belong to multiple teams. Remove `teamId` from `member`, add the required `teamMembers` join table, and regenerate types. Clients can infer server organization types:

```ts
organizationClient({
  $inferAuth: {} as typeof auth,
})
```

The API-key migration renames `ApiKey.userId` to `referenceId` and adds `configId` with default `"default"`. Returned keys expose `references` as the owner type. `defaultPermissions` receives `referenceId`.

## OAuth schemas

Rename OIDC `redirectURLs` to `redirectUrls` and run its database migration.

Migrating from the deprecated OIDC Provider to `@better-auth/oauth-provider` requires:

- A required `consentPage`.
- Default ID-token and refresh-token lifetimes of 10 hours and 30 days.
- Registration scopes expressed as an array.
- Per-client PKCE policy; the global PKCE opt-out is removed.
- Hashed client secrets by default.
- Rename `oauthApplication` to `oauthClient`.
- Split refresh tokens into their own table.
- Hash legacy plain client secrets and stored token values.
- Move legacy MCP routes from `/mcp/*` to `/oauth2/*`.

## Identifier configuration

Move ID configuration from removed top-level `advanced.generateId` to `advanced.database.generateId`. Replace `advanced.database.useNumberId` with `generateId: "serial"`; select UUIDs with `generateId: "uuid"`.

```ts
advanced: {
  database: { generateId: "uuid" },
}
```

## Endpoint and method changes

- Rename `authClient.forgotPassword` to `authClient.requestPasswordReset`.
- Call account info as `GET /account-info` with `query`, not `POST` with a body.
- Replace removed `/forget-password/email-otp` with the standard password-reset flow.
- Replace deprecated Dodo `authClient.dodopayments.checkout()` with `checkoutSession({ slug })`.
- Move legacy MCP authorization-server behavior to OAuth Provider; the built-in MCP plugin is retired.

The `/change-email` response is deliberately enumeration-safe: `{ status: true }` acknowledges processing but does not prove that an address exists or changed.

## Email lifecycle callbacks

Use `emailVerification.sendVerificationEmail` for new-address verification. The former change-email `sendChangeEmailVerification` callback is removed.

Use `afterEmailVerification` instead of removed `onEmailVerification`.

Callbacks that formerly received `request` now receive `ctx`; access the request through `ctx.request`. This affects:

- Email OTP `sendVerificationOTP` and `generateOTP`.
- Magic link `sendMagicLink`.
- Phone `sendOTP`, `sendPasswordResetOTP`, and `callbackOnVerification`.
- Organization `teams.defaultTeam.customCreateDefaultTeam` and `teams.maximumTeams`.

## Framework helper changes

SvelteKit cookie helpers take `getRequestEvent` explicitly and may require explicit `building`; implicit request-event lookup is gone.

React Start imports are replaced by:

```ts
import { tanstackStartCookies } from "better-auth/tanstack-start";

plugins: [tanstackStartCookies()]
```

Expo session polling requires `expo-network`. Cloudflare Workers require AsyncLocalStorage through `nodejs_compat` with compatibility date `2024-09-23`, or `nodejs_als`.

## Hook migration

Global and plugin request hooks use `AuthMiddleware`. Global hooks may be direct middleware; plugin hooks remain matcher/handler entries. After middleware reads the returned response from `ctx.context.returned`.

```ts
hooks: {
  before: createAuthMiddleware(async (ctx) => console.log(ctx.path)),
  after: createAuthMiddleware(async (ctx) =>
    console.log(ctx.context.returned)),
}
```

Database `create.after`, `update.after`, and `delete.after` now run after transaction commit. Move atomic follow-up writes into the adapter's main operation.

## Plugin type migration

`PluginContext<Options>` is generic. Plugins may augment `BetterAuthPluginRegistry`, allowing `getPlugin()` and `hasPlugin()` to infer registered types. `init()` receives the same mutable context reference used throughout auth and may return arbitrary context keys for other plugins.

A plugin `$ERROR_CODES` uses `Record<string, RawError>` rather than `Record<string, string>` (since `1.5.0`). Assign the object from `defineErrorCodes()`:

```ts
$ERROR_CODES: defineErrorCodes({
  MY_ERROR: "My error message",
})
```

`AuthContext` exposes the running Better Auth version for compatibility checks and diagnostics.

## Removed adapter APIs and exports

- Replace `createAdapter` with `createAdapterFactory`.
- Import `testAdapter` and `createTestSuite` from `@better-auth/test-utils/adapter`; `better-auth/adapters/test` is removed.
- Import `getMigrations` from `better-auth/db/migration`, not `better-auth`.

## Renamed and removed types

| Removed | Replacement |
| --- | --- |
| `Adapter` | `DBAdapter` |
| `TransactionAdapter` | `DBTransactionAdapter` |
| `Store` | `ClientStore` |
| `AtomListener` | `ClientAtomListener` |
| `ClientOptions` | `BetterAuthClientOptions` |
| `InferUser` | Generic `User` |
| `InferSession` | Generic `Session` |

`LiteralUnion` and `DeepPartial` move from `better-auth/types/helper` to `@better-auth/core`. The organization model field is plural `permissions`, not `permission`.

The `@better-auth/core/utils` barrel is removed. Import subpaths such as `@better-auth/core/utils/id`, `/json`, and `/error-codes`.

## Session storage compatibility

Sessions read from secondary storage no longer contain `id`; do not depend on it. Stateless cookie cache uses JWE by default, and cookie values may be chunked automatically.
