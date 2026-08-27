# Data Model, Storage, and Adapters

## Identifier generation

`advanced.database.generateId` selects `"uuid"` or `"serial"` generation and replaces the removed top-level `advanced.generateId` and `useNumberId` settings (since 1.4.0). A callback may return `false` or `undefined` for selected models to delegate their IDs to the database. Serial values are exposed and accepted as numeric strings. MongoDB may use string IDs instead of ObjectIDs.

```ts
advanced: {
  database: {
    generateId: ({ model }) =>
      model === "user" || model === "users" ? false : crypto.randomUUID(),
  },
}
```

## Join-backed schema

`experimental.joins: true` enabled join-backed endpoints in 1.4.0 across all adapters. Rerun migration or schema generation after enabling it. The organization multi-team change also removes `teamId` from `member` and adds the required `teamMembers` join table (since 1.3.0).

## Adapter packages and minimal imports

Drizzle, Prisma, Kysely, MongoDB, and memory adapters have independent `@better-auth/*-adapter` packages (since 1.5-guide), while the main package still re-exports them. Pair direct imports with `better-auth/minimal` to avoid importing the full distribution.

```ts
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
import { betterAuth } from "better-auth/minimal";

const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
});
```

## Native Cloudflare D1

Pass a D1 binding directly as `database`. Better Auth auto-detects it and uses native execution, introspection, and `batch()` atomicity rather than unsupported interactive transactions.

```ts
export default {
  async fetch(request, env) {
    const auth = betterAuth({ database: env.DB });
    return auth.handler(request);
  },
} satisfies ExportedHandler<{ DB: D1Database }>;
```

## Native transactions for direct instances

Raw `better-sqlite3`, `node:sqlite`, `bun:sqlite`, `mysql2`, and `pg` objects passed directly as `database` support native adapter transactions (since 1.7.1), matching explicit `{ db }` and `{ dialect }` forms. Transaction-dependent plugins such as SCIM therefore work with quickstart direct-database configuration; PostgreSQL and MySQL test instances also support transactions.

## Drizzle schema mapping

The Drizzle adapter receives logical Better Auth model names even when physical tables are renamed. Map tables through adapter `schema`, auth `modelName` and `fields`, or `usePlural: true`. Physical column names may change while Drizzle property names remain unchanged.

```ts
database: drizzleAdapter(db, {
  provider: "pg",
  schema: { ...schema, user: schema.users },
})
```

## Kysely dialects

Any Kysely dialect is accepted, including organization and community dialects beyond the PostgreSQL, MySQL, SQLite, and MS SQL core set; CLI generation and migration are available. MS SQL needs an explicit dialect and type. A directly passed MySQL pool should use `timezone: "Z"`.

```ts
database: { dialect, type: "mssql" }
```

## Built-in SQLite drivers

Besides `better-sqlite3`, Better Auth accepts Node's experimental `node:sqlite` `DatabaseSync` on Node 22.5+ and Bun's `bun:sqlite` database. Run CLI operations under Bun with `bunx --bun` so module types are recognized.

## PostgreSQL non-default schemas

Set PostgreSQL `search_path` in the URI, pool `options`, or database-user default. Create the schema and privileges first. `npx auth migrate` then inspects only that schema, ignores same-named tables elsewhere, and creates auth tables there.

```ts
database: new Pool({
  connectionString:
    "postgres://user:password@localhost:5432/database?options=-c%20search_path%3Dauth",
})
```

## Schema and type tooling

Better Auth uses Zod 4. A custom adapter may supply `createSchema` to the CLI, and `inferAuth` derives server types from a client (since 1.3.0). `getMigrations` is imported from `better-auth/db/migration`, not the package root.

## Transaction hook timing

Database `create.after`, `update.after`, and `delete.after` hooks run only after the transaction commits. Atomic follow-up writes must occur in the adapter during the main operation.
