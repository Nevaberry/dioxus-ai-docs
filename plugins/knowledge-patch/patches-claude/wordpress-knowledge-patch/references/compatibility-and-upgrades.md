# Compatibility and upgrades

## Runtime, installation, and authentication

### Bcrypt password hashes (WordPress 6.8)

WordPress makes bcrypt the default password hash. After a successful login,
an existing password is transparently rehashed.

Installation and upgrade explicitly require the PHP `hash` extension.

### PHP compatibility boundaries

WordPress 6.9 adds beta support for PHP 8.5 while retaining the older
supported range. WordPress 7.0 raises the minimum PHP version to 7.4.

## Hook and query compatibility

### Transient action rename (WordPress 6.8)

The `setted_transient` action is renamed to `set_transient`. Extensions
listening to the old hook must migrate.

### `WP_Query` and request parsing (WordPress 6.9)

`WP_Query` cache-key generation changes, though persistent object-cache
drop-ins should remain compatible.

Admin-menu search uses parsed `$_GET` values instead of
`$_SERVER['QUERY_STRING']`.

Changes to the `get_adjacent_post()` query require compatibility testing for
Storefront-derived themes.

## URL and browser behavior

### HTTPS defaults in URL sanitizers (WordPress 6.9)

`esc_url()`, `esc_url_raw()`, and `sanitize_url()` can prepend `https://` to
schemeless input when `'https'` is first in the supplied `$protocols` array.

### Legacy browser and asset behavior

WordPress 6.9 removes Internet Explorer conditional script and style loading.

WordPress 7.0 allows scripts to depend on modules, removes HTML5 script theme
support, and makes margin-free editor component styles the default.

## Bundled dependency changes

### WordPress 7.0 dependencies

WordPress updates:

- Backbone to 1.6.1.
- Requests to 2.0.17.
- PHPMailer to 7.0.2.
- The CodeMirror 5 lint stack, replacing Esprima with Espree.

### WordPress 7.1 dependency

WordPress updates jQuery UI to 1.14.2. This can change dependent plugin
behavior or styling.

## Release operations

### Forced security update for WordPress 7.0.2

WordPress 7.0.2 addressed critical and high-severity security issues.
WordPress.org enabled forced automatic updates for affected sites rather than
relying only on the normal update path.

### WordPress 6.9 corrective upgrade sequence

WordPress 6.9.2 could leave the front end blank for themes that passed
stringable objects when loading template files. WordPress 6.9.3 addressed
that regression. WordPress 6.9.4 was then required because some WordPress
6.9.2 security fixes had not been fully applied.

### Features deferred from WordPress 7.1

The Classic block remains available in the inserter. React 19 remains
experimental outside Core. Real-time collaborative editing is not enabled in
WordPress 7.1.
