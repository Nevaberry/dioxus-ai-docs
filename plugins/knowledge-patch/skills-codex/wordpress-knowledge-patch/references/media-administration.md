# Media and administration

## Image metadata and author-link attributes

The WordPress 7.0 `wp_get_image_alttext()` function imports image alt text
from IPTC metadata.

Two author-link functions gain a `$use_title_attr` parameter, while three
author-link functions omit title attributes by default.

## Media processing and library defaults

WordPress 7.1 introduces client-side image processing before upload, REST
dimension validation, size-aware encoding quality, and registration of one
sideloaded file for multiple image sizes.

The Media Library grid defaults to infinite scrolling, with a per-user
pagination opt-out.

## Redesigned media editor

WordPress 7.1 introduces a redesigned media editor. Media-editing workflows and
their interface differ from earlier releases.

## SVG Icon API

WordPress 7.1 provides a Core API for registering and rendering custom SVG
icons.

## Site Editor and plugin-list extensibility

The WordPress 7.0 `@wordpress/boot` package and route validation establish a
path for plugin-defined Site Editor pages. `@wordpress/scripts` can build from
directories with less Webpack dependence.

Custom statuses added with `plugins_list` appear as filter tabs.
`plugins_list_status_text` controls their labels.

## Safer default roles

WordPress 7.0 excludes Administrator and Editor from the default-role selector
and adds a Site Health warning for an existing unsafe selection.
`default_role_dropdown_excluded_roles` changes the excluded role set.

## Admin navigation and styling

WordPress 7.0 introduces the Modern dashboard theme, cross-document admin View
Transitions, a dashboard-wide Command Palette shortcut, and a font-management
page for block, hybrid, and Classic themes.

In WordPress 7.1, the toolbar persists across supported front-end, admin, Site
Editor, and Block Editor navigation. Extensions must handle client-side
navigation and each context.
