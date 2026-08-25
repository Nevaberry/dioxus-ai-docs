# Data Model, Storage, and Adapters

## Identifier generation

Use `advanced.database.generateId`; the removed top-level `advanced.generateId` no longer applies. String UUIDs use `"uuid"`, and serial identifiers replace `advanced.database.useNumberId` with `"serial"`. MongoDB can use strings rather than ObjectIDs.

```ts
advanced: { database: { generateId: "uuid" } } // or "serial"
```

The generator may return `false` or `undefined` for selected models to delegate their IDs to the database while generating other model IDs itself. Better Auth exposes serial values as numeric strings.

```ts
advanced: {
  database: {
    generateId: ({ model }) =>
      model === "user" || model === "users"
        ? false
        : crypto.randomUUID(),
  },
}
```

## Database joins

Database joins began behind `experimental.joins` in 1.4.0 and work across adapters. Enabling joins changes the expected schema, so rerun migrations or schema generation.

```ts
export const auth = betterAuth({ experimental: { joins: true } });
```

## Adapter packages and minimal imports

Drizzle, Prisma, Kysely, MongoDB, and memory adapters have independent `@better-auth/*-adapter` packages while remaining re-exported by the main package. A direct adapter import paired with `better-auth/minimal` avoids importing the full distribution.

```ts
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
import { betterAuth } from "better-auth/minimal";

const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
});
```

Custom adapters can provide `createSchema` to the CLI. Better Auth uses Zod 4, and `inferAuth` can derive client types from the auth instance.

## Transactions and lifecycle hooks

Database `create.after`, `update.after`, and `delete.after` hooks execute only after their transaction commits. They cannot make a follow-up write atomic with the original operation; put such work inside the adapter operation or its transaction.

As of 1.7.1, raw `better-sqlite3`, `node:sqlite`, `bun:sqlite`, `mysql2`, and `pg` database instances support native adapter transactions, like explicit `{ db }` and `{ dialect }` forms. This permits transaction-dependent plugins such as SCIM to use quickstart direct-database configuration. PostgreSQL and MySQL test instances support these transactions too.

## Cloudflare D1

Pass a D1 binding directly as `database`. Better Auth detects it and uses D1-native execution, schema introspection, and `batch()` atomicity instead of unsupported interactive transactions.

```ts
export default {
  async fetch(request, env) {
    const auth = betterAuth({ database: env.DB });
    return auth.handler(request);
  },
} satisfies ExportedHandler<{ DB: D1Database }>;
```

## Drizzle schema mapping

The Drizzle adapter expects logical Better Auth model names even when physical tables are renamed. Map tables through adapter `schema`, map auth models with `modelName` and `fields`, or use `usePlural: true` when every table is plural. Physical column names may change while Drizzle property names stay logical.

```ts
database: drizzleAdapter(db, {
  provider: "pg",
  schema: { ...schema, user: schema.users },
})
```

## Kysely dialects

Any Kysely relational dialect may be used, including organization or community dialects beyond the PostgreSQL, MySQL, SQLite, and MS SQL core set. CLI generation and migration are available. MS SQL needs an explicit dialect and type. A directly supplied MySQL pool should use `timezone: "Z"`.

```ts
export const auth = betterAuth({
  database: { dialect, type: "mssql" },
});
```

## SQLite drivers

Supported built-ins include `better-sqlite3`, Node's experimental `node:sqlite` `DatabaseSync` on Node 22.5+, and Bun's `bun:sqlite`. Run CLI commands under Bun with `bunx --bun` so module types are detected.

```ts
export const auth = betterAuth({
  database: new DatabaseSync("database.sqlite"),
});
```

## PostgreSQL schemas

Select a non-default schema through PostgreSQL `search_path` in the URI, pool `options`, or database-user default. Create the schema and grant privileges first. `npx auth migrate` then inspects only that schema and creates auth tables there, ignoring same-named tables elsewhere.

```ts
database: new Pool({
  connectionString:
    "postgres://user:password@localhost:5432/database?options=-c%20search_path%3Dauth",
})
```

## Adapter predicates

Set `mode: "insensitive"` on an individual string `where` clause to request a case-insensitive comparison on any adapter.

```ts
await adapter.findOne({
  model: "user",
  where: [{
    field: "email",
    value: "user@example.com",
    mode: "insensitive",
  }],
});
```

## Migration safety

The Auth CLI refuses to add a required column without a default to an already-populated table. Choose a staged nullable/defaulted migration or backfill path instead of expecting the CLI to apply the unsafe change silently.
