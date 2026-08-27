# Admin, plugins, and UI

## Dashboard and UI compatibility

### Admin user deletion (since 2.12.0)

Admin users can now delete other users. This capability precedes the planned permissions system, so integrations should not assume fine-grained deletion permissions are available in this release.

### Dashboard upload size limit (since 2.12.0)

The Admin dashboard now limits file uploads to 1 MB and reports clearer upload errors; larger files must not be submitted through that UI flow.

### Feed-only Admin notifications (since 2.13.0)

The Admin notification drawer now fetches only notifications whose channel is `feed`. Custom notifications intended for that drawer must use the feed channel; notifications for other channels are excluded because their content does not follow the drawer's required format.

### New Admin configuration and metadata controls (since 2.5.0)

Admins can now update the default Sales Channel and Stock Location. Product Collection and Order pages also expose metadata forms, including editing Order metadata.

### Opinionated UI data tables (since 2.4.0)

`@medusajs/ui` now provides a `DataTable` built on the existing `Table` component and `@tanstack/react-table`. It supplies pagination, sorting, filtering, row selection, and commands without requiring each Admin customization to assemble those behaviors itself.

### React 19 alignment for direct Icons consumers (since 2.14.0)

`@medusajs/icons` now targets React 19. Projects that install the Icons package directly must either upgrade React to 19 or pin an earlier Icons release; indirect consumers need no change.

### React 19 compatibility for UI packages (since 2.2.0)

The Medusa UI and icons packages now include React 19 and React 19 RC in their peer dependencies.

### Required React Router upgrade for direct dependencies (since 2.13.0)

Medusa upgrades `react-router-dom` from `6.20.1` to `6.30.3` for a security fix. Projects that declare the package directly must also upgrade it to `6.30.3`.

### Vite 6 peer compatibility (since 2.6.0)

Medusa now accepts either Vite 5 or Vite 6 as a peer dependency, allowing projects to upgrade to Vite 6 without a peer-dependency conflict.

## Languages and localization

### Additional Admin languages (since 2.4.0)

Medusa Admin now includes Macedonian, Romanian, Chinese, Persian, Czech, Arabic, and Mongolian translations, allowing the dashboard to be used in those languages.

### Admin locale updates (since 2.14.0)

Admin adds Croatian, completes Turkish translations, and adds British English with European-style date and time formatting.

### Lithuanian locale (since 2.13.0)

Lithuanian (`lt-LT`) is now included in the default locale list.

## Plugins and Admin extensions

### Admin extension routing and labels (since 2.12.0)

Custom Admin routes now support React Router splat and optional segments, plus route ranking for resolving custom-route matches. Menu-item extensions can also use internationalized labels.

### Environment variables in plugin Admin extensions (since 2.11.0)

The Admin bundler now forwards environment variables to Admin extensions supplied by plugins, so those extensions can consume their configured build-time environment values.

### Packaged Admin extensions require an export (since 2.7.0)

Plugin builds now emit Admin extensions as both `.medusa/server/src/admin/index.mjs` and `index.js`. Plugin authors must expose those builds through `./admin`; otherwise the dashboard does not recognize the package as an extension source:

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

### Plugin development and Admin extensions (since 2.3.0)

Plugin modules are now merged, and the plugin toolchain adds scaffolding through `create-medusa-app` plus develop, build, publish, add, and database-generation flows. Admin extensions can load from plugin packages or source and are included in the plugin build path.
