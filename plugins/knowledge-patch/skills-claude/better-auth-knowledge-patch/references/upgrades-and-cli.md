# Upgrades, CLI, and Compatibility

## Standalone Auth CLI

The standalone `npx auth` executable supersedes `@better-auth/cli` (since 1.5-guide). `init` scaffolds auth configuration, its adapter, and framework integration. Migration and generation use the standalone executable, and `generate --adapter` works without a complete auth config.

```sh
npx auth init
npx auth migrate
npx auth generate --adapter prisma
npx auth upgrade
```

For Bun SQLite, use `bunx --bun` so CLI module detection sees Bun's types. Workers virtual-module imports are supported.

## ESM-only distribution

The distribution is ESM-only as of 1.4.0. Convert CommonJS `require` loading and related build configuration before upgrading.

## Package extraction

Install extracted functionality directly:

```ts
import { sso } from "@better-auth/sso";
import { scim } from "@better-auth/scim";
import { passkey } from "@better-auth/passkey";
import { apiKey } from "@better-auth/api-key";
import { oauthProvider } from "@better-auth/oauth-provider";
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
```

Redis storage is `@better-auth/redis-storage`. Direct adapter packages may be paired with `better-auth/minimal`. The main package still re-exports official adapters.

## Version alignment and security updates

Update every directly installed scoped package; updating only `better-auth` does not update `@better-auth/sso`, `@better-auth/scim`, or `@better-auth/oauth-provider` (since 1.6.0). The June security cycle used `better-auth@1.6.14` on stable, while the SCIM provider-ownership and OAuth resource-indicator fixes required the documented `1.7.0-beta.4` route or its advisory workaround.

The untagged package is stable. Changes requiring code, configuration, or schema work first ship on `beta`:

```sh
npm install better-auth
npm install better-auth@beta
```

## Duplicate dependency diagnosis

`No request state found` after an upgrade may indicate duplicate copies of `better-auth`, `@better-auth/core`, or `better-call`. Inspect the dependency graph, align all Better Auth packages in production dependencies, and force a single `better-call` resolution where older Yarn or pnpm layouts still duplicate it.

```sh
pnpm why better-auth
pnpm why @better-auth/core
pnpm why better-call
```

## Migration safety

As of 1.7.1, the Auth CLI refuses to add a required column without a default to a table that already contains rows. Use a staged nullable/defaulted migration and backfill rather than expecting an unsafe alteration to run silently.
