---
name: stripe-knowledge-patch
description: Stripe
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Stripe Knowledge Patch

## Use this patch

Load this skill when upgrading a Stripe API version or SDK, changing Billing or
payment flows, consuming events, or adopting Accounts v2.

Before changing an integration:

1. Record the API version used by requests and Event Destinations.
2. Record the SDK package version and its mapped API release.
3. Identify whether each event consumer receives snapshot events or thin event
   notifications.
4. Separate stable contracts from public-preview and private-preview contracts.
5. Audit generated types, closed enums, optional fields, and removed request
   parameters before upgrading.

## Reference index

| Reference | Topics |
| --- | --- |
| [billing.md](references/billing.md) | Invoices, subscriptions, discounts, meters, credits, and flexible billing |
| [checkout-and-payments.md](references/checkout-and-payments.md) | Checkout, Elements, PaymentIntents, Payment Links, payment methods, refunds, and line items |
| [connect-and-accounts.md](references/connect-and-accounts.md) | Accounts v2, Connect, Financial Connections, balances, identity, and Treasury |
| [events-and-releases.md](references/events-and-releases.md) | API release cadence, snapshot and thin events, destinations, retrieval, and pagination |
| [node-sdk.md](references/node-sdk.md) | Node SDK runtime, requests, API pins, event parsing, types, and generated contracts |
| [python-sdk.md](references/python-sdk.md) | Python SDK runtime, namespaces, paging, events, Decimal, and objects |
| [terminal-issuing-tax-and-risk.md](references/terminal-issuing-tax-and-risk.md) | Terminal, Issuing, Tax, Radar, disputes, and test helpers |

## Breaking API migrations

### Billing data models

- Replace Invoice Item and Invoice Line Item top-level price fields with the
  newer price representation.
- Replace top-level tax properties on Invoices, Invoice Line Items, and Credit
  Note Line Items with the replacement representations.
- Read billing periods from individual Subscription Items, not the
  Subscription.
- Reconcile multiple partial Invoice payments; do not assume one payment
  settles an Invoice.
- Replace Upcoming Invoice methods with Create Preview Invoice and remove
  dependencies on legacy usage-based billing.
- Give discount coupons an end time and use the remaining multi-discount
  contracts instead of the removed singular coupon and promotion-code
  parameters.
- Stop sending Subscription Schedule `iterations`; allow billing-cycle-anchor
  changes to alter projected phase dates.
- Set the intended billing mode explicitly when new Subscription lifecycle
  behavior must remain stable.
- Do not wait for a Refund after partial capture or payment cancellation; those
  operations no longer create one.

### Checkout, Elements, and Stripe.js

- Remove `redirectToCheckout` and the deprecated messaging and bank Elements.
- Use synchronous `initCheckout` directly rather than awaiting it.
- Remove the duplicate saved-payment-method opt-in when using Elements with a
  Checkout Session.
- Never reuse an Intent client secret in a state rejected by initialization as
  capable of producing a broken payment form.
- Explicitly collect postal codes for Canadian, United Kingdom, and Puerto Rico
  card payments when the integration still needs them.
- Read Adaptive Pricing from `presentment_details`, not removed
  `currency_conversion`.
- Set Payment Element layout explicitly when preserving the former default is
  important.
- Do not assume a Subscription exists before a subscription-mode Checkout
  Session's payment completes.

### Pagination and response assumptions

- Stop using expanded `total_count` or the removed `page` parameter on list
  APIs.
- Treat Accounts v2 include-dependent `null` values as omitted data, not proof
  that the underlying value is unset.
- Add an unknown-value branch for expanding error, status, reason, payment
  method, network, risk, and transaction-type enums.

## Accounts v2 essentials

- Model merchant, customer, and recipient roles as additive configurations of
  one `/v2/core/accounts` identity.
- Request needed paths such as `configuration.merchant`, `identity`, and
  `requirements` with `include`.
- Use `customer_account=<acct_id>` where an API accepts a Customer and the v2
  Account has customer configuration.
- Require `recipient.stripe_balance.stripe_transfers` for indirect charges.
- Keep v1 integration paths for OAuth, recipient service agreements, Treasury
  or Issuing capabilities, and specified deprecated or preview payment-method
  capabilities.

## Event processing essentials

- Snapshot events carry an eventually consistent resource snapshot and
  `previous_attributes`; their schema follows the destination API version.
- Thin notifications carry identifiers. Use `fetchRelatedObject()` for latest
  resource state or `fetchEvent()` for complete event context and changes.
