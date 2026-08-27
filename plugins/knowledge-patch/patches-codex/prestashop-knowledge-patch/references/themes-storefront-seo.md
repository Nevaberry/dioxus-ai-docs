# Themes, Storefront, and SEO

## Hummingbird foundation

Hummingbird in PrestaShop 9.0.0 is a new, optional theme foundation rather
than the default. It uses:

- Bootstrap 5
- TypeScript
- BEM naming
- a directory layout that moves away from the legacy `_dev` structure
- layered SCSS based on CSS `@layer`

Bootstrap and PrestaShop-specific styles are separated for overrides.
Bootstrap dark mode can be enabled with an SCSS variable.

## Default-theme handling

Fresh PrestaShop 9.1.0 installations use Hummingbird 2.0 instead of Classic.
Code that needs the distribution default can call:

```php
Theme::getDefaultTheme()
```

Use that method rather than hard-coding `classic`. Theme activation can unhook
modules designated by the theme.

## Front-office presentation services

As of 9.0.0, categories, manufacturers, suppliers, and stores are rendered
through Presenters for a standardized presentation path.

An experimental Symfony container is also available in the front office.
Modules that use it should treat it as experimental.

## Media, cart notice, and navigation

PrestaShop 9.0.0 adds native WebP and AVIF support.

The front office adds an option to notify a visitor when the viewed product is
already in their cart. It also permits guest ordering even when an account
already exists.

Product breadcrumbs follow the category through which the product was
accessed.

## URLs, redirects, and indexing

Product URLs omit the category by default in 9.0.0.

Shops can remove the default-language prefix to avoid redirects when another
language is added.

Inactive categories can issue either 301 or 302 redirects. Filtered
product-listing pages are excluded from indexing.

PrestaShop 9.1.0 marks Ajax controllers `noindex` to keep internal endpoints
out of search indexes.

## Search queries

Search queries accept special characters in 9.1.0. Custom search integrations
should preserve them rather than assuming core search rejects or strips them.
