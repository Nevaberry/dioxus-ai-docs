# Client generation and driver adapters

## Application-owned client generation

The `prisma-client` generator first split output across multiple files to avoid
large `index.d.ts` editor problems (6.7.0), added explicit runtime, module
format, and file-extension controls while in Preview (6.12.0), and became the
GA, ESM-first generator in 6.16.0. It requires an explicit output directory.

```prisma
generator client {
  provider               = "prisma-client"
  output                 = "../src/generated/prisma"
  runtime                = "nodejs"
  moduleFormat           = "esm"
  generatedFileExtension = "ts"
  importFileExtension    = "ts"
}
```

Import `PrismaClient` from that generated output, not automatically from
`@prisma/client`. If a legacy `prisma-client-js` generator has a custom
`output`, install `@prisma/client-runtime-utils` as well (7.0.0).

## Query Compiler architecture

The Rust-free path began with the `queryCompiler` and `driverAdapters` flags
for PostgreSQL in 6.7.0, reached Preview for PostgreSQL and SQLite in 6.9.0,
then added SQL Server and PlanetScale in 6.10.0 and MySQL, MariaDB, Neon, and
CockroachDB in 6.11.0. The TypeScript Query Compiler and driver adapters became
GA in 6.16.0, including use with Prisma Accelerate and Prisma Postgres.

With `prisma-client`, select that architecture using `engineType = "client"`;
do not retain the earlier Preview flags.

```prisma
generator client {
  provider   = "prisma-client"
  output     = "../src/generated/prisma"
  engineType = "client"
}
```

The old library and binary engines, Data Proxy and its controls, the former
Accelerate engine, and the React Native client engine are removed. The legacy
`prisma-client-js/wasm` entry point is now `/edge` and targets edge JavaScript
runtimes, not Accelerate (7.0.0).

## Runtime targets and compiler builds

Deno moved off the removed `deno` Preview feature on `prisma-client-js` and
onto `prisma-client` with an explicit output and `runtime = "deno"` in 6.8.0.
Generation can run under Bun without a separate Node.js installation since
6.6.0.

Runtime names were consolidated in 6.15.0: use `nodejs`, `deno`, `bun`,
`workerd` (or `cloudflare`), `vercel-edge` (or `edge-light`), and
`react-native`. The former `node`, `deno-deploy`, and `vercel` names are not
valid. Prisma 7 subsequently removed `runtime = "react-native"` (7.0.0).

The `compilerBuild` generator option added in 7.3.0 accepts `fast` or `small`.
`fast` is the default and favors execution speed with a larger compiler;
`small` favors compiler size at the cost of speed.

```prisma
generator client {
  provider      = "prisma-client"
  output        = "../src/generated/prisma"
  compilerBuild = "small"
}
```

## Explicit client construction

The generated client needs a connection path. Pass a driver adapter, or pass
`accelerateUrl` for Prisma Accelerate. `datasources`, `datasourceUrl`, an empty
options object, and a bare `new PrismaClient()` are no longer connection
mechanisms for this client (7.0.0).

```ts
import { PrismaPg } from '@prisma/adapter-pg'
import { PrismaClient } from './generated/prisma/client'

const adapter = new PrismaPg(process.env.DATABASE_URL!)
const prisma = new PrismaClient({ adapter })
```

## Adapter selection and configuration

### SQLite, D1, and LibSQL

The JavaScript-native `better-sqlite3` adapter entered Preview in 6.7.0. Its
constructor accepts the SQLite URL. Prisma 7 normalized adapter export casing:

- `PrismaBetterSQLite3` became `PrismaBetterSqlite3`.
- `PrismaD1HTTP` became `PrismaD1Http`.
- `PrismaLibSQL` became `PrismaLibSql`.
- `PrismaNeonHTTP` became `PrismaNeonHttp`.

Use the normalized names in imports (7.0.0). Remote D1 and Turso/LibSQL can
run `db push`, `db pull`, and `migrate diff` through adapters supplied by
Prisma Config; that Early Access path did not support `migrate dev` or
`migrate deploy` in 6.6.0.

D1's savepoint methods are logged no-ops rather than real SQL. Nested code on
D1 must not depend on savepoint rollback semantics (7.8.0).

### PostgreSQL and Neon

`PrismaPg` accepts a connection string directly as of 7.6.0. Its
`statementNameGenerator` option supports custom prepared-statement names and
the `pg` driver's statement cache. `@prisma/adapter-pg` includes `@types/pg`
directly as of 7.5.0.

When an interactive transaction exceeds `maxWait` during startup, Prisma now
issues `ROLLBACK` before returning the connection to adapters such as
`@prisma/adapter-pg` and `@prisma/adapter-neon` (7.9.0). This prevents later
queries from inheriting or committing the abandoned transaction.

### MariaDB and MySQL

`@prisma/adapter-mariadb` switched to the binary MySQL protocol to preserve
number fidelity in 7.5.0. The adapter added `useTextProtocol` in 7.6.0 for an
explicit protocol switch. MariaDB statement caching is disabled by default to
avoid a reported leak.

### SQL Server

The SQL Server Query Compiler path uses `@prisma/adapter-mssql` (6.10.0). The
adapter gained Microsoft Entra ID authentication in 6.17.0, including the
default Azure credential chain:

```ts
const adapter = new PrismaMssql({
  server: 'localhost',
  port: 1433,
  database: 'mydb',
  authentication: { type: 'azure-active-directory-default' },
  options: { encrypt: true },
})
```

## Query-plan and statement caching

`PrismaClient` accepts `queryPlanCacheMaxSize` (7.8.0). Omit it for the
default, set it to `0` to disable query-plan caching, raise it for workloads
with many distinct queries, or lower it to reduce memory use.

```ts
const prisma = new PrismaClient({ adapter, queryPlanCacheMaxSize: 0 })
```

`createMany` queries stopped populating the query cache in 7.6.0, preventing
bulk operations from bloating it. Keep adapter-specific statement caching
separate from Prisma's query-plan cache when tuning memory and throughput.

## Generated types and runtime correctness

- Generator DMMF includes referential-action `onUpdate` data (6.3.0), so
  custom generators can inspect it.
- Generated `Bytes` mappings select the appropriate `Uint8Array` shape for the
  TypeScript version in use (6.18.0).
- Relation-join JSON aggregation preserves `BigInt` values above
  `Number.MAX_SAFE_INTEGER` on PostgreSQL (7.3.0) and on MySQL and CockroachDB
  (7.4.0) by casting them to text before parsing.
- `Prisma.DbNull` no longer becomes `{}` in bundles, `unixepoch-ms`
  timestamps no longer become `Invalid Date`, and cursor pagination works on
  `@db.Date` columns (7.5.0).
- Current-time defaults are generated lazily, avoiding eager `new Date()`
  evaluation errors in cached Next.js components (7.6.0).
- The `prisma-client` generator again exports its group-by payload types
  (7.6.0).
- PostgreSQL JSON-list equality uses the correct `jsonb` cast; SQL Server
  parameterized strings receive `VARCHAR` casts; parameter-limit checks raise
  `P2029` without rejecting valid queries; and mapped enum query parameters
  use their database `@map` values (7.8.0).
