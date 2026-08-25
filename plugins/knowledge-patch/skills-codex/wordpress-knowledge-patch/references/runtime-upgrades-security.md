# Runtime, upgrades, and security

## Password hashing and the `hash` extension

WordPress 6.8 makes bcrypt the default password hash. It transparently
rehashes an existing password after a successful login. Installation and
upgrade explicitly require the PHP `hash` extension.

## PHP compatibility boundaries

WordPress 6.9 adds beta support for PHP 8.5 while retaining the older supported
range. WordPress 7.0 raises the minimum PHP version to 7.4.

## Transient action rename

WordPress 6.8 renames `setted_transient` to `set_transient`. Extensions
listening to the old action must migrate.

## Query compatibility

WordPress 6.9 changes `WP_Query` cache-key generation, although persistent
object-cache drop-ins should remain compatible. Admin-menu search now uses
parsed `$_GET` values instead of `$_SERVER['QUERY_STRING']`.

The `get_adjacent_post()` query changes require compatibility testing for
Storefront-derived themes.

## HTTPS defaults in URL sanitizers

In WordPress 6.9, `esc_url()`, `esc_url_raw()`, and `sanitize_url()` can
prepend `https://` to schemeless input when `'https'` is first in the supplied
`$protocols` array.

## Removed legacy browser and asset behavior

WordPress 6.9 removes Internet Explorer conditional script and style loading.
WordPress 7.0 allows scripts to depend on modules, removes HTML5 script theme
support, and makes margin-free editor component styles the default.

## Bundled dependency changes

WordPress 7.0 updates Backbone to 1.6.1, Requests to 2.0.17, PHPMailer to
7.0.2, and the CodeMirror 5 lint stack, replacing Esprima with Espree.

WordPress 7.1 updates jQuery UI to 1.14.2. This can change dependent plugin
behavior or styling.

## Forced security update for 7.0.2

WordPress 7.0.2 addressed critical and high-severity security issues.
WordPress.org therefore enabled forced automatic updates for affected sites
instead of relying only on the normal update path.

## WordPress 6.9 corrective upgrade sequence

WordPress 6.9.2 could leave the front end blank for themes that passed
stringable objects when loading template files. WordPress 6.9.3 addressed that
regression, but WordPress 6.9.4 was then required because some 6.9.2 security
fixes had not been fully applied.
