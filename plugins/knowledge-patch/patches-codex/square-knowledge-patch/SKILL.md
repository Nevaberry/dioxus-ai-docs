---
name: square-knowledge-patch
description: Square
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Square Knowledge Patch

Use this skill when implementing or updating Square integrations involving
Connect APIs, Square SDKs, Terminal, Web Payments SDK, catalog and inventory,
orders, subscriptions, reporting, labor, devices, or payment operations.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-compatibility.md](references/migrations-and-compatibility.md) | Retired and deprecated APIs, SDK rewrites, webhook retry behavior, and required migrations |
| [payments-checkout-and-risk.md](references/payments-checkout-and-risk.md) | Payments, refunds, disputes, cards, invoices, subscriptions, Terminal, and wallets |
| [catalog-orders-and-inventory.md](references/catalog-orders-and-inventory.md) | Catalog schemas, locations, inventory, fulfillment, and transfer orders |
| [platforms-devices-and-reporting.md](references/platforms-devices-and-reporting.md) | OAuth, Reporting, GraphQL, Devices, bank accounts, Marketplace eligibility, and MCP |
| [web-payments-sdk.md](references/web-payments-sdk.md) | ACH, tokenization results, wallet UI, secure contexts, errors, and TypeScript types |

## Breaking changes and required migrations

### Replace customer card access

With Square API version `2025-01-23`, `Customer.cards` is retired. Enumerate
cards with `ListCards?customer_id=...` and gift cards with
`ListGiftCards?customer_id=...`.

`CreateCustomerCard` and `DeleteCustomerCard` remain deprecated; no retirement
date is specified for them here.

### Move from Reader SDK

Reader SDK and its Mobile Authorization API were scheduled for retirement on
December 31, 2025. Migrate to Mobile Payments SDK and use its authorization
methods.

### Account for rewritten language SDKs

The rewritten SDK generations are Node.js 40, PHP 41, Java 44, .NET 41,
Python 42, and Ruby 44. They change class and method shapes and add
auto-pagination, so follow the respective migration guides for ongoing API
updates.

Node.js uses native `fetch`. Python supports Pydantic validation and
`ApiError`-derived exceptions with Python 3.8+. Ruby requires 3.1+. Every
webhook payload has a corresponding SDK object as of June.

### Replace Shift APIs with Timecard APIs

All `Shift` endpoints, types, and webhooks are deprecated in favor of their
`Timecard` equivalents for create, update, delete, retrieve, and search.
Replace `GetShift` with `RetrieveTimecard`.

### Replace retired inventory transfers

As of Square version `2026-07-15`, cross-location movement is an `ADJUSTMENT`
with `from_location_id` and `to_location_id`.

`TRANSFER`, `InventoryTransfer`, `RetrieveInventoryTransfer`, and
`InventoryAdjustment.location_id` are retired. Responses now expose the
`UNTRACKED` state and Square-generated inferred and component adjustments.

### Remove offline payment details

`CreatePayment.offline_payment_details` was deprecated in August and was
scheduled for retirement on November 19, 2025.

### Resolve loyalty rewards through pricing rules

`LoyaltyProgramRewardTier.definition` is retired. Resolve reward discount
details through `pricing_rule_reference` instead.

### Use the final webhook retry policy

Webhook subscriptions use at most 11 retries over 24 hours on every Square API
version. This supersedes the January policy of 19 retries over 48 hours.

### Require secure Web Payments contexts

Every Web Payments SDK integration must run in a secure HTTPS context as of
October 1, 2025. Insecure HTTP contexts are no longer supported.

### Update ACH initialization and tokenization

`ach()` no longer requires `redirectURI`, and `transactionId` is optional.
`AchChargeTokenOptions.total` is deprecated in favor of separate `amount` and
`currency` arguments.

Catch `InvalidOptionError` for a missing ACH name. `PlaidMissingNameError`
remains for backward compatibility but is no longer emitted.

### Treat statuses and method types as strings

Token status values return strings instead of the former enumeration.
`PaymentRequestEvent` and `MethodType` are string-union types rather than
enumerations.

