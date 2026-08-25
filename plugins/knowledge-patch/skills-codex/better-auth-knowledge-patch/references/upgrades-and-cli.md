# Upgrades, CLI, and Compatibility

## Standalone Auth CLI

The standalone CLI introduced through the 1.5-guide supersedes `@better-auth/cli`. `init` scaffolds auth configuration, database adapter, and framework integration. Migration and generation use the same executable, and `generate --adapter` works without a complete auth config.

```sh
npx auth init
npx auth migrate
npx auth generate --adapter prisma
npx auth upgrade
```

When using Bun's built-in SQLite driver, invoke CLI commands with `bunx --bun` so Bun module types are recognized.

## ESM-only distribution

The package became ESM-only in 1.4.0. Convert `require()` consumers and CommonJS-only tooling before the upgrade.

## Package alignment

Security updates are package-specific. Upgrading `better-auth` alone does not upgrade directly installed `@better-auth/sso`, `@better-auth/scim`, or `@better-auth/oauth-provider`. The documented June security-cycle stable target is `better-auth@1.6.14`; SCIM provider-ownership and OAuth resource-indicator fixes require the documented `1.7.0-beta.4` path or its advisory workaround.

Keep all Better Auth packages in compatible production dependency ranges. If request state disappears after an upgrade, inspect duplicates:

```sh
pnpm why better-auth
pnpm why @better-auth/core
pnpm why better-call
```

Resolve to one `better-call` copy when older pnpm or Yarn layouts duplicate it.

## Stable and beta tracks

The untagged package is the stable track. Changes needing code, configuration, or schema updates first ship under `beta`.

```sh
npm install better-auth
npm install better-auth@beta
```

## Runtime prerequisites

- Cloudflare Workers need `nodejs_compat` with compatibility date `2024-09-23` or `nodejs_als` for AsyncLocalStorage.
- Node's `node:sqlite` `DatabaseSync` requires Node 22.5 or later.
- Expo session polling requires `expo-network`.
- Express 5 auth routes require a named wildcard; Express 4 uses the unnamed form.

`AuthContext` exposes the running version for plugin compatibility and diagnostics.

## Schema-generation safeguards

Rerun migration or generation after enabling database joins or any schema-bearing plugin. The CLI refuses to add a no-default required column to a table with existing rows. Choose a safe staged migration rather than bypassing this protection.

## Removed public surface

Use the migration guide for the full replacement matrix. Common upgrade blockers include removed `createAdapter`, `onEmailVerification`, `forgotPassword`, `/forget-password/email-otp`, `better-auth/adapters/test`, the `@better-auth/core/utils` barrel, and old client/store/adapter type names.

The SvelteKit cookie helper now requires explicit request-event input; the old React Start helper became `tanstackStartCookies` from `better-auth/tanstack-start`. The passkey, SSO, SCIM, API-key, Redis-storage, and database-adapter packages have extracted import paths.
