# API Lifecycle and Removals

## Stable-version lifecycle and fall-forward behavior

Stable API versions release quarterly at 17:00 UTC, remain supported for at
least 12 months, and overlap consecutive versions by at least nine months.
Requests for an inaccessible version fall forward to the oldest accessible
stable version. Responses and versioned webhooks expose the version actually
used in `X-Shopify-API-Version`.

## Published API access deadlines

Access ends at 15:00 UTC on:

| API version | Date |
| --- | --- |
| `2025-07` | `2026-07-16` |
| `2025-10` | `2026-10-16` |
| `2026-01` | `2027-01-16` |
| `2026-04` | `2027-04-16` |
| `2026-07` | `2027-07-16` |
| `2026-10` | `2027-10-16` |
| `2027-01` | `2028-01-16` |

## Versioned and independently changing surfaces

Quarterly versioning covers:

- Admin GraphQL API
- Customer Account GraphQL API
- Function APIs
- Partner GraphQL API
- Payments Apps GraphQL API
- Storefront GraphQL API
- Webhooks

ShopifyQL follows the selected Admin API version. Admin, Checkout, Customer
Account, and POS UI extension documentation retains only four stable versions,
and Shopify CLI rejects targets older than 12 months.

Hydrogen, Hydrogen React, and Shopify App React Router use major versions.
Ajax, App Home, Catalog, Customer Privacy, Liquid, OAuth, Shop Minis, Shop Pay
Wallet, Storefront Web Components, Web Pixels, and anything not explicitly
listed as versioned can change without a quarterly version boundary.

## Unsupported-resource enforcement

Deprecations can apply across every supported stable version, so pinning an
older version does not defer an explicitly all-version change. Continued use
of an unsupported resource after its deadline can delist an app and block
installs for at least seven days. Admin warnings remain until seven days after
the last detected use.

## Removed banking fields and price-list error codes

`ShopifyPaymentsBankAccount.accountNumber` and
`ShopifyPaymentsBankAccount.routingNumber` were removed.

`PriceListUserErrorCode` lost these values:

- `CONTEXT_RULE_COUNTRIES_LIMIT`
- `CONTEXT_RULE_COUNTRY_TAKEN`
- `CONTEXT_RULE_LIMIT_REACHED`
- `CONTEXT_RULE_MARKET_NOT_FOUND`
- `CONTEXT_RULE_MARKET_TAKEN`
- `COUNTRY_CURRENCY_MISMATCH`
- `CURRENCY_COUNTRY_MISMATCH`
- `MARKET_CURRENCY_MISMATCH`