## Payment and checkout quick reference

### Use the consolidated card tokenization flow

In Beta, `Card.tokenize()` supports a consolidated flow for payment processing,
buyer verification, and storing, charging, or both charging and storing a card
on file.

### Pass a subscription plan variation

For subscription checkout, `CreatePaymentLink.subscription_plan_id` must
contain a subscription plan variation ID, not a subscription plan ID.

### Handle gift-card insufficient funds metadata

A failed Square gift-card payment always returns
`GIFT_CARD_AVAILABLE_AMOUNT` with `INSUFFICIENT_FUNDS`, even without partial
authorization. This applies to every Square API version.

### Use application-fee allocations

`Payment.app_fee_allocations` can distribute one application fee among up to
three parties. For a refund of a payment that used allocations, set
`PaymentRefund.app_fee_allocations` to control each party's contribution.

### Read payment-source diagnostics

`Payment.BuyNowPayLaterDetails.errors` and
`Payment.DigitalWalletDetails.errors` expose source-specific failures. The
card nested under `CardPaymentDetails` adds `created_at` and `disabled_at`.

The added error codes are `PARTIAL_PAYMENT_DELAY_CAPTURE_NOT_SUPPORTED`,
`PAYMENT_SOURCE_NOT_ENABLED_FOR_TARGET`, and `AMOUNT_TOO_LOW`.

### Account for Terminal defaults and surcharges

`PaymentOptions.autocomplete` defaults to `true`. The Terminal API can add
credit-card surcharges in the US, and payments report seller-added card
surcharges.

### Handle completed subscriptions

Fixed-phase subscriptions can enter the non-billing, non-resumable `COMPLETED`
status, expose their expected `completed_date`, and receive a
`SubscriptionAction` of type `COMPLETE`.

Plans containing any non-fixed-length phase have no defined completion date,
so `completed_date` is unset.

## Catalog, inventory, and orders quick reference

### Migrate catalog modifier fields

Modifier-list selection constraints can live at list level. Deprecated fields
are list `selection_type` and `max_quantity`, item-list-info
`hidden_from_customer`, and override `hidden_online` and `on_by_default`.

See the catalog reference for their new list-, item-list-, and override-level
fields and for `CatalogItem.is_alcoholic`.

### Work with inventory cost and vendors

In Beta, stock-receiving adjustments accept `cost_money` and `vendor_id`.
`UpdateInventoryAdjustment` can edit a past adjustment's `quantity`,
`cost_money`, `vendor_id`, and `reason_id`.

Writing cost or vendor data requires an active Retail Plus, Restaurants Plus,
or Restaurants Premium subscription.

### Retrieve nested modifiers

In Beta, `CatalogModifier.child_modifier_list_ids` links nested modifier lists
for multi-step choices. Set `include_options` on
`BatchRetrieveCatalogObjects`, `SearchCatalogItems`, or `SearchCatalogObjects`
to include related modifier lists in responses.

### Represent in-store fulfillment

`IN_STORE` represents an order received by the buyer at the seller's location
at sale time. Writing this fulfillment type is limited to partners in the
closed Beta.

## Platform API quick reference

### Query the Reporting API

The Beta, cube-based Reporting API uses `GET /v1/meta` to discover views,
cubes, measures, dimensions, and segments, then `POST /v1/load` to run
analytical queries. It supports automatic joins across cubes.

Authenticate with a personal access token or an OAuth token carrying
`REPORTING_READ`.

### Use JWT OAuth access tokens

The OAuth API accepts `use_jwt` for authentication with a JSON Web Token. The
token behaves like a standard access token.

### Create and disable customer bank accounts

Use `CreateBankAccount` to store a new customer bank account and
`DisableBankAccount` to disable one.

### Use GraphQL entry points

Square GraphQL provides `scheduledShifts` and `timecards` for Labor data, with
`timecards` replacing deprecated `shifts`. It also provides `devices` for a
seller's POS and peripheral devices.

### Use the Square MCP server

Square provides an MCP server through which compatible AI assistants can
control and interact with a Square account.
