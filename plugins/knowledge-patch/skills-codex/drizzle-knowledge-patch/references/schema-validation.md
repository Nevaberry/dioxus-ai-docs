# Schema Validation

## Use the built-in Zod entry point

Starting with `drizzle-orm@1.0.0-beta.15`, import Drizzle's Zod schema
generators from `drizzle-orm/zod`.

The separate `drizzle-zod` package is deprecated and will receive no new
updates. Keep `zod` installed as a direct application dependency.

The built-in entry point supports schema generation for select, insert, and
update operations:

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

## Migration procedure

Before changing imports, confirm that the installed `drizzle-orm` version
contains the built-in entry point.

Then:

1. Add `zod` as a direct dependency if it is not already direct.
2. Find every import from `drizzle-zod`.
3. Replace generator imports with imports from `drizzle-orm/zod`.
4. Preserve existing `createSelectSchema()` calls.
5. Preserve existing `createInsertSchema()` calls.
6. Preserve existing `createUpdateSchema()` calls.
7. Remove `drizzle-zod` only when no imports still require it.
8. Run type checks and validation tests.

The import source changes, but the three generator function names do not.

## Mixed-version support

Do not introduce a compatibility wrapper unless the repository must support
an older ORM release that lacks `drizzle-orm/zod`.

If old and new ORM releases must coexist, make that constraint explicit and
choose the import strategy around the actual supported versions. Do not assume
that the separate deprecated package will receive future updates.

## Review checklist

- `zod` is a direct dependency.
- Supported projects import generators from `drizzle-orm/zod`.
- No new imports rely on `drizzle-zod`.
- Select, insert, and update schema generation remain covered where used.
- Dependency removal happens only after all old imports are gone.
