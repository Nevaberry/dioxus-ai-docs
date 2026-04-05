# Database Adapters

## Adapter Packages vs Direct Connections

Kysely-backed databases (PostgreSQL, MySQL, SQLite, MS SQL) accept a direct connection pool — no adapter package needed. ORM adapters require separate packages:

```ts
// Direct connection (Kysely auto-wraps):
import { Pool } from "pg";
export const auth = betterAuth({ database: new Pool({ connectionString: "..." }) });

// ORM adapters need packages:
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
import { prismaAdapter } from "@better-auth/prisma-adapter";
import { mongodbAdapter } from "@better-auth/mongo-adapter";
```

## Drizzle Adapter: Schema Mapping

Map custom table/field names via `schema` object or config-level `modelName`/`fields`:

```ts
export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg", // or "sqlite" or "mysql"
    schema: { ...schema, user: schema.users },
    usePlural: true,
  }),
});
```

For `experimental.joins`, Drizzle requires relations defined in schema. Run `npx auth@latest generate` to get them.

## MongoDB Adapter: Client for Transactions

Pass both `db` and `client` — without `client`, transactions are disabled:

```ts
const client = new MongoClient("mongodb://localhost:27017/database");
const db = client.db();
export const auth = betterAuth({
  database: mongodbAdapter(db, { client }),
});
```

No schema generation/migration needed for MongoDB.

## MS SQL Support

```ts
export const auth = betterAuth({
  database: { dialect: mssqlDialect, type: "mssql" },
});
```

## Prisma Adapter Gotchas

- **Generate only, no migrate**: `npx auth@latest generate` works, but `migrate` is not supported — use Prisma's own migration tools
- **Prisma 7+**: The `output` field is now required in `schema.prisma`. Import PrismaClient from the configured output path, not `@prisma/client`

## PostgreSQL Non-Default Schema

Set `search_path` to use a custom schema:

```ts
export const auth = betterAuth({
  database: new Pool({
    connectionString: "postgres://user:pass@localhost:5432/db?options=-c search_path=auth",
  }),
});
```

The CLI auto-detects `search_path` and only inspects/creates tables in that schema.

## SQLite: Node.js & Bun Built-in Support

Node.js 22.5+ built-in `node:sqlite` and Bun's `bun:sqlite` both work as direct connections. For Bun, use `bunx --bun auth@latest generate`.

## Bundle Size with `better-auth/minimal`

When using ORM adapters, import from `better-auth/minimal` to exclude bundled Kysely:

```ts
import { betterAuth } from "better-auth/minimal";
import { prismaAdapter } from "better-auth/adapters/prisma";
```

Limitations: no direct database connections, no built-in migrations.

## Custom Database Adapters: `createAdapterFactory`

```ts
import { createAdapterFactory } from "better-auth";

export const myAdapter = (config) =>
  createAdapterFactory({
    config: {
      adapterId: "my-adapter",
      adapterName: "My Adapter",
      supportsJSON: false,
      supportsDates: true,
      supportsBooleans: true,
      supportsNumericIds: true,
      usePlural: false,
      debugLogs: false,
    },
    adapter: ({ schema, getFieldName, getModelName, transformInput, transformOutput, transformWhereClause }) => ({
      create: async ({ model, data, select }) => { /* insert & return row */ },
      update: async ({ model, where, update }) => { /* update & return full row */ },
      updateMany: async ({ model, where, update }) => { /* bulk update */ },
      delete: async ({ model, where }) => { /* delete row */ },
      deleteMany: async ({ model, where }) => { /* bulk delete */ },
      findOne: async ({ model, where, select, join }) => { /* return single row or null */ },
      findMany: async ({ model, where, limit, sortBy, offset, join }) => { /* return array */ },
      count: async ({ model, where }) => { /* return number */ },
      // Optional:
      createSchema: async ({ file, tables }) => { /* generate schema file for CLI */ },
    }),
  });
```

Key: `model` values are pre-transformed to DB names. Missing fields in returned rows are auto-filled from schema. `select` is optimization-only — the factory filters output.

## Adapter Testing: `@better-auth/test-utils` (v1.5+)

Moved from `better-auth/adapters/test` to `@better-auth/test-utils/adapter`:

```ts
import { testAdapter, createTestSuite } from "@better-auth/test-utils/adapter";

const suite = createTestSuite("Normal", ({ test, adapter }) => [
  test("should create a user", async () => { /* ... */ }),
]);

const { execute } = await testAdapter({
  adapter: (options) => myAdapter(/* config */),
  runMigrations: async (options) => { /* run migrations */ },
  tests: [suite()],
  async onFinish() { /* cleanup */ },
});
execute();
```

## Recommended Database Indexes

| Table         | Fields                     | Plugin       |
| ------------- | -------------------------- | ------------ |
| users         | `email`                    |              |
| accounts      | `userId`                   |              |
| sessions      | `userId`, `token`          |              |
| verifications | `identifier`               |              |
| invitations   | `email`, `organizationId`  | organization |
| members       | `userId`, `organizationId` | organization |
| organizations | `slug`                     | organization |
| passkey       | `userId`                   | passkey      |
| twoFactor     | `secret`                   | twoFactor    |
