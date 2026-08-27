# Stripe Node SDK

## Version, API pin, and runtime matrix (`node-sdk-stable-2025-2026`)

| SDK | Pinned API release |
| --- | --- |
| v18 | `2025-03-31.basil` |
| v19 | `2025-09-30.clover` |
| v20 | `2025-11-17.clover` |
| v21 | `2026-03-25.dahlia` |

V19 drops Node versions below 16 and deprecates Node 16. V21 drops Node 16.
From v18.1, `@types/node` is an optional peer dependency rather than an
unconditional dependency.

Node v22.4 changes its pinned API version to `2026-07-29.dahlia`
(`sdk-stable-through-2026-08-10`). Test the Dahlia contract when relying on the
SDK default and taking that release.

## Webhooks and event notifications

### V18 webhook accessor (`node-sdk-stable-2025-2026`)

`Stripe.webhooks` and an instance's `webhooks` member are plain objects, not
factory functions. Replace `Stripe.webhooks().constructEvent(...)` with:

```ts
const event = Stripe.webhooks.constructEvent(payload, signature, secret);
```

### V19 event notification API (`node-sdk-stable-2025-2026`)

V19 moves event types from `Stripe.V2` to `Stripe.V2.Core`, renames
`parseThinEvent` to `parseEventNotification`, removes `Stripe.ThinEvent`, and
returns the typed `Stripe.V2.EventNotification` union with `fetchEvent()` and,
when applicable, `fetchRelatedObject()`.

Cast unknown notifications to `UnknownEventNotification`. From v19.1, its fetch
method is always present and returns `null` when no related object exists.

### Parser separation and verified handoff

V21 throws when a webhook payload is passed to the wrong parser
(`node-sdk-stable-2025-2026`). Use `webhooks.constructEvent` for snapshots and
`parseEventNotification` for event notifications.

Node v22.5 adds parsers for payloads whose authenticity was verified before
queueing or handoff (`sdk-stable-through-2026-08-10`):

```js
const event = stripe.webhooks.constructEventWithoutVerification(payload);
const notification = stripe.parseEventNotificationWithoutVerification(payload);
```

The available methods are
`stripe.webhooks.constructEventWithoutVerification()`,
`stripe.constructEventWithoutVerification()`, and
`stripe.parseEventNotificationWithoutVerification()`. They also parse AWS
EventBridge and Azure Event Grid deliveries natively. Do not use them for an
unverified inbound payload.

## Request context, transport, and serialization

### StripeContext migration (`node-sdk-stable-2025-2026`)

V18.3 adds `stripeContext` to per-request options and client configuration. V19
represents notification context as a request-serializable `StripeContext` object
instead of a string. V19 also stops stripping `stripe-context` from v1 requests
or `stripe-account` from v2 requests. Do not send both headers; prefer context
when migrating.

### Raw requests (`node-sdk-stable-2025-2026`)

From v18.1, `rawRequest` accepts `host` and `streaming` options, while request
data is accepted only for `POST`:

```ts
await stripe.rawRequest('GET', '/v1/files/file_123/contents', {}, {
  host: 'files.stripe.com',
  streaming: true,
});
```

V18.4 exposes the pinned API version as `Stripe.API_VERSION`. Node v22.5 exposes
the major API version separately as `stripe.major_api_version`
(`sdk-stable-through-2026-08-10`):

```js
const majorApiVersion = stripe.major_api_version;
```

### V2 query and failure behavior (`node-sdk-stable-2025-2026`)

V20 serializes arrays for v2 retrieve and list calls with indexed keys such as
`include[0]=foo&include[1]=bar`; update mock-server assertions. It replaces
event-list `gt`/`gte`/`lt`/`lte` filters with `created`. From v20.3.1, failed v2
list calls reject normally instead of crashing Node through an unhandled
rejection.

### Alternate runtimes and release tags (`node-sdk-stable-2025-2026`)

Starting with v19, npm releases use `latest`, `public-preview`, or
`private-preview` rather than `beta`. V19 fixes FetchHttpClient file uploads in
runtimes such as Bun, Unicode JSON content lengths, and Buffer-dependent
encoding in other JavaScript runtimes. V20.1.2 also fixes multipart upload
content lengths.

## Generated types and object shapes

### Removed v18 aliases (`node-sdk-stable-2025-2026`)

V18 removes February 2024 deprecated types in favor of resource-scoped names:

| Removed | Replacement |
| --- | --- |
| `CapabilityListParams` | `AccountListCapabilitiesParams` |
| `PersonCreateParams` | `AccountCreatePersonParams` |
| `InvoiceLineItemUpdateParams` | `InvoiceUpdateLineItemParams` |
| `TransferReversalCreateParams` | `TransferCreateReversalParams` |

Migrate imports because the aliases are no longer exported.

### V19 response and compile-time breaks (`node-sdk-stable-2025-2026`)

