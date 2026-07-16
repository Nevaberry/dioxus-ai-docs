# Stripe Node SDK v18-v21

## SDK-to-API pins

| Node SDK | Associated API release |
| --- | --- |
| v18.0.0 | `2025-03-31.basil` |
| v18.1.0 | `2025-04-30.basil` |
| v18.2.0 | `2025-05-28.basil` |
| v18.3.0 | `2025-06-30.basil` |
| v18.4.0 | `2025-07-30.basil` |
| v18.5.0 | `2025-08-27.basil` |
| v19.0.0 | `2025-09-30.clover` |
| v19.2.0 | `2025-10-29.clover` |
| v20.0.0 | `2025-11-17.clover` |
| v20.1.0 | `2025-12-15.clover` |
| v20.3.0 | `2026-01-28.clover` |
| v20.4.0 | `2026-02-25.clover` |
| v21.0.0 | `2026-03-25.dahlia` |

Starting with v18.4.0, `Stripe.API_VERSION` exposes the package's active API pin.

## Runtime and dependency requirements

- v19 drops Node versions below 16 and deprecates Node 16.
- v21 drops Node 16, making Node 18 the minimum supported line.
- v18.1.0 changes `@types/node` to an optional peer dependency. Applications that consume Node types should declare their chosen version directly.

## Core breaking changes

### Webhook accessor in v18

`Stripe.webhooks` and `stripe.webhooks` are plain objects, not factory functions. Replace `stripe.webhooks().constructEvent(...)` with property access.

```ts
const event = stripe.webhooks.constructEvent(payload, signature, secret);
```

### Removed operation type aliases

v18 removes unscoped aliases for operations on:

- capabilities;
- cash balances;
- Credit Note Line Items;
- Customer balance and cash-balance transactions;
- Customer sources;
- external accounts;
- fee refunds;
- Invoice Line Items;
- Login Links;
- Persons; and
- Transfer Reversals.

Use resource-owned aliases whose names begin with the owning resource. Examples:

| Removed | Replacement |
| --- | --- |
| `CapabilityRetrieveParams` | `AccountRetrieveCapabilityParams` |
| `CustomerSourceVerifyParams` | `CustomerVerifySourceParams` |
| `FeeRefundCreateParams` | `ApplicationFeeCreateRefundParams` |
| `PersonUpdateParams` | `AccountUpdatePersonParams` |
| `AccountDebitSource` | `Account` |

### Other removed Clover shapes

v19 also changes generated types beyond the main API migration:

- Account Session components remove `balance_report` and `payout_reconciliation_report`.
- Weekly payout days remove Saturday and Sunday.
- `PaymentMethodUpdateParams` removes `link` and `pay_by_bank`.
- `Invoice.id` becomes required, including in locally constructed and narrowed Invoice shapes.

## Event notifications and request context

### Context migration

- v18.3.0 adds `stripeContext` to `RequestOptions` and `StripeConfig`.
- v19 adds a serializable `StripeContext` class.
- `EventNotification.context` changes from `string` to `StripeContext`.
- v19 no longer strips `stripe-context` from v1 requests or `stripe-account` from v2 requests.
- The server can reject requests carrying both headers. Migrate shared code to context and remove `stripeAccount` when both would be sent.

### Namespace and parser migration

v19 moves these types from `Stripe.V2` into `Stripe.V2.Core`:

- `Stripe.V2.EventDestination` to `Stripe.V2.Core.EventDestination`;
- `Stripe.V2.Event` to `Stripe.V2.Core.Event`;
- `Stripe.V2.EventBase` to `Stripe.V2.Core.EventBase`; and
- `Stripe.V2.Events.RelatedObject`, now `Stripe.V2.Core.Events.RelatedObject`.

It also:

- renames `StripeClient.parseThinEvent` to `parseEventNotification`;
- removes `Stripe.ThinEvent`;
- returns the typed `Stripe.V2.EventNotification` union; and
- adds `relatedObject`, `fetchRelatedObject()`, and `fetchEvent()` support.

From v19.1.0, `UnknownEventNotification` declares `fetchEvent()`. `fetchRelatedObject()` is always callable and returns `null` when no related object exists.

### Parser separation in v21

v21 throws when a payload is passed to the wrong webhook parser. Use:

- `parseEventNotification` for thin notifications; and
- `webhooks.constructEvent` for snapshot events.

v21 also adds distinct OAuth error classes and runtime handling for string-encoded v2 `int64` fields.

## V2 response and request behavior

### Response types

- v19 delete methods return `V2DeletedObject`, including the deleted object's ID and type.
- Nullable v2 response fields change from `prop: T | null` to optional `prop?: T`.

### List serialization and failures

