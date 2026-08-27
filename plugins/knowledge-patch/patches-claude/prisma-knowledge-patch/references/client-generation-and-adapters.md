# Client generation and driver adapters

## Choose the current generated-client architecture

The application-owned `prisma-client` generator reached Preview in 6.12.0 and
GA in 6.16.0. It requires an explicit output directory, emits ESM-compatible
code by default, splits output across files to keep large schemas responsive,
and can select the runtime, module format, generated-file extension, and import
extension. The split-file output originated in 6.7.0.

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

Deno moved off the `deno` flag on `prisma-client-js` in 6.8.0; use
`provider = "prisma-client"`, an explicit output, and `runtime = "deno"`.
Generation also works under Bun without a separate Node.js installation
(6.6.0). The CLI's Bun-aware initialization is covered in the tooling
reference.

Runtime names were consolidated in 6.15.0: use `nodejs` instead of `node`,
`deno` instead of `deno-deploy`, and `vercel-edge` instead of `vercel`.
Supported aliases include `cloudflare` for `workerd` and `edge-light` for
`vercel-edge`. Prisma 7 removed `generator.runtime = "react-native"`.

Use `compilerBuild = "fast"` for the default, speed-oriented compiler or
`compilerBuild = "small"` for a smaller, slower compiler (7.3.0).

## Follow the Query Compiler transition

The Rust-free architecture began in Early Access in 6.7.0 with both
`queryCompiler` and `driverAdapters` preview flags. It reached Preview for
PostgreSQL and SQLite in 6.9.0, SQL Server and PlanetScale in 6.10.0, and
MySQL/MariaDB, Neon, and CockroachDB in 6.11.0.

In 6.16.0 the TypeScript Query Compiler and driver adapters became GA, including
use with Prisma Accelerate and Prisma Postgres. With `prisma-client`, that
release selected the architecture using `engineType = "client"`; the old
preview flags were no longer required. Prisma 7 then removed the legacy
library, binary, Data Proxy, Accelerate, and React Native client engines and
their engine-selection controls. Use a current generated client and adapter
rather than retaining old engine configuration.

## Construct a client with an explicit connection

Since 7.0.0, the generated client cannot be constructed with
`new PrismaClient()` or `new PrismaClient({})`. Pass a driver adapter, or pass
`accelerateUrl` for Prisma Accelerate. The old `datasources` and
`datasourceUrl` constructor options are removed.

```ts
import { PrismaPg } from '@prisma/adapter-pg'
import { PrismaClient } from './generated/prisma/client'

const adapter = new PrismaPg(process.env.DATABASE_URL!)
const prisma = new PrismaClient({ adapter })
```

`@prisma/adapter-pg` accepts a connection string directly as of 7.6.0. It also
supports `statementNameGenerator` for custom prepared-statement names and
`pg` statement caching. Its package has included `@types/pg` directly since
7.5.0.

If `prisma-client-js` is temporarily retained with a custom `output`, install
`@prisma/client-runtime-utils` (7.0.0). The old `/wasm` entry point for that
generator became `/edge`; it targets edge JavaScript runtimes, not Accelerate.

## Import adapter exports with current casing

Prisma 7 normalized these export names (7.0.0):

| Old | Current |
| --- | --- |
| `PrismaBetterSQLite3` | `PrismaBetterSqlite3` |
| `PrismaD1HTTP` | `PrismaD1Http` |
| `PrismaLibSQL` | `PrismaLibSql` |
| `PrismaNeonHTTP` | `PrismaNeonHttp` |

The `better-sqlite3` adapter first appeared in Preview in 6.7.0. Current code
should use the normalized export:

```ts
import { PrismaBetterSqlite3 } from '@prisma/adapter-better-sqlite3'
import { PrismaClient } from './generated/prisma/client'

const adapter = new PrismaBetterSqlite3({ url: 'file:./prisma/dev.db' })
const prisma = new PrismaClient({ adapter })
```

## Configure database-specific behavior

### SQL Server authentication

`@prisma/adapter-mssql` accepts Microsoft Entra ID authentication, including
the default Azure credential chain with
`type: 'azure-active-directory-default'` (6.17.0).

```ts
const adapter = new PrismaMssql({
  server: 'localhost',
  port: 1433,
  database: 'mydb',
  authentication: { type: 'azure-active-directory-default' },
  options: { encrypt: true },
})
```

### MariaDB protocols and caching

The MariaDB adapter switched to the binary MySQL protocol in 7.5.0 to preserve
number fidelity. Since 7.6.0, `useTextProtocol` can select the text protocol;
statement caching is disabled by default to avoid a reported leak.

### D1 transaction limits

The D1 adapter treats top-level transactions as non-transactional and, since
7.8.0, logs `createSavepoint`, `rollbackToSavepoint`, and
`releaseSavepoint` as no-ops instead of issuing SQL. Never rely on D1 nested
transactions for rollback semantics.

## Size and protect the query-plan cache

`PrismaClient` accepts `queryPlanCacheMaxSize` as of 7.8.0. Omit it for the
default, set it to `0` to disable caching, raise it for many distinct query
shapes, or lower it to save memory.

```ts
const prisma = new PrismaClient({ adapter, queryPlanCacheMaxSize: 0 })
```

`createMany` queries no longer enter the query cache as of 7.6.0, preventing
bulk operations from filling it and exhausting Node.js memory.

## Account for adapter and generated-client correctness fixes

- Relation joins preserve `BigInt` values above `Number.MAX_SAFE_INTEGER` by
  casting them to text inside JSON aggregation: PostgreSQL since 7.3.0, and
  MySQL and CockroachDB since 7.4.0.
- PlanetScale adapter transactions propagate commit failures (7.4.0).
- `Prisma.DbNull` survives bundling, `unixepoch-ms` timestamps produce valid
  dates, and cursor pagination works with `@db.Date` columns (7.5.0).
- Generated current timestamps are evaluated lazily, avoiding dynamic-usage
  errors in cached Next.js components, and group-by payload types are exported
  again by `prisma-client` (7.6.0).
- Query parameter handling uses mapped enum database names, reports parameter
  overflow as `P2029` without rejecting valid queries, and applies required
  `VARCHAR` casts for SQL Server strings (7.8.0).
- A transaction that exceeds `maxWait` during startup explicitly rolls back
  before its adapter connection returns to the pool (7.9.0).
- Generated `Bytes` types select the correct `Uint8Array` shape for the active
  TypeScript version (6.18.0).
- Generator DMMF includes referential-action `onUpdate` data for custom
  generators (6.3.0).
