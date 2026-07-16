---
name: stripe-knowledge-patch
description: Stripe rolling coverage. Use for Stripe work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Stripe Knowledge Patch

## Use this patch

Load this skill before changing a Stripe integration, selecting an API release, upgrading Stripe.js or an SDK, consuming events, or using preview APIs.

Before editing code:

1. Identify the request or account API version.
2. Identify the SDK language, package version, and its pinned API release.
3. Separate stable, public-preview, beta, and private-preview contracts.
4. Determine whether each consumer receives snapshot events or thin event notifications.
5. Read the breaking-change notes before relying on generated types or exhaustive enum handling.

## Reference index

| Reference | Topics |
| --- | --- |
| [billing.md](references/billing.md) | Invoices, subscriptions, discounts, meters, Credit Grants, flexible billing, Trial Offers |
| [checkout-and-payments.md](references/checkout-and-payments.md) | Checkout, Elements, Stripe.js, PaymentIntents, line items, Payment Records, payment methods, crypto |
| [connect-and-accounts.md](references/connect-and-accounts.md) | Accounts v2, Connect, KYC, Financial Connections, balances, payouts, Treasury |
| [events-and-releases.md](references/events-and-releases.md) | API release lifecycle, snapshot and thin events, destinations, retention, Batch Jobs |
| [node-sdk.md](references/node-sdk.md) | Node SDK v18-v21 runtime, types, requests, API pins, and generated contracts |
| [python-sdk.md](references/python-sdk.md) | Python SDK v12-v15 runtime, namespaces, objects, Decimal, events, and preview contracts |
| [terminal-issuing-tax-and-risk.md](references/terminal-issuing-tax-and-risk.md) | Terminal, Issuing, Tax, Radar, Climate, disputes, and test helpers |

## Release and contract selection

- Plant-named major API releases arrive twice yearly and can break compatibility.
- Monthly releases retain the current plant name and add backward-compatible features.
- Every API release has an associated SDK release, but SDK packages continue to use semantic versions.
- Plan API and SDK upgrades together; do not infer an API contract from the SDK major alone.
- Treat preview tags as distinct schemas. A nearby stable package or another preview build can expose different resources and field shapes.
- API v2 responses can require `include` for stored values that otherwise appear as `null`.

## Highest-risk API migrations

### Billing schemas and lifecycle

- Replace Invoice Item and Invoice Line Item top-level price fields with pricing configurations.
- Replace top-level tax properties on Invoices, Invoice Line Items, and Credit Note Line Items with tax configurations.
- Read current billing periods from subscription items, not the Subscription object.
- Support multiple and partial Invoice payments; never assume one payment settles an Invoice.
- Replace Upcoming Invoice methods with Create Preview Invoice and replace legacy usage billing with Meters.
- Give coupons an end condition and migrate direct coupon fields to the newer promotion and discount-source shapes.
- Remove Subscription Schedule `iterations`; represent phase duration with the supported duration fields.
- New Subscriptions use flexible billing behavior by default. Set the desired mode explicitly when lifecycle details matter.
- Do not infer a Refund from partial capture or payment cancellation; those operations no longer create one.

See [billing.md](references/billing.md) for invoice, subscription, credit, and migration rules.

### Checkout, Elements, and Stripe.js

- Remove `redirectToCheckout` and superseded messaging and bank Elements.
- Replace removed legacy PaymentIntent, SetupIntent, and Sources helpers with current Stripe.js methods.
- Rename `initCheckout` to `initCheckoutElements` and `initEmbeddedCheckout` to `createEmbeddedCheckoutPage` on the newer surface.
- Do not await the earlier synchronous `initCheckout`; do await the newer Promise-returning `elements.update()`.
- Stop passing booleans to `options.layout.radios`.
- Review Payment Element future-usage configuration, Customer Session interaction, and Checkout `ui_mode` validation.
- Configure a layout explicitly if the Payment Element's implicit default matters.
- Collect postal codes explicitly when required for Canadian, UK, or Puerto Rican card payments.
- Read Adaptive Pricing from `presentment_details`, not removed `currency_conversion`.
- Do not reuse an Intent client secret in a state that can produce a broken payment form.

See [checkout-and-payments.md](references/checkout-and-payments.md) for payment-method, Payment Record, crypto, and line-item details.

### Accounts v2 and Connect

- Model merchant, customer, and recipient roles as configurations of one `/v2/core/accounts` identity.
- Where an API accepts `customer`, it can also accept `customer_account` for an Account with customer configuration.
- Request `configuration.customer`, `configuration.merchant`, `identity`, and `requirements` with `include` when those values are needed.
- Require `recipient.stripe_balance.stripe_transfers` for indirect charges.
- Follow returned risk and onboarding requirements rather than always forcing external-account collection.
- Allow the expanded Financial Connections filters and failure codes.

See [connect-and-accounts.md](references/connect-and-accounts.md) for configuration, capability, balance, and payout details.

### Event parsing

