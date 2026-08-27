---
name: drizzle-knowledge-patch
description: Drizzle ORM
version: "1.0.0-beta.19"
license: MIT
metadata:
  author: Nevaberry
---


# Drizzle ORM Knowledge Patch

Use this skill when work touches Drizzle SQL identifiers or aliases,
Drizzle Kit module loading, or Zod schemas generated from Drizzle tables.

The relevant behavior is controlled by different packages and, for the CLI,
by the runtime used to launch it. Establish those boundaries before changing
code or dependencies.

## Working method

Before editing:

1. Read the installed `drizzle-orm` version.
2. Read the installed `drizzle-kit` version separately.
3. Identify whether Drizzle Kit is launched with Node, Bun, or Deno.
4. Search for `sql.identifier()` and `sql.as()` calls.
5. Search for imports from `drizzle-zod` and `drizzle-orm/zod`.
6. Confirm whether `zod` is a direct application dependency.
7. Open the task-specific reference below before selecting a change.

Do not use the ORM version to infer CLI loader behavior.

Do not use the Drizzle Kit version to infer schema-generator availability.

Do not assume every JavaScript runtime follows the Node loader path.

## Reference index

| Reference | Topics | Read when |
| --- | --- | --- |
| [queries-and-runtime.md](references/queries-and-runtime.md) | Identifier and alias escaping; SQL injection risk | Reviewing or changing `sql.identifier()` or `sql.as()` |
| [migrations-and-kit.md](references/migrations-and-kit.md) | Runtime-aware Drizzle Kit loading; ESM and CommonJS | Running the CLI or diagnosing module-loading failures |
| [schema-validation.md](references/schema-validation.md) | Built-in Zod generators; deprecated package; direct dependency | Creating or migrating select, insert, or update schemas |

## Quick reference

### Upgrade code that constructs identifiers or aliases

Current Drizzle ORM releases properly escape values passed to
`sql.identifier()` and `sql.as()`.

Earlier releases could leave those values improperly escaped and expose an
application to SQL injection.

If either helper is present, verify the installed ORM and upgrade from an
affected release. Treat this as a security change, not routine cleanup.

Then review every helper call and test the values the application can pass.

See [queries-and-runtime.md](references/queries-and-runtime.md) for the
security boundary and focused review procedure.

### Move schema generation to the built-in Zod entry point

With `drizzle-orm@1.0.0-beta.15` or newer, import the schema generators from
`drizzle-orm/zod`.

The separate `drizzle-zod` package is deprecated and receives no new
updates. Keep `zod` installed directly by the application.

Use the built-in entry point for all three schema purposes:

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

Preserve the generator calls while changing the import source.

Remove `drizzle-zod` only after the repository no longer imports it.

See [schema-validation.md](references/schema-validation.md) for a narrow
migration sequence.

### Match Drizzle Kit diagnosis to the launch runtime

Starting with `drizzle-kit@0.31.10`, a Node launch uses the `tsx` loader
instead of `esbuild-register`.

That Node path can load both ESM and CommonJS projects.

Bun and Deno bypass `tsx` and use their native import systems.

Before changing loader dependencies, record the command and runtime that
actually launch Drizzle Kit.

See [migrations-and-kit.md](references/migrations-and-kit.md) for the runtime
matrix and diagnostic workflow.

## SQL identifier and alias workflow

Use this workflow whenever a query constructs an identifier or alias:

1. Find each `sql.identifier()` call.
2. Find each `sql.as()` call.
3. Record the installed `drizzle-orm` version.
4. Determine which calls can receive values outside the static query text.
5. Upgrade if the project is on a release with improper escaping.
6. Retest the queries after the upgrade.
7. Call out the SQL injection risk in the handoff.

Correct helper escaping is the required security boundary.

Application validation may narrow inputs, but it is not a substitute for
using a corrected ORM release.

Avoid local quoting workarounds that preserve an affected helper
implementation.

## Schema-validation workflow

Use this workflow for Drizzle-derived Zod schemas:

1. Confirm the installed `drizzle-orm` supports `drizzle-orm/zod`.
2. Inventory imports from the deprecated `drizzle-zod` package.
3. Confirm `zod` is declared as a direct dependency.
4. Change generator imports to `drizzle-orm/zod`.
5. Preserve `createSelectSchema()` calls.
6. Preserve `createInsertSchema()` calls.
7. Preserve `createUpdateSchema()` calls.
8. Remove `drizzle-zod` after its final import is gone.
9. Run type checks and the validation tests used by the project.

Keep this migration narrow. The entry-point change does not require renaming
the three generator functions.

If the repository must retain an older ORM that lacks the built-in entry
point, state that compatibility constraint before proposing the migration.

## Drizzle Kit workflow

Use this workflow when the CLI cannot load configuration or project modules:

1. Capture the exact launch command.
2. Identify whether the command runs under Node, Bun, or Deno.
3. Record the installed `drizzle-kit` version.
4. For Node, evaluate the `tsx` loader path.
5. For Bun, evaluate Bun's native imports.
6. For Deno, evaluate Deno's native imports.
7. Apply a fix only to the runtime path the project uses.
8. Retest through that same runtime and command.

Do not prescribe `esbuild-register` for the current Node loading path.

Do not add `tsx` to control a Bun or Deno launch that bypasses it.

Distinguish a project module-format problem from a mismatch between the
assumed and actual launch runtime.

## Review checklist

### SQL security

- Locate both `sql.identifier()` and `sql.as()` usage.
- Verify the installed ORM has the escaping correction.
- Treat an affected version as an upgrade requirement.
- Report the SQL injection exposure when the correction is needed.

### Zod integration

- Use `drizzle-orm/zod` where the installed ORM supports it.
- Keep `zod` as a direct dependency.
- Avoid new imports from deprecated `drizzle-zod`.
- Cover each select, insert, and update generator used by the project.

### CLI loading

- Identify Node, Bun, or Deno before changing loader configuration.
- Expect `tsx` on the current Node path.
- Expect runtime-native imports on Bun and Deno paths.
- Verify using the project's real launch command.

## Handoff

State which package controlled the behavior that changed.

For query-helper work, name the helper and describe the escaping correction as
security-sensitive.

For schema-validation work, report both the import migration and the direct
`zod` dependency.

For CLI work, report the launch runtime and whether the tested path used
Node's loader or a runtime-native import system.