- Parse and verify thin notifications with the endpoint secret before fetching
  either resource.
- A restricted key needs `Read` access to the event type's underlying resource;
  Workbench viewing requires the Admin or Developer role.
- Plan around full API payload retention of 30 days and the shorter Workbench
  window for delivery attempts and manual resend.
- Keep destinations within the per-account and unique-version limits described
  in [events-and-releases.md](references/events-and-releases.md).

## Billing credits quick reference

- Apply grants only to Meter-reported metered subscription items with matching
  currency, eligible invoice period, and balance at finalization.
- Do not use grants for gift cards, stored value, third-party payments,
  digital-wallet balances, one-off invoices, setup items, licensed prices, or
  legacy Usage Records.
- Apply credits after discounts and before tax and
  `invoice_credit_balance`.
- Treat draft and preview allocations as provisional; credits commit at Invoice
  finalization.
- Allocate by Invoice finalization order and line order, then grant priority,
  expiration, category, effective time, and creation time.
- Void only an entirely unused grant; expire remaining credit after any portion
  has been applied.
- Voiding an Invoice restores applied grant balance; a Credit Note does not.
- Distinguish available balance from the immutable-ledger-backed ledger balance.
- Enforce the 100-unused-grant limit from pending state or positive ledger
  balance, not available balance.

## PaymentIntent line-item quick reference

- Supply at most 200 line items for cards, Klarna, or PayPal.
- Every line requires `product_name`, nonnegative `unit_cost`, and positive
  `quantity`.
- Put transaction references in `payment_details`; put shipping, tax, and
  discounts in `amount_details`.
- Expand `amount_details.line_items` when responses need the omitted-by-default
  line items.
- Do not combine transaction-level and line-level tax or transaction-level and
  line-level discounts.
- Keep arithmetic validation enabled unless mismatch handling is intentional.
  Invalid card line items are not sent to networks and cannot qualify for L2 or
  L3 savings.
- PayPal does not accept capture-time line items.
- L2 requires transaction tax and an order reference; L3 or Product 3 also
  requires the documented per-line product fields and tax.

## Node SDK upgrade guardrails

- In v18, treat `Stripe.webhooks` and instance `webhooks` as objects, migrate
  removed aliases to resource-scoped names, and add `@types/node` explicitly
  when needed.
- In v19, use `Stripe.V2.Core`, `parseEventNotification`, typed event
  notifications, and `StripeContext`.
- Do not send both Stripe context and connected-account headers.
- For v2 responses, handle optional properties and `V2DeletedObject`.
- Update v2 mocks for indexed array query parameters and use v20.3.1 or later
  to avoid a process crash on failed v2 list calls.
- In v21, use `Stripe.Decimal` for every `decimal_string` field and preserve v2
  int64 strings rather than coercing them through JavaScript numbers.
- Parse snapshot payloads with `constructEvent` and event notifications with
  `parseEventNotification`.
- Use parsers without verification only for payloads that were already
  verified before handoff.

## Python SDK upgrade guardrails

- In v12, replace async stream `read()` with `read_async()`.
- Use `client.v1` services; direct service access is deprecated from v13.
- In v13, use shared generated parameter types, pass both Invoice and line-item
  IDs to `InvoiceLineItem.modify`, and import compatibility classes directly
  from `stripe`.
- Use `parse_event_notification()` and typed notifications for thin event
  payloads, and pass `StripeContext` objects through as objects.
- Install `stripe[async]` for async HTTP dependencies.
- In v15, require Python 3.9 or newer, use `decimal.Decimal` for every
  `decimal_string` field, and keep snapshot and event-notification parsers
  separate.
- Treat `StripeObject` as a Stripe object rather than a `dict`; use attribute or
  bracket access and call `to_dict()` for a detached recursive snapshot.

## Implementation checklist

- Track the SDK version and its mapped API release together during upgrades.
- Treat plant-named major releases as possible breaking boundaries and monthly
  releases under the current plant name as additive.
- Update generated types and remove deleted request fields before upgrading.
- Distinguish optional, nullable, and include-dependent response properties.
- Verify notification signatures and select the parser that matches the Event
  format.
- Handle newly added enum values and preserve an unknown fallback.
- Treat draft and preview billing-credit allocation as provisional.
- Configure Checkout layout and postal-code collection explicitly when former
  defaults matter.
- Enforce PaymentIntent line-item arithmetic and method-specific capture rules.
- Treat preview contracts as distinct from stable contracts.
