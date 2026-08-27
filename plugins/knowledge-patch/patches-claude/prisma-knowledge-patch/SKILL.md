---
name: prisma-knowledge-patch
description: Prisma
version: "7.8.0"
license: MIT
metadata:
  author: Nevaberry
---


# Prisma Knowledge Patch

Use this skill when choosing current Prisma ORM patterns, upgrading an older
project, configuring Prisma Postgres, or diagnosing behavior that changed
across recent Prisma releases. Read the reference file for every area touched;
connection setup, generated code, migrations, and runtime construction often
change together.

## Reference index

| Reference | Topics |
| --- | --- |
| [client-generation-and-adapters.md](references/client-generation-and-adapters.md) | `prisma-client`, Query Compiler, driver adapters, runtime targets, client construction, cache behavior, adapter correctness |
| [extensions-and-observability.md](references/extensions-and-observability.md) | Client Extensions, event listeners, tracing, SQL comments, read replicas, metrics, driver errors |
| [prisma-postgres-and-products.md](references/prisma-postgres-and-products.md) | Prisma Postgres, local development, direct connections, Console, Management API, MCP, Compute, integrations |
| [schema-migrations-and-queries.md](references/schema-migrations-and-queries.md) | Schema features, indexes, views, migrations, transactions, filters, bulk queries, introspection |
| [studio-and-tooling.md](references/studio-and-tooling.md) | Studio, editor integrations, bootstrap and init workflows, CLI output, large schemas |
| [upgrading-and-configuration.md](references/upgrading-and-configuration.md) | Breaking upgrades, Prisma Config, datasource ownership, removed CLI inputs, environment loading, command side effects |

## Start with the connection architecture

Treat generated client code and the database connection as separate choices:

1. Generate application-owned code with `provider = "prisma-client"` and an
   explicit `output`.
2. Put CLI datasource details in `prisma.config.ts`.
3. Construct `PrismaClient` with a driver adapter, or with `accelerateUrl` for
   Prisma Accelerate.
4. Run generation and seeding explicitly in installation, migration, and
   deployment workflows.

```prisma
generator client {
  provider = "prisma-client"
  output   = "../src/generated/prisma"
}

datasource db {
  provider = "postgresql"
}
```

```ts
// prisma.config.ts
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

```ts
import { PrismaPg } from '@prisma/adapter-pg'
import { PrismaClient } from './src/generated/prisma/client'

const adapter = new PrismaPg(process.env.DATABASE_URL!)
const prisma = new PrismaClient({ adapter })
```

Do not rely on connectionless `new PrismaClient()`, schema-level datasource
URLs, automatic CLI `.env` loading, postinstall generation, or migration-
triggered generation and seeding.

## Apply the breaking-change checklist

Before upgrading an existing application:

- Verify the installed Node.js and TypeScript versions satisfy the target
  Prisma release.
- Keep MongoDB applications on Prisma 6; Prisma 7 does not support MongoDB.
- Prefer `prisma-client`, set an explicit generated output, and update imports
  to that application-owned path.
- Pass a driver adapter or `accelerateUrl` when constructing the client.
- Normalize adapter export casing, including `PrismaBetterSqlite3`,
  `PrismaD1Http`, `PrismaLibSql`, and `PrismaNeonHttp`.
- Remove legacy engine selections, engine environment variables, Data Proxy
  controls, and removed generator flags.
- Move CLI datasource, schema, migration, and seed configuration into
  `prisma.config.ts`.
- Import environment loading before calling `env()`.
- Replace removed CLI options and `prisma introspect` invocations.
- Add explicit `prisma generate` and `prisma db seed` steps where the old
  workflow depended on side effects.
- Pin `@prisma/extension-read-replicas@0.4.1` for Prisma 6; use the current
  extension release with Prisma 7.

Read [upgrading-and-configuration.md](references/upgrading-and-configuration.md)
before changing package scripts, CI, migrations, or environment handling.

## Configure generated output deliberately

Use generator options only when the deployment target needs them:

```prisma
generator client {
  provider               = "prisma-client"
  output                 = "../src/generated/prisma"
  runtime                = "nodejs"
  moduleFormat           = "esm"
  generatedFileExtension = "ts"
  importFileExtension    = "ts"
  compilerBuild          = "small"
}
```

`compilerBuild = "fast"` is the speed-oriented default; `small` reduces the
compiler size at the cost of execution speed. Use current runtime names:
`nodejs`, `deno`, `bun`, `workerd`/`cloudflare`, and
`vercel-edge`/`edge-light`. React Native is not a Prisma 7 runtime target.

Match the driver adapter to the database. Check
[client-generation-and-adapters.md](references/client-generation-and-adapters.md)
for adapter maturity, protocol switches, statement caching, Entra ID
authentication, D1 transaction limits, and correctness fixes.

## Use migration and schema guardrails

- Request destructive resets explicitly; `migrate dev` exits on drift or an
  unclean migration instead of offering an interactive reset.
- Expect an additional confirmation checkpoint when destructive commands run
  through supported automated coding environments.
- Manage PostgreSQL extensions in custom SQL migrations instead of
  `postgresqlExtensions`.
- Keep migrations beside the datasource schema file for multi-file schemas
  unless Prisma Config specifies independent paths.
- Use `tables.external` for queryable tables that migrations must ignore.
- Add uniqueness to a view only when its data guarantees it; client operations
  and relationships depend on that declaration.
- Do not expect a partial unique index to produce a `findUnique` input.
- Use `CREATE INDEX CONCURRENTLY` in PostgreSQL migration SQL when an index
  must be built without blocking writes.
- Treat rolled-back migration files as unapplied when reading migration status.

Read [schema-migrations-and-queries.md](references/schema-migrations-and-queries.md)
before editing schema attributes or generated migration SQL.

## Prefer current query capabilities

```ts
const changed = await prisma.user.updateManyAndReturn({
  where: { status: 'pending' },
  data: { status: 'active' },
})

