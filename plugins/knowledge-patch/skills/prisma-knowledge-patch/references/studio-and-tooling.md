# Studio and developer tooling

Use this reference when browsing data, embedding Studio, working through the editor extension, automating CLI output, initializing a project, or handling very large schemas.

## Contents

- [Choose a Studio surface](#choose-a-studio-surface)
- [Connect Studio through a driver adapter](#connect-studio-through-a-driver-adapter)
- [Embed Studio in a React application](#embed-studio-in-a-react-application)
- [Use current Studio workflows](#use-current-studio-workflows)
- [Manage databases from the editor](#manage-databases-from-the-editor)
- [Initialize and bootstrap projects](#initialize-and-bootstrap-projects)
- [Automate CLI output and large-schema work](#automate-cli-output-and-large-schema-work)

## Choose a Studio surface

Hosted Prisma Studio returned in Prisma Console for PostgreSQL and MySQL in 6.3.0, providing an in-console data browser and editor.

The redesigned Studio became available from `prisma studio` in 7.0.0. It added relationship visualization and could inspect a remote database through `--url`; that initial CLI release supported PostgreSQL, MySQL, and SQLite only.

```sh
npx prisma studio --url "$DATABASE_URL"
```

Use a current Prisma Config datasource when the CLI should share project configuration. Use `--url` for an intentional one-command override, not as a hidden substitute for missing project configuration.

Query Insights is embedded in Studio in the `product-updates` batch, allowing slow-query investigation in the same surface used to browse data.

## Connect Studio through a driver adapter

Prisma Config added a `studio.adapter` factory in 6.5.0. It lets Studio connect through a driver adapter rather than requiring a conventional datasource URL:

```ts
import type { PrismaConfig } from 'prisma'
import { PrismaLibSql } from '@prisma/adapter-libsql'
import { createClient } from '@libsql/client'

export default {
  schema: './prisma/schema.prisma',
  studio: {
    adapter: async () =>
      new PrismaLibSql(createClient({ url: 'file:./dev.db' })),
  },
} satisfies PrismaConfig
```

The original release required `earlyAccess: true` and used the older adapter export casing. Current configurations omit that obsolete opt-in and use `PrismaLibSql`.

## Embed Studio in a React application

`@prisma/studio-core` can embed the Studio data editor in a React interface as of 6.11.0. This supports applications that expose database editing to their own users, including products that provision a separate Prisma Postgres database for each user.

## Use current Studio workflows

Studio capabilities added in 7.5.0 include:

- Multi-cell selection.
- Value search across a table.
- Raw SQL filters.
- A `Cmd+K` command palette.
- A dedicated SQL tab for raw queries.
- AI-generated filters in the Console-hosted Studio.

The 7.6.0 tooling update adds or restores:

- Dark mode.
- Copying one or more rows as Markdown or CSV.
- Editing multiple cells before choosing to save or discard all changes.
- Links from reference values to related records.
- Natural-language generation of SQL statements.

## Manage databases from the editor

With the Prisma editor extension installed, agent mode can check migration status, create and run migrations, authenticate with Prisma Console, and provision Prisma Postgres databases (6.8.0).

The Prisma Activity Bar database UI expanded in 6.9.0. It can:

- Authenticate with Prisma Console.
- Create or delete hosted Prisma Postgres instances.
- Display local instances.
- Edit data through embedded Studio.
- Visualize schemas.

The **Push to Cloud** action deploys a local Prisma Postgres instance for remote applications (6.10.0). Local database management stopped requiring a Console login in 6.15.0. CLI `prisma dev stop` and `prisma dev rm` can manage instances that the editor started.

## Initialize and bootstrap projects

`prisma init` detects Bun and tailors generated setup to that runtime as of 7.2.0. Avoid replacing the generated Bun setup with Node-specific scripts unless the project intentionally uses both runtimes.

`prisma bootstrap` orchestrates Prisma Postgres setup as of 7.7.0:

```sh
npx prisma@latest bootstrap
npx prisma@latest bootstrap --template nextjs
npx prisma@latest bootstrap --api-key "$PRISMA_API_KEY" --database "db_abc123"
```

The command inspects project state and runs only missing steps:

1. Scaffold or initialize the application.
2. Authenticate and link a Prisma Postgres database.
3. Install dependencies.
4. Migrate the database.
5. Generate the client.
6. Seed data.

Side-effecting steps require confirmation, and completed steps are skipped when the command is rerun. Supply an API key and database ID for non-interactive execution.

For an already initialized project, `prisma postgres link` links the local project to a Prisma Postgres database (7.6.0):

```sh
npx prisma postgres link
```

This command introduced the `prisma postgres` command group.

## Automate CLI output and large-schema work

`prisma version --json` writes only JSON to stdout as of 7.2.0. Scripts can parse or redirect it without stripping unrelated CLI messages:

```sh
npx prisma version --json > prisma-version.json
```

The CLI falls back to streaming parsing for schemas too large for V8 string limits as of 7.6.0. Do not pre-concatenate a very large multi-file schema into one JavaScript string in wrapper tooling; let the CLI use its streaming path.

`prisma generate` can execute under Bun without a separate Node.js installation as of 6.6.0. If generation hangs in an older Bun-only environment, upgrade the CLI before adding Node solely as a workaround.
