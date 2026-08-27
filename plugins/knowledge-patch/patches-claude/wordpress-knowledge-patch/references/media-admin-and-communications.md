# Media, administration, and communications

## Email and notifications

### Email handling and embedded images (WordPress 6.9)

`wp_mail()` sender handling is extensible, encoding headers are preserved
between calls, and content-type handling is delegated more consistently to
PHPMailer.

HTML mail can embed images and reference them with `cid:` URLs.

### Post-author notification filtering (WordPress 7.1)

The `notify_post_author` filter has final authority over whether post-author
notifications are sent.

## Image and media APIs

### Image metadata (WordPress 7.0)

`wp_get_image_alttext()` imports image alt text from IPTC metadata.

### Media processing and library defaults (WordPress 7.1)

WordPress introduces client-side image processing before upload, REST
dimension validation, size-aware encoding quality, and registration of one
sideloaded file for multiple image sizes.

The Media Library grid defaults to infinite scrolling, with a per-user
pagination opt-out.

### Redesigned media editor (WordPress 7.1)

WordPress introduces a redesigned media editor. Media-editing workflows and
their interface differ from earlier releases.

### SVG Icon API (WordPress 7.1)

Core provides an API for registering and rendering custom SVG icons.

## Author links and roles

### Author-link attributes (WordPress 7.0)

Two author-link functions gain a `$use_title_attr` parameter. Three
author-link functions omit title attributes by default.

### Safer default roles (WordPress 7.0)

The default-role selector excludes Administrator and Editor. Site Health adds
a warning for an existing unsafe selection.

`default_role_dropdown_excluded_roles` changes the excluded role set.

## Administration and navigation

### Modern dashboard and navigation (WordPress 7.0)

WordPress introduces the Modern dashboard theme, cross-document admin View
Transitions, a dashboard-wide Command Palette shortcut, and a font-management
page for block, hybrid, and Classic themes.

### Persistent toolbar (WordPress 7.1)

The toolbar persists across supported front-end, admin, Site Editor, and
Block Editor navigation. Extensions must handle client-side navigation and
each context.

### Style Book in Classic themes (WordPress 6.8)

The streamlined Style Book is available in select Classic themes. Using it no
longer necessarily requires a block theme.
