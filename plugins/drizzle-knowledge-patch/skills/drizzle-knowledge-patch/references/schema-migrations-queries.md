# Schema, Migrations & Query Features

## Breaking: `.generatedAlwaysAs()` Signature Change (beta.12)

`.generatedAlwaysAs()` now only accepts `` sql`...` `` or `` () => sql`...` ``. Raw strings are no longer accepted.

```ts
// Before (no longer works)
generatedAlwaysAs("col1 + col2")

// After
generatedAlwaysAs(sql`col1 + col2`)
generatedAlwaysAs(() => sql`${table.col1} + ${table.col2}`)
```

## `drizzle-kit check` Command (beta.16)

Detects non-commutative migrations in team workflows. When multiple developers generate migrations from the same base schema on different branches, `check` finds conflicts (e.g., two branches altering the same column). Available for PostgreSQL and MySQL.

```bash
npx drizzle-kit check
```

## `.comment()` for SQL Comments / sqlcommenter (beta.19)

Add metadata tags to queries as SQL comments. Useful for database traffic control (e.g., PlanetScale). Works with PostgreSQL and MySQL. Cannot be used with prepared statements.

```ts
// String form
db.select().from(users).comment("key='val'");

// Object form (recommended)
db.select().from(users).comment({ priority: 'high', category: 'analytics' });
// → select "id", "name" from "users" /*priority='high',category='analytics'*/
```
