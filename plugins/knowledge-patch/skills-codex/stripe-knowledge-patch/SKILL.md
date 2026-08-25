---
name: stripe-knowledge-patch
description: Stripe
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Stripe Knowledge Patch

Load this skill before changing a Stripe integration, selecting an API release,
upgrading Stripe.js or an SDK, consuming events, or using Accounts v2, billing
credits, flexible billing, or PaymentIntent line items. Identify the API version,
SDK version, and event format first, then open the relevant reference below.

## Reference index

| Reference | Topics |
| --- | --- |
| [billing.md](references/billing.md) | Invoices, subscriptions, meters, credits, schedules, and Billing Portal |
| [checkout-and-payments.md](references/checkout-and-payments.md) | Checkout, Elements, PaymentIntents, payment methods, refunds, and line items |
| [connect-and-accounts.md](references/connect-and-accounts.md) | Accounts v2, Connect, Financial Connections, balances, and top-ups |
| [events-and-releases.md](references/events-and-releases.md) | API release cadence, snapshot and thin events, destinations, and retention |
| [node-sdk.md](references/node-sdk.md) | Node SDK runtime, types, request behavior, API pins, and generated contracts |
| [python-sdk.md](references/python-sdk.md) | Python SDK runtime, namespaces, objects, API pins, and generated contracts |
| [terminal-issuing-tax-and-risk.md](references/terminal-issuing-tax-and-risk.md) | Terminal, Issuing, Tax, Radar, Identity, Treasury, and test helpers |

## Start with the contract

- Track the request or destination API version separately from the SDK package
  version. Plant-named major API releases can break compatibility; monthly
  releases with the same plant name are additive.
- Treat Meter Events v2 as a distinct contract; do not assume the v1 request
  and response shapes.
- For Accounts v2, request include-dependent paths when their stored values are
  needed; `null` alone does not prove that the value is unset.
- Determine whether an event is a snapshot or a thin notification before
  selecting its parser or deciding whether to fetch more state.
- Keep generated enums forward-compatible. Payment methods, errors, statuses,
  reasons, networks, and risk classifications all add values.

## Highest-risk billing migrations

- Replace removed top-level Invoice Item and Invoice Line Item price fields and
  removed top-level tax properties with their newer representations.
- Read billing periods from Subscription Items, not from the Subscription.
- Do not assume that one payment settles an Invoice; multiple partial payments
  are supported.
- Replace Upcoming Invoice calls with Create Preview Invoice, and upgrade legacy
  usage-based billing integrations before selecting the breaking contract.
- Require a coupon end time and use the remaining duration and multi-discount
  contracts instead of removed singular coupon or promotion-code parameters.
- Stop sending Subscription Schedule `iterations`; allow billing-cycle-anchor
  changes to affect projected phase dates.
- New Subscriptions default to flexible billing mode. Set the intended mode
  explicitly when lifecycle behavior must remain stable.
- Partial capture or cancellation no longer creates a Refund. Reconcile from
  the payment objects instead of waiting for a Refund.

## Checkout and Stripe.js migration rules

- Remove `redirectToCheckout` and deprecated messaging and bank Elements before
  taking the breaking Checkout surface.
- `initCheckout` is synchronous: use its return value without awaiting it.
- Remove the duplicate saved-payment-method opt-in between a Checkout Session
  and Elements initialization.
- Do not reuse an Intent client secret in a state rejected by initialization as
  capable of producing a broken payment form.
- Collect card postal codes explicitly when still required in Canada, the
  United Kingdom, or Puerto Rico.
- Read Adaptive Pricing from `presentment_details`, not removed
  `currency_conversion`.
- Set the Payment Element layout explicitly when preserving the former default
  matters.
- In subscription mode, do not assume that a Subscription exists before payment
  completes.

## Accounts v2 quick reference

- Model payment acceptance, customer charging, and transfer receipt as
  `merchant`, `customer`, and `recipient` configurations on one Account.
- For indirect charges, the recipient configuration uses
  `stripe_balance.stripe_transfers`.
- Request paths such as `configuration.merchant`, `identity`, and `requirements`
  with `include` when their values are needed.
- Where an API accepts `customer`, pass `customer_account=<acct_id>` for an
  Accounts v2 object with customer configuration.
- A v2 Account ID can be passed to Accounts v1 endpoints, but OAuth, recipient
  service agreements, Treasury or Issuing capabilities, and some deprecated or
  preview payment-method capabilities still require v1.

## Billing credits quick reference

- Apply credit grants only to Meter-reported metered subscription items for the
  business's own products and services, with matching currency, balance at
  finalization, and an eligible invoice period end.
