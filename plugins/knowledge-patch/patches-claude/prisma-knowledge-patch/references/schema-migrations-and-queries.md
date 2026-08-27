# Schema, migrations, and queries

## Use current schema-language features

Full-text index and search features are GA in Prisma 6; remove
`fullTextIndex` and `fullTextSearch` from `previewFeatures` (6.0.0). Prisma
Schema Language also accepts `/* ... */` block comments in addition to `//`
line comments (6.1.0).

SQLite schemas support `Json` fields and enums (6.2.0). String fields can use
`ulid()` for automatic 26-character, lexicographically sortable ULIDs:

```prisma
model User {
  id   String @id @default(ulid())
  role Role
  data Json
}

enum Role {
  Customer
  Admin
}
```

Multi-file Prisma schemas became GA in 6.7.0, removing the old
`prismaSchemaFolder` preview flag. PostgreSQL and SQL Server multi-schema
support became GA in 6.13.0; declare namespaces on the datasource and use
`@@schema` on each model:

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

PlanetScale shard keys entered Preview in 6.10.0. With the `shardKeys`
preview feature, use `@shardKey` for a single field or `@@shardKey([...])` for
a compound key.

## Keep multi-file paths and migrations explicit

With the earlier `prismaSchemaFolder` preview workflow, projects had to supply
the schema directory through `--schema`, `prisma.schema` in `package.json`, or
Prisma Config. Migrations belonged beside the `.prisma` file containing the
datasource, so the implicit `prisma/schema` layout required
`prisma/schema/migrations` (6.6.0).

Current Prisma Config can give schema, migration, view, and TypedSQL locations
independent paths. Prefer those explicit paths to relying on inference.

## Manage destructive and rolled-back migrations safely

`prisma migrate dev` no longer offers an interactive reset when it sees drift
or cannot apply a migration. It exits; run `prisma migrate reset` explicitly
only when destructive reset is intended (6.5.0).

Supported automated coding environments add a confirmation checkpoint for
destructive resets, including forced resets (6.15.0). The checkpoint also
covers `prisma db push --accept-data-loss`, recognizes `AI_AGENT` and `AGENT`
environment conventions, and is used on Linux (7.9.0). The MCP surface does
not provide a reset shortcut.

Since 7.9.0, `prisma migrate status` reports a rolled-back migration that
remains on disk as unapplied rather than saying the schema is current.

## Manage PostgreSQL extensions and indexes

`postgresqlExtensions` is deprecated. Remove its preview flag, create an empty
migration, and put extension SQL in the migration file (6.16.0):

```sh
npx prisma migrate dev --name add-extension --create-only
```

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

The `partialIndexes` preview feature adds `where` predicates to `@@index` and
`@@unique` for PostgreSQL, SQLite, SQL Server, and CockroachDB, including
migration and introspection support. Predicates can be typed object expressions
or provider-specific `raw()` SQL; 7.4.1 also added `where` to field-level
`@unique` (7.4.0).

```prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["partialIndexes"]
}

model Post {
  id        Int     @id
  title     String
  published Boolean

  @@index([title], where: { published: true })
}
```

Migration behavior was tightened in 7.5.0: manually created partial indexes
remain when the preview feature is disabled, and semantically equivalent
quoted and unquoted predicates do not trigger recreation. Partial unique
indexes are excluded from DMMF uniqueness metadata, so no incorrect
`findUnique` input is generated.

PostgreSQL migration SQL can use `CREATE INDEX CONCURRENTLY` to build an index
without blocking writes (7.4.0):

```sql
CREATE INDEX CONCURRENTLY "Post_title_idx" ON "Post" ("title");
```

## Model externally managed tables and views

Use top-level `tables.external` to keep tables queryable in Prisma Client while
excluding them from Prisma Migrate (6.13.0):

```ts
export default defineConfig({
  tables: { external: ['users'] },
})
```

The initial 6.13.0 SQL-view Preview surface removed IDs, indexes, unique
attributes, `findUnique`, cursor pagination, writes, implicit ordering, and
relationships. Since 6.14.0, a view field can use `@unique`; genuine uniqueness
enables `findUnique`, cursor pagination, implicit ordering, and relationships.
Do not claim uniqueness unless the view data guarantees it.

```prisma
view UserSummary {
  userId Int @unique
}
```

## Apply enum mapping correctly

Prisma 7.0.0 initially made generated enum constants and query values use the
string supplied to `@map`. Prisma 7.3.0 reversed that behavior: generated
values again use the schema member name, while `@map` remains the database
representation.

```prisma
enum PaymentProvider {
  MixplatSMS @map("mixplat/sms")
}
```

```ts
PaymentProvider.MixplatSMS // "MixplatSMS"
```

Database parameters still use the mapped database name; parameterization was
corrected in 7.8.0. Use the generated schema member in application code.

## Use bulk mutation and omission APIs

`omit` is GA and works per query or globally from the client constructor;
remove the former `omitApi` preview flag (6.2.0).

`updateManyAndReturn` updates matching rows and returns their resulting
records on PostgreSQL, CockroachDB, and SQLite (6.2.0):

```ts
const users = await prisma.user.updateManyAndReturn({
  where: { email: { contains: 'prisma.io' } },
  data: { role: 'ADMIN' },
})
```

Top-level `updateMany` and `deleteMany` accept `limit` to cap affected records
(6.3.0).

## Filter JSON values safely

JSON string filters support `mode: 'insensitive'` with `string_contains`,
`string_starts_with`, and `string_ends_with` at a JSON path (6.4.0).

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

PostgreSQL JSON-list equality uses the proper `jsonb` cast, and case-
insensitive equality works for JSON string fields (7.8.0):

```ts
await prisma.item.findMany({
  where: { jsonListField: { equals: ['one', 'two'] } },
})

await prisma.item.findMany({
  where: { jsonField: { equals: 'VALUE', mode: 'insensitive' } },
})
```

## Handle transaction boundaries and raw values

Interactive transactions surface database exceptions raised during commit,
including trigger-related failures (6.3.0). Since 7.5.0, SQL interactive
transactions can nest by calling `$transaction()` on the transaction client;
Prisma reuses the engine transaction and tracks nesting through savepoints.
An outer rollback rolls back nested work.

```ts
await prisma.$transaction(async (tx) => {
  await tx.user.create({ data: { email: 'outer@example.com' } })
  await tx.$transaction((nested) =>
    nested.user.create({ data: { email: 'inner@example.com' } }),
  )
})
```

D1 savepoints are logged no-ops and provide no rollback semantics (7.8.0).
PlanetScale commit failures propagate to callers (7.4.0). A transaction whose
startup exceeds `maxWait` is rolled back before its connection returns to the
pool (7.9.0).

`$queryRaw` and `$executeRaw` reject an invalid `Date` with a validation error
instead of serializing it as `null` (7.9.0). Validate or catch bad inputs.

## Expect stable introspection output

`prisma db pull` orders generator-block fields deterministically; the first
pull after upgrading may reorder them once (6.3.0). PostgreSQL introspection
preserves schema-qualified sequence defaults such as
`pg_catalog.nextval('sequence_name'::regclass)` as
`@default(autoincrement())` (7.8.0).
