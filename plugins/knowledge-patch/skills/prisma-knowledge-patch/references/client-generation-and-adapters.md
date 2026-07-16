# Client generation and driver adapters

Use this reference when selecting a generator, constructing `PrismaClient`, configuring a driver adapter, targeting a JavaScript runtime, or diagnosing generated-client and adapter behavior.

## Contents

- [Generate application-owned client code](#generate-application-owned-client-code)
- [Use the Query Compiler architecture](#use-the-query-compiler-architecture)
- [Construct the client with an explicit connection](#construct-the-client-with-an-explicit-connection)
- [Choose runtime and compiler output](#choose-runtime-and-compiler-output)
- [Configure individual adapters](#configure-individual-adapters)
- [Account for client correctness changes](#account-for-client-correctness-changes)
- [Tune query caching](#tune-query-caching)

## Generate application-owned client code

The `prisma-client` generator began emitting multiple generated files instead of one large `index.d.ts` in 6.7.0, avoiding editor and autocomplete failures for large schemas. It became Preview in 6.12.0 and generally available in 6.16.0. It emits ESM-compatible, application-owned code by default and requires an explicit output directory.

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

Import from the generated output rather than assuming `@prisma/client`:

```ts
import { PrismaClient } from './generated/prisma/client'
```

Package installation no longer runs generation, and migration commands no longer generate or seed as side effects (7.0.0). Add explicit steps wherever deployment or development previously relied on those behaviors:

```sh
npx prisma generate
npx prisma db seed
```

If an older project retains `prisma-client-js` with a custom `output`, install `@prisma/client-runtime-utils`. The legacy generator remains relevant to compatibility work, but new projects default to `prisma-client`.

`prisma generate` can run under Bun without a separate Node.js installation as of 6.6.0. Very large schemas are handled by the CLI's streaming parser; see the tooling reference for that behavior.

## Use the Query Compiler architecture

The Rust-free path replaces the standalone Query Engine with a TypeScript Query Compiler and database driver adapter.

- In 6.7.0, the Early Access path required both `queryCompiler` and `driverAdapters` in `previewFeatures`.
- In 6.9.0, PostgreSQL and SQLite support reached Preview.
- In 6.10.0, SQL Server and PlanetScale reached Preview; use `@prisma/adapter-mssql` or `@prisma/adapter-planetscale`.
- In 6.11.0, Preview support expanded to MySQL, MariaDB, Neon, and CockroachDB.
- In 6.16.0, the Query Compiler and driver-adapter architecture became generally available, including use with Prisma Accelerate and Prisma Postgres. The two Preview flags are no longer needed.

For a current `prisma-client` generator, select the client engine when an explicit setting is useful:

```prisma
generator client {
  provider   = "prisma-client"
  output     = "../src/generated/prisma"
  engineType = "client"
}
```

The legacy library and binary engines, Data Proxy engine, old Accelerate engine, and React Native engine were removed in 7.0.0. Do not set `engineType = "library"` or `engineType = "binary"`, and remove old engine-control environment variables during an upgrade. Accelerate remains available through its connection URL rather than as a legacy engine selection.

## Construct the client with an explicit connection

With the default generator, `new PrismaClient()` and `new PrismaClient({})` are invalid as of 7.0.0. Pass an adapter, or pass `accelerateUrl` when using Prisma Accelerate. The former `datasources` and `datasourceUrl` constructor overrides are removed.

```ts
import { PrismaPg } from '@prisma/adapter-pg'
import { PrismaClient } from './generated/prisma/client'

const adapter = new PrismaPg(process.env.DATABASE_URL!)
const prisma = new PrismaClient({ adapter })
```

For Accelerate:

```ts
const prisma = new PrismaClient({
  accelerateUrl: process.env.PRISMA_ACCELERATE_URL!,
})
```

Existing Accelerate connection strings remain usable. Prisma Accelerate is the dedicated caching layer, while Prisma Postgres supplies native connection pooling.

Adapter export casing was normalized in 7.0.0. Use these names:

| Old export | Current export |
| --- | --- |
| `PrismaBetterSQLite3` | `PrismaBetterSqlite3` |
| `PrismaD1HTTP` | `PrismaD1Http` |
| `PrismaLibSQL` | `PrismaLibSql` |
| `PrismaNeonHTTP` | `PrismaNeonHttp` |

The Preview `@prisma/adapter-better-sqlite3` package first provided a JavaScript-native SQLite connection in 6.7.0:

```ts
import { PrismaBetterSqlite3 } from '@prisma/adapter-better-sqlite3'
import { PrismaClient } from './generated/prisma/client'

const adapter = new PrismaBetterSqlite3({ url: 'file:./prisma/dev.db' })
const prisma = new PrismaClient({ adapter })
```

## Choose runtime and compiler output

Deno moved away from the `deno` Preview flag on `prisma-client-js` in 6.8.0. Generate an explicit Deno target instead:

```prisma
generator client {
  provider = "prisma-client"
  output   = "../src/generated/prisma"
  runtime  = "deno"
}
```

Runtime names were consolidated in 6.15.0:

- Replace `node` with `nodejs`.
- Replace `deno-deploy` with `deno`.
- Replace `vercel` with `vercel-edge`.
- Use `nodejs`, `deno`, `bun`, `workerd` (alias `cloudflare`), `vercel-edge` (alias `edge-light`), or `react-native` where supported by that release line.

The `react-native` runtime setting was then removed from current Prisma Config/generation behavior in 7.0.0 along with the React Native client engine. Do not carry it into a current upgrade.

For `prisma-client-js` compatibility only, the legacy `/wasm` import became `/edge` in 7.0.0. This entry point targets edge JavaScript runtimes, not Prisma Accelerate.

Choose a Query Compiler build with `compilerBuild` (7.3.0):

```prisma
generator client {
  provider      = "prisma-client"
  output        = "../src/generated/prisma"
  compilerBuild = "small"
}
```

`fast` is the default and favors runtime speed with a larger compiler. `small` reduces compiler size at the cost of speed.

## Configure individual adapters

### PostgreSQL

`@prisma/adapter-pg` accepts a connection string directly as of 7.6.0:

```ts
const adapter = new PrismaPg(process.env.DATABASE_URL!)
```

Its `statementNameGenerator` option supports custom prepared-statement names and enables integration with `pg` statement caching. The package includes `@types/pg` directly as of 7.5.0, so consumers no longer need separate driver-type setup.

### MariaDB

`@prisma/adapter-mariadb` switched to the binary MySQL protocol in 7.5.0 to prevent lossy numeric conversions. In 7.6.0, `useTextProtocol` was added for applications that explicitly need the text protocol. MariaDB statement caching is disabled by default to avoid a reported memory leak.

### SQL Server

`@prisma/adapter-mssql` accepts Microsoft Entra ID authentication parameters as of 6.17.0, including the default Azure credential chain:

```ts
const adapter = new PrismaMssql({
  server: 'localhost',
  port: 1433,
  database: 'app',
  authentication: {
    type: 'azure-active-directory-default',
  },
  options: { encrypt: true },
})
```

### D1

The D1 adapter treats `createSavepoint`, `rollbackToSavepoint`, and `releaseSavepoint` as logged no-ops as of 7.8.0, matching its top-level transaction behavior. Never assume nested transaction rollback semantics on D1.

For CLI schema operations against remote D1, see the configuration reference.

## Account for client correctness changes

- Generated `Bytes` types select the appropriate `Uint8Array` shape for the installed TypeScript version (6.18.0).
- PostgreSQL relation-join JSON aggregation preserves `BigInt` values above `Number.MAX_SAFE_INTEGER` by casting them to text before parsing (7.3.0). The same protection covers MySQL and CockroachDB as of 7.4.0.
- `Prisma.DbNull` no longer serializes to `{}` in bundles such as Next.js, `unixepoch-ms` values no longer become `Invalid Date`, and cursor pagination works with `@db.Date` columns (7.5.0).
- Current timestamps are generated lazily instead of calling `new Date()` synchronously, avoiding dynamic-usage errors in Next.js cached components (7.6.0).
- The `prisma-client` generator again exports group-by payload types (7.6.0).
- PlanetScale adapter errors raised by `COMMIT` are propagated rather than allowing a failed commit to appear successful (7.4.0).
- SQL Server parameterized strings receive their required `VARCHAR` casts, mapped enum parameters use their database-side `@map` names, and parameter-limit checks raise `P2029` only when appropriate (7.8.0).

## Tune query caching

`createMany` queries stopped populating the query cache in 7.6.0, preventing high-volume inserts from bloating it and potentially crashing Node.js.

Set `queryPlanCacheMaxSize` on `PrismaClient` to tune the remaining plan cache (7.8.0):

```ts
const prisma = new PrismaClient({
  adapter,
  queryPlanCacheMaxSize: 0,
})
```

- Omit the option to use the default.
- Set it to `0` to disable caching.
- Increase it for workloads with many distinct query shapes.
- Lower it to trade repeat-query speed for reduced memory use.