V2 delete methods return `V2DeletedObject` with the deleted object's ID and
type. Nullable v2 properties become optional (`prop?: string`) instead of
explicit null unions (`prop: string | null`), so use presence checks rather than
null-only checks.

V19 also removes `balance_report` and `payout_reconciliation_report` from
AccountSession components, weekend values from weekly payout days, and `link`
and `pay_by_bank` from `PaymentMethodUpdateParams`; `Invoice.id` becomes
required. These are compile-time breaks even without use of new Clover
resources.

### Decimal and integer values (`node-sdk-stable-2025-2026`)

V21 changes every `decimal_string` request and response field from `string` to
the vendored `Stripe.Decimal`, including decimal prices and quantities, Climate
amounts, Issuing amounts, ownership percentages, and Checkout currency-
conversion rates:

```ts
const quantity = Stripe.Decimal.from('1.25');
const serialized = quantity.toString();
```

V21 also supports v2 int64 fields encoded as strings. Preserve those strings
instead of coercing them through JavaScript numbers. Dedicated OAuth error
classes require error classifiers to accept the new subclasses.

### Non-exhaustive enums and removed fields (`sdk-stable-through-2026-08-10`)

Node v22.4 adds shared `OtherString` typing for non-exhaustive generated enums.
Switches still need an unknown-value branch.

V22.4 removes `proof_of_registration` from Account creation documents and
`dynamic_tax_rates` from Checkout Session line-item creation parameters. Remove
those fields before upgrading generated request code.

Generated error unions add `tax_id_prohibited`,
`forwarding_api_upstream_error`, `customer_session_expired`,
`india_recurring_payment_mandate_canceled`,
`payment_intent_rate_limit_exceeded`, `account_token_required_for_v2_account`,
`request_blocked`, `storer_capability_missing`, and
`storer_capability_not_active` (`node-sdk-stable-2025-2026`). Add cases and a
forward-compatible fallback.

## Generated resource surfaces (`node-sdk-stable-2025-2026`)

### Billing, Checkout, and payment records

April 2025 types add billing-details tax IDs, Checkout `wallet_options`,
automatic-tax providers on Checkout Sessions, Invoices, and Quotes,
ConfirmationToken installment test helpers, and Refund `pending_reason`.

May adds Invoice `attach_payment`, refund-and-dispute prefunding, balance types,
mixed Credit Notes with pre- and post-payment amounts, the
`invoice.payment.paid` snapshot event, and restored billing-threshold fields.

July and August add Checkout `origin_context`, rendering templates,
schedule-phase duration and cancel-at sentinels, Payment Link inline
`price_data`, named Billing Portal configurations, payout methods, PIX IOF
handling, and additional payment transaction IDs.

October adds `PaymentAttemptRecord` list and retrieve and `PaymentRecord`
retrieve plus payment-attempt, payment, and refund reporting. Invoice payments
and credit-note refunds can reference payment records rather than only
PaymentIntents and ordinary refunds.

December adds PayTo across Intent, Checkout, Billing, Payment Link, mandate, and
payment-method surfaces. Checkout line items become updateable and accept
metadata, debit-method details add expected debit dates, and Payment Records add
richer card details and reporter attribution.

February 2026 adds Reserve Hold, Plan, and Release resources with snapshot
events, Pay by Bank billing support, US-bank transaction purpose, and
`payment_behavior` when deleting a Subscription Item.

### Accounts, identity, and financial data

April 2025 types add account compliance fields. June adds account payout-day
settings, Identity related-person matching, and Treasury status filtering. July
and August add AccountSession reporting components and Issuing card expiration
input.

November adds `Tax.Association.find`, Financial Connections account-number data
and expiry/update events, and nullable Financial Connections Session client
secrets. December exposes v2 Core Account, AccountPerson, token, and link
resources, and Identity Sessions can reference customer accounts.

January 2026 adds typed notifications for v2 Account, AccountPerson, and
AccountLink changes plus additional v2 account identity fields.

Node v22.4 also exposes `FinancialConnections.Authorization`, adds
`bank_account_token` to Financial Connections Sessions, and adds
`sepa_debit_payments` to Account update settings
(`sdk-stable-through-2026-08-10`). Preserve all three generated additions.

### Terminal, risk, and payment methods

May 2025 adds Terminal reader input collection and test helpers. June adds
Terminal `collect_payment_method` and `confirm_payment_intent`, crypto
payment-method surfaces, and expanded card-installment plans.

November adds `Terminal.OnboardingLink.create`, PaymentIntent hooks,
card-present capture-method options, and refund destination details. January
2026 adds `Radar.PaymentEvaluation.create` and 3DS versions `2.3.0` and `2.3.1`.
February adds Terminal S710 and cellular configuration plus Terminal Wi-Fi
certificate file purposes.

Generated SDKs add `stripe_internal_error` to Issuing Authorization request-
history reasons (`sdk-stable-through-2026-08-10`). Accept the value in
exhaustive handling.
