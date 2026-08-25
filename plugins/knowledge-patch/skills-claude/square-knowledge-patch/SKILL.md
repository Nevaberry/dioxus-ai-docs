---
name: square-knowledge-patch
description: Square
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Square Knowledge Patch

Use this skill for Square API, SDK, catalog, inventory, order, payment,
Terminal, Labor, location, reporting, and Web Payments work covered by the
topics below. Read the reference file for the area being changed before
choosing fields, endpoint names, status values, or migration steps.

## Reference index

| Reference | Topics |
| --- | --- |
| [API and SDK migrations](references/api-and-sdk-migrations.md) | Customer cards, Reader SDK, language SDK rewrites, Timecards, inventory movement, loyalty, offline payment requests |
| [Payments, cards, and disputes](references/payments-cards-and-disputes.md) | Refunds, gift cards, disputes, bank accounts, fees, surcharges, payment-source diagnostics |
| [Web and mobile payments](references/web-and-mobile-payments.md) | Card tokenization, ACH, wallets, secure contexts, Afterpay, token result types |
| [Catalog, orders, and inventory](references/catalog-orders-and-inventory.md) | Modifiers, kitchen fields, vendors, adjustment reasons, fulfillments, transfer orders, subscriptions |
| [Customers, invoices, subscriptions, and labor](references/customer-commerce-and-labor.md) | Invoice links, completed subscriptions, scheduling, GraphQL Labor |
| [Terminal, locations, and devices](references/terminal-locations-and-devices.md) | Terminal defaults and regions, receipt fields, device details and GraphQL |
| [Platform integration and reporting](references/platform-integration-and-reporting.md) | Webhooks, OAuth, Reporting API, Channels API, SDK webhook objects, Marketplace, MCP server |

## Breaking changes and deprecations

### Replace `Customer.cards`

With Square API version `2025-01-23`, `Customer.cards` is retired.

- Enumerate cards with `ListCards?customer_id=...`.
- Enumerate gift cards with `ListGiftCards?customer_id=...`.
- `CreateCustomerCard` and `DeleteCustomerCard` remain deprecated; no
  retirement date is given for them here.

### Move from Reader SDK

Reader SDK and its Mobile Authorization API were scheduled for retirement on
December 31, 2025. Migrate to Mobile Payments SDK and use its authorization
methods.

### Follow rewritten SDK migration guides

The rewritten SDK generations change class and method shapes and add
auto-pagination:

| Language | SDK generation | Additional requirement or behavior |
| --- | ---: | --- |
| Node.js | 40 | Uses native `fetch` |
| PHP | 41 | — |
| Java | 44 | — |
| .NET | 41 | — |
| Python | 42 | Python 3.8+, Pydantic validation, and `ApiError`-derived exceptions |
| Ruby | 44 | Ruby 3.1+ |

Follow the migration guide for the relevant language when continuing API
updates.

### Use Timecard equivalents

All `Shift` endpoints, types, and webhooks are deprecated in favor of
`Timecard` equivalents for create, update, delete, retrieve, and search.
`GetShift` becomes `RetrieveTimecard`. In GraphQL, `timecards` replaces the
deprecated `shifts` entry point.

### Replace retired loyalty reward definitions

`LoyaltyProgramRewardTier.definition` is retired. Resolve reward discount
details through `pricing_rule_reference`.

### Remove retired inventory movement shapes

As of Square version `2026-07-15`, cross-location movement is an `ADJUSTMENT`
with `from_location_id` and `to_location_id`. The following are retired:

- `TRANSFER`
- `InventoryTransfer`
- `RetrieveInventoryTransfer`
- `InventoryAdjustment.location_id`

Responses can expose `UNTRACKED` plus Square-generated inferred and component
adjustments.

### Update Web Payments SDK integrations

As of October 1, 2025, Web Payments SDK integrations must run in a secure HTTPS
context; insecure HTTP contexts are unsupported.

For ACH:

- `ach()` no longer requires `redirectURI`; `transactionId` is optional.
- Replace deprecated `AchChargeTokenOptions.total` with separate `amount` and
  `currency` arguments.
