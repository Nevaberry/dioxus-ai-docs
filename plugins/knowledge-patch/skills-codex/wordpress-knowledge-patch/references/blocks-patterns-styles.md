# Blocks, patterns, and styles

## On-demand block assets and speculative loading

WordPress 6.8 adds `should_load_block_assets_on_demand` to choose global or
on-demand block CSS and JavaScript. It also introduces Speculation Rules API
prefetching and prerendering and a `useSelect` warning for inline selectors
that can cause excess renders.

WordPress 6.9 applies on-demand block styles to Classic themes.

## Post editor iframe migration

For new or updated blocks, the WordPress 6.9 `block.json` schema accepts only
`apiVersion` 3 and warns when versions 1 or 2 are registered.

WordPress 7.0 iframes the post editor when every inserted Block API block uses
version 3 or newer. WordPress 7.1 enforces the iframe even with legacy meta
boxes, so extension CSS and JavaScript must handle a separate editor document.

## Expanded Core blocks

WordPress 6.9 adds Math with MathML and LaTeX rendering, Accordion, Terms
Query, Comments Link, and Comments Count blocks, plus `fitText`.

WordPress 7.0 adds Heading, Icons, Breadcrumbs, and Navigation Overlay Close
blocks, block-built mobile navigation overlays, Gallery lightbox slideshows,
and video backgrounds in Cover.

WordPress 7.1 lets Query Loop exclude the current post. Supported blocks remain
editable in Custom HTML previews.

## Block Bindings and Pattern Overrides

WordPress 6.9 adds
`block_bindings_supported_attributes_{$block_type}` for controlling bindable
attributes.

In WordPress 7.0, Pattern Overrides work with custom and Core blocks through
those supported attributes. Bound values render for static and dynamic blocks,
but complex static attributes may require a render callback when the HTML API
cannot process them.

## Pattern `contentOnly` behavior

WordPress 7.0 applies `contentOnly` more broadly to unsynced patterns. Opt out
with `disableContentOnlyForUnsyncedPatterns` or
`block_editor_settings_all`.

Content attributes should declare `"role": "content"` in `block.json`.
Blocks can declare `"listView": true` support for a dedicated List View
inspector tab.

## PHP-only block registration

A server-rendered block in WordPress 7.0 can declare
`'supports' => array( 'autoRegister' => true )` with a render callback to
register without a separate client implementation. PHP-defined attributes are
exposed to the editor and can receive generated DataForm inspector controls.

## Block and Global Styles capabilities

WordPress 7.0 adds per-block custom CSS, `textIndent`, width, height, and
minimum-height supports and presets, plus Button pseudo-element states in
`theme.json`.

WordPress 7.1 adds background-gradient and minimum-width supports, responsive
style variations with configurable viewports, pseudo and custom states, text
shadows, and a design-token theming foundation.