- v20 serializes arrays on v2 retrieve and list calls with indexed keys such as `include[0]=foo&include[1]=bar`. Update mocks that expect repeated `include=...` keys.
- Upgrade to at least v20.3.1. Earlier v20 builds can turn a v2 list API error into an unhandled rejection that crashes Node rather than normally rejecting the list operation.

## HTTP clients and raw requests

### Raw file streaming

From v18.1.1, `rawRequest` accepts `host` and `streaming` options, enabling direct streaming from the Files host.

```ts
const file = await stripe.rawRequest(
  'GET',
  '/v1/files/file_123/contents',
  {},
  {host: 'files.stripe.com', streaming: true}
);
```

v18.2.1 limits request data to POST requests and stops incorrectly warning about v2 GET requests.

### Alternate runtimes and request bodies

- v19 fixes `FetchHttpClient` file uploads in alternate runtimes such as Bun. The regression affects v18.1.0 through v18.5.0.
- v19 computes JSON body length correctly for Unicode.
- Non-Node environments use `TextEncoder` instead of `Buffer.byteLength`.
- v20.1.2 fixes multipart upload content-length calculation.

## Decimal values in v21

Every generated `decimal_string` request and response field becomes `Stripe.Decimal` instead of `string`, including:

- Checkout foreign-exchange rates;
- Climate quantities;
- Billing decimal quantities and unit amounts;
- Issuing amount fields;
- Plan and Price decimal amounts; and
- Accounts v2 ownership percentages.

Construct with `Stripe.Decimal.from(...)` and serialize explicitly:

```ts
const quantity = Stripe.Decimal.from('1.25');
const serialized = quantity.toString();
```

Use v21.0.1 or newer for corrected CommonJS and ESM exports.

## Preview package channels

Starting with v19, preview packages no longer use the `beta` npm dist-tag. Select `latest`, `public-preview`, or `private-preview` for the intended release phase.

## Generated Accounts, Connect, and financial contracts

### Account and Person data

- v18.1.0 adds `minority_owned_business_designation`, company `registration_date`, and Person `us_cfpb_data`.
- v18.3.0 adds Account proof-of-address fields and payout-day settings.
- v18.4.0 adds Account Session instant-payout promotion; Identity related-person Account and Person fields become required.
- v18.5.0 adds Account Session balance-report, payout-details, and payout-reconciliation components.
- v20.1.0 generates `V2.Core.Account`, `AccountToken`, `AccountLink`, `AccountPerson`, and `AccountPersonToken`, with create, list, retrieve, update, close, and delete operations as applicable.
- v20.3.0 adds more Accounts v2 business-identity fields.

### Accounts v2 notifications

v20.2 adds typed notifications for:

- Account creation and closure;
- general and include-dependent Account updates;
- capability-status updates;
- Account Link returns; and
- Account Person creation, update, and deletion.

Account and Person notifications expose the corresponding `V2.Core.Account` or `V2.Core.AccountPerson` as their related object.

### Financial Connections, balances, and payouts

- v18.2.0 adds Account Session dispute components plus balance-type and dispute-prefunding fields.
- v18.2.0 adds the Pix Account capability.
- v18.5.0 adds `Payout.payout_method`.
- v20.0.0 adds Financial Connections account-number fields and account-number expiry/update events; Session client secrets become nullable.
- v20.3.0 adds reserve-related balance types.

## Generated Billing and invoicing contracts

- v18.1.0 makes `InvoiceLineItem.parent.subscription_item_details.subscription` nullable and adds Affirm Invoice settings.
- v18.2.0 adds Invoice `attach_payment` and the `invoice_payment.paid` event.
- v18.2.0 requires `usage_threshold.meter` when creating Billing Alerts.
- v18.2.0 restores Subscription `billing_thresholds` to generated types.
- v18.2.0 adds Credit Note pre- and post-payment amounts and the `mixed` type.
- v18.3.0 adds Subscription `migrate` and requires hosted payment-method saving in Account Invoice settings.
- v18.4.0 adds adjustable quantities to Billing Portal Subscription updates and Invoice rendering-template selection.
- v18.4.0 adds Schedule Phase `duration`; Subscription cancellation accepts `max_period_end` or `min_period_end`.
- v18.5.0 adds named Billing Portal configurations and metadata plus periods on Subscription-added Invoice Items.
- v19.2.0 makes Credit Grant `category` optional and adds `invoice.payment_attempt_required`.
- v19.2.0 lets Invoice Payments attach and filter by Payment Record.
- v19.3 adds `payment_record` as an InvoicePayment discriminator.
- v20.1.0 makes Invoice Item and Invoice Line Item Prices expandable and adds Invoice Line Item `subtotal`.
- v20.3.0 requires PayTo payment settings on Invoice and Subscription responses.
- v20.4.0 adds Pay by Bank to Invoice and Subscription settings and `payment_behavior` to Subscription Item deletion.