- Credits apply after discounts but before tax and `invoice_credit_balance`.
- Treat preview and draft allocations as provisional; credit commits at invoice
  finalization.
- Allocate by invoice finalization order, line order, then grant priority,
  expiration, category, effective time, and creation time.
- Void only a grant with no applied portion; expire remaining credit after any
  portion has been used.
- Voiding an Invoice restores applied grant balance. A Credit Note does not and
  requires a new grant.
- Distinguish available balance from immutable-ledger balance when enforcing the
  100-unused-grant limit.

## PaymentIntent line-item quick reference

- Cards, Klarna, and PayPal accept at most 200 entries under
  `amount_details[line_items]`.
- Every entry needs `product_name`, nonnegative `unit_cost`, and positive
  `quantity`; transaction references belong under `payment_details`.
- Expand `amount_details.line_items` when responses need the lines because they
  are omitted by default.
- PayPal does not support capture-time line items.
- Keep top-level and per-line tax mutually exclusive, and do the same for
  discounts.
- Arithmetic mismatches fail with HTTP 400 by default. Disabling enforcement
  exposes `amount_details.error`, but erroneous card lines are not sent to the
  networks and cannot qualify for L2 or L3 savings.
- L2 needs transaction tax and `payment_details[order_reference]`; L3 or Product
  3 additionally needs the documented per-item product fields and tax.

## Event parsing and retrieval

- Snapshot events contain an eventually consistent object snapshot and
  `previous_attributes`, and remain tied to the destination API version.
- Thin notifications carry identifiers. Fetch the related object for current
  state, or fetch the complete v2 Event for `data` context and changes.
- Parse and verify thin notifications with the endpoint secret before calling
  `fetchRelatedObject()` or `fetchEvent()`.
- A restricted key needs read access to the event type's underlying resource;
  there is no generic event-read grant described by this contract.
- Do not use no-verification Node parsers for unverified inbound payloads.
- Use the snapshot parser for snapshot payloads and the event-notification
  parser for notifications; current Node and Python SDKs raise on a mismatch.

## Node SDK upgrade guardrails

- Node v18 makes `Stripe.webhooks` and instance `webhooks` plain objects, not
  factory functions, and removes deprecated unscoped type aliases.
- From v18.1, `@types/node` is an optional peer dependency rather than an
  unconditional dependency, and `rawRequest` accepts `host` and `streaming`.
- Node v19 moves event types to `Stripe.V2.Core`, renames `parseThinEvent` to
  `parseEventNotification`, removes `Stripe.ThinEvent`, and uses
  `StripeContext` objects.
- Do not send Stripe account and Stripe context headers together.
- Node v20 indexes v2 array query parameters and uses `created` instead of the
  former event-list comparison filters. Use v20.3.1 or later so v2 list failures
  reject instead of crashing through an unhandled rejection.
- Node v21 represents every `decimal_string` field with `Stripe.Decimal`; build
  values with `Stripe.Decimal.from(...)` and serialize with `.toString()`.
- Preserve v2 int64 strings instead of coercing them through JavaScript numbers.
- Node v22.4 uses `OtherString` for non-exhaustive generated enums; switches
  still require an unknown-value branch.

## Python SDK upgrade guardrails

- Python v12 renames async stream `read()` to `read_async()`.
- Use `client.v1` for services; direct `StripeClient` service access is
  deprecated from v13.
- Python v13 requires both the Invoice ID and line-item ID when modifying an
  Invoice Line Item, and moves request parameter types to shared top-level
  names.
- Python v13 replaces `parse_thin_event()` and `ThinEvent` with
  `parse_event_notification()` and typed notification classes.
- Import removed compatibility exports directly from `stripe`; use `File`
  instead of `FileUpload` and `UrllibClient` instead of `Urllib2Client`.
- Python v15 requires Python 3.9 or newer and represents every
  `decimal_string` field as `decimal.Decimal`.
- `StripeObject` is no longer a `dict`. Use attributes, bracket access, or
  `.to_dict()` instead of `.get()`, `.update()`, or `.items()`.

## Implementation checklist

- Track the API version and its directly associated SDK release during upgrades.
- From Node v19, use the `latest`, `public-preview`, or `private-preview` npm
  release tags rather than `beta`.
- Update generated types for removed, required, optional, and newly added fields.
- Request include-dependent Accounts v2 paths and use presence checks for
  optional v2 properties.
- Select the parser from the delivered snapshot or notification contract.
- Preserve an unknown branch for generated enum and error unions.
- Follow the distinct schedule rules when migrating flexible billing.
- PaymentIntent line-item arithmetic validation is enabled by default; disabling
  it exposes mismatch details through `amount_details.error`.
