# Prisma Postgres and product surfaces

Use this reference when provisioning or operating Prisma Postgres, choosing local versus hosted connections, integrating through APIs or MCP, or working with Prisma Compute and Prisma Next.

## Contents

- [Provision Prisma Postgres](#provision-prisma-postgres)
- [Develop with local databases](#develop-with-local-databases)
- [Connect directly and pool connections](#connect-directly-and-pool-connections)
- [Choose a region and integration](#choose-a-region-and-integration)
- [Use backups, metrics, and account controls](#use-backups-metrics-and-account-controls)
- [Automate with the Management API](#automate-with-the-management-api)
- [Operate through MCP](#operate-through-mcp)
- [Deploy with Prisma Compute](#deploy-with-prisma-compute)
- [Evaluate Prisma Next](#evaluate-prisma-next)

## Provision Prisma Postgres

Prisma Postgres became generally available in 6.4.0. Start an interactive project with the database-aware init path:

```sh
npx prisma init --db
```

Prompt-driven scaffolding arrived in 6.6.0. `--prompt` generates a schema from a natural-language description and deploys it to a new Prisma Postgres instance; `--vibe` is an alias.

```sh
npx prisma init --prompt "Simple habit tracker application"
```

For a temporary database without authentication, use `create-db` (6.13.0):

```sh
npx create-db
```

The database expires after 24 hours unless claimed into a Prisma Console account. Use machine-readable output in scripts (6.15.0):

```sh
npx create-db --json
```

Use `prisma bootstrap` for a state-aware end-to-end setup and `prisma postgres link` for an existing project; their command behavior is detailed in the tooling reference.

## Develop with local databases

`prisma dev` starts local Prisma Postgres without Docker and prints a Prisma connection URL (6.8.0):

```sh
npx prisma dev
```

```prisma
datasource db {
  provider = "postgresql"
  url      = "prisma+postgres://localhost:51213/?api_key=..."
}
```

The schema example reflects the original command behavior; current projects put the CLI datasource URL in Prisma Config.

Local databases persist across runs and multiple instances can run concurrently as of 6.9.0. That release also made local Prisma Postgres the default database chosen by `prisma init`.

Manage instances by glob with `prisma dev stop <globs>` and `prisma dev rm <globs>`, added in 6.11.0:

```sh
prisma dev stop mydb
prisma dev rm mydb
```

`stop` stops matching instances; `rm` removes them from the file system. These commands can also manage instances started by the editor extension.

Local instances can expose a standard `postgres://` URL for non-Prisma tools, an Early Access capability introduced in 6.10.0. The editor extension can push a local instance to the hosted service (6.10.0), while its local database management UI no longer requires a Console login (6.15.0).

## Connect directly and pool connections

New hosted databases began supplying standard PostgreSQL TCP URLs in 6.9.0, letting PostgreSQL clients such as Drizzle, Kysely, TypeORM, and command-line tools connect without Prisma ORM. At introduction, serverless environments could instead use Prisma's Early Access serverless driver. The direct connection path became generally available for production use in 6.17.0.

Use serverless connection options only when the execution environment requires them. The standard URL keeps the database interoperable with PostgreSQL tooling.

Opt into pooling on a direct Prisma Postgres URL with `pool=true` (6.19.0):

```text
postgres://.../postgres?sslmode=require&pool=true
```

Prisma Postgres provides native pooling. Prisma Accelerate is positioned as the caching layer (7.0.0); existing Accelerate URLs continue to work and current clients receive them through `accelerateUrl`.

## Choose a region and integration

Region additions include:

- Asia Pacific (Singapore), `ap-southeast-1` (6.8.0).
- San Francisco, `us-west-1` (6.9.0).
- Frankfurt, `eu-central-1` (6.11.0).

Prisma Postgres entered the Vercel Marketplace in 6.7.0, supporting dashboard provisioning, Vercel billing, and one-click application connection. By 6.11.0 it worked with all PostgreSQL Vercel templates, including applications using Drizzle ORM or Postgres.js.

Additional integrations:

- Pipedream workflows can provision and use databases in response to connected-application events without custom provisioning scripts (6.15.0).
- A database can be added to a Stripe project through the one-command integration in the `product-updates` batch; it includes spending limits and CLI plan changes.

A private Early Access capability introduced in 6.7.0 allows frontend applications to access Prisma Postgres directly under fine-grained TypeScript security rules. It requires admission to that private program; do not treat it as a generally available client architecture.

## Use backups, metrics, and account controls

The Console **Backups** tab can restore a database to an automated backup selected by the user (6.9.0).

Console operational and billing surfaces include:

- Estimated upcoming invoice, total storage, database count, cumulative operations, and operations per day (6.17.0).
- Per-database total egress, average response size, average query duration, and query-caching guidance (6.18.0).
- A Pricing Calculator based on predicted storage and operation counts for operation-based plans (6.11.0).
- Query Insights embedded in Studio for investigating slow queries beside the browsed data (`product-updates`).

Prisma Console lists connected OAuth applications and can revoke an application's access immediately (6.14.0).

Prisma Postgres can enable `pgvector` in Early Access (6.13.0), but that release does not provide native Prisma ORM vector fields or operators. Create the extension in a custom migration and use TypedSQL for vector operations.

## Automate with the Management API

The Prisma Postgres REST Management API was introduced in 6.13.0 for programmatic project and database operations. It can provision and delete databases, create or retrieve connection strings, and manage Console projects.

The API became generally available in 6.15.0. A project no longer needs an automatically created default database, so project creation and database provisioning can be independent steps.

## Operate through MCP

The local Prisma Postgres MCP server entered Preview in 6.6.0. It can create databases, design schemas, and work through migrations via the Prisma CLI:

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

The hosted MCP endpoint added in 6.10.0 can manage databases and connection strings, create and re-instantiate backups, execute SQL, and introspect schemas:

```sh
npx -y mcp-remote https://mcp.prisma.io/mcp
```

The Prisma MCP server can also answer cited documentation questions about Prisma ORM, Prisma Postgres, and Prisma Compute without extra setup (`product-updates`).

## Deploy with Prisma Compute

Prisma Compute is in Public Beta in the `product-updates` batch. It deploys TypeScript applications beside Prisma Postgres and supports custom domains and database branches.

Define deployment configuration in `prisma.compute.ts`. If a deployment regresses, restore any prior service version from Prisma Console.

The Compute Management API manages Public Beta services through `/v1/apps` and `/v1/deployments`. It also exposes deployment logs and failed-build diagnostics, allowing automation without the dashboard.

## Evaluate Prisma Next

Prisma Next adds schema-language support for scalar lists and MongoDB enums, reads native PostgreSQL enums, and previews migrations (`product-updates`). Setup paths exist for both new and existing PostgreSQL and MongoDB projects.

Prisma ORM's current major support for MongoDB differs from Prisma Next's advertised MongoDB schema capabilities; do not assume one product's compatibility statement applies to the other.
