---
name: prisma-knowledge-patch
description: Prisma 7.8.0 compatibility. Use for Prisma work.
license: MIT
version: 7.8.0
metadata:
  author: Nevaberry
---

# Prisma Knowledge Patch

Use this skill to choose current Prisma ORM patterns, upgrade older projects, and avoid removed APIs. Read the reference file for every area touched by the task; several changes span configuration, generated code, and runtime construction.

## Reference index

| Reference | Topics |
| --- | --- |
| [client-generation-and-adapters.md](references/client-generation-and-adapters.md) | `prisma-client`, Query Compiler, driver adapters, runtime targets, client construction, cache behavior, adapter correctness |
| [extensions-and-observability.md](references/extensions-and-observability.md) | Client Extensions, event listeners, tracing, SQL comments, read replicas, metrics, driver errors |
| [prisma-postgres-and-products.md](references/prisma-postgres-and-products.md) | Prisma Postgres, local development, direct connections, Console, Management API, MCP, Compute, integrations |
| [schema-migrations-and-queries.md](references/schema-migrations-and-queries.md) | Schema features, indexes, views, migrations, transactions, filters, bulk queries, introspection |
| [studio-and-tooling.md](references/studio-and-tooling.md) | Studio, editor integrations, bootstrap/init workflows, CLI output, large schemas |
| [upgrading-and-configuration.md](references/upgrading-and-configuration.md) | Breaking upgrades, Prisma Config, datasource ownership, removed CLI inputs, environment loading, command overrides |

## Start with the connection architecture

Treat the generated client and its database connection as separate choices:

1. Generate application-owned code with `provider = "prisma-client"` and an explicit `output`.
2. Configure CLI datasource details in `prisma.config.ts`.
3. Construct `PrismaClient` with a driver adapter, or with `accelerateUrl` for Prisma Accelerate.
4. Run generation and seeding explicitly in installation, migration, and deployment workflows.

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

Do not rely on `new PrismaClient()` without a connection path, schema-level datasource URLs, automatic `.env` loading by the CLI, postinstall generation, or migration-triggered generation and seeding.

## Apply the breaking-change checklist

Before upgrading an existing application:

- Keep MongoDB applications on the supported Prisma major rather than upgrading them blindly.
- Replace `prisma-client-js` with `prisma-client` when practical and update imports to the configured generated output.
- Normalize adapter export casing, including `PrismaBetterSqlite3`, `PrismaD1Http`, `PrismaLibSql`, and `PrismaNeonHttp`.
- Remove legacy engine selections, engine environment variables, Data Proxy controls, and removed generator flags.
- Move CLI datasource, schema, migration, and seed configuration into `prisma.config.ts`.
- Load environment variables explicitly before calling `env()`.
- Replace removed CLI options and deprecated `prisma introspect` invocations.
- Add explicit `prisma generate` and `prisma db seed` steps where the old workflow depended on side effects.
- Verify Node.js and TypeScript satisfy the current minimums before changing dependencies.

Read [upgrading-and-configuration.md](references/upgrading-and-configuration.md) before changing package scripts, CI, migrations, or environment handling.

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

`compilerBuild = "fast"` is the speed-oriented default; `small` trades execution speed for a smaller compiler. Runtime names are constrained and older aliases were removed. Deno uses `runtime = "deno"`; Bun is detected by relevant CLI setup commands.

Use the driver adapter matching the database. Check [client-generation-and-adapters.md](references/client-generation-and-adapters.md) for supported adapters, protocol switches, statement caching, Entra ID authentication, D1 transaction limits, and correctness fixes.

## Use migration and schema guardrails

- Request destructive resets explicitly; do not expect `migrate dev` to offer an interactive reset after drift or failed application.
- Expect an additional confirmation guard when destructive commands are invoked through supported automated coding environments.
- Manage PostgreSQL extensions in custom SQL migrations instead of `postgresqlExtensions`.
- Keep migrations beside the datasource schema file when using a multi-file schema unless Prisma Config specifies the paths independently.
- Treat externally managed tables as queryable but migration-excluded through `tables.external`.
- Add uniqueness to a view only when its data truly guarantees it; client operations and relationships depend on that declaration.
- Remember that a partial unique index does not create a `findUnique` input.
- Use `CREATE INDEX CONCURRENTLY` in PostgreSQL migration SQL when an index must be built without blocking writes.

Read [schema-migrations-and-queries.md](references/schema-migrations-and-queries.md) before editing schema attributes or generated migrations.

## Prefer current query capabilities

Use the newer APIs directly where they fit:

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
- Use nested interactive transactions on SQL databases when savepoint semantics are available.
- Do not depend on rollback semantics from D1 savepoints; its adapter treats them as no-ops.
- Size `queryPlanCacheMaxSize` for query diversity and memory use, or set it to `0` to disable the cache.
- Handle unmapped driver failures as catchable `P2039` errors.

Mapped enum members use their schema names in generated code while `@map` controls the database representation. Do not send the mapped database string merely because it appears in the schema.

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

- Keep separately derived clients behaviorally isolated while recognizing that they share the base client's pool.
- Expect the last extension to win a same-name member conflict.
- Expect query extensions to begin in declaration order.
- Check whether a client-level method exists before calling it on an extended client.
- Do not attempt to intercept nested reads or writes with a `query` extension.

Read [extensions-and-observability.md](references/extensions-and-observability.md) for tracing span names, instrumentation dependencies, SQL commenter plugins, and extension-version compatibility.

## Choose product and tooling surfaces intentionally

- Use `prisma studio` for supported local or remote databases; Studio includes relationship navigation, SQL workflows, search, filtering, and multi-cell editing.
- Use the editor extension for local and hosted database workflows when an interactive UI is appropriate.
- Use `prisma bootstrap` for state-aware Prisma Postgres setup and `prisma postgres link` to link an existing project.
- Use `prisma dev` to run local Prisma Postgres instances, and manage persisted instances explicitly.
- Use direct PostgreSQL URLs for standard PostgreSQL tools; add pooling only when the direct Prisma Postgres connection should use it.
- Treat Accelerate as the cache layer and Prisma Postgres as the pooled database layer.

Read [prisma-postgres-and-products.md](references/prisma-postgres-and-products.md) for provisioning, regions, backups, metrics, APIs, MCP, integrations, and Compute. Read [studio-and-tooling.md](references/studio-and-tooling.md) for command and UI behavior.
