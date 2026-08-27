# Prisma Postgres and product surfaces

## Provisioning Prisma Postgres

Prisma Postgres became generally available in 6.4.0. The original CLI entry
point was `prisma init --db`:

```sh
npx prisma init --db
```

`prisma init --prompt` can scaffold a schema from a natural-language
description and deploy it to a new instance; `--vibe` is an alias (6.6.0).
`npx create-db` creates a database without authentication and deletes it after
24 hours unless it is claimed in Prisma Console (6.13.0). Add `--json` for
script-consumable connection details (6.15.0).

Use `prisma bootstrap` for the current state-aware setup path (7.7.0). It
detects and runs only missing steps: scaffold or initialize, authenticate and
link a database, install dependencies, migrate, generate, and seed. It skips
completed steps on reruns and confirms side effects. API credentials and a
database ID allow non-interactive use.

```sh
npx prisma@latest bootstrap
npx prisma@latest bootstrap --template nextjs
npx prisma@latest bootstrap --api-key "$PRISMA_API_KEY" --database "db_abc123"
```

Link an existing local project with the `prisma postgres` command group added
in 7.6.0:

```sh
npx prisma postgres link
```

## Local development

`prisma dev` starts a local Prisma Postgres server without Docker (6.8.0).
Local databases persist across runs and multiple instances can run at once;
`prisma init` began choosing local Prisma Postgres by default in 6.9.0.

```sh
npx prisma dev
prisma dev stop 'mydb*'
prisma dev rm 'mydb*'
```

The stop and remove commands accept globs and can manage instances created by
the editor extension (6.11.0); `stop` halts matches and `rm` removes them from
the file system. The editor's local database UI no longer needs a Prisma
Console login (6.15.0). Local instances gained Early Access direct
`postgres://` connections for non-Prisma tools in 6.10.0.

## Direct connections, pooling, and Accelerate

Prisma Postgres introduced standard `postgres://` TCP URLs for PostgreSQL
tools and other database libraries in 6.9.0; this became GA for production in
6.17.0. Add `pool=true` to opt into connection pooling on a direct URL
(6.19.0):

```text
postgres://.../postgres?sslmode=require&pool=true
```

Use the direct URL with tools such as standard PostgreSQL clients and non-
Prisma query libraries. A serverless driver was an Early Access alternative
when TCP was unsuitable.

Prisma Postgres provides native pooling, while Prisma Accelerate is the cache
layer (7.0.0). Existing Accelerate URLs continue to work, and new generated
clients receive them through `accelerateUrl`.

## Regions, backups, and usage

Provisioning regions added across the stream include Singapore
`ap-southeast-1` (6.8.0), San Francisco `us-west-1` (6.9.0), and Frankfurt
`eu-central-1` (6.11.0).

The Console Backups tab can list and restore automated backups (6.9.0). The
remote MCP surface can also create and re-instantiate backups. Console metrics
include estimated invoice, storage, database count, cumulative and daily
operations (6.17.0), plus per-database egress, average response size, average
query duration, and caching guidance (6.18.0). The Pricing Calculator estimates
plan charges from storage and operation counts (6.11.0).

## Management API and remote administration

The Prisma Postgres Management API can provision and delete instances, fetch
connection strings, and manage Console projects (6.13.0). It became GA in
6.15.0 and can create a project without an automatic default database, letting
project and database provisioning happen separately.

The CLI-hosted MCP server introduced in 6.6.0 can create databases, design
schemas, and work through migrations:

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

The hosted MCP endpoint added in 6.10.0 can manage databases and connection
strings, create or restore backups, execute SQL, and introspect schemas:

```sh
npx -y mcp-remote https://mcp.prisma.io/mcp
```

The MCP server can also answer cited documentation questions about Prisma ORM,
Prisma Postgres, and Prisma Compute directly in an editor (product-updates).

## Console and editor workflows

The database-management editor UI can authenticate with Console, create or
delete remote instances, show local instances, edit data in embedded Studio,
and visualize schemas (6.9.0). It gained a Push to Cloud action for deploying a
local instance for remote applications (6.10.0).

OAuth applications connected to Prisma Console can be listed and revoked;
revocation immediately prevents further access (6.14.0).

## Integrations

- Prisma Postgres joined Vercel Marketplace with Vercel billing and one-click
  application connections in 6.7.0. It works with every Vercel PostgreSQL
  template, including templates using other database libraries (6.11.0).
- Pipedream workflows can provision and use Prisma Postgres in response to
  connected-application events (6.15.0).
- A database can be added to a Stripe project through one command, with
  spending limits and CLI plan changes (product-updates).

## Controlled frontend access

A private Early Access feature introduced in 6.7.0 allowed frontend
applications to access Prisma Postgres directly under fine-grained TypeScript
security rules. Treat it as gated functionality that requires admission; do
not generalize it into an ordinary unrestricted browser connection.

## PostgreSQL extensions and vectors

Prisma Postgres can enable `pgvector` (6.13.0), but that release did not give
Prisma ORM native vector support. Create the extension in custom migration SQL
and perform vector operations with TypedSQL.

## Prisma Next

Prisma Next adds scalar lists and MongoDB enums to its schema language, reads
native PostgreSQL enums, and can preview migrations. Setup paths cover new and
existing PostgreSQL and MongoDB projects (product-updates).

Studio recognizes Prisma Next's migration ledger and shows a newest-first
timeline with visual diffs for models, fields, enums, relations, executed SQL,
and schema changes (7.9.0). The view stays hidden for databases managed by
classic Prisma Migrate because they do not have that ledger.

## Prisma Compute

Prisma Compute is a Public Beta for deploying TypeScript applications beside
Prisma Postgres, including custom domains and database branches
(product-updates). Configure deployment in `prisma.compute.ts`; restore an
earlier service version from Prisma Console when rollback is required.

The Public Beta Management API exposes `/v1/apps` and `/v1/deployments`, plus
deployment-log access and failed-build diagnostics.
