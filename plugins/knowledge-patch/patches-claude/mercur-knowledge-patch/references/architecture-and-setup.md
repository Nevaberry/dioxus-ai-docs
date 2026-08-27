# Architecture and Setup

## Marketplace baseline and maturity (0.9.0)

Mercur's first marketplace release runs on Medusa 2.x and includes upgrades
through Medusa 2.7.0.

The release was still under heavy testing. Known limitations were:

- multi-vendor order edge cases;
- commission calculations for some currencies; and
- incomplete API input validation.

## Core plugin and application-owned blocks (2.0.0)

Mercur 2.0 replaces the 1.x monolith and fork-based customization model with a
core plugin plus blocks whose source is copied into the project. A block can
span:

- modules;
- module links;
- workflows;
- API routes; and
- Admin or Vendor extensions.

Cart, order, pricing, and vendor workflows can be extended, replaced, or
hooked rather than rebuilt.

`@mercurjs/core-plugin` supplies the marketplace baseline. It includes seller,
commission, payout, custom-field, Admin UI, Vendor UI, and code-generation
modules, along with the core Medusa integrations.

Optional features are installed from registries. Their source remains owned
and editable by the application.

## Project-local development governance (2.0.0)

Generated templates include `.ai/skills/` definitions for:

- Mercur CLI and block conventions;
- Medusa UI conformance;
- Admin pages;
- forms;
- tabbed wizards; and
- 1.x-to-2.0 migration.

These files are the project-local source of extension and migration
conventions.

## Bootstrap and runtime requirements (2.0.0)

Mercur 2.0 requires:

- Node.js 20 or newer;
- PostgreSQL;
- Redis; and
- Git.

The monorepo uses Bun. Create a project with:

```bash
bunx @mercurjs/cli create my-marketplace
```

After project creation, `npm run dev` starts:

- the backend at `http://localhost:9000`;
- Admin at `/dashboard`; and
- Vendor at `/seller`.
