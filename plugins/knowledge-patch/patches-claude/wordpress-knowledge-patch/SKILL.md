---
name: wordpress-knowledge-patch
description: WordPress
version: null
license: MIT
metadata:
  author: Nevaberry
---


# WordPress Knowledge Patch

Use this skill for WordPress core, plugin, theme, editor, REST API, media,
administration, and upgrade work when the changes below may affect the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility-and-upgrades.md](references/compatibility-and-upgrades.md) | PHP requirements, hook and query compatibility, browser and asset changes, dependency updates, security and corrective upgrades |
| [blocks-editor-and-styles.md](references/blocks-editor-and-styles.md) | Block assets, editor iframe, block APIs, Interactivity and HTML APIs, patterns, styles, Notes, Core blocks |
| [data-abilities-and-extension-apis.md](references/data-abilities-and-extension-apis.md) | REST access, calendar, Fields, DataViews, DataForm, View Config, Abilities, AI Client, Connectors, Site Editor extension APIs |
| [media-admin-and-communications.md](references/media-admin-and-communications.md) | Mail, media, icons, roles, admin navigation, plugin lists, author links, notifications, release-visible interfaces |

## Breaking changes and upgrade hazards

### Password hashing and installation requirements

WordPress 6.8 makes bcrypt the default password hash and transparently
rehashes an existing password after a successful login. Installation and
upgrade explicitly require the PHP `hash` extension.

### Renamed transient action

WordPress 6.8 renames `setted_transient` to `set_transient`. Extensions that
listen to the old action must migrate.

### Block API version and editor iframe

For new or updated blocks, WordPress 6.9 accepts only `apiVersion` 3 in the
`block.json` schema and warns when version 1 or 2 is registered. WordPress 7.0
iframes the post editor when every inserted Block API block uses version 3 or
newer. WordPress 7.1 enforces the iframe even with legacy meta boxes, so
extension CSS and JavaScript must handle a separate editor document.

### PHP minimum

WordPress 6.9 adds beta support for PHP 8.5 while retaining the older
supported range. WordPress 7.0 raises the minimum PHP version to 7.4.

### Query compatibility

WordPress 6.9 changes `WP_Query` cache-key generation, though persistent
object-cache drop-ins should remain compatible. Its `get_adjacent_post()`
query changes require compatibility testing for Storefront-derived themes.
Admin-menu search uses parsed `$_GET` values instead of
`$_SERVER['QUERY_STRING']`.

### Removed and changed asset behavior

WordPress 6.9 removes Internet Explorer conditional script and style loading.
WordPress 7.0 allows scripts to depend on modules, removes HTML5 script theme
support, and makes margin-free editor component styles the default.

### Bundled dependencies

WordPress 7.0 updates Backbone to 1.6.1, Requests to 2.0.17, PHPMailer to
7.0.2, and the CodeMirror 5 lint stack, replacing Esprima with Espree.
WordPress 7.1 updates jQuery UI to 1.14.2, which can change dependent plugin
behavior or styling.

## Release operations

### Forced security update

WordPress.org enabled forced automatic updates for sites affected by the
critical and high-severity issues addressed in WordPress 7.0.2 instead of
relying only on the normal update path.

### WordPress 6.9 corrective sequence

WordPress 6.9.2 could leave the front end blank for themes that passed
stringable objects when loading template files. WordPress 6.9.3 addressed
that regression, but 6.9.4 was then required because some 6.9.2 security
fixes had not been fully applied.

### Features not enabled in WordPress 7.1

The Classic block remains available in the inserter. React 19 remains
experimental outside Core, and real-time collaborative editing is not
enabled.

## High-value Core and extension APIs

### Block asset loading and speculation

WordPress 6.8 adds `should_load_block_assets_on_demand` to choose global or
on-demand block CSS and JavaScript. It also adds Speculation Rules API
prefetching and prerendering. WordPress 6.9 applies on-demand block styles to
Classic themes.

