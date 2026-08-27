# Platform, Upgrades, and Security

## Runtime and build requirements

PrestaShop 9.0.0 is based on Symfony 6.4 LTS and supports PHP 8.1 through 8.4.
Because this is a major release, existing modules and themes may need
compatibility updates and should be tested before a shop upgrade.

PrestaShop 9.1.0 supports PHP 8.1 through 8.5 and requires Composer 2, Node.js
20, and NPM 10. Core asset builds default to Node.js 20.19.5.

## Update Assistant

The upgrade module formerly called 1-Click Upgrade is named Update Assistant
as of 9.0.0. Version 7 provides guided backup, update, and restore flows, plus a
CLI for automated upgrades. It also exposes more detailed requirement checks,
logs, and error reports.

Update Assistant 7.6 supports upgrades from 9.0.x to 9.1. It checks installed
modules against the target version and automatically uninstalls modules it
finds incompatible.

Beta and RC1 installations cannot be upgraded to final 9.1 with Update
Assistant and require a fresh installation.

Regular module upgrades separate download from installation into two steps in
9.1.0.

## Console maintenance commands

PrestaShop 9.1.0 makes thumbnail regeneration, search indexing, and
module-translation export available from the console:

```bash
php bin/console prestashop:thumbnails:regenerate
php bin/console prestashop:search:index
php bin/console prestashop:module:export-translations --help
```

## Installation and debugging security

In 9.0.0, debug mode can be restricted to users carrying a specific cookie.

Fresh 9.0.0 installations randomize the database table prefix by default.
Installation in 9.1.0 can explicitly use a static database prefix when a
deterministic prefix is needed.

PrestaShop 9.0.0 protects direct access to PHP files and improves tracking for
module install, update, and uninstall actions.

## Security fixes and indexing protection

PrestaShop 9.1.0 fixes:

- stored XSS in back-office templates (`GHSA-35pf-37c6-jxjv`)
- improper use of the validation framework (`GHSA-283w-xf3q-788v`)
- exposure of sensitive product attributes in the front office

Ajax controllers are also marked `noindex` to keep internal endpoints out of
search indexes.

PrestaShop 9.1.5 fixes five security issues and closes the 9.1.x release line
ahead of 9.2. Shops remaining on the 8.2 branch should update to 8.2.8, which
fixes five reported vulnerabilities.

## Distribution packages

The Classic download in 9.0.0 includes these modules:

- PrestaShop Checkout
- Account
- Marketplace in the back office
- CloudSync
- Shipping
- Marketing
- Socials

A custom ZIP built with the PrestaShop Release Creation Tool omits those
PrestaShop SA modules.
