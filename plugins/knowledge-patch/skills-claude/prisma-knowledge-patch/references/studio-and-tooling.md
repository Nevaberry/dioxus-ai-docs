# Studio and developer tooling

## Choose a Studio surface

Hosted Prisma Studio returned in Prisma Console for PostgreSQL and MySQL in
6.3.0. The redesigned Studio became available through `prisma studio` in
7.0.0, initially for PostgreSQL, MySQL, and SQLite; it can inspect a remote
database with `--url`:

```sh
npx prisma studio --url "$DATABASE_URL"
```

Early Prisma Config can supply `studio.adapter` as an async driver-adapter
factory, allowing Studio to connect through LibSQL or another adapter (6.5.0).
Use current Prisma Config syntax even though the original feature required
`earlyAccess: true`.

```ts
import { defineConfig } from 'prisma/config'
import { PrismaLibSql } from '@prisma/adapter-libsql'
import { createClient } from '@libsql/client'

export default defineConfig({
  schema: './prisma/schema.prisma',
  studio: {
    adapter: async () =>
      new PrismaLibSql(createClient({ url: 'file:./dev.db' })),
  },
})
```

Applications that provision Prisma Postgres for users can embed the data
editor in React through `@prisma/studio-core` (6.11.0).

## Use current data-editing and SQL workflows

Studio added table-wide value search, raw SQL filters, multi-cell selection, a
`Cmd+K` command palette, and a dedicated raw-SQL tab in 7.5.0. Console Studio
also offers generated filters.

In 7.6.0 Studio restored dark mode, added row copying as Markdown or CSV,
allowed several cells to be edited before a single save-or-discard decision,
and linked references to related records. It can also turn a natural-language
request into SQL.

Query Insights is embedded in Studio for investigating slow queries beside
the browsed data (product-updates).

Since 7.9.0, SQL execution, linting, and navigation resolve unqualified names
against the schema selected in Studio instead of always using the adapter's
default schema.

## Inspect next-generation migrations and streams

For databases using a Prisma Next migration ledger, Studio shows a newest-
first timeline and visual diffs for models, fields, enums, relations, executed
SQL, and schema changes. The view stays hidden for databases managed by classic
Prisma Migrate because they do not store that ledger (7.9.0).

Studio also includes a Prisma Streams browser with live aggregations,
diagnostics, routing-key browsing, table-to-WAL-history handoff, and summarized
event-log and OpenTelemetry observability (7.9.0).

## Manage databases from the editor extension

With the Prisma editor extension installed, agent mode can check migration
status, create and run migrations, authenticate with Prisma Console, and
provision Prisma Postgres (6.8.0).

The Prisma Activity Bar can create or delete hosted databases, list local
instances, embed Studio, and visualize schemas (6.9.0). It can push a local
Prisma Postgres instance to the cloud (6.10.0), and local-instance management
does not require a Console login (6.15.0).

## Initialize and bootstrap projects

`prisma init` detects Bun and emits runtime-appropriate project setup when
invoked under Bun (7.2.0). It creates `prisma.config.ts` for Prisma 6.18.0 and
later, preparing projects for the Prisma 7 configuration requirement.

New projects receive the version-relevant `prisma/skills` catalog through a
best-effort install that cannot block initialization. Pass `--no-skills` to
opt out (7.9.0):

```sh
npx prisma@latest init --no-skills
```

`prisma bootstrap` is state-aware: it performs only missing setup, asks before
side effects, skips completed work on rerun, and supports templates or
non-interactive API credentials plus a database ID (7.7.0).

## Make CLI output automation-friendly

`prisma version --json` emits only JSON to stdout, allowing direct parsing and
redirection (7.2.0).

Prisma provides command, option, flag, and option-value completions for Bash,
Zsh, Fish, and PowerShell (7.9.0). For a project-local CLI, initialize
`@bomb.sh/tab` for the package-manager command. `npm exec` and `bun x` work;
`npx` and `bunx` do not. A globally installed CLI can use
`prisma complete <shell>` directly.

```sh
npm install -g @bomb.sh/tab
source <(tab pnpm zsh)

# Globally installed CLI
source <(prisma complete zsh)
```

## Handle large schemas and engine binaries

The CLI can switch to streaming parsing when a schema exceeds V8 string
limits, allowing database commands to operate on very large schemas (7.6.0).

Prisma binaries can load from local-network locations, supporting deployments
that keep them on network-accessible storage (6.5.0).

On Windows, engine binaries are cached under `%APPDATA%\Prisma` rather than a
working-directory-relative `node_modules\.cache`. This avoids duplicate caches
and accidental inclusion in serverless or container bundles (7.9.0).

## Preserve destructive-command checkpoints

Destructive CLI commands invoked through supported automated coding
environments require explicit confirmation. The later checkpoint covers
`prisma db push --accept-data-loss`, recognizes generic `AI_AGENT` and `AGENT`
conventions, and applies on Linux. The MCP server does not expose its former
reset tool; use the guarded CLI workflow (7.9.0).
