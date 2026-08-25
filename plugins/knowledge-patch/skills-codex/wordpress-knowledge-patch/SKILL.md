---
name: wordpress-knowledge-patch
description: WordPress
version: null
license: MIT
metadata:
  author: Nevaberry
---


# WordPress Knowledge Patch

Load this skill when upgrading WordPress sites, plugins, themes, blocks, or
editor integrations, or when implementing against the APIs described here.
Use the quick references for compatibility-sensitive decisions and open the
topic guide that matches the work at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [Runtime, upgrades, and security](references/runtime-upgrades-security.md) | PHP requirements, hashing, hooks, query and URL compatibility, dependency changes, corrective and security upgrades |
| [Blocks, patterns, and styles](references/blocks-patterns-styles.md) | Block registration and assets, editor iframe behavior, Core blocks, bindings, patterns, Global Styles |
| [Data and integration APIs](references/data-integration-apis.md) | REST access, calendar and HTML processing, Field and view APIs, abilities, AI, connectors, interactivity, email |
| [Media and administration](references/media-administration.md) | Image handling, media workflows, SVG icons, roles, navigation, Site Editor and plugin-list extensibility |
| [Collaboration and editorial behavior](references/collaboration-editorial.md) | Notes, visibility controls, author notifications, Style Book, deferred features |

## Breaking changes and migration checks

### Meet the PHP runtime requirements

WordPress 6.8 installation and upgrade explicitly require the PHP `hash`
extension. WordPress 7.0 raises the minimum PHP version to 7.4. WordPress 6.9
adds beta support for PHP 8.5 while retaining the older supported range.

### Migrate the renamed transient action

WordPress 6.8 renames `setted_transient` to `set_transient`. Move extension
listeners to the new action.

### Prepare block code for the iframe editor

For new or updated blocks, WordPress 6.9 accepts only `apiVersion` 3 in the
`block.json` schema and warns when version 1 or 2 blocks are registered.

WordPress 7.0 iframes the post editor when every inserted Block API block uses
version 3 or newer. WordPress 7.1 enforces the iframe even with legacy meta
boxes. Extension CSS and JavaScript must handle a separate editor document.

### Recheck removed browser and asset behavior

WordPress 6.9 removes Internet Explorer conditional script and style loading.
WordPress 7.0 permits scripts to depend on modules, removes HTML5 script theme
support, and makes margin-free editor component styles the default.

### Test query-dependent integrations

WordPress 6.9 changes `WP_Query` cache-key generation, although persistent
object-cache drop-ins should remain compatible. Its `get_adjacent_post()`
query changes require compatibility testing for Storefront-derived themes.
Admin-menu search now uses parsed `$_GET` values instead of
`$_SERVER['QUERY_STRING']`.

### Account for bundled dependency updates

WordPress 7.0 updates Backbone to 1.6.1, Requests to 2.0.17, PHPMailer to
7.0.2, and the CodeMirror 5 lint stack, replacing Esprima with Espree.
WordPress 7.1 updates jQuery UI to 1.14.2, which can change dependent plugin
behavior or styling.

## Security and corrective upgrades

### Treat 7.0.2 as a forced security update

WordPress.org enabled forced automatic updates for sites affected by the
critical and high-severity issues addressed in WordPress 7.0.2 instead of
relying only on the normal update path.

### Follow the 6.9 corrective sequence

WordPress 6.9.2 could leave the front end blank when themes passed stringable
objects while loading template files. WordPress 6.9.3 addressed that
regression. WordPress 6.9.4 was then required because some 6.9.2 security fixes
had not been fully applied.

### Apply safer role defaults

WordPress 7.0 excludes Administrator and Editor from the default-role selector
and adds a Site Health warning for an existing unsafe selection. Use
`default_role_dropdown_excluded_roles` to change the excluded role set.

## Block and editor quick reference

### Control block asset loading

WordPress 6.8 adds `should_load_block_assets_on_demand` to choose global or
on-demand block CSS and JavaScript. It also warns about inline `useSelect`
selectors that can cause excess renders. WordPress 6.9 applies on-demand block
styles to Classic themes.

### Register a PHP-only server-rendered block

In WordPress 7.0, declare
`'supports' => array( 'autoRegister' => true )` with a render callback to
register a server-rendered block without a separate client implementation.
PHP-defined attributes are exposed to the editor and can receive generated
DataForm inspector controls.

### Configure Pattern Overrides and content-only editing

WordPress 6.9 adds
`block_bindings_supported_attributes_{$block_type}` for controlling bindable
attributes. In WordPress 7.0, Pattern Overrides work with custom and Core
blocks through those supported attributes.

WordPress 7.0 applies `contentOnly` more broadly to unsynced patterns. Opt out
with `disableContentOnlyForUnsyncedPatterns` or
`block_editor_settings_all`. Declare content attributes with
`"role": "content"` in `block.json`; use `"listView": true` support for a
dedicated List View inspector tab.

### Use newer block and style capabilities

WordPress 7.0 adds per-block custom CSS, `textIndent`, width, height, and
minimum-height supports and presets, plus Button pseudo-element states in
`theme.json`.

WordPress 7.1 adds background-gradient and minimum-width supports, responsive
style variations with configurable viewports, pseudo and custom states, text
shadows, and a design-token theming foundation.

## API and integration quick reference

### Expose and consume abilities

The WordPress 6.9 Abilities API lets Core, plugins, and themes register
functionality in a standardized machine-readable form. WordPress 7.1 adds
filtering to `wp_get_abilities()`, execution lifecycle hooks, a unified
`public` exposure flag, and client-compatible JSON Schema preparation.

WordPress 7.0 adds `@wordpress/core-abilities` for fetching and registering
server abilities through REST and `@wordpress/abilities` for client-side and
hybrid abilities. The `core/abilities` store provides reactive `useSelect`
access.

### Use the AI client and connectors

WordPress 7.0 introduces a provider-agnostic AI client with centralized
request routing and credentials. Plugins can order models with
`using_model_preference()`, select by required capabilities, build calls with
`WP_AI_Client_Prompt_Builder`, and use `wordpress/wp-ai-client` for transition
compatibility.

The WordPress 7.0 Connectors API discovers providers from the AI Client
registry and supplies the Settings > Connectors screen. Metadata supports
`api_key` and `none` authentication. `wp_connectors_init` can override
connector metadata; other authentication methods can use the PHP registry;
client-side registration customizes the UI.

### Use current Interactivity API behavior

WordPress 6.9 adds unique directive IDs and the router-region `attachTo`
CSS-selector property. WordPress 7.0 adds signal-tracking `watch()` and the
`data-wp-watch` lifecycle directive. Server directive processing populates
`state.url` until the first client navigation.

## Media, admin, and collaboration quick reference

### Handle current media processing

WordPress 7.1 introduces client-side image processing before upload, REST
dimension validation, size-aware encoding quality, and registration of one
sideloaded file for multiple image sizes. The Media Library grid defaults to
infinite scrolling, with a per-user pagination opt-out.

### Support persistent cross-context navigation

WordPress 7.1 keeps the toolbar across supported front-end, admin, Site
Editor, and Block Editor navigation. Extensions must handle client-side
navigation and each context.

### Respect editorial notifications and Notes

WordPress 6.9 adds threaded block Notes with resolution, editing, and post
author email notification. WordPress 7.1 adds mentions and inline feedback.
In WordPress 7.1, `notify_post_author` has final authority over whether
post-author notifications are sent.

### Do not assume deferred features shipped

In WordPress 7.1, the Classic block remains in the inserter, React 19 remains
experimental outside Core, and real-time collaborative editing is not
enabled.
