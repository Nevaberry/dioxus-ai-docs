# Schema, migrations, and queries

Use this reference when editing Prisma Schema Language, generating migrations, introspecting a database, selecting query APIs, or reasoning about transaction and index behavior.

## Contents

- [Use current schema-language features](#use-current-schema-language-features)
- [Split schemas and database namespaces](#split-schemas-and-database-namespaces)
- [Manage external tables and views](#manage-external-tables-and-views)
- [Define PlanetScale shard keys](#define-planetscale-shard-keys)
- [Manage PostgreSQL extensions](#manage-postgresql-extensions)
- [Create partial and concurrent indexes](#create-partial-and-concurrent-indexes)
- [Use current query APIs](#use-current-query-apis)
- [Filter JSON correctly](#filter-json-correctly)
- [Handle enums across schema and database names](#handle-enums-across-schema-and-database-names)
- [Compose transactions safely](#compose-transactions-safely)
- [Preserve introspection and generator metadata](#preserve-introspection-and-generator-metadata)

## Use current schema-language features

Full-text indexing and search became generally available in 6.0.0. Remove `fullTextIndex` and `fullTextSearch` from `previewFeatures`; use the features without preview opt-in.

Block comments are valid in Prisma schemas as of 6.1.0:

```prisma
/*
 * Document a group of related fields.
 */
model User {
  id Int @id
}
```

SQLite schemas support Prisma `Json` fields and enums as of 6.2.0:

```prisma
model User {
  id   Int  @id @default(autoincrement())
  role Role
  data Json
}

enum Role {
  Customer
  Admin
}
```

Generate lexicographically sortable, 26-character ULIDs with `ulid()` (6.2.0):

```prisma
model User {
  id String @id @default(ulid())
}
```

## Split schemas and database namespaces

Multi-file Prisma schemas became generally available in 6.7.0, so the `prismaSchemaFolder` Preview flag is no longer required.

Projects still using that Preview layout must provide the schema directory explicitly through `--schema`, `prisma.schema` in `package.json`, or Prisma Config. Beginning with 6.6.0, the `migrations` directory belongs beside the `.prisma` file containing the datasource block. For the common `./prisma/schema` layout, that means moving `./prisma/migrations` to `./prisma/schema/migrations` unless current Prisma Config gives an independent path.

```sh
npx prisma migrate dev --schema ./prisma/schema
```

Current Prisma Config can specify schema, migrations, views, and TypedSQL paths independently; see the configuration reference.

Multi-schema support for PostgreSQL and SQL Server became generally available in 6.13.0. List database namespaces on the datasource and assign each schema object with `@@schema`:

```prisma
datasource db {
  provider = "postgresql"
  schemas  = ["base", "shop"]
}

model User {
  id Int @id

  @@schema("base")
}
```

The datasource URL shown in older examples belongs in Prisma Config in current projects.

## Manage external tables and views

List externally managed tables under `tables.external` in Prisma Config (6.13.0). Prisma Client keeps their models queryable, while Prisma Migrate ignores them:

```ts
import { defineConfig } from 'prisma/config'

export default defineConfig({
  tables: {
    external: ['users'],
  },
})
```

View client capabilities changed in two steps:

- In 6.13.0, Preview view definitions lost ID, index, and unique attributes. Without a trustworthy unique key, Prisma disabled `findUnique`, cursor pagination, writes, implicit ordering, and relationships.
- In 6.14.0, view fields regained `@unique`. A declared unique field enables relationships, `findUnique`, cursor pagination, and implicit ordering.

```prisma
view UserSummary {
  userId Int @unique
}
```

Only declare `@unique` if the underlying view actually guarantees uniqueness. View writes remain inappropriate unless the current connector explicitly supports the intended operation.

## Define PlanetScale shard keys

Native PlanetScale sharding entered Preview in 6.10.0. Enable `shardKeys`, use `@shardKey` for a field, and use `@@shardKey([...])` for a compound key:

```prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["shardKeys"]
}

model User {
  id String @id @default(uuid()) @shardKey
}

model Customer {
  country    String
  customerId String

  @@id([country, customerId])
  @@shardKey([country, customerId])
}
```

Adapt the generator to `prisma-client` for a current project while retaining the Preview feature only if the installed release still requires it.

## Manage PostgreSQL extensions

`postgresqlExtensions` is deprecated as of 6.16.0. Remove the Preview flag and manage extensions in migration SQL:

```sh
npx prisma migrate dev --name add-extension --create-only
```

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

Prisma Postgres `pgvector` support was Early Access in 6.13.0, but Prisma ORM did not yet expose native vector operations. Enable it through a custom migration and query it through TypedSQL for that release line.

## Create partial and concurrent indexes

The `partialIndexes` Preview feature adds `where` predicates to `@@index` and `@@unique` for PostgreSQL, SQLite, SQL Server, and CockroachDB, with migration and introspection support (7.4.0). Predicates can be type-safe object expressions or database-specific `raw()` SQL. Patch 7.4.1 also supports `where` on field-level `@unique`.

```prisma
generator client {
  provider        = "prisma-client"
  output          = "../generated/prisma"
  previewFeatures = ["partialIndexes"]
}

model Post {
  id        Int     @id
  title     String
  published Boolean

  @@index([title], where: { published: true })
}
```

Migration and client behavior was tightened in 7.5.0:

- Preserve manually created partial indexes when the Preview feature is disabled.
- Treat equivalent quoted and unquoted predicates as the same instead of recreating the index.
- Exclude partial unique indexes from DMMF uniqueness metadata, so they do not incorrectly generate `findUnique` inputs.

PostgreSQL migration scripts accept `CREATE INDEX CONCURRENTLY` as of 7.4.0, allowing index creation without blocking writes:

```sql
CREATE INDEX CONCURRENTLY "Post_title_idx" ON "Post" ("title");
```

## Use current query APIs

Exclude fields with `omit`, generally available since 6.2.0, either per query or globally through the `PrismaClient` constructor. Remove the former `omitApi` Preview feature.

```ts
const users = await prisma.user.findMany({
  omit: { password: true },
})
```

Use `updateManyAndReturn` to update and return records instead of receiving only an affected-row count (6.2.0). It is supported for PostgreSQL, CockroachDB, and SQLite:

```ts
const users = await prisma.user.updateManyAndReturn({
  where: { email: { contains: 'prisma.io' } },
  data: { role: 'ADMIN' },
})
```

Top-level `updateMany()` and `deleteMany()` accept `limit` as of 6.3.0:

```ts
await prisma.user.updateMany({
  where: { status: 'inactive' },
  data: { archived: true },
  limit: 100,
})
```

The parameter layer in 7.8.0 correctly:

- Uses the mapped database value for enum parameters.
- Raises `P2029` for actual parameter-limit violations without rejecting valid queries.
- Adds required `VARCHAR` casts to parameterized SQL Server strings.

## Filter JSON correctly

Case-insensitive JSON string filtering became available in 6.4.0. Combine `mode: 'insensitive'` with `string_contains`, `string_starts_with`, or `string_ends_with` at a JSON path:

```ts
await prisma.user.findMany({
  where: {
    pets: {
      path: ['favorites', 'catBreed'],
      string_contains: 'Van',
      mode: 'insensitive',
    },
  },
})
```

PostgreSQL JSON equality fixes in 7.8.0 use the correct `jsonb` cast for JSON-list equality and support case-insensitive equality for JSON string fields:

```ts
await prisma.item.findMany({
  where: { jsonListField: { equals: ['one', 'two'] } },
})

await prisma.item.findMany({
  where: { jsonField: { equals: 'VALUE', mode: 'insensitive' } },
})
```

## Handle enums across schema and database names

Enum-member mapping changed during the current architecture transition:

- In 7.0.0, generated constants and query values initially used the string supplied to `@map`.
- In 7.3.0, generated enum values returned to the Prisma schema member name; `@map` continues to control only the database representation.

```prisma
enum PaymentProvider {
  MixplatSMS @map("mixplat/sms")
}
```

```ts
PaymentProvider.MixplatSMS // "MixplatSMS"
```

Use the generated schema-side constant in application code. Prisma parameterization sends the database-side mapped value where required.

## Compose transactions safely

Interactive transactions now surface database exceptions raised during commit, including trigger-related failures fixed in 6.3.0. Always handle rejection from the entire `$transaction()` call rather than assuming successful callback completion guarantees a successful commit.

Nested interactive transactions on SQL databases are supported through savepoints as of 7.5.0. Prisma reuses the open engine transaction and tracks nesting depth:

```ts
await prisma.$transaction(async (tx) => {
  await tx.user.create({ data: { email: 'outer@example.com' } })

  await tx.$transaction(async (nested) => {
    await nested.user.create({ data: { email: 'inner@example.com' } })
  })

  throw new Error('roll back both inserts')
})
```

If the outer transaction fails, nested work rolls back with it. Commit failures from the PlanetScale adapter are propagated as of 7.4.0.

D1 is different: `createSavepoint`, `rollbackToSavepoint`, and `releaseSavepoint` are logged no-ops as of 7.8.0. Do not rely on nested rollback behavior there.

## Preserve introspection and generator metadata

`prisma db pull` orders fields inside `generator` blocks deterministically as of 6.3.0. The first pull after upgrading may reorder them once; subsequent pulls preserve the stable order.

The DMMF returned by `@prisma/generator-helper` includes `onUpdate` referential-action data as of 6.3.0, allowing custom generators to inspect update behavior.

PostgreSQL introspection recognizes schema-qualified sequence defaults such as `pg_catalog.nextval('sequence_name'::regclass)` as of 7.8.0. It preserves the corresponding `@default(autoincrement())` instead of dropping it.
