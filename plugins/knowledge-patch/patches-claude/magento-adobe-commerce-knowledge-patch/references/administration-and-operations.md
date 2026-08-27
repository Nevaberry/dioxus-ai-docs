# Administration and operations

## Security administration

In Adobe Commerce 2.4.8 (`2.4.8-adobe-commerce`), Duo 2FA uses Web SDK v4 and
Universal Prompt. Admin configuration requires a Client ID and Secret. The OTP
Window default changes from `1` to `29`.

Encryption-key changes and re-encryption of supported configuration, payment,
and custom-field data are CLI-only.

SRI hashes live under `pub/static` by area and survive cache flushes. The
System > Support > Data Collector tool is removed.

## Indexing, ACL, and configuration locks

New indexers default to **Update by Schedule**, while existing indexer modes
are preserved. Switching an index back to **Update on Save** removes its unused
changelog tables and marks it invalid.

Permissions newly introduced by custom modules are no longer automatically
granted to existing roles.

Values locked with `config:set --lock-env` or `--lock-conf` cannot be changed
through Admin forms.

## Adobe Commerce CLI behavior

- `dev:di:info` can target an application area instead of only GLOBAL.
- `setup:di:compile` fails on preferences for missing or excluded classes.
- Magento CLI supports Symfony `CommandLoaderInterface` for deferred command
  initialization.
- Maintenance-mode IP allowlists accept CIDR ranges.
- `maintenance:status` reports **enabled/disabled** instead of
  **active/not active**.

## Cache behavior

The built-in full-page cache removes marketing query parameters in the same way
as Varnish. Varnish exclusions include `gad_source`, `srsltid`, and `msclkid`.
This prevents campaign parameters from multiplying cache entries.

Redis cache garbage collection enables Lua mode by default to avoid cache-tag
cleanup races.

## Adobe Commerce frontend output

- A new critical-head block places critical CSS before other assets.
- Developer-mode server-side LESS compilation emits source maps.
- Grunt-generated source-map paths no longer include the `/pub` prefix.
- Static deployment excludes CSS belonging to disabled modules.

## Magento Open Source product layouts

In Magento Open Source 2.4.8 (`2.4.8-magento-open-source`), frontend product
layouts can be selected by attribute set in addition to the existing SKU- and
product-type-based choices.

## Environment, cron, and Varnish

`MAGENTO_DC_INDEXER__USE_APPLICATION_LOCK` parses `false` as a Boolean rather
than a truthy string, so this setting disables application locking as intended:

```dotenv
MAGENTO_DC_INDEXER__USE_APPLICATION_LOCK=false
```

Cron groups running in separate processes retain both standard output and
standard error in logs.

Admin adds an **Export VCL for Varnish 7** action.

## Region configuration during upgrade

When an upgrade adds a country with required states or regions, Magento Open
Source adds only that country to `general/region/state_required`. It does not
reset the merchant's configured list to the default set.
