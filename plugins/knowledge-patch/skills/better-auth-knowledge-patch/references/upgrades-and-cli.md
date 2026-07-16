# Upgrades, CLI, and Compatibility

## Standalone Auth CLI

Use standalone `npx auth` instead of `@better-auth/cli`.

```sh
npx auth init
npx auth migrate
npx auth generate --adapter prisma
npx auth upgrade
```

`init` scaffolds auth configuration, database adapter, and framework integration. Migration and generation commands use the new executable. `generate --adapter` can operate without a complete auth config.

## ESM-only distribution

The package is ESM-only. CommonJS applications must migrate import/loading behavior before upgrade.

## Package alignment

Security fixes are package-specific. Updating `better-auth` does not update directly installed packages such as `@better-auth/sso`, `@better-auth/scim`, or `@better-auth/oauth-provider`.

The June security cycle's stable target is `better-auth@1.6.14`. The SCIM provider-ownership and OAuth resource-indicator fixes require the documented `1.7.0-beta.4` path or the advisory workaround.

Align all Better Auth packages to compatible versions in production dependencies. `No request state found` can indicate duplicate `better-auth`, `@better-auth/core`, or `better-call` resolutions.

```sh
pnpm why better-auth
pnpm why @better-auth/core
pnpm why better-call
```

Use one `better-call` resolution where older Yarn or pnpm otherwise duplicates it.

## Release tracks

The untagged package is the stable track. Changes requiring code, configuration, or schema updates first ship under the `beta` tag.

```sh
npm install better-auth
npm install better-auth@beta
```

## Extracted packages

The following features have dedicated packages:

- SSO: `@better-auth/sso`.
- SCIM: `@better-auth/scim`.
- OAuth Provider: `@better-auth/oauth-provider`.
- Passkeys: `@better-auth/passkey`.
- API keys: `@better-auth/api-key` and `@better-auth/api-key/client`.
- Redis secondary storage: `@better-auth/redis-storage`.
- Database adapters: matching `@better-auth/*-adapter` packages.

The main package still re-exports database adapters. Use `better-auth/minimal` with direct adapter imports for a smaller dependency surface.

## Runtime compatibility

### Cloudflare Workers

Enable AsyncLocalStorage with `nodejs_compat` and compatibility date `2024-09-23`, or use `nodejs_als`. The CLI understands Workers virtual-module imports.

```toml
compatibility_flags = ["nodejs_compat"]
compatibility_date = "2024-09-23"
```

### Expo

Install `expo-network` when using client session polling:

```sh
npx expo install expo-network
```

### SQLite and Bun

Node's `node:sqlite` `DatabaseSync` requires Node 22.5 or later. For Bun's built-in SQLite driver, run CLI commands with `bunx --bun` so Bun module types are recognized.

## Type-system compatibility

Better Auth uses Zod 4.

`AuthClient` is available as a client type helper. `inferAuth` infers auth types from a client. Generic `User` and `Session` types replace `InferUser` and `InferSession`.

| Removed type | Replacement |
| --- | --- |
| `Adapter` | `DBAdapter` |
| `TransactionAdapter` | `DBTransactionAdapter` |
| `Store` | `ClientStore` |
| `AtomListener` | `ClientAtomListener` |
| `ClientOptions` | `BetterAuthClientOptions` |

`LiteralUnion` and `DeepPartial` move to `@better-auth/core`. Import core utilities through explicit subpaths such as `@better-auth/core/utils/id`, `/json`, and `/error-codes`; the `@better-auth/core/utils` barrel is gone.

## Removed and renamed APIs

- `authClient.forgotPassword` → `authClient.requestPasswordReset`.
- `createAdapter` → `createAdapterFactory`.
- `onEmailVerification` → `afterEmailVerification`.
- Organization `permission` → `permissions`.
- OIDC `redirectURLs` → `redirectUrls` plus migration.
- `better-auth` root `getMigrations` → `better-auth/db/migration`.
- `better-auth/adapters/test` → `@better-auth/test-utils/adapter`.
- `/forget-password/email-otp` → standard password-reset flow.

## Compatibility checks in plugins

`AuthContext` includes the running Better Auth version. Plugins can use it for diagnostics or compatibility branches, while package manifests should still enforce supported dependency versions.
