# Upgrading and configuration

## Check the runtime before changing dependencies

Prisma ORM 6 raised the minimum supported Node.js and TypeScript versions
(6.0.0). Inspect the target Prisma package's engine and peer requirements, then
upgrade the runtime and compiler before installing Prisma if necessary.

MongoDB applications must remain on Prisma 6 because Prisma ORM 7.0.0 does not
support MongoDB. Do not apply the Prisma 7 migration checklist to a MongoDB
project.

## Use current Prisma Config

`prisma.config.ts` began as Early Access in 6.4.0. That syntax required
`earlyAccess: true`, looked in the CLI working directory, represented a
multi-file schema with `kind: 'multi'` and `folderPath`, and stopped automatic
`.env` loading whenever a config was present. Because it executes TypeScript,
it could also retrieve secrets programmatically. The 6.5.0 surface supported
`defineConfig` from `prisma/config` and the `PrismaConfig` type from `prisma`.

Prisma Config became GA in 6.13.0. It accepts `.js`, `.ts`, `.mjs`, `.cjs`,
`.mts`, and `.cts`, including `.config/prisma.*`; Preview or Early Access
capabilities moved under `experimental`. It can independently locate
migrations, views, and TypedSQL (introduced in 6.12.0), and the migrations
configuration can carry the seed command.

Prisma 6.18.0 allowed datasource configuration to move into Prisma Config. At
that point a configured datasource overrode the schema datasource and used an
`engine` setting. Prisma 7.0.0 then made Prisma Config the owner of CLI
datasource settings and removed the config's `engine` and `adapter` fields.

Use the current shape:

```ts
import 'dotenv/config'
import { defineConfig, env } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
    seed: 'tsx prisma/seed.ts',
  },
  views: { path: 'prisma/views' },
  typedSql: { path: 'prisma/queries' },
  datasource: {
    url: env('DATABASE_URL'),
    shadowDatabaseUrl: env('SHADOW_DATABASE_URL'),
  },
})
```

The CLI no longer loads environment variables automatically. Import
`dotenv/config` or another loader before calling `env()`. Move
`datasource.url` and `datasource.shadowDatabaseUrl` out of `schema.prisma`,
remove `datasource.directUrl`, and move schema and seed settings out of the
removed `prisma` block in `package.json`.

For connection-free workflows, the datasource URL may be undefined; commands
such as `prisma generate` can run without database credentials (7.2.0).

## Override a datasource for one command

`prisma db pull`, `prisma db push`, and `prisma migrate dev` accept `--url` for
a one-invocation override as of 7.2.0:

```sh
npx prisma db pull --url "$DATABASE_URL"
npx prisma db push --url "$DATABASE_URL"
npx prisma migrate dev --url "$DATABASE_URL"
```

Do not confuse these current overrides with the undocumented `db pull --url`
input removed in 7.0.0; the supported option was added back explicitly in
7.2.0 for the three listed commands.

## Configure remote D1 and LibSQL schema commands

Prisma Config can provide driver adapters for `db push`, `db pull`, and
`migrate diff` against remote Cloudflare D1 and Turso/LibSQL databases. The
initial 6.6.0 Early Access surface did not support `migrate dev` or
`migrate deploy` for those databases.

In Prisma 7, the removed `db pull --local-d1` input is replaced by configuring
local D1 through `listLocalDatabases()`. Keep provider limits in mind rather
than assuming all migration commands work because introspection and diff do.

## Make generation and seeding explicit

Since 7.0.0, package installation does not run `prisma generate`, and Prisma
Migrate does not generate the client or run seeding implicitly. Add explicit
steps wherever installation, deployment, or migration scripts previously
depended on side effects:

```sh
npx prisma generate
npx prisma db seed
```

If `prisma-client-js` remains temporarily and uses a custom output, install
`@prisma/client-runtime-utils`.

## Replace removed CLI inputs

Prisma 7.0.0 removed these `prisma generate` flags:

- `--data-proxy`
- `--accelerate`
- `--no-engine`
- `--allow-no-models`

For `migrate diff`, rename `--from-schema-datamodel` and
`--to-schema-datamodel` to `--from-schema` and `--to-schema`. URL,
schema-datasource, and local-D1 inputs became
`--from-config-datasource` and `--to-config-datasource`; one config cannot diff
two different datasource URLs.

`prisma introspect` is removed; use `prisma db pull`. `db pull --local-d1` is
removed as described above.

## Remove legacy engines and environment controls

Prisma 7 removed the library and binary engines, Data Proxy, the old Accelerate
engine, and the React Native client engine. Remove `engineType = "library"`,
`engineType = "binary"`, and the following controls (7.0.0):

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

Accelerate remains available as a cache connection through the client's
`accelerateUrl`; what disappeared is the legacy engine architecture and its
controls.

## Update generator targets and imports

Prefer `provider = "prisma-client"`, set an explicit output, and import from
the generated application path. The GA generator emits ESM-compatible code by
default (6.16.0).

Runtime names changed in 6.15.0: `node` became `nodejs`, `deno-deploy` became
`deno`, and `vercel` became `vercel-edge`. Prisma 7 removed
`runtime = "react-native"`.

Normalize driver export casing in Prisma 7:

- `PrismaBetterSQLite3` → `PrismaBetterSqlite3`
- `PrismaD1HTTP` → `PrismaD1Http`
- `PrismaLibSQL` → `PrismaLibSql`
- `PrismaNeonHTTP` → `PrismaNeonHttp`

For legacy `prisma-client-js`, update `/wasm` imports to `/edge`; the new entry
targets edge JavaScript runtimes rather than Accelerate (7.0.0).

## Audit old workflow assumptions

After migrating configuration, verify all of the following:

- The client is constructed with an adapter or `accelerateUrl`.
- `.env` loading happens before Prisma Config evaluates `env()`.
- CI and deployment run `prisma generate` explicitly.
- Seeding runs through `prisma db seed` explicitly when intended.
- Reset automation handles the additional confirmation checkpoint.
- Migrations for PostgreSQL extensions contain custom SQL.
- Scripts use `prisma db pull`, current diff flags, and supported `--url`
  overrides.
- The application no longer reads removed metrics or engine controls.