## Generated Checkout and payment contracts

### Checkout and payment methods

- v18.1.0 adds billing-details `tax_id`, Checkout `wallet_options`, automatic-tax `provider`, ConfirmationToken test payment-method options and card installments, Refund `pending_reason`, Billie PaymentIntent options, Pix PaymentMethodConfiguration, Klarna PaymentMethod Domains, and more tax IDs and registration countries.
- v18.2.0 makes Naver Pay `buyer_id` required.
- v18.3.0 adds crypto capabilities and payment-method fields plus recurring or future-use Klarna options.
- v18.4.0 adds Checkout `origin_context`, Pix future usage, and New Zealand bank accounts.
- v18.4.0 lets Payment Link lines use inline `price_data` instead of `price`.
- v18.5.0 adds transaction IDs across local methods, PayNow Reader and Location data, and Pix `amount_includes_iof`.
- v20.1.0 adds PayTo throughout payment flows.

### Payment records, attempts, and line items

- v19.2.0 adds `PaymentAttemptRecord`, `PaymentIntentAmountDetailsLineItem`, and `PaymentRecord` with list/retrieve operations and Payment Record reporting methods.
- v19.2.0 adds SetupIntent payment-method exclusions.
- v19.3 adds per-method `capture_method` for `card_present` PaymentIntents.
- v20.0.0 adds PaymentIntent `hooks`.
- v20.1.0 adds Checkout Line Item metadata and updates, Payment Record card details, and optional `PaymentIntent.transfer_data` and `Product.tax_code`.
- v20.3.0 adds adjustable quantities on Line Items and 3DS versions `2.3.0` and `2.3.1`.
- v20.4.0 makes Boleto tax IDs nullable and US-bank expected debit dates required on Payment Records.
- v20.4.0 adds Bacs mandate display details and US-bank `transaction_purpose`.

### Customer Sessions

v19.2.0 adds Customer Session mobile-sheet components.

## Generated Terminal, Issuing, Radar, Tax, and Treasury contracts

### Terminal

- v18.2.0 adds Terminal Reader input collection and success/timeout test helpers.
- v18.3.0 adds Terminal Reader `collect_payment_method`, `confirm_payment_intent`, and typed `terminal.reader.action_updated` snapshot events.
- v18.5.0 adds Terminal Android APK file purposes and card input for Reader test helpers.
- v19.2.0 adds Terminal Reader `last_seen_at`.
- v20.0.0 adds `Terminal.OnboardingLink.create`.
- v20.3.0 removes BGN from Terminal tipping.
- v20.4.0 adds Wi-Fi certificate/private-key file purposes, cellular configuration, and S710 device values.

### Issuing and Radar

- v18.5.0 adds expiration fields to Issuing Card creation.
- v20.3.0 adds `Radar.PaymentEvaluation.create`.
- v21 renames `risk_level` to `level` under both `Issuing.AuthorizationCreateParams.testHelpers.risk_assessment.card_testing_risk` and `merchant_dispute_risk`.
- v21 changes `Radar.PaymentEvaluation`: `recommended_action` and `signals` replace `insights` from the earlier preview shape.

### Tax, Identity, Reserve, and Treasury

- v18.1.0 makes `Tax.CalculationLineItem.reference` required.
- v18.3.0 adds Identity related-person matching and a Treasury Financial Account status filter.
- v20.0.0 adds `Tax.Association.find`.
- v20.1.0 adds Identity `related_customer_account`.
- v20.3.0 adds a `topup` linked flow to Treasury Received Debits.
- v20.4.0 adds `Reserve.Hold`, `Reserve.Plan`, and `Reserve.Release` plus their snapshot events.

## V2 events and filters

- v18.1.0 adds Event `context`.
- v19.2.0 adds comparison/type filters to `V2.Core.EventListParams` and adds `balance_settings.updated`.
- v20.0.0 replaces v2 Event-list `gt`, `gte`, `lt`, and `lte` filters with `created`.
- v20.1.0 adds `changes` to `V2.Core.Event`.

## Capability and error unions

- v18.4.0 removes `disabled` from `Capability.status`.
- During Basil, error unions add `tax_id_prohibited`, `forwarding_api_upstream_error`, `customer_session_expired`, and `india_recurring_payment_mandate_canceled`.
- During Clover, they add `payment_intent_rate_limit_exceeded`, `account_token_required_for_v2_account`, `request_blocked`, `storer_capability_missing`, and `storer_capability_not_active`.
- During Dahlia, they add `service_period_coupon_with_metered_tiered_item_unsupported`.
