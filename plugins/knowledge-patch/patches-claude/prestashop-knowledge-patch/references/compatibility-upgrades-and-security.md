# Compatibility, Upgrades, and Security

## Runtime and upgrade baseline

PrestaShop 9 is based on Symfony 6.4 LTS and supports PHP 8.1 through 8.4
(since 9.0.0). Because it is a major release, existing modules and themes may
need compatibility updates and should be tested before a shop upgrade.

PrestaShop 9.1 supports PHP 8.1 through 8.5 and requires Composer 2, Node.js
20, and NPM 10. Core asset builds default to Node.js 20.19.5 (since 9.1.0).

## Installation behavior

Fresh installations randomize the database table prefix by default, and
direct access to PHP files is protected (since 9.0.0). Module install, update,
and uninstall actions also receive improved tracking.

Installation can explicitly use a static database prefix when a deterministic
prefix is needed (since 9.1.0).

## Debug-mode access

Debug mode can be restricted to users carrying a specific cookie (since
9.0.0).

## Update Assistant

The upgrade module formerly named 1-Click Upgrade is named Update Assistant
(since 9.0.0). Version 7 provides:

- guided backup, update, and restore flows;
- a CLI for automated upgrades;
- more detailed requirement checks;
- more detailed logs and error reports.

Update Assistant 7.6 supports upgrades from 9.0.x to 9.1 (since 9.1.0). It
checks installed modules against the target version and automatically
uninstalls modules it finds incompatible.

Beta and RC1 installations cannot be upgraded to final 9.1 with Update
Assistant and require a fresh installation. Regular module upgrades separate
download from installation into two steps.

## Distribution packages

The Classic download includes these modules (since 9.0.0):

- PrestaShop Checkout
- Account
- Marketplace in the back office
- CloudSync
- Shipping
- Marketing
- Socials

A custom ZIP made with the PrestaShop Release Creation Tool omits those
PrestaShop SA modules.

## Security changes

PrestaShop 9.1 fixes the following security issues (since 9.1.0):

- stored XSS in back-office templates (`GHSA-35pf-37c6-jxjv`);
- improper use of the validation framework (`GHSA-283w-xf3q-788v`);
- exposure of sensitive product attributes in the front office.

Ajax controllers are also marked `noindex` to keep internal endpoints out of
search indexes.

## Current security releases

PrestaShop 9.1.5 fixes five security issues and closes the 9.1.x release line
ahead of 9.2. Shops remaining on the 8.2 branch should update to 8.2.8, which
fixes five reported vulnerabilities.