- Parse API v1 snapshot events with webhook helpers; they contain an API-versioned resource snapshot and `previous_attributes`.
- Parse thin notifications with the SDK event-notification parser, then call `fetchEvent()` or `fetchRelatedObject()` only when more data is needed.
- Keep payloads away from the wrong parser; current SDKs raise on parser/payload mismatches.
- Do not treat a thin notification's related object as event-time state: fetching it returns the latest resource state.
- Restricted keys need read access to the event's resource; secret keys can retrieve all event types by default.
- Design around the shorter delivery-attempt and resend window even though Workbench retains summaries longer.

See [events-and-releases.md](references/events-and-releases.md) for retention windows, destination limits, and Azure delivery.

## Billing credits quick reference

- Credit Grants apply only to metered subscription items reporting through Meters.
- Currency must match, and the invoice `period_end` must be inside the grant's effective window.
- Apply credit after discounts and before tax and the customer's invoice credit balance.
- Credit is consumed at invoice finalization, so draft and preview allocations are provisional.
- Within an invoice, displayed line order controls consumption; across invoices, finalization order controls it.
- Order competing grants by priority, expiration, category, effective time, then creation time.
- Void an entirely unused grant; expire a grant once any amount has been invoiced.
- Voiding an Invoice restores its applied credit, but issuing a Credit Note does not.
- Distinguish immutable-ledger `ledger_balance` from the broader `available_balance`.
- Enforce the 100-unused-grant limit using the documented ledger-based counting rule.

## PaymentIntent line items quick reference

- Line items support cards, Klarna, and PayPal, with at most 200 entries; American Express receives only the first four.
- Every line needs `product_name`, nonnegative `unit_cost`, and positive integer `quantity`.
- Put transaction identifiers under `payment_details`.
- Level 2 card data requires an order reference and transaction-level tax; Level 3 adds per-line tax, product code, and unit of measure.
- Do not mix transaction-level and line-level tax, or transaction-level and line-level discounts.
- Card line items cannot accompany partial or decrement authorization or airline, lodging, and car-rental metadata.
- Capture-time line items are unsupported for PayPal.
- Request `expand[]=amount_details.line_items`; line items are omitted from responses by default.
- Keep arithmetic validation enabled unless mismatch handling is intentional. Invalid card arithmetic prevents network submission and Level 2/3 qualification.

## Node SDK upgrade guardrails

- In v18, `Stripe.webhooks` and `stripe.webhooks` are objects, not factory functions.
- Replace removed unscoped operation aliases with resource-owned type names.
- Supply your own `@types/node` dependency when the application consumes Node types.
- In v19, move v2 events under `Stripe.V2.Core`, use `parseEventNotification`, and adopt `StripeContext`.
- Do not send `stripeAccount` and Stripe context together when the server would receive both headers.
- Adjust v2 response code for optional properties and `V2DeletedObject`.
- Change v2 list mocks to indexed query parameters.
- Use at least v20.3.1 to avoid crashes from v2 list errors.
- In v21, use `Stripe.Decimal` for every `decimal_string` field and Node 18 or newer.
- Keep snapshot parsing on `webhooks.constructEvent` and thin parsing on `parseEventNotification`.

See [node-sdk.md](references/node-sdk.md) for the complete pin table, runtime fixes, type removals, and generated contract changes.

## Python SDK upgrade guardrails

- In v12, await `StripeStreamResponseAsync.read_async()` rather than removed `read()`.
- Move service access to `StripeClient.v1`; direct client accessors are deprecated.
- In v13, use shared top-level request parameter classes and direct top-level exports.
- Pass both Invoice ID and line-item ID to `InvoiceLineItem.modify`.
- Use `parse_event_notification` and the typed notification classes for thin events.
- In v15, require Python 3.9 or newer and send payloads to the correct event parser.
- Treat every `decimal_string` field as `decimal.Decimal`, constructed from text.
- `StripeObject` is not a `dict`; use attributes, bracket access, or `to_dict()`.
- Treat beta and private-preview package pins as separate, evolving schemas.

See [python-sdk.md](references/python-sdk.md) for installer requirements, compatibility removals, caller-owned async clients, and preview resources.

## Cross-cutting enum and optionality rules

- Avoid exhaustive switches without an unknown-value path; payment methods, decline codes, risk levels, cancellation reasons, crypto networks, and error-code unions continue to expand.
- Honor fields that became optional, including Issuing Token card references and several reporting fields.
- Honor fields that became required, especially generated SDK fields and preview contracts.
- Preserve decimal quantities as decimal values rather than binary floats or ad hoc strings.
- Treat public and private preview APIs as opt-in contracts and migrate each tagged build independently.

## Implementation checklist

- Pin and record the API version used by tests.
- Verify the SDK's associated API release.
- Regenerate or update local types after a major SDK change.
- Test omitted, optional, nullable, and include-dependent fields separately.
- Test webhook signature verification and parser selection with raw payloads.
- Test event handlers with newly added enum values and unknown fallbacks.
- Test Invoice previews against concurrent Credit Grant consumption.
- Test Checkout and Elements initialization without relying on former defaults.
- Test card line-item arithmetic and method-specific field behavior.
- Keep preview-only models isolated from stable-contract code.
