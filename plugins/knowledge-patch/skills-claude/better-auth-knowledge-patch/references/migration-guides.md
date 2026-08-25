# Migration Guides

## Organization teams

Multi-team membership replaces the single `member.teamId` relation (since 1.3.0). Remove `teamId`, add the required `teamMembers` join table, migrate membership data, and regenerate types. Clients can infer organization shapes with:

```ts
organizationClient({ $inferAuth: {} as typeof auth })
```

## Database identifiers and joins

Move `advanced.generateId` to `advanced.database.generateId`. Replace `advanced.database.useNumberId` with `generateId: "serial"`; use `"uuid"` for UUID keys. Enabling `experimental.joins` in 1.4.0 requires regenerated or migrated schema.

## Email and account endpoints

- Replace `authClient.forgotPassword` with `authClient.requestPasswordReset`.
- Call account info through `GET /account-info` and `query`, not POST and `body`.
- Replace the removed change-email `sendChangeEmailVerification` callback with `user.changeEmail.sendChangeEmailConfirmation` for the old address and `emailVerification.sendVerificationEmail` for the new one.
- Replace `onEmailVerification` with `afterEmailVerification`.
- The removed `/forget-password/email-otp` route is replaced by the standard password-reset flow.

## Extracted plugins

Move SSO, passkeys, API keys, SCIM, OAuth Provider, Redis secondary storage, and database adapters to their dedicated `@better-auth/*` packages. API-key client imports come from `@better-auth/api-key/client`.

## Callback context migration

Email OTP, magic-link, phone-number, and organization callbacks that received `request` now receive `ctx`; the request is `ctx.request` (since 1.4.0). This applies to `sendVerificationOTP`, `generateOTP`, `sendMagicLink`, `sendOTP`, `sendPasswordResetOTP`, `callbackOnVerification`, `teams.defaultTeam.customCreateDefaultTeam`, and `teams.maximumTeams`.

## OIDC and API-key schema

Rename OIDC `redirectURLs` to `redirectUrls` and migrate the stored field. The extracted API-key schema renames `ApiKey.userId` to `referenceId` and adds `configId` defaulting to `"default"` (since 1.5-guide). Returned keys expose `references` as owner type; `defaultPermissions` receives `referenceId`. Server `updateApiKey` calls require at least `userId` or request headers.

## OAuth Provider migration

Moving from the deprecated OIDC provider to `@better-auth/oauth-provider` makes `consentPage` required, changes default ID-token and refresh-token lifetimes to 10 hours and 30 days, makes default registration scopes an array, removes global PKCE opt-out, and hashes client secrets by default.

Rename `oauthApplication` to `oauthClient`, split refresh tokens into their own table, and hash legacy plaintext secrets and stored token values. Move legacy MCP endpoints from `/mcp/*` to `/oauth2/*`.

## Type and export replacements

The 1.5-guide removed these deprecated names:

| Removed | Replacement |
| --- | --- |
| `Adapter` | `DBAdapter` |
| `TransactionAdapter` | `DBTransactionAdapter` |
| `Store` | `ClientStore` |
| `AtomListener` | `ClientAtomListener` |
| `ClientOptions` | `BetterAuthClientOptions` |
| `InferUser` | generic `User` |
| `InferSession` | generic `Session` |

`LiteralUnion` and `DeepPartial` moved from `better-auth/types/helper` to `@better-auth/core`. Replace the removed `@better-auth/core/utils` barrel with subpaths such as `/utils/id`, `/utils/json`, and `/utils/error-codes`. Rename the organization model field `permission` to `permissions`.

Replace removed `createAdapter` with `createAdapterFactory` (since 1.5.0). Import `getMigrations` from `better-auth/db/migration`.

## Adapter testing

`better-auth/adapters/test` is removed. Adapter authors import `testAdapter` and `createTestSuite` from `@better-auth/test-utils/adapter`.

## Hook transaction timing

Database `create.after`, `update.after`, and `delete.after` hooks execute after commit. Move atomic dependent writes into the adapter's main operation or transaction.

## SCIM and managed features

Run migrations after enabling SCIM, Agent Auth, dynamic organization roles, infrastructure activity tracking, persisted Creem subscriptions, or any other feature that contributes tables/columns. Managed SCIM connections add connection and credential persistence; direct database objects support the transactions those workflows need.
