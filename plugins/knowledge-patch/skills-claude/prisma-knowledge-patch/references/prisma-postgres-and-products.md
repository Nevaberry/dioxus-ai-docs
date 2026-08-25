# Prisma Postgres and product surfaces

## Provision and link Prisma Postgres

Prisma Postgres became generally available in 6.4.0. `prisma init --db` was
the initial CLI provisioning entry point:

```sh
npx prisma init --db
```

`prisma init --prompt` can derive a schema from a natural-language description
and deploy it to a new instance; `--vibe` is an alias (6.6.0).

```sh
npx prisma init --prompt "Simple habit tracker application"
```

For an existing local project, `prisma postgres link` links a Prisma Postgres
database and introduced the `prisma postgres` command group (7.6.0).

```sh
npx prisma postgres link
```

`prisma bootstrap` inspects project state and runs only missing setup steps:
scaffold or initialize, authenticate and link a database, install dependencies,
migrate, generate, and seed. It confirms side effects, skips completed steps on
reruns, accepts templates, and supports non-interactive API credentials plus a
database ID (7.7.0).

```sh
npx prisma@latest bootstrap
npx prisma@latest bootstrap --template nextjs
npx prisma@latest bootstrap --api-key "$PRISMA_API_KEY" --database "db_abc123"
```

`npx create-db` creates an authentication-free temporary Prisma Postgres
database that expires after 24 hours unless claimed (6.13.0). Add `--json` to
obtain script-consumable connection details (6.15.0).

## Run and manage local instances

`prisma dev` starts a local Prisma Postgres server without Docker and prints a
connection URL (6.8.0). Put that URL in a PostgreSQL datasource; migrations and
queries then work as they do against a hosted instance. Local databases persist
across runs, multiple instances can run concurrently, and `prisma init` chose
local Prisma Postgres by default as of 6.9.0.

```sh
npx prisma dev
```

Use `prisma dev stop <globs>` to stop matching instances and
`prisma dev rm <globs>` to remove their persisted files. These commands also
manage instances started from the editor extension (6.11.0).

The editor's local database management does not require a Console login as of
6.15.0. An Early Access direct `postgres://` URL for local instances appeared
in 6.10.0, allowing normal PostgreSQL tools and non-Prisma libraries to connect.

## Choose direct, pooled, and cached connections

Standard `postgres://` TCP URLs for hosted Prisma Postgres appeared in 6.9.0
and became generally available for production in 6.17.0. Use them with normal
PostgreSQL tools and libraries. The initial release also offered an Early
Access serverless driver for serverless environments. Add `pool=true` to opt
into pooling on a direct URL (6.19.0):

```text
postgres://.../postgres?sslmode=require&pool=true
```

Prisma Postgres provides the pooled database layer. Prisma Accelerate is the
dedicated cache layer; existing Accelerate connection strings continue to
work, while current clients pass one through `accelerateUrl` (7.0.0).

## Operate instances in Prisma Console

The Console can restore an automated backup from its **Backups** tab (6.9.0).
It also supports revoking connected OAuth applications immediately (6.14.0).

Console reporting expanded in 6.17.0 with estimated upcoming invoices, total
storage, database counts, cumulative operations, and operations per day. Since
6.18.0, per-database views also show total egress, average response size,
average query duration, and query-caching guidance.

Prisma Postgres regions added during this stream include:

- Singapore, `ap-southeast-1` (6.8.0).
- San Francisco, `us-west-1` (6.9.0).
- Frankfurt, `eu-central-1` (6.11.0).

The Pricing Calculator estimates plan charges from expected storage and
operation counts (6.11.0).

## Automate with the Management API

The Management API first supported provisioning and deleting databases,
creating or retrieving connection strings, and managing Console projects in
6.13.0. It became GA in 6.15.0 and can create a project without a default
database, allowing project and database provisioning to be separate steps.

Prisma Compute's Public Beta API exposes `/v1/apps` and `/v1/deployments`,
including deployment logs and failed-build diagnostics (product-updates).

Prisma Platform stores credentials at
`~/.config/prisma-platform/auth.json`. Since 7.9.0 the file is created with
mode `0o600` and its directory with `0o700`; preserve those private
permissions.

## Use MCP administration and documentation surfaces

The CLI-hosted Prisma Postgres MCP server began in Preview in 6.6.0 and can
create databases, design schemas, and work through migrations:

```json
{
  "mcpServers": {
    "Prisma": {
      "command": "npx",
      "args": ["-y", "prisma", "mcp"]
    }
  }
}
```

A remote server added database and connection-string management, backup
creation and re-instantiation, plain SQL, and schema introspection (6.10.0):

```sh
npx -y mcp-remote https://mcp.prisma.io/mcp
```

The Prisma MCP server can also answer cited documentation questions about
Prisma ORM, Prisma Postgres, and Prisma Compute without extra setup
(product-updates). It deliberately does not expose a migration-reset tool;
destructive resets go through the guarded CLI path as of 7.9.0.

## Use marketplace and workflow integrations

- Vercel Marketplace can provision, bill, and one-click connect Prisma
  Postgres (6.7.0). Since 6.11.0 it works with every Vercel PostgreSQL template,
  including templates using other database libraries.
- The editor extension can push a local instance to the cloud (6.10.0).
- Pipedream workflows can provision and use Prisma Postgres in response to
  connected-application events (6.15.0).
- A Stripe project can add a database with one command, with spending limits
  and CLI plan changes (product-updates).

An invite-only direct-frontend feature uses TypeScript security rules for
fine-grained database access (6.7.0). Treat it as private Early Access rather
than a generally available application architecture.

## Account for extension and next-generation product surfaces

Prisma Postgres can enable `pgvector`, but Prisma ORM did not provide native
vector support when introduced. Create the extension in custom migration SQL
and use TypedSQL for vector operations (6.13.0).

Prisma Next adds scalar list fields, MongoDB enums, native PostgreSQL enum
reading, migration previews, and setup paths for new or existing PostgreSQL
and MongoDB projects (product-updates).

Prisma Compute entered Public Beta with TypeScript applications deployed next
to Prisma Postgres, database branches, and custom domains. Configure it in
`prisma.compute.ts`; use Prisma Console to roll back to any earlier service
version (product-updates).
