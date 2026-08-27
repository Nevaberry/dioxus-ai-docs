# Data, abilities, and extension APIs

## REST and server APIs

### Public menu access through REST (WordPress 6.8)

The `rest_menu_read_access` filter controls whether navigation menus, menu
items, and menu locations are publicly readable through the REST API.

### Calendar post-type support (WordPress 6.8)

`get_calendar()` supports post types. The `get_calendar_args` filter can
alter its arguments.

## Field, DataViews, DataForm, and View Config APIs

### Field API (WordPress 6.9)

The Field API expands its field types, validated edit controls, filter
operators, user-input filters, and `readOnly` support.

### DataViews (WordPress 6.9)

DataViews gains custom `children` layouts, infinite scrolling, text actions,
and persistence through `@wordpress/views`.

### DataForm (WordPress 6.9)

DataForm gains panel, card, and row layouts plus controlled validation.

### Activity, Details, and third-party fields (WordPress 7.0)

The APIs add Activity and Details layouts and third-party field types.

### View Config (WordPress 7.1)

View Config controls can filter Site Editor screens, views, and layouts.

## Abilities APIs

### Server Abilities API (WordPress 6.9)

The Abilities API lets Core, plugins, and themes register functionality in a
standardized machine-readable form.

### Client-side and hybrid abilities (WordPress 7.0)

`@wordpress/core-abilities` fetches and registers server abilities through
REST. `@wordpress/abilities` supplies client-side and hybrid abilities.

Abilities support categories, metadata, filtering, querying, unregistering,
and reactive `useSelect` access through the `core/abilities` store.

### Abilities API evolution (WordPress 7.1)

WordPress adds filtering to `wp_get_abilities()`, execution lifecycle hooks,
a unified `public` exposure flag, and client-compatible JSON Schema
preparation.

## AI Client and Connectors

### Core AI Client (WordPress 7.0)

WordPress introduces a provider-agnostic AI client with centralized request
routing and credentials.

Plugins can:

- Order models with `using_model_preference()`.
- Select models by required capabilities.
- Build calls with `WP_AI_Client_Prompt_Builder`.
- Use the `wordpress/wp-ai-client` package for transition compatibility.

### Connectors API (WordPress 7.0)

The Connectors API discovers providers from the AI Client registry and
supplies the Settings > Connectors screen. Connector metadata supports
`api_key` and `none` authentication.

The `wp_connectors_init` action can override connector metadata. Other
authentication methods can use the PHP registry. Client-side registration
customizes the UI.

## Site Editor and plugin-list extensibility

### Site Editor extension path (WordPress 7.0)

The `@wordpress/boot` package and route validation establish a path for
plugin-defined Site Editor pages. `@wordpress/scripts` can build from
directories with less Webpack dependence.

### Plugin-list statuses (WordPress 7.0)

Custom statuses added with `plugins_list` appear as filter tabs.
`plugins_list_status_text` controls their labels.
