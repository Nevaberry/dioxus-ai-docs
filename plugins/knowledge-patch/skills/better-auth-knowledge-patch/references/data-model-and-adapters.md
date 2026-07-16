# Data Model, Storage, and Adapters

## Identifier generation

Configure primary-key generation under `advanced.database.generateId`. The old top-level `advanced.generateId` is removed. Use `"uuid"` for UUIDs and `"serial"` instead of removed `advanced.database.useNumberId`; MongoDB may use string IDs instead of ObjectIDs.

```ts
advanced: {
  database: { generateId: "uuid" }, // or "serial"
}
```

`generateId` can also be a function that returns `false` or `undefined` for individual models, delegating only those IDs to the database while generating the rest. Better Auth exposes and accepts serial IDs as numeric strings.

```ts
advanced: {
  database: {
    generateId: ({ model }) =>
      model === "user" || model === "users" ? false : crypto.randomUUID(),
  },
}
```

## Experimental joins

`experimental.joins` opts endpoints into database joins. All adapters support the mode. Enabling it changes the expected schema, so rerun migrations or schema generation.

```ts
export const auth = betterAuth({ experimental: { joins: true } });
```

## Schema and type tooling

Better Auth uses Zod 4. A custom adapter may expose `createSchema` for CLI schema generation, and `inferAuth` infers client types from the client instance.

The `AuthClient` helper is available for client typing. Generic `User` and `Session` exports replace removed `InferUser` and `InferSession`.

## Extracted adapter packages

Drizzle, Prisma, Kysely, MongoDB, and memory adapters have independent `@better-auth/*-adapter` packages, while the main package still re-exports them. Pair direct adapter imports with `better-auth/minimal` to avoid pulling the full distribution.

```ts
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
import { betterAuth } from "better-auth/minimal";

const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
});
```

The adapter-test export at `better-auth/adapters/test` is removed. Adapter authors import `testAdapter` and `createTestSuite` from `@better-auth/test-utils/adapter`.

## Cloudflare D1

A D1 binding can be passed directly as `database`. Better Auth auto-detects it and uses native execution, introspection, and `batch()` atomicity instead of unsupported interactive transactions.

```ts
export default {
  async fetch(request, env) {
    const auth = betterAuth({ database: env.DB });
    return auth.handler(request);
  },
} satisfies ExportedHandler<{ DB: D1Database }>;
```

## Drizzle schema mapping

The Drizzle adapter expects logical Better Auth model names even when physical tables are renamed. Map tables through the adapter `schema`, use auth `modelName` and `fields` mappings, or set `usePlural: true` when every table is plural. Physical column names may differ while Drizzle property names remain unchanged.

```ts
database: drizzleAdapter(db, {
  provider: "pg",
  schema: {
    ...schema,
    user: schema.users,
  },
})
```

## Kysely dialects

Better Auth accepts arbitrary Kysely relational dialects, including organization and community dialects beyond the core PostgreSQL, MySQL, SQLite, and MS SQL set. CLI schema generation and migration work with them.

MS SQL requires an explicit dialect object and `type`. When passing a MySQL pool directly, set `timezone: "Z"` so stored times remain consistent.

```ts
export const auth = betterAuth({
  database: {
    dialect,
    type: "mssql",
  },
});
```

## Built-in SQLite drivers

Alongside `better-sqlite3`, Better Auth accepts Node's experimental `node:sqlite` `DatabaseSync` on Node 22.5 or later and Bun's `bun:sqlite` database. Run CLI operations under Bun with `bunx --bun` so module types are recognized.

```ts
export const auth = betterAuth({
  database: new DatabaseSync("database.sqlite"),
});
```

## PostgreSQL non-default schemas

Choose the Better Auth schema through PostgreSQL `search_path`, supplied in the connection URI, pool `options`, or database user's default. The schema must already exist with suitable privileges. `npx auth migrate` then inspects only that schema, ignores same-named tables elsewhere, and creates auth tables there.

```ts
export const auth = betterAuth({
  database: new Pool({
    connectionString:
      "postgres://user:password@localhost:5432/database?options=-c%20search_path%3Dauth",
  }),
});
```

## Adapter predicates

Any adapter can request case-insensitive string comparison by putting `mode: "insensitive"` on an individual `where` clause.

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

## Transaction boundaries

Database `create.after`, `update.after`, and `delete.after` hooks run only after commit. If a follow-up write must be atomic, perform it through the adapter during the main operation rather than in an `after` hook.
