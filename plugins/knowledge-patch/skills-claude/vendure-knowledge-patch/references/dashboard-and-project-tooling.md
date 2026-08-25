# Dashboard and project tooling

Source batch: `official-changelog-2025-current`.

## CLI lifecycle and diagnostics

The CLI adds:

- non-interactive operation;
- a `schema` command;
- `dev`, `build`, and `start` lifecycle commands; and
- a `doctor` project check.

A codemod supports the Dashboard's Radix-to-Base-UI migration.

## Project scaffolding

New projects include the React Dashboard and can optionally scaffold a Next.js
storefront. Generated Dashboard configuration uses API URL `auto`. Scaffolded
projects read the server port from `VENDURE_SERVER_PORT`.

## Dashboard package and builds

`DashboardPlugin` is exported from `@vendure/dashboard`. The old AdminUiPlugin
`compatibilityMode` is deprecated.

Dashboard builds support Vite 7, user stylesheets, and an opt-in pre-bundled
mode through `useExperimentalBundle`.

Dashboard supports Zod 4 and re-exports Zod from `@vendure/dashboard`.

## Routing and authentication

Dashboard extensions can define:

- unauthenticated routes;
- TanStack Router `validateSearch`; and
- router-plugin options.

The Dashboard supports bearer-token authentication and custom React providers.

## Shell extension points

Extensions can:

- replace the login screen;
- supply static or functional `navSections`;
- add header `toolbarItems`;
- extend the `ActionBar`; and
- conditionally add or replace page blocks.

Navigation, custom fields, widgets, and custom pages can be permission-gated.

## Forms and queries

Extensions can replace detail-form inputs, provide custom input and display
components, transform relation fields, and extend detail-page and list-query
documents.

Detail pages receive their entity object. List columns can be disabled or
given configurable default visibility.

## Tables and bulk actions

The Dashboard exposes bulk actions globally and per row, including hooks for
product variants and collections.

Data tables support:

- saved views;
- customizable custom-field columns;
- date-range widget filters; and
- configurable column-view defaults.

## Merchant workflows

The Dashboard handles:

- multiple-currency prices;
- stock across multiple locations;
- split orders;
- draft-order modification;
- refunds;
- surcharges;
- product and channel assignment;
- collection reordering; and
- configurable operations.

## Schema-derived choices

Dashboard language and currency choices are derived dynamically from the
schema.
