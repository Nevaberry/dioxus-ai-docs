# Stripe Node SDK

## API pins and runtimes

Node SDK v18, v19, v20, and v21 pin API versions
`2025-03-31.basil`, `2025-09-30.clover`, `2025-11-17.clover`, and
`2026-03-25.dahlia`, respectively. V19 drops Node versions below 16 and
deprecates Node 16. V21 drops Node 16.

From v18.1, `@types/node` is an optional peer dependency rather than an
unconditional dependency. Applications that consume Node types must declare it
themselves.

Node v22.4 changes its pinned API version to `2026-07-29.dahlia`. Test the
Dahlia contract when relying on the SDK's default version.

## Webhooks and event notifications

### V18 webhook accessor

`Stripe.webhooks` and an instance's `webhooks` are objects, not factory
functions:

```ts
const event = Stripe.webhooks.constructEvent(payload, signature, secret);
```

Replace `Stripe.webhooks().constructEvent(...)` and equivalent instance calls
with property access.

### V19 event API

V19 moves Event types from `Stripe.V2` to `Stripe.V2.Core`, renames
`parseThinEvent` to `parseEventNotification`, removes `Stripe.ThinEvent`, and
returns a typed `Stripe.V2.EventNotification` union. Notifications provide
`fetchEvent()` and, where applicable, `fetchRelatedObject()`.

Cast unknown notifications to `UnknownEventNotification`. From v19.1, its fetch
method always exists and returns `null` when there is no related object.

### Parser separation in v21

V21 throws when a payload is sent to the wrong parser. Use
`webhooks.constructEvent` for snapshot payloads and
`parseEventNotification` for Event Notification payloads.

### Already-verified and native cloud events

Node v22.5 adds parsers for payloads verified before they were queued or handed
off:

```js
const event = stripe.webhooks.constructEventWithoutVerification(payload);
const notification = stripe.parseEventNotificationWithoutVerification(payload);
```

The added entry points are
`stripe.webhooks.constructEventWithoutVerification()`,
`stripe.constructEventWithoutVerification()`, and
`stripe.parseEventNotificationWithoutVerification()`. They also parse AWS
EventBridge and Azure Event Grid deliveries natively. Never use them on an
unverified inbound payload.

## Request context and raw requests

### Raw request options

From v18.1, `rawRequest` accepts `host` and `streaming` options for operations
such as file-content downloads. Request data is accepted only for `POST`.

```ts
await stripe.rawRequest('GET', '/v1/files/file_123/contents', {}, {
  host: 'files.stripe.com',
  streaming: true,
});
```

V18.4 exposes the pinned version as `Stripe.API_VERSION`.

### Stripe context

V18.3 adds `stripeContext` to per-request options and client configuration. V19
represents notification context as a `StripeContext` object that serializes for
requests, not as a string.

V19 stops stripping `stripe-context` from v1 requests or `stripe-account` from
v2 requests. Do not send both headers; prefer context when migrating.

### Major API version

Node v22.5 exposes the SDK's major API version separately:

```js
const majorApiVersion = stripe.major_api_version;
```

## V2 response and transport contracts

### Deletes and optional properties

V19 v2 delete methods return a `V2DeletedObject` containing the deleted object's
ID and type. Nullable v2 response properties change from explicit null unions
such as `prop: string | null` to optional properties such as `prop?: string`.
Use presence checks rather than null-only checks.

### Preview tags and alternate runtimes

Starting in v19, npm release tags are `latest`, `public-preview`, and
`private-preview`, replacing `beta`. V19 fixes FetchHttpClient uploads in Bun,
Unicode JSON content lengths, and Buffer-dependent encoding in other JavaScript
runtimes. V20.1.2 also fixes multipart-upload content lengths.

### V20 serialization and failures

V20 serializes v2 retrieve/list arrays with indexed keys such as
`include[0]=foo&include[1]=bar`; update mock-server assertions. It replaces Event
list filters `gt`, `gte`, `lt`, and `lte` with `created`.

Use v20.3.1 or later so a failed v2 list request rejects normally rather than
crashing Node through an unhandled rejection.

### Int64 values

V21 supports v2 int64 fields encoded as strings. Preserve them rather than
coercing them through JavaScript numbers.

## Type migrations

### Removed v18 aliases

V18 removes types deprecated in February 2024 in favor of resource-scoped
names, including:

| Removed | Replacement |
| --- | --- |
| `CapabilityListParams` | `AccountListCapabilitiesParams` |
| `PersonCreateParams` | `AccountCreatePersonParams` |
| `InvoiceLineItemUpdateParams` | `InvoiceUpdateLineItemParams` |
| `TransferReversalCreateParams` | `TransferCreateReversalParams` |

