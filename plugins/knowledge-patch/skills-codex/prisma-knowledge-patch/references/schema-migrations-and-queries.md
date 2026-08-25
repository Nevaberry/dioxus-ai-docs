# Schema, migrations, and queries

## Schema language capabilities

### Full-text search, comments, IDs, and SQLite

`fullTextIndex` and `fullTextSearch` are GA and no longer require preview flags
(6.0.0). Prisma Schema Language accepts `/* ... */` block comments as well as
`//` line comments (6.1.0).

SQLite supports Prisma `Json` and enum fields (6.2.0). String IDs can use the
26-character, lexicographically sortable `ulid()` default:

```prisma
model Event {
  id   String @id @default(ulid())
  data Json
  role Role
}

enum Role {
  Customer
  Admin
}
```

### Multi-file and multi-schema layouts

Multi-file schemas became GA in 6.7.0, so remove the former
`prismaSchemaFolder` flag. Projects that were still using that preview in
6.6.0 had to declare their schema directory through `--schema`,
`prisma.schema` in `package.json`, or Prisma Config. Their migrations directory
belongs beside the `.prisma` file that owns the datasource unless Prisma
Config provides independent paths.

PostgreSQL and SQL Server multi-schema support became GA in 6.13.0. List
database schemas on the datasource and assign each model with `@@schema`:

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

### PlanetScale shard keys

With the `shardKeys` preview feature, use `@shardKey` on one field or
`@@shardKey([...])` for a compound PlanetScale shard key (6.10.0). Keep a
compound shard key aligned with the fields in its compound identifier when
that is the intended data model.

## Views and externally managed tables

List externally managed tables in Prisma Config's `tables.external`. Prisma
Migrate ignores them while Prisma Client retains their models (6.13.0).

The initial restricted Preview view surface in 6.13.0 disabled unique
metadata, `findUnique`, cursor pagination, writes, implicit ordering, and view
relationships. In 6.14.0, view fields regained `@unique`; a genuinely unique
field enables relationships, `findUnique`, cursor pagination, and implicit
ordering. Do not assert uniqueness unless the underlying view data guarantees
it.

```prisma
view UserSummary {
  userId Int @unique
}
```

## PostgreSQL extensions and indexes

`postgresqlExtensions` is deprecated. Remove its preview feature and create
extensions in custom migration SQL (6.16.0):

```sh
npx prisma migrate dev --name add-extension --create-only
```

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

The `partialIndexes` preview feature adds `where` predicates to `@@index` and
`@@unique` for PostgreSQL, SQLite, SQL Server, and CockroachDB (7.4.0). It
supports type-safe object predicates and database-specific `raw()` SQL; field-
level `@unique` gained `where` support in 7.4.1.

```prisma
model Post {
  id        Int     @id
  title     String
  published Boolean

  @@index([title], where: { published: true })
}
```

Manually created partial indexes remain intact when the preview flag is off,
and equivalent quoted and unquoted predicates do not trigger needless
recreation (7.5.0). A partial unique index is excluded from DMMF uniqueness
metadata and does not generate a `findUnique` input.

PostgreSQL migration SQL accepts `CREATE INDEX CONCURRENTLY` for indexes that
must be built without blocking writes (7.4.0):

```sql
CREATE INDEX CONCURRENTLY "Post_title_idx" ON "Post" ("title");
```

## Migrations and status

`migrate dev` exits on drift or an unappliable migration instead of offering
an interactive reset; invoke `prisma migrate reset` explicitly when the
destructive operation is intended (6.5.0). Supported automated coding
environments add their own confirmation guard; see the upgrade reference.

An interactive transaction now surfaces database exceptions raised at commit,
including trigger-driven failures (6.3.0). The PlanetScale adapter likewise
propagates `COMMIT` failures instead of reporting false success (7.4.0).

`prisma migrate status` treats a rolled-back migration that remains on disk as
unapplied instead of reporting the schema as current (7.9.0).

## Bulk writes and returned rows

`updateManyAndReturn` updates matching rows and returns their new records on
PostgreSQL, CockroachDB, and SQLite (6.2.0):

```ts
const users = await prisma.user.updateManyAndReturn({
  where: { status: 'pending' },
  data: { status: 'active' },
})
```

Top-level `updateMany()` and `deleteMany()` accept `limit` to bound affected
rows (6.3.0):

```ts
await prisma.user.updateMany({
  where: { status: 'inactive' },
  data: { archived: true },
  limit: 100,
})
```

## Selecting and filtering data

`omit` is GA for per-query and global field exclusion; remove the old
`omitApi` preview flag (6.2.0).

JSON string filters accept `mode: 'insensitive'` with `string_contains`,
`string_starts_with`, and `string_ends_with` (6.4.0). PostgreSQL JSON equality
also supports case-insensitive string matching, and JSON-list equality now uses
the correct `jsonb` cast instead of panicking (7.8.0).

```ts
await prisma.user.findMany({
  where: {
    profile: {
      path: ['name'],
      string_contains: 'Ada',
      mode: 'insensitive',
    },
  },
})
```

## Mapped enums

Prisma 7.0.0 temporarily made generated enum constants use the string supplied
to `@map`. Prisma 7.3.0 reversed that behavior: generated values again use the
schema member name, while `@map` remains the database representation.

```prisma
enum PaymentProvider {
  MixplatSMS @map("mixplat/sms")
}
```

```ts
PaymentProvider.MixplatSMS // "MixplatSMS"
```

When Prisma sends the parameter, it uses the mapped database name (7.8.0).

## Transactions and savepoints

Interactive transactions can nest on SQL databases as of 7.5.0. A nested
`$transaction()` uses the existing engine transaction and savepoints; failure
of the outer transaction rolls back all nested work.

```ts
await prisma.$transaction(async (tx) => {
  await tx.user.create({ data: { email: 'outer@example.com' } })
  await tx.$transaction((nested) =>
    nested.user.create({ data: { email: 'inner@example.com' } }),
  )
  throw new Error('roll back both inserts')
})
```

Cloudflare D1 is different: its savepoint creation, rollback, and release
methods are logged no-ops. Do not assume nested rollback semantics there
(7.8.0).

If interactive transaction startup exceeds `maxWait`, Prisma rolls back the
connection before returning it to the adapter pool (7.9.0), preventing a later
query from inheriting the abandoned transaction.

## Raw SQL validation

`$queryRaw` and `$executeRaw` reject invalid JavaScript `Date` values with a
validation error instead of serializing them as `null` (7.9.0). Validate dates
at input boundaries or catch the query validation error; do not expect a bad
date to be silently stored.

## Introspection and generated metadata

The first `prisma db pull` after 6.3.0 may reorder fields inside generator
blocks once; later pulls retain deterministic order. Generator DMMF exposes
referential-action `onUpdate` data to custom generators in that release.

PostgreSQL introspection recognizes schema-qualified sequence defaults such as
`pg_catalog.nextval('sequence_name'::regclass)` and preserves the corresponding
`@default(autoincrement())` (7.8.0).

## Precision and parameter correctness

Relation joins preserve large `BigInt` values on PostgreSQL (7.3.0) and on
MySQL and CockroachDB (7.4.0). Prisma also avoids lossy MariaDB numeric
conversion, fixes `@db.Date` cursor pagination, correctly reports parameter
limit errors as `P2029`, and applies required SQL Server string casts; see the
client-generation reference for adapter details.
