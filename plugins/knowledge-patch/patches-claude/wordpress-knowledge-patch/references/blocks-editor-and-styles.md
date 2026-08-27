# Blocks, editor, and styles

## Asset loading and editor architecture

### On-demand block assets and speculative loading

WordPress 6.8 adds `should_load_block_assets_on_demand` to choose global or
on-demand block CSS and JavaScript. It also adds a `useSelect` warning for
inline selectors that can cause excess renders and introduces Speculation
Rules API prefetching and prerendering.

WordPress 6.9 applies on-demand block styles to Classic themes.

### Post editor iframe migration

For new or updated blocks, the WordPress 6.9 `block.json` schema accepts only
`apiVersion` 3 and warns when versions 1 or 2 are registered.

WordPress 7.0 iframes the post editor when every inserted Block API block uses
version 3 or newer. WordPress 7.1 enforces the iframe even with legacy meta
boxes. Extension CSS and JavaScript must handle a separate editor document.

## Block structure and HTML

### Streaming block parsing (WordPress 6.9)

`WP_Block_Processor` scans and adjusts block structure in HTML without
changing text. It can produce a nested structural view with parsed JSON
attributes.

### HTML API changes (WordPress 6.9)

`WP_HTML_Processor::serialize_token()` is public for safe HTML modification
and composition.

`set_modifiable_text()` rejects SCRIPT contents that could interfere with the
element's closing tag.

## Interactivity API

### Directives and router regions (WordPress 6.9)

The Interactivity API adds unique directive IDs and the router-region
`attachTo` CSS-selector property.

### Watch lifecycle and URL state (WordPress 7.0)

The Interactivity API adds signal-tracking `watch()` and the `data-wp-watch`
lifecycle directive. It populates `state.url` during server directive
processing until the first client navigation.

## Block Bindings and patterns

### Supported binding attributes (WordPress 6.9)

The `block_bindings_supported_attributes_{$block_type}` filter controls
bindable attributes.

### Pattern Overrides (WordPress 7.0)

Pattern Overrides work with custom and Core blocks through supported binding
attributes. Bound values render for static and dynamic blocks. Complex static
attributes may require a render callback when the HTML API cannot process
them.

### Unsynced pattern `contentOnly` behavior (WordPress 7.0)

`contentOnly` applies more broadly to unsynced patterns. Opt out with
`disableContentOnlyForUnsyncedPatterns` or `block_editor_settings_all`.

Content attributes should declare `"role": "content"` in `block.json`.
Blocks can declare `"listView": true` support for a dedicated List View
inspector tab.

## Block registration and inspector controls

### PHP-only registration (WordPress 7.0)

A server-rendered block can declare
`'supports' => array( 'autoRegister' => true )` with a render callback to
register without a separate client implementation.

PHP-defined attributes are exposed to the editor and can receive generated
DataForm inspector controls.

## Block and Global Styles capabilities

### WordPress 7.0

WordPress adds:

- Per-block custom CSS.
- `textIndent` support.
- Width, height, and minimum-height supports and presets.
- Button pseudo-element states in `theme.json`.

### WordPress 7.1

WordPress adds:

- Background-gradient and minimum-width supports.
- Responsive style variations with configurable viewports.
- Pseudo and custom states.
- Text shadows.
- A design-token theming foundation.

## Notes and visibility

### Block notes and visibility (WordPress 6.9)

Editors can attach threaded notes to individual blocks, resolve or edit them,
and notify the post author by email. Editors also gain hide and reveal
controls.

### Device-specific visibility (WordPress 7.0)

Visibility controls extend to device-specific rules exposed in the toolbar,
inspector, command palette, and List View.

### Mentions and inline feedback (WordPress 7.1)

Notes expand with mentions and inline feedback, adding collaboration
affordances beyond block-level threaded comments.

## Expanded Core blocks

### WordPress 6.9

WordPress adds Math with MathML and LaTeX rendering, Accordion, Terms Query,
Comments Link, and Comments Count blocks, plus `fitText`.

### WordPress 7.0

WordPress adds Heading, Icons, Breadcrumbs, and Navigation Overlay Close
blocks, block-built mobile navigation overlays, Gallery lightbox slideshows,
and video backgrounds in Cover.

### WordPress 7.1

Query Loop can exclude the current post. Supported blocks remain editable in
Custom HTML previews.