Migrate imports before upgrading; the aliases are no longer exported.

### Non-exhaustive enum types

Node v22.4 adds shared `OtherString` for non-exhaustive generated enums. Switches
on these unions still need an unknown-value branch.

### Added error unions

Generated error unions add:

- `tax_id_prohibited`
- `forwarding_api_upstream_error`
- `customer_session_expired`
- `india_recurring_payment_mandate_canceled`
- `payment_intent_rate_limit_exceeded`
- `account_token_required_for_v2_account`
- `request_blocked`
- `storer_capability_missing`
- `storer_capability_not_active`

TypeScript switches need cases for these values and a forward-compatible
fallback.

## Decimal values and OAuth errors

V21 changes every `decimal_string` request and response field from `string` to
the vendored `Stripe.Decimal`. This includes decimal prices and quantities,
Climate and Issuing amounts, ownership percentages, and Checkout
currency-conversion rates.

```ts
const quantity = Stripe.Decimal.from('1.25');
const serialized = quantity.toString();
```

V21 also adds dedicated OAuth error classes. Error classification must accept
the new subclasses.

## Stable generated contracts

### April and May 2025 Basil

April-generated types add Account compliance fields, billing-details tax IDs,
Checkout `wallet_options`, automatic-tax providers on Checkout Sessions,
Invoices, and Quotes, ConfirmationToken installment test helpers, and Refund
`pending_reason`.

May adds Invoice `attach_payment`, Terminal reader input collection and test
helpers, refund-and-dispute prefunding, balance types, mixed Credit Notes with
pre- and post-payment amounts, the `invoice.payment.paid` snapshot Event, and
restored billing-threshold fields.

### June through August 2025 Basil

June adds Terminal `collect_payment_method` and `confirm_payment_intent` actions,
crypto PaymentMethod surfaces, Account payout-day settings, Identity
related-person matching, expanded card-installment plans, and Treasury status
filtering.

July and August add Checkout `origin_context`, rendering templates,
schedule-phase duration and cancel-at sentinels, Payment Link inline
`price_data`, AccountSession reporting components, named Billing Portal
configurations, payout methods, Issuing card-expiration input, PIX IOF handling,
and additional payment transaction IDs.

### Residual v19 Clover breaks

V19 removes `balance_report` and `payout_reconciliation_report` from
AccountSession components, weekend values from weekly payout days, and `link`
and `pay_by_bank` from `PaymentMethodUpdateParams`. `Invoice.id` becomes
required. Treat these as compile-time migration breaks even without adopting new
Clover resources.

### October and November 2025

October adds `PaymentAttemptRecord` list and retrieve operations plus
`PaymentRecord` retrieve, payment-attempt, payment, and refund reporting methods.
Invoice payments and Credit Note refunds can reference Payment Records instead
of only PaymentIntents and ordinary Refunds.

November adds `Tax.Association.find`, `Terminal.OnboardingLink.create`, Financial
Connections account-number data and expiry/update Events, PaymentIntent hooks,
card-present capture-method options, and Refund destination details. Financial
Connections Session client secrets become nullable.

### December 2025

December exposes v2 Core Account, AccountPerson, token, and link resources. It
adds PayTo across Intent, Checkout, Billing, Payment Link, mandate, and
PaymentMethod surfaces. Checkout line items become updateable and accept
metadata. Debit-method details add expected debit dates, Identity Sessions can
reference Customer Accounts, and Payment Records add richer card details and
reporter attribution.

### January and February 2026

January adds typed notifications for v2 Account, AccountPerson, and AccountLink
changes; `Radar.PaymentEvaluation.create`; 3DS versions `2.3.0` and `2.3.1`; and
more v2 Account identity fields.

February adds Reserve Hold, Plan, and Release resources with snapshot Events;
Terminal S710 and cellular configuration; Terminal Wi-Fi certificate file
purposes; US-bank transaction purpose; Pay by Bank Billing support; and
`payment_behavior` when deleting a Subscription Item.

### Node v22.4 generated changes

Remove `proof_of_registration` from Account creation documents and
`dynamic_tax_rates` from Checkout Session line-item creation parameters. The SDK
adds `FinancialConnections.Authorization`, Session `bank_account_token`, Account
setting `sepa_debit_payments`, and Issuing Authorization request-history reason
`stripe_internal_error`. Accept the added resources, properties, and reason.