- Catch `InvalidOptionError` for a missing name. `PlaidMissingNameError`
  remains for backward compatibility but is no longer emitted.

Token status values now return strings. `PaymentRequestEvent` and `MethodType`
are string-union types rather than enumerations.

### Account for offline-payment retirement

`CreatePayment.offline_payment_details` was deprecated in August and scheduled
for retirement on November 19, 2025.

## High-use payment changes

### Consolidated card tokenization

In Beta, `Card.tokenize()` supports a consolidated flow for payment processing,
buyer verification, and storing, charging, or both charging and storing a card
on file.

### Payment diagnostics

- `Payment.BuyNowPayLaterDetails.errors` and
  `Payment.DigitalWalletDetails.errors` expose source-specific failures.
- The card nested under `CardPaymentDetails` adds `created_at` and
  `disabled_at`.
- New error codes are `PARTIAL_PAYMENT_DELAY_CAPTURE_NOT_SUPPORTED`,
  `PAYMENT_SOURCE_NOT_ENABLED_FOR_TARGET`, and `AMOUNT_TOO_LOW`.
- Failed Square gift-card payments always return
  `GIFT_CARD_AVAILABLE_AMOUNT` with `INSUFFICIENT_FUNDS`, even without partial
  authorization, on every Square API version.

### Application-fee allocations

`Payment.app_fee_allocations` can distribute one application fee among up to
three parties. For a refund of a payment that used allocations, set
`PaymentRefund.app_fee_allocations` to control each party's contribution.

### Card and wallet details

- Read-only Beta `Card` fields are `hsa_fsa`, `issuer_alert`, and
  `issuer_alert_at`; supported Mastercard cards can report
  `ISSUER_ALERT_CARD_CLOSED`.
- `CreateCard` accepts ZIP+4 billing `postal_code` values such as
  `12345-6789`.
- `CardPaymentDetails.wallet_type` identifies Apple Pay payments.
- `ElectronicMoneyDetails` represents Japanese e-money payments and exposes
  `felica_details` for FeliCa.

## High-use commerce changes

### Catalog modifiers

Modifier-list selection constraints can live at list level. Nested modifier
lists are available in Beta through `CatalogModifier.child_modifier_list_ids`.
Set `include_options` on `BatchRetrieveCatalogObjects`, `SearchCatalogItems`,
or `SearchCatalogObjects` to include related modifier lists.

Review [Catalog, orders, and inventory](references/catalog-orders-and-inventory.md)
for the complete new and deprecated modifier field map.

### Inventory cost and reasons

In Beta, stock-receiving adjustments accept `cost_money` and `vendor_id`, and
`UpdateInventoryAdjustment` can edit a past adjustment's `quantity`,
`cost_money`, `vendor_id`, and `reason_id`. Writing cost or vendor data requires
an active Retail Plus, Restaurants Plus, or Restaurants Premium subscription.

Beta adjustment reasons use `InventoryAdjustment.reason_id` and provide list,
retrieve, create, update, delete, and restore operations under
`/v2/inventory/adjustment-reasons`. Change history can be filtered by
`reason_ids`; `BatchRetrieveInventoryChanges.sort` orders history by
`occurred_at`.

### Reporting API

The Beta, cube-based Reporting API uses `GET /v1/meta` to discover views,
cubes, measures, dimensions, and segments, then `POST /v1/load` to run
analytical queries. It supports automatic joins across cubes. Authenticate
with a personal access token or an OAuth token carrying `REPORTING_READ`.

### Terminal defaults and surcharges

`PaymentOptions.autocomplete` defaults to `true`. The Terminal API can add
credit-card surcharges in the US, and payments report seller-added card
surcharges.

For the regional Terminal capability matrix, read
[Terminal, locations, and devices](references/terminal-locations-and-devices.md).

## Scope discipline

Apply only guidance relevant to the Square surface in the task. Preserve Beta
and closed-Beta qualifiers, regional limitations, exact endpoint and field
names, and stated retirement wording. Do not infer a completed retirement from
a scheduled retirement date.
