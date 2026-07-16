# Schema Validation

## First-class Zod schema generation

Starting with `drizzle-orm@1.0.0-beta.15`, import Drizzle's Zod schema
generators from `drizzle-orm/zod`.

The separate `drizzle-zod` package is deprecated and will receive no new
updates.

Install `zod` directly rather than relying on the deprecated integration
package to provide the integration surface.

## Supported generators

The built-in entry point provides generators for select, insert, and
update schemas:

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

## Migration workflow

For a project that imports `drizzle-zod`:

1. Verify that its `drizzle-orm` version includes `drizzle-orm/zod`.
2. Ensure `zod` is installed as a direct dependency.
3. Change generator imports to `drizzle-orm/zod`.
4. Keep the existing select, insert, and update generator calls.
5. Search again for remaining `drizzle-zod` imports.
6. Remove the deprecated package when no imports require it.
7. Run the repository's type checks and validation tests.

Do not introduce new `drizzle-zod` usage in code that can use the built-in
entry point.

If a repository deliberately supports an ORM version without that entry
point, preserve that compatibility constraint explicitly rather than
silently switching imports.

## Review checklist

- Confirm the import source is `drizzle-orm/zod`.
- Confirm `zod` is a direct dependency.
- Confirm all used generators remain imported.
- Confirm no accidental `drizzle-zod` imports remain after migration.
- Confirm generated select, insert, and update schemas still pass the
  project's checks.
