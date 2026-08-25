# Upgrading and configuration

## Runtime prerequisites

Prisma ORM 6 raised the minimum supported Node.js and TypeScript versions
(6.0.0). Check the exact requirements of the Prisma release being installed
before changing dependencies, CI images, or production runtimes.

## Prisma Config evolution

### Early configuration shapes

`prisma.config.ts` began as Early Access in 6.4.0. It was resolved relative to
the CLI working directory, required `earlyAccess: true`, stopped automatic
`.env` loading when present, and could run arbitrary TypeScript such as secret
retrieval. A single schema used `{ kind: 'single', filePath: ... }`, while a
multi-file schema used `{ kind: 'multi', folderPath: ... }`.

Early adapter-backed schema commands and Studio connections used config-level
factories (6.5.0 and 6.6.0). Those shapes are historical; do not copy their
`migrate.adapter` or `studio.adapter` fields into current Prisma Config without
checking that the installed release still accepts them. That early API exposed
`defineConfig` from `prisma/config` and the `PrismaConfig` type from `prisma`.

In 6.12.0, config could independently locate migrations, views, and TypedSQL:

```ts
import { defineConfig } from 'prisma/config'

export default defineConfig({
  earlyAccess: true,
  migrations: { path: './db/migrations' },
  views: { path: './db/views' },
  typedSql: { path: './db/queries' },
})
```

### Stable configuration

Prisma Config became GA in 6.13.0. Remove `earlyAccess: true`; opt into
unfinished config capabilities through `experimental`. Supported module
extensions are `.js`, `.ts`, `.mjs`, `.cjs`, `.mts`, and `.cts`, and the CLI
also searches `.config/prisma.*`. A seed command belongs under `migrations`.

`prisma init` started creating `prisma.config.ts` in 6.18.0. That release could
place a datasource URL in config and select `engine: 'classic'`; a config
datasource took precedence over the schema datasource.

### Required Prisma 7 shape

For Prisma 7, Prisma Config is required for introspection and migrations and
owns CLI datasource settings (7.0.0). Move
`datasource.url` and `datasource.shadowDatabaseUrl` out of `schema.prisma`,
remove `datasource.directUrl`, and move schema and seed settings out of the
removed `prisma` block in `package.json`. The former config-level `engine` and
`adapter` fields are removed.

The CLI does not load `.env` automatically. Import a loader explicitly before
calling `env()`:

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

Connection-free commands tolerate an undefined datasource URL as of 7.2.0,
so `prisma generate` can run where no database secret is available. Database
commands can override the configured datasource for one invocation:

```sh
npx prisma db pull --url "$DATABASE_URL"
npx prisma db push --url "$DATABASE_URL"
npx prisma migrate dev --url "$DATABASE_URL"
```

## Generated client and connection changes

New projects use the application-owned `prisma-client` generator. Give it an
explicit output and import from that path. Construct its client with a driver
adapter or with `accelerateUrl`; a bare constructor, an empty options object,
`datasources`, and `datasourceUrl` are removed connection paths (7.0.0).

Normalize renamed exports during the upgrade:

- `PrismaBetterSQLite3` to `PrismaBetterSqlite3`
- `PrismaD1HTTP` to `PrismaD1Http`
- `PrismaLibSQL` to `PrismaLibSql`
- `PrismaNeonHTTP` to `PrismaNeonHttp`

The `node`, `deno-deploy`, and `vercel` runtime names were consolidated into
`nodejs`, `deno`, and `vercel-edge` in 6.15.0. Prisma 7 removes the generator's
`react-native` runtime (7.0.0).

## Explicit generation and seeding

Package installation no longer invokes `prisma generate`, and Prisma Migrate
no longer generates the client or seeds implicitly (7.0.0). Add the intended
steps explicitly to local, CI, deployment, and installation workflows:

```sh
npx prisma generate
npx prisma db seed
```

If a legacy `prisma-client-js` generator keeps a custom output directory,
install `@prisma/client-runtime-utils`.

## Removed CLI inputs

Prisma 7 removes these `prisma generate` flags (7.0.0):

- `--data-proxy`
- `--accelerate`
- `--no-engine`
- `--allow-no-models`

For `migrate diff`, rename `--from-schema-datamodel` and
`--to-schema-datamodel` to `--from-schema` and `--to-schema`. URL,
schema-datasource, and local-D1 inputs become
`--from-config-datasource`/`--to-config-datasource`; one config cannot diff two
different datasource URLs.

`db pull --local-d1`, its undocumented `--url` option, and `prisma introspect`
were removed. Configure local D1 with `listLocalDatabases()` and use
`prisma db pull`. The general `--url` override returned for `db pull`,
`db push`, and `migrate dev` in 7.2.0.

## Removed engines and environment controls

Remove library and binary engine selection, Data Proxy controls, and these
environment variables (7.0.0):

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

The deprecated `metrics` preview API is also removed; collect pool and driver
metrics from the selected adapter.

## MongoDB compatibility

Prisma ORM 7.0.0 does not support MongoDB. Keep MongoDB projects on a supported
Prisma 6 release rather than applying the SQL-focused major upgrade.

## Destructive-operation guardrails

`prisma migrate dev` stopped offering an interactive reset after drift or a
failed migration in 6.5.0. It exits with an error; run `prisma migrate reset`
explicitly only when data destruction is intended.

Starting in 6.15.0, destructive CLI commands launched through supported
automated coding environments require explicit confirmation even with
`migrate reset --force`. The safeguard expanded in 7.9.0 to cover
`prisma db push --accept-data-loss`, more environment conventions including
`AI_AGENT` and `AGENT`, and Linux. The Prisma MCP server no longer exposes its
`migrate-reset` operation; use the guarded CLI path when a reset is required.

## PostgreSQL extensions

Remove the deprecated `postgresqlExtensions` preview feature and manage
extensions in custom migration SQL (6.16.0). Create an empty migration, insert
the required `CREATE EXTENSION` statement, review it, and apply it through the
ordinary migration workflow.