await prisma.session.deleteMany({
  where: { expired: true },
  limit: 500,
})
```

- Use `omit` per query or globally to exclude fields.
- Use `mode: 'insensitive'` with supported JSON string filters.
- Use nested interactive transactions on SQL databases when savepoint
  semantics are available.
- Do not depend on rollback semantics from D1 savepoints; its adapter treats
  them as logged no-ops.
- Set `queryPlanCacheMaxSize` according to query diversity and memory use, or
  to `0` to disable the cache.
- Catch unmapped database-driver failures as `P2039` errors.
- Validate dates before raw SQL; invalid `Date` values are rejected.

Mapped enum members use their schema names in generated code while `@map`
controls the database representation. Do not send the mapped database string
merely because it appears in the schema.

## Compose extensions predictably

Register event listeners before extending a client:

```ts
const prisma = new PrismaClient({
  adapter,
  log: [{ emit: 'event', level: 'query' }],
})
  .$on('query', (event) => console.log(event.query))
  .$extends(extension)
```

For extension chains:

- Separately derived clients isolate behavior while sharing the base client's
  pool.
- The last extension wins a same-name member conflict.
- Query extensions begin in declaration order.
- Check whether a client-level method exists before calling it on an extended
  client.
- Query extensions cannot intercept nested reads or writes.

Read [extensions-and-observability.md](references/extensions-and-observability.md)
for tracing span names, instrumentation dependencies, SQL commenter plugins,
and extension compatibility.

## Choose product and tooling surfaces intentionally

- Use `prisma studio` for supported local or remote databases; Studio includes
  relationship navigation, SQL workflows, search, filtering, and multi-cell
  editing.
- Use the editor extension for local and hosted database workflows when an
  interactive UI is appropriate.
- Use `prisma bootstrap` for state-aware Prisma Postgres setup and
  `prisma postgres link` to link an existing project.
- Use `prisma dev` to run local Prisma Postgres instances, and stop or remove
  persisted instances explicitly.
- Use direct PostgreSQL URLs for standard PostgreSQL tools; add `pool=true`
  only when the direct Prisma Postgres connection should use pooling.
- Treat Accelerate as the cache layer and Prisma Postgres as the pooled
  database layer.

Read [prisma-postgres-and-products.md](references/prisma-postgres-and-products.md)
for provisioning, regions, backups, metrics, APIs, MCP, integrations, and
Compute. Read [studio-and-tooling.md](references/studio-and-tooling.md) for
command and UI behavior.
