# Schema Validation

## First-class Zod schema generation

Starting with `drizzle-orm@1.0.0-beta.15`, Drizzle's Zod schema generators
are available from the built-in `drizzle-orm/zod` entry point.

The separate `drizzle-zod` package is deprecated and receives no new
updates. Applications using the built-in entry point must install `zod`
directly.

Use the built-in generators for select, insert, and update schemas:

```ts
import {
  createInsertSchema,
  createSelectSchema,
  createUpdateSchema,
} from 'drizzle-orm/zod';

const selectUserSchema = createSelectSchema(users);
const insertUserSchema = createInsertSchema(users);
const updateUserSchema = createUpdateSchema(users);
```

## Package responsibilities

`drizzle-orm` supplies the built-in generator entry point.

`zod` remains a direct application dependency.

`drizzle-zod` is the deprecated separate entry point and should not receive
new reliance.

Keep these dependencies distinct when reviewing a migration. The presence of
one does not prove the others are correctly declared or imported.

## Migration procedure

1. Record the installed `drizzle-orm` version.
2. Confirm it supports `drizzle-orm/zod`.
3. Search for every import from `drizzle-zod`.
4. Add `zod` as a direct dependency if it is not already direct.
5. Replace generator imports with imports from `drizzle-orm/zod`.
6. Preserve calls to `createSelectSchema()`.
7. Preserve calls to `createInsertSchema()`.
8. Preserve calls to `createUpdateSchema()`.
9. Confirm no source file still imports `drizzle-zod`.
10. Remove the deprecated package only after the import search is clean.
11. Run the project's type checks and validation tests.

The import-source migration does not require renamed generator calls. Keep
the change focused on the entry point and dependency ownership.

## Compatibility boundary

Do not switch a project to `drizzle-orm/zod` without confirming that its
installed ORM meets the entry-point threshold.

If the project must support an older ORM without the built-in entry point,
record that constraint before choosing a compatibility strategy.

Do not leave `zod` available only transitively. The application uses it as a
direct dependency alongside the built-in Drizzle integration.

Do not add new `drizzle-zod` imports. The package is deprecated and will not
receive new updates.

## Verification checklist

- Generator imports come from `drizzle-orm/zod` where supported.
- `zod` is declared directly by the application.
- No required select-schema generator was dropped.
- No required insert-schema generator was dropped.
- No required update-schema generator was dropped.
- No source import still requires `drizzle-zod` before its removal.
- Type checks and schema-validation tests pass.

In the handoff, report both the import-source change and the direct `zod`
dependency.
