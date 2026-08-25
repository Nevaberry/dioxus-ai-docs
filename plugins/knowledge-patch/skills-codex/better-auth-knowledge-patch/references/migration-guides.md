# Migration Guides

## Schema migrations

### Organizations and teams

The 1.3.0 multi-team schema removes `teamId` from `member` and adds `teamMembers`. Generate or migrate before serving traffic. Dynamic roles add `organizationRole`; infrastructure activity tracking adds `lastActiveAt` to users; Agent Auth adds host, agent, grant, and approval tables; persisted billing plugins add their own tables.

### API keys

The extracted API-key plugin renames `ApiKey.userId` to `referenceId` and adds `configId` with default `"default"`. Returned keys expose `references` as their owner type, and `defaultPermissions` receives `referenceId`.

### OIDC/OAuth

Rename OIDC `redirectURLs` to `redirectUrls` and migrate the stored column. Moving from the legacy OIDC provider renames `oauthApplication` to `oauthClient`, creates a separate refresh-token table, and requires legacy plain client secrets and stored tokens to be hashed.

### Joins and required columns

Enabling database joins changes the generated schema and requires regeneration or migration. The CLI in 1.7.1 refuses to add a required column without a default to a populated table; stage the column, default, and backfill explicitly.

## Package migrations

Use feature-specific packages:

```ts
import { sso } from "@better-auth/sso";
import { scim } from "@better-auth/scim";
import { passkey } from "@better-auth/passkey";
import { apiKey } from "@better-auth/api-key";
import { oauthProvider } from "@better-auth/oauth-provider";
```

The API-key client is `@better-auth/api-key/client`, and Redis secondary storage is `@better-auth/redis-storage`. Drizzle, Prisma, Kysely, MongoDB, and memory adapters have `@better-auth/*-adapter` packages. Direct adapters can be paired with `better-auth/minimal`.

## CLI and module migration

The 1.5-guide transition replaces `@better-auth/cli` with the standalone Auth CLI:

```sh
npx auth init
npx auth migrate
npx auth generate --adapter prisma
npx auth upgrade
```

Better Auth has been ESM-only since 1.4.0. Replace CommonJS loading before upgrading.

## Endpoint and method changes

| Old | Current |
| --- | --- |
| `authClient.forgotPassword` | `authClient.requestPasswordReset` |
| `POST /account-info` with `body` | `GET /account-info` with `query` |
| `/forget-password/email-otp` | standard password-reset flow |
| `authClient.dodopayments.checkout()` | `checkoutSession()` with a product slug |
| legacy `/mcp/*` OAuth endpoints | `/oauth2/*` |

The 1.5.0 email-change endpoint always returns `{ status: true }` under enumeration protection; it no longer confirms whether an address exists or changed.

## Callback and option migrations

- Replace `onEmailVerification` with `afterEmailVerification`.
- For new-address verification use `emailVerification.sendVerificationEmail`; the old change-flow `sendChangeEmailVerification` callback is removed.
- Replace `advanced.generateId` with `advanced.database.generateId`.
- Replace `advanced.database.useNumberId` with `generateId: "serial"`.
- Rename the organization model's `permission` field to `permissions`.
- Replace older `organizationCreation` hooks with `organizationHooks`.

Email OTP, magic-link, phone-number, and organization callbacks that used to receive `request` now receive `ctx`; their request is `ctx.request`. This applies to `sendVerificationOTP`, `generateOTP`, `sendMagicLink`, `sendOTP`, `sendPasswordResetOTP`, `callbackOnVerification`, `teams.defaultTeam.customCreateDefaultTeam`, and `teams.maximumTeams`.

## Adapter and hook migrations

Replace removed `createAdapter` with `createAdapterFactory`. Database `create.after`, `update.after`, and `delete.after` hooks now execute after commit, so atomic follow-up writes belong inside the adapter operation or transaction.

`getMigrations` moved from `better-auth` to `better-auth/db/migration`. Adapter test helpers moved from removed `better-auth/adapters/test` to `@better-auth/test-utils/adapter`:

```ts
import {
  testAdapter,
  createTestSuite,
} from "@better-auth/test-utils/adapter";
```

Sessions loaded from secondary storage no longer have `id`.

## Type and export migrations

| Removed name | Replacement |
| --- | --- |
| `Adapter` | `DBAdapter` |
| `TransactionAdapter` | `DBTransactionAdapter` |
| `Store` | `ClientStore` |
| `AtomListener` | `ClientAtomListener` |
| `ClientOptions` | `BetterAuthClientOptions` |
| `InferUser` | generic `User` from `better-auth` |
| `InferSession` | generic `Session` from `better-auth` |

`LiteralUnion` and `DeepPartial` moved from `better-auth/types/helper` to `@better-auth/core`. The `@better-auth/core/utils` barrel was removed; import subpaths such as `@better-auth/core/utils/id`, `/json`, and `/error-codes`.

`PluginContext<Options>` is generic. Plugin `$ERROR_CODES` is `Record<string, RawError>` and should use `defineErrorCodes()`, not a string map.

## OAuth-provider migration

The legacy provider's replacement requires `consentPage`, changes default ID-token and refresh-token lifetimes to 10 hours and 30 days, changes registration scopes to an array, removes global PKCE opt-out, and hashes client secrets by default. Migrate tables, secrets, stored token values, endpoints, and consent UI together.

The built-in MCP authorization-server plugin was deprecated in 1.6.0 for removal on the next line. Use `@better-auth/oauth-provider` for authorization and keep `createMcpAuthClient` at resource servers.
