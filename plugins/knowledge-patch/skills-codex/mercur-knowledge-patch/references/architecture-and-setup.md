# Architecture and setup

## Block-owned architecture (2.0.0)

Mercur 2.0 replaces the 1.x monolith and fork-based customization model with a core
plugin plus blocks whose source is copied into the project. The application owns and
can edit installed optional-feature source.

A block can span modules, module links, workflows, API routes, and Admin or Vendor
extensions. Cart, order, pricing, and vendor workflows can be extended, replaced, or
hooked rather than rebuilt.

`@mercurjs/core-plugin` supplies the marketplace baseline, including seller,
commission, payout, custom-field, Admin UI, Vendor UI, and code-generation modules,
plus the core Medusa integrations. Optional features are installed from registries.

## Runtime requirements and services (2.0.0)

Mercur 2.0 requires Node.js 20 or newer, PostgreSQL, Redis, and Git. The monorepo uses
Bun.

After project creation, run:

```bash
npm run dev
```

This starts:

- the backend at `http://localhost:9000`;
- Admin at `/dashboard`;
- Vendor at `/seller`.

## Project-local development governance (2.0.0)

Generated templates include `.ai/skills/` definitions for Mercur CLI and block
conventions, Medusa UI conformance, Admin pages, forms, tabbed wizards, and
1.x-to-2.0 migration. These files are the project-local source of extension and
migration conventions.

## Initial marketplace maturity (0.9.0)

Mercur's first marketplace release runs on Medusa 2.x and includes upgrades through
Medusa 2.7.0. The release was still under heavy testing. Known limitations were:

- multi-vendor order edge cases;
- commission calculations for some currencies;
- incomplete API input validation.
