# API Versioning and Access

## Stable API lifecycle

Stable API versions release quarterly at 17:00 UTC. Each remains supported for at
least 12 months, and consecutive versions overlap for at least nine months.

When a request names an inaccessible version, Shopify falls it forward to the oldest
accessible stable version. Responses and versioned webhooks expose the version
actually used in `X-Shopify-API-Version`.

## Published access deadlines

| Version | Access ends |
| --- | --- |
| `2025-07` | `2026-07-16 15:00 UTC` |
| `2025-10` | `2026-10-16 15:00 UTC` |
| `2026-01` | `2027-01-16 15:00 UTC` |
| `2026-04` | `2027-04-16 15:00 UTC` |
| `2026-07` | `2027-07-16 15:00 UTC` |
| `2026-10` | `2027-10-16 15:00 UTC` |
| `2027-01` | `2028-01-16 15:00 UTC` |

## Versioned and unversioned surfaces

Quarterly versioning covers:

- Admin GraphQL API
- Customer Account GraphQL API
- Function APIs
- Partner API
- Payments Apps API
- Storefront GraphQL API
- Webhooks

ShopifyQL follows the selected Admin API version. Admin, Checkout, Customer Account,
and POS UI extension documentation retains only four stable versions, and Shopify
CLI rejects targets older than 12 months.

Hydrogen, Hydrogen React, and Shopify App React Router use major versions.

The following can change without a quarterly version boundary: Ajax, App Home,
Catalog, Customer Privacy, Liquid, OAuth, Shop Minis, Shop Pay Wallet, Storefront Web
Components, Web Pixels, and anything else not explicitly listed as versioned.

## Unsupported-resource enforcement

Deprecations can apply across every supported stable version. Pinning an older
version therefore does not defer a change explicitly applied to all versions.

Continued use of an unsupported resource after its deadline can delist an app and
block installs for at least seven days. Admin warnings remain until seven days after
the last detected use.

## Public-app offline tokens

All public apps must use expiring offline access tokens starting January 1, 2027.

## Card-deposit transport

The card-deposit endpoint requires an mTLS certificate.