The WordPress 6.8 `useSelect` warning identifies inline selectors that can
cause excess renders.

### Public navigation-menu REST access

In WordPress 6.8, `rest_menu_read_access` controls whether navigation menus,
menu items, and menu locations are publicly readable through the REST API.

### Calendar post types

In WordPress 6.8, `get_calendar()` supports post types and
`get_calendar_args` can alter its arguments.

### HTML API

In WordPress 6.9, `WP_HTML_Processor::serialize_token()` is public for safe
HTML modification and composition. `set_modifiable_text()` rejects SCRIPT
contents that could interfere with the element's closing tag.

### URL sanitizer HTTPS defaults

In WordPress 6.9, `esc_url()`, `esc_url_raw()`, and `sanitize_url()` can
prepend `https://` to schemeless input when `'https'` is first in the supplied
`$protocols` array.

### Abilities

WordPress 6.9 introduces the Abilities API for machine-readable functionality
registered by Core, plugins, and themes. WordPress 7.0 adds server-ability
REST access through `@wordpress/core-abilities` and client-side and hybrid
abilities through `@wordpress/abilities`.

WordPress 7.1 adds filtering to `wp_get_abilities()`, execution lifecycle
hooks, a unified `public` exposure flag, and client-compatible JSON Schema
preparation.

### AI Client and Connectors

WordPress 7.0 introduces a provider-agnostic AI client with centralized
request routing and credentials. Plugins can order models with
`using_model_preference()`, select by required capabilities, and build calls
with `WP_AI_Client_Prompt_Builder`. The `wordpress/wp-ai-client` package
provides transition compatibility.

The WordPress 7.0 Connectors API discovers providers from the AI Client
registry and supplies Settings > Connectors. Connector metadata supports
`api_key` and `none` authentication. `wp_connectors_init` can override
metadata, other authentication methods can use the PHP registry, and
client-side registration customizes the UI.

## Block editor quick reference

### Binding and pattern controls

WordPress 6.9 adds
`block_bindings_supported_attributes_{$block_type}` to control bindable
attributes. WordPress 7.0 extends Pattern Overrides to custom and Core blocks
through those attributes. Complex static attributes may require a render
callback when the HTML API cannot process them.

WordPress 7.0 applies `contentOnly` more broadly to unsynced patterns. Opt out
with `disableContentOnlyForUnsyncedPatterns` or
`block_editor_settings_all`. Content attributes should declare
`"role": "content"` in `block.json`; `"listView": true` enables a dedicated
List View inspector tab.

### PHP-only server-rendered blocks

In WordPress 7.0, a server-rendered block can declare
`'supports' => array( 'autoRegister' => true )` with a render callback and no
separate client implementation. PHP-defined attributes are exposed to the
editor and can receive generated DataForm inspector controls.

### Interactivity lifecycle

WordPress 6.9 adds unique directive IDs and the router-region `attachTo`
CSS-selector property. WordPress 7.0 adds signal-tracking `watch()` and the
`data-wp-watch` lifecycle directive. During server directive processing,
`state.url` is populated until the first client navigation.

### Fields and data-driven views

WordPress 6.9 expands Field API types, edit controls, filters, and `readOnly`;
DataViews adds custom layouts, infinite scrolling, text actions, and
`@wordpress/views` persistence; DataForm adds panel, card, and row layouts
with controlled validation. Later additions include Activity and Details
layouts, third-party field types, and View Config filtering controls. See the
data API reference for exact version attribution.

### Notes and visibility

WordPress 6.9 adds threaded block notes with resolve, edit, and post-author
email notification behavior, plus hide and reveal controls. WordPress 7.0
adds device-specific visibility rules. WordPress 7.1 expands Notes with
mentions and inline feedback.

## Focused references

Use the indexed references for the full durable guidance. They retain the
version-specific details for Core blocks, styles, media processing, admin
navigation, email, notifications, DataViews, Abilities, and extension APIs.
