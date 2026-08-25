# Admin, storefront, and tooling

## Admin UI capabilities

### React 19 compatibility for UI packages (2.2.0)

The Medusa UI and icons packages include React 19 and React 19 RC in their peer
dependencies.

### Opinionated UI data tables (2.4.0)

`@medusajs/ui` provides a `DataTable` built on `Table` and
`@tanstack/react-table`. It supplies pagination, sorting, filtering, row
selection, and commands without requiring every Admin customization to
assemble them.

### Additional Admin languages (2.4.0)

Medusa Admin includes Macedonian, Romanian, Chinese, Persian, Czech, Arabic,
and Mongolian translations.

### New Admin configuration and metadata controls (2.5.0)

Admins can update the default Sales Channel and Stock Location. Product
Collection and Order pages expose metadata forms, including Order metadata
editing.

### Product Tag metadata (2.10.0)

Product Tags have a metadata field. Admin can create and edit those metadata
values.

### Admin user deletion (2.12.0)

Admin users can delete other users. This predates the planned permissions
system, so integrations must not assume fine-grained deletion permissions in
this release.

### Dashboard upload size limit (2.12.0)

The Admin dashboard limits file uploads to 1 MB and reports clearer upload
errors. Do not submit larger files through that UI flow.

### Feed-only Admin notifications (2.13.0)

The Admin notification drawer fetches only notifications whose channel is
`feed`. Custom notifications for the drawer must use that channel. Other
channels are excluded because their content does not follow the drawer's
required format.

### Lithuanian locale (2.13.0)

Lithuanian (`lt-LT`) is included in the default locale list.

### Stock-location metadata in Admin (2.14.0)

Admin provides a Stock Location metadata form for operators to view and edit
custom metadata.

### Admin locale updates (2.14.0)

Admin adds Croatian, completes Turkish translations, and adds British English
with European-style date and time formatting.

## Plugins and Admin extensions

### Plugin development and Admin extensions (2.3.0)

Plugin modules are merged. The plugin toolchain adds scaffolding through
`create-medusa-app` plus develop, build, publish, add, and database-generation
flows. Admin extensions load from plugin packages or source and participate in
the plugin build path.

### Packaged Admin extensions require an export (2.7.0)

Plugin builds emit Admin extensions as
`.medusa/server/src/admin/index.mjs` and `index.js`. Expose them through
`./admin`; otherwise the dashboard does not recognize the package as an
extension source:

```json
{
  "exports": {
    "./admin": {
      "import": "./.medusa/server/src/admin/index.mjs",
      "require": "./.medusa/server/src/admin/index.js",
      "default": "./.medusa/server/src/admin/index.js"
    }
  }
}
```

### Environment variables in plugin Admin extensions (2.11.0)

The Admin bundler forwards environment variables to Admin extensions supplied
by plugins, allowing them to consume configured build-time values.

### Admin extension routing and labels (2.12.0)

Custom Admin routes support React Router splat and optional segments and use
route ranking to resolve custom-route matches. Menu-item extensions support
internationalized labels.

## Store API and product behavior

### Store product-type and product-tag endpoints (2.4.0)

The Store API exposes product-type and product-tag endpoints, making both
resources available to storefront clients.

### Variant updates preserve prices (2.5.0)

Updating variants no longer unintentionally unsets their prices. Integrations
do not need to restore prices after an update.

### Product-variant search by product fields (2.8.0)

Product-variant searches can match properties of the variant's product rather
than only fields on the variant itself.

### Published-only cart additions (2.11.0)

`addToCartWorkflow` permits only published products. Attempts to add unpublished
products do not proceed through the core flow.

### Variant identifier filters (2.14.0)

Store and Admin APIs support variant filtering by `sku`, `barcode`, `ean`, and
`upc`.

### Product export behavior (2.14.0)

Product export includes variant images and no longer fails when a
`sales_channel_id` filter is supplied.

## SDK and project tooling

### SDK token retrieval (2.9.0)

The JS SDK client lets callers retrieve the token it holds, exposing that
credential when an integration needs it outside normal client request helpers.

### Package-manager-aware project creation (2.13.0)

`create-medusa-app` uses the package manager that launched it, including pnpm.
Override the choice with `--use-npm`, `--use-yarn`, or `--use-pnpm`:

```sh
pnpm dlx create-medusa-app@latest
```
