# Studio and developer tooling

## Studio connection surfaces

Hosted Prisma Studio returned in Prisma Console for PostgreSQL and MySQL in
6.3.0. The redesigned CLI Studio in 7.0.0 supports PostgreSQL, MySQL, and
SQLite, visualizes relationships, and can inspect a remote database with a
direct URL:

```sh
npx prisma studio --url "$DATABASE_URL"
```

Early Prisma Config could provide a `studio.adapter` factory so Studio could
connect through a driver adapter (6.5.0). Prefer the current stable Prisma
Config shape when carrying that pattern into a newer project.

Studio can be embedded in a React application through
`@prisma/studio-core`, including products that provision Prisma Postgres for
their own users (6.11.0).

## Data browsing and editing

Studio's 7.5.0 workflows include:

- multi-cell selection;
- value search across a table;
- raw SQL filters;
- a `Cmd+K` command palette;
- a dedicated SQL query tab;
- generated filters in the Console-hosted UI.

Studio 7.6.0 restored dark mode, added Markdown or CSV copying for one or more
rows, and allowed multiple cells to be edited before a single save-or-discard
prompt. References link to related records for relationship navigation. Studio
can also turn natural-language requests into SQL.

SQL execution, linting, and navigation resolve unqualified identifiers against
the schema selected in Studio rather than always using the adapter's default
schema (7.9.0).

## Query Insights, Streams, and migration history

Query Insights is embedded in Studio for investigating slow queries beside the
data being browsed (product-updates).

Studio includes a Prisma Streams browser with live aggregations, diagnostics,
routing-key browsing, WAL-history handoff from tables, and summarized event-log
and OpenTelemetry observability (7.9.0).

For a Prisma Next migration ledger, Studio shows a newest-first migration
timeline and visual diffs spanning models, fields, enums, relations, executed
SQL, and schema changes (7.9.0). This view is hidden for classic Prisma Migrate
databases because they do not store that ledger.

## Editor integration

With the Prisma editor extension installed, assisted workflows can check
migration status, create and run migrations, authenticate to Prisma Console,
and provision Prisma Postgres (6.8.0). The Prisma Activity Bar can create or
delete remote instances, show local instances, edit data through embedded
Studio, and visualize schemas (6.9.0).

The extension added Push to Cloud for local instances in 6.10.0. Its local
database-management UI stopped requiring a Console login in 6.15.0.

## Initialization and bootstrap

`prisma init` detects Bun and tailors the generated setup to that runtime
(7.2.0). New scaffolded projects receive the version-relevant `prisma/skills`
catalog through a best-effort install that cannot block initialization
(7.9.0). Pass `--no-skills` to opt out:

```sh
npx prisma@latest init --no-skills
```

Use `prisma bootstrap` for a state-aware Prisma Postgres workflow (7.7.0). It
skips completed work on reruns and confirms side-effecting steps. It can
initialize, authenticate, link a database, install dependencies, migrate,
generate, and seed.

## CLI output and shell completion

`prisma version --json` writes only JSON to stdout, so scripts can parse or
redirect it without filtering unrelated CLI text (7.2.0).

Prisma provides completions for commands, options, flags, and option values in
Bash, Zsh, Fish, and PowerShell (7.9.0). For a project-local CLI, initialize
`@bomb.sh/tab` for the package manager. `npm exec` and `bun x` work; `npx` and
`bunx` do not. A global installation can use `prisma complete <shell>`.

```sh
npm install -g @bomb.sh/tab
source <(tab pnpm zsh)

# Globally installed Prisma CLI
source <(prisma complete zsh)
```

## Large schemas and generated assets

The multi-file `prisma-client` generator avoids one oversized `index.d.ts`
(6.7.0). For schemas that exceed V8 string limits, the CLI can fall back to
streaming parsing so database workflows can continue (7.6.0).

Prisma binaries may load from local-network locations, which supports
deployments storing binaries on network-accessible storage (6.5.0).
On Windows, engine binaries use `%APPDATA%\Prisma` rather than the old
working-directory-relative `node_modules\.cache` path (7.9.0). This avoids
duplicate caches and accidental inclusion in serverless or container bundles.

## Credential-file permissions

Prisma Platform writes `~/.config/prisma-platform/auth.json` with mode `0o600`
and its directory with mode `0o700` (7.9.0), preventing other local users from
reading stored OAuth tokens.
