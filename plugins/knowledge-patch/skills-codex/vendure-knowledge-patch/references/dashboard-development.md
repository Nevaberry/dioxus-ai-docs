# Dashboard Development

## Package and build modes

`DashboardPlugin` is exported from `@vendure/dashboard`. The old AdminUiPlugin
`compatibilityMode` is deprecated.

Dashboard builds support Vite 7, user stylesheets, and an opt-in pre-bundled
mode through `useExperimentalBundle`.

## Routing and authentication

Dashboard extensions can define unauthenticated routes, TanStack Router
`validateSearch`, and router-plugin options. The Dashboard supports
bearer-token authentication and custom React providers.

## Shell extension points

Extensions can:

- Replace the login screen.
- Supply static or functional `navSections`.
- Add header `toolbarItems`.
- Extend the `ActionBar`.
- Conditionally add or replace page blocks.

Navigation, custom fields, widgets, and custom pages can be permission-gated.

## Forms and field components

Extensions can replace detail-form inputs, provide custom input and display
components, and transform relation fields.

## Detail-page and list queries

Extensions can extend detail-page and list-query documents. Detail pages
receive their entity object.

List columns can be disabled or given configurable default visibility.

## Tables and bulk actions

The Dashboard exposes bulk actions globally and per row, including hooks for
product variants and collections.

Data tables support:

- Saved views.
- Customizable custom-field columns.
- Date-range widget filters.
- Configurable column-view defaults.

## Merchant workflows

The Dashboard handles:

- Multiple-currency prices.
- Stock across multiple locations.
- Split orders.
- Draft-order modification.
- Refunds and surcharges.
- Product and channel assignment.
- Collection reordering.
- Configurable operations.

## Schema-derived choices

Dashboard language and currency choices are derived dynamically from the
schema.

_Source batch: `official-changelog-2025-current`._
