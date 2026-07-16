# Upgrading and configuration

Use this reference before upgrading dependencies, rewriting `prisma.config.ts`, changing migration automation, or translating removed CLI and engine options.

## Contents

- [Check runtime prerequisites](#check-runtime-prerequisites)
- [Understand Prisma Config's evolution](#understand-prisma-configs-evolution)
- [Write current Prisma Config](#write-current-prisma-config)
- [Configure independent project paths](#configure-independent-project-paths)
- [Use driver adapters for schema commands](#use-driver-adapters-for-schema-commands)
- [Handle destructive migration workflows](#handle-destructive-migration-workflows)
- [Replace removed CLI inputs](#replace-removed-cli-inputs)
- [Remove legacy engine controls](#remove-legacy-engine-controls)
- [Make generation and seeding explicit](#make-generation-and-seeding-explicit)
- [Override or omit a connection URL intentionally](#override-or-omit-a-connection-url-intentionally)

## Check runtime prerequisites

Prisma ORM raised its minimum supported Node.js and TypeScript versions in 6.0.0. Verify the actual runtime used by local development, CI, builds, and production before upgrading packages; checking only a developer shell can miss an older deployment image or editor TypeScript service.

Generated `Bytes` types also vary with the installed TypeScript version as of 6.18.0. Keep the compiler used for generation and application type-checking aligned.

Prisma ORM 7 does not support MongoDB (7.0.0). Keep a MongoDB application on Prisma 6 unless a separately documented migration path has become available; do not apply the SQL-database upgrade checklist to it.

## Understand Prisma Config's evolution

The first `prisma.config.ts` in 6.4.0 was Early Access. It was loaded from the CLI's current working directory, could run arbitrary TypeScript such as secret retrieval, and required `earlyAccess: true`. When the file existed, the CLI stopped automatically loading `.env`. The original structured schema form used `kind: 'single'` plus `filePath`, or `kind: 'multi'` plus `folderPath`.

In 6.5.0, configurations could use `defineConfig` from `prisma/config` or the `PrismaConfig` type from `prisma`. That release also added the Studio adapter factory described in the tooling reference.

Prisma Config became generally available in 6.13.0:

- Remove `earlyAccess: true`.
- Put opt-ins for Preview or Early Access config capabilities under `experimental`.
- Use `.js`, `.ts`, `.mjs`, `.cjs`, `.mts`, or `.cts`.
- Name the root file `prisma.config.*`, or use the supported `.config/prisma.*` location.
- Attach a seed command to `migrations.seed`.

New projects created by `prisma init` began receiving `prisma.config.ts` in 6.18.0. That release temporarily allowed an `engine` field and a config-owned datasource; when present, the config datasource overrode the schema datasource.

The current breaking architecture in 7.0.0 makes Prisma Config required for introspection and migration but removes the transitional top-level `engine` and `adapter` config fields. Distinguish historical examples from current configuration.

## Write current Prisma Config

Keep CLI datasource settings, project paths, and seed commands in `prisma.config.ts`:

```ts
import 'dotenv/config'
import { defineConfig, env } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
    seed: 'tsx prisma/seed.ts',
  },
  datasource: {
    url: env('DATABASE_URL'),
    shadowDatabaseUrl: env('SHADOW_DATABASE_URL'),
  },
})
```

The CLI no longer loads environment variables automatically (7.0.0). Import `dotenv/config`, use a platform secret loader, or otherwise populate `process.env` before calling `env()`.

In the Prisma schema, retain the provider but remove CLI-owned URLs:

```prisma
datasource db {
  provider = "postgresql"
}
```

Upgrade mappings:

- Move `datasource.url` from the schema to `datasource.url` in Prisma Config.
- Move `datasource.shadowDatabaseUrl` to `datasource.shadowDatabaseUrl` in Prisma Config.
- Remove `datasource.directUrl`; it has no current schema/config equivalent.
- Move schema and seed settings out of the removed `prisma` block in `package.json`.
- Remove obsolete top-level config `engine` and `adapter` fields.
- Remove `generator.runtime = "react-native"` from current projects.

## Configure independent project paths

Prisma Config gained Early Access independent top-level paths for migrations, views, and TypedSQL in 6.12.0:

```ts
import { defineConfig } from 'prisma/config'

export default defineConfig({
  schema: 'db/schema.prisma',
  migrations: {
    path: 'db/migrations',
    seed: 'tsx db/seed.ts',
  },
  views: { path: 'db/views' },
  typedSql: { path: 'db/queries' },
})
```

This removes the need to infer every artifact location from the schema location. For older multi-file layouts without independent config paths, the migrations directory belongs beside the schema file containing the datasource block (6.6.0).

## Use driver adapters for schema commands

Early Access support in 6.6.0 allowed `db push`, `db pull`, and `migrate diff` to operate on remote Cloudflare D1 and Turso/LibSQL databases through a migration adapter supplied by Prisma Config. At introduction, `migrate dev` and `migrate deploy` were not supported for these databases.

The original D1 shape was:

```ts
import type { PrismaConfig } from 'prisma'
import { PrismaD1Http } from '@prisma/adapter-d1'

type Env = {
  CLOUDFLARE_D1_TOKEN: string
  CLOUDFLARE_ACCOUNT_ID: string
  CLOUDFLARE_DATABASE_ID: string
}

export default {
  schema: 'prisma/schema.prisma',
  migrate: {
    async adapter(env: Env) {
      return new PrismaD1Http({
        CLOUDFLARE_D1_TOKEN: env.CLOUDFLARE_D1_TOKEN,
        CLOUDFLARE_ACCOUNT_ID: env.CLOUDFLARE_ACCOUNT_ID,
        CLOUDFLARE_DATABASE_ID: env.CLOUDFLARE_DATABASE_ID,
      })
    },
  },
} satisfies PrismaConfig<Env>
```

The snippet uses current adapter export casing; verify the current config type before copying the historical `migrate.adapter` shape unchanged.

Local D1 introspection no longer uses `db pull --local-d1` (7.0.0). Configure it through `listLocalDatabases()` and use the normal `prisma db pull` command.

## Handle destructive migration workflows

`prisma migrate dev` stopped offering an interactive reset when it detects drift or cannot apply a migration cleanly in 6.5.0. It exits with an error. Run the destructive operation explicitly only when data loss is intended:

```sh
npx prisma migrate reset
```

As of 6.15.0, when the CLI detects invocation from a supported automated coding environment, even `prisma migrate reset --force` asks for explicit confirmation. Account for that guardrail in automation; do not attempt to bypass it accidentally.

Prisma binaries may load from local network locations as of 6.5.0. This supports deployments that put binaries on network-accessible storage, but the execution environment still needs reliable access and correct platform binaries.

## Replace removed CLI inputs

The following `prisma generate` options were removed in 7.0.0:

- `--data-proxy`
- `--accelerate`
- `--no-engine`
- `--allow-no-models`

For `prisma migrate diff`:

- Replace `--from-schema-datamodel` with `--from-schema`.
- Replace `--to-schema-datamodel` with `--to-schema`.
- Replace legacy URL, schema-datasource, and local-D1 inputs with `--from-config-datasource` or `--to-config-datasource` as appropriate.
- Do not try to diff two datasource URLs through one config file; one Prisma Config cannot represent both sides that way.

Also remove:

- `prisma db pull --local-d1`; use `listLocalDatabases()` configuration.
- The undocumented legacy `db pull --url` behavior from the 7.0.0 transition; an official `--url` override returned for selected commands in 7.2.0, as described below.
- `prisma introspect`; use `prisma db pull`.

## Remove legacy engine controls

The library, binary, Data Proxy, old Accelerate, and React Native engines were removed in 7.0.0. Remove `engineType = "library"` and `engineType = "binary"` plus these retired environment variables:

- `PRISMA_CLI_QUERY_ENGINE_TYPE`
- `PRISMA_CLIENT_ENGINE_TYPE`
- `PRISMA_QUERY_ENGINE_BINARY`
- `PRISMA_QUERY_ENGINE_LIBRARY`
- `PRISMA_GENERATE_SKIP_AUTOINSTALL`
- `PRISMA_SKIP_POSTINSTALL_GENERATE`
- `PRISMA_GENERATE_IN_POSTINSTALL`
- `PRISMA_GENERATE_DATAPROXY`
- `PRISMA_GENERATE_NO_ENGINE`
- `PRISMA_CLIENT_NO_RETRY`
- `PRISMA_MIGRATE_SKIP_GENERATE`
- `PRISMA_MIGRATE_SKIP_SEED`

Use the Query Compiler and a driver adapter for direct database access, or `accelerateUrl` for Prisma Accelerate.

## Make generation and seeding explicit

Package installation no longer invokes `prisma generate`, and Prisma Migrate no longer generates or seeds automatically as of 7.0.0. Add the commands to the exact workflows that require them:

```sh
npx prisma migrate deploy
npx prisma generate
npx prisma db seed
```

Do not run seeding after every production deploy unless it is intentionally idempotent. If a retained `prisma-client-js` generator uses a custom output path, install `@prisma/client-runtime-utils` explicitly.

## Override or omit a connection URL intentionally

`prisma db pull`, `prisma db push`, and `prisma migrate dev` accept an official `--url` override as of 7.2.0:

```sh
npx prisma db pull --url "$DATABASE_URL"
npx prisma db push --url "$DATABASE_URL"
npx prisma migrate dev --url "$DATABASE_URL"
```

Use this for an intentional one-invocation target.

Connection-free commands tolerate an undefined datasource URL as of 7.2.0. For example, allow `prisma generate` to run in a build stage without database credentials:

```ts
import { defineConfig } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  datasource: {
    url: process.env.DATABASE_URL,
  },
})
```

Use an optional environment lookup only for genuinely connection-free workflows.
