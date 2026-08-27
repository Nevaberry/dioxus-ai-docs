# Data and integration APIs

## Public menu access through REST

The WordPress 6.8 `rest_menu_read_access` filter controls whether navigation
menus, menu items, and menu locations are publicly readable through the REST
API.

## Calendar post-type support

In WordPress 6.8, `get_calendar()` supports post types. The new
`get_calendar_args` filter can alter its arguments.

## Field, DataViews, DataForm, and View Config APIs

WordPress 6.9 expands Field API types, validated edit controls, filter
operators, user-input filters, and `readOnly`.

DataViews gains custom `children` layouts, infinite scrolling, text actions,
and persistence through `@wordpress/views`. DataForm gains panel, card, and
row layouts plus controlled validation.

WordPress 7.0 adds Activity and Details layouts and third-party field types.
WordPress 7.1 adds View Config controls for filtering Site Editor screens,
views, and layouts.

## Streaming block parsing

The WordPress 6.9 `WP_Block_Processor` scans and adjusts block structure in
HTML without changing text. It can produce a nested structural view with
parsed JSON attributes.

## Abilities API evolution

The WordPress 6.9 Abilities API lets Core, plugins, and themes register
functionality in a standardized machine-readable form.

WordPress 7.1 adds filtering to `wp_get_abilities()`, execution lifecycle
hooks, a unified `public` exposure flag, and client-compatible JSON Schema
preparation.

## Client-side abilities

WordPress 7.0 adds `@wordpress/core-abilities` to fetch and register server
abilities through REST and `@wordpress/abilities` for client-side and hybrid
abilities.

Abilities support categories, metadata, filtering, querying, unregistering,
and reactive `useSelect` access through the `core/abilities` store.

## Core AI client

WordPress 7.0 introduces a provider-agnostic AI client with centralized
request routing and credentials. Plugins can order models with
`using_model_preference()`, select by required capabilities, build calls with
`WP_AI_Client_Prompt_Builder`, and use the `wordpress/wp-ai-client` package for
transition compatibility.

## Connectors API

The WordPress 7.0 Connectors API discovers providers from the AI Client
registry and supplies the Settings > Connectors screen. Metadata supports
`api_key` and `none` authentication.

The `wp_connectors_init` action can override connector metadata. Other
authentication methods can use the PHP registry, and client-side registration
customizes the UI.

## Interactivity API changes

WordPress 6.9 adds unique directive IDs and the router-region `attachTo`
CSS-selector property.

WordPress 7.0 adds signal-tracking `watch()` and the `data-wp-watch` lifecycle
directive. It populates `state.url` during server directive processing until
the first client navigation.

## HTML API changes

In WordPress 6.9, `WP_HTML_Processor::serialize_token()` becomes public for
safe HTML modification and composition. `set_modifiable_text()` now rejects
SCRIPT contents that could interfere with the element's closing tag.

## Email handling and embedded images

WordPress 6.9 makes `wp_mail()` sender handling extensible, preserves encoding
headers between calls, and delegates content-type handling more consistently
to PHPMailer. HTML mail can embed images and reference them with `cid:` URLs.
