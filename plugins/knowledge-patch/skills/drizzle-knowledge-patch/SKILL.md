---
name: drizzle-knowledge-patch
description: Drizzle ORM 1.0.0-beta.19 compatibility. Use for Drizzle ORM work.
license: MIT
version: 1.0.0-beta.19
metadata:
  author: Nevaberry
---

# Drizzle ORM Knowledge Patch

## Working method

Use this patch when changing Drizzle queries, schema-derived validation,
or Drizzle Kit execution.

Before editing:

1. Identify the installed `drizzle-orm` and `drizzle-kit` package versions.
2. Identify whether the CLI is launched by Node, Bun, or Deno.
3. Check whether the project imports `drizzle-zod`.
4. Search for dynamic values passed to `sql.identifier()` or `sql.as()`.
5. Read the reference matching the task before choosing a migration.

Keep package versions distinct while reasoning:

- `drizzle-orm` controls query helpers and built-in Zod generators.
- `drizzle-kit` controls CLI module loading.
- `zod` remains a direct application dependency for generated schemas.

Do not infer one package's behavior from another package's version.

## Reference index

| Reference | Topics | Read when |
| --- | --- | --- |
| [queries-and-runtime.md](references/queries-and-runtime.md) | SQL identifier and alias escaping; security review | Building dynamic SQL or auditing `sql.identifier()` and `sql.as()` |
| [migrations-and-kit.md](references/migrations-and-kit.md) | Runtime-aware CLI loading; ESM and CommonJS projects | Running Drizzle Kit or diagnosing module-loading failures |
| [schema-validation.md](references/schema-validation.md) | Built-in Zod entry point; deprecated package; select, insert, and update schemas | Generating or migrating schema-derived validation |

## Quick reference

### Upgrade code that builds identifiers or aliases

Treat dynamic identifier and alias construction as security-sensitive.

Current releases properly escape values passed to:

- `sql.identifier()`
- `sql.as()`

Earlier releases could leave those values improperly escaped and expose
applications to SQL injection.

Upgrade when either helper is used.

Then audit every call site that accepts a value originating outside the
static query definition.

Read [queries-and-runtime.md](references/queries-and-runtime.md) for the
security boundary and review checklist.

### Replace the deprecated `drizzle-zod` entry point

For `drizzle-orm@1.0.0-beta.15` and newer, import schema generators from
`drizzle-orm/zod`.

Install `zod` directly.

Do not expect new updates to the separate `drizzle-zod` package.

Use the built-in generators for all three supported schema purposes:

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

Read [schema-validation.md](references/schema-validation.md) before
changing dependencies or imports.

### Match Drizzle Kit loading to the launch runtime

Starting with `drizzle-kit@0.31.10`, a Node launch uses the `tsx` loader
instead of `esbuild-register`.

This lets the CLI load both ESM and CommonJS projects.

Bun and Deno launches do not use that Node loader path.

They use their native import systems instead.

Read [migrations-and-kit.md](references/migrations-and-kit.md) before
changing loader dependencies or debugging module format errors.

## Query and SQL workflow

When a task touches dynamic SQL:

1. Search for `sql.identifier(` and `.as(` usages.
2. Determine whether values passed to them are static or dynamic.
3. Verify that the installed ORM contains the escaping correction.
4. Prefer upgrading over compensating for old helper behavior locally.
5. Review tests that exercise unusual identifier and alias values.
6. Treat a version upgrade as a security change in the handoff.

Do not claim that application-side validation replaces correct escaping.

Do not preserve an affected release merely because common values appear
to work.

Use the exact helper names in review notes so the affected surface is
easy to find.

## Schema-validation workflow

When a project uses Drizzle-derived Zod schemas:

1. Confirm that the ORM supports the built-in Zod entry point.
2. Add `zod` as a direct dependency if it is not already direct.
3. Replace generator imports from `drizzle-zod` with `drizzle-orm/zod`.
4. Preserve calls to `createSelectSchema()`.
5. Preserve calls to `createInsertSchema()`.
6. Preserve calls to `createUpdateSchema()`.
7. Remove `drizzle-zod` only after no imports still depend on it.
8. Run the project's type checks and validation tests.

Keep the migration narrow.

The entry-point change does not require renaming the three generator
functions shown above.

Do not add a second compatibility wrapper unless the repository must
support an older ORM that lacks the built-in entry point.

If old and new package support must coexist, state that constraint before
selecting an import strategy.

## Drizzle Kit workflow

When the CLI cannot load project configuration or source modules:

1. Record the actual launch runtime.
2. Record the installed `drizzle-kit` version.
3. For Node, reason about the `tsx` loader path.
4. For Bun, reason about Bun's native imports.
5. For Deno, reason about Deno's native imports.
6. Check whether a proposed fix belongs to the active runtime path.
7. Retest through the same runtime used by the project.

Do not prescribe `esbuild-register` for the current Node loading path.

Do not add `tsx` solely to control a Bun or Deno launch that bypasses it.

Distinguish a package-format problem from a launch-runtime mismatch in
the final diagnosis.

## Review checklist

Before completing a Drizzle change, verify the relevant items.

### SQL security

- Confirm whether `sql.identifier()` is used.
- Confirm whether `sql.as()` is used.
- Confirm that affected code runs on a corrected ORM release.
- Call out the injection risk when an upgrade is required.

### Zod integration

- Import generators from `drizzle-orm/zod` where supported.
- Keep `zod` as a direct dependency.
- Avoid introducing new reliance on `drizzle-zod`.
- Cover select, insert, and update generators used by the project.

### CLI loading

- Identify Node, Bun, or Deno before changing loader configuration.
- Expect `tsx`, not `esbuild-register`, on the current Node path.
- Expect native imports on Bun and Deno paths.
- Reproduce and verify with the project's real launch command.

## Handoff

State which package and runtime controlled the behavior you changed.

Mention any required minimum package version only where the code depends
on that threshold.

For security-sensitive helper usage, explicitly recommend the corrected
release rather than presenting the upgrade as optional cleanup.

For Zod migration work, report both the import change and the direct
`zod` dependency.

For CLI work, report whether the tested path used Node's loader or a
runtime-native import system.
