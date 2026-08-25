# Checkout and Payments

## Checkout and Elements initialization

### Customer Sessions and Checkout updates (`2024-09-30.acacia`)

Customer Sessions can enable the Payment Element. Checkout Sessions have a
metadata update method, and `LineItem.description` is optional. Product creation
accepts `custom_unit_amount`; generated types and request builders must accept
these shapes.

### Custom Checkout UI (`2025-03-31.basil`)

Checkout Sessions accept `ui_mode=custom`, which keeps the Checkout Session as
the backing object for a custom Elements-based checkout. Use the new Checkout
initialization flow instead of the hosted-page flow for this mode.

### Saved-payment-method initialization (`2025-09-30.clover`)

Elements with Checkout Sessions no longer requires saved payment methods to be
enabled both on the Session and in the initialization call. Remove the duplicate
opt-in. Do not reuse an Intent client secret when initialization rejects its
state as capable of producing a broken payment form.

### Removed Stripe.js entry points (`2025-09-30.clover`)

`redirectToCheckout` and deprecated messaging and bank Elements are removed.
Migrate callers to the replacement Checkout flow or replacement Elements before
selecting this API contract.

### Synchronous initialization (`2025-09-30.clover`)

`initCheckout` returns synchronously. Use its return value directly instead of
awaiting it; Elements can then mount without waiting for an initialization
Promise.

### Payment Element layout (`2025-03-31.basil`)

The Payment Element's default layout changes. Set `layout` explicitly when the
former rendering must be preserved.

## Checkout collection and presentation

### Tax-ID collection (`2024-09-30.acacia`)

Checkout Sessions and Payment Links can require Customer tax-ID collection
rather than only enabling it.

### Shipping, permissions, and optional items (`2025-03-31.basil`)

Checkout Sessions remove the shipping-details contract but add shipping-option
updates and a permissions parameter. Checkout Sessions and Payment Links both
support optional items.

### Postal-code collection (`2025-09-30.clover`)

Checkout and the Payment Element no longer automatically collect postal codes
for card payments in Canada, the United Kingdom, or Puerto Rico. Collect them
explicitly when still required.

### Adaptive Pricing (`2025-09-30.clover`)

Checkout Sessions remove `currency_conversion`. Read Adaptive Pricing data from
`presentment_details`. Payment Link custom fields also gained a default value in
`2025-03-31.basil`; preserve it in presentation models.

### Identity, branding, and units (`2025-09-30.clover`)

Checkout Sessions can collect business and individual names and configure
branding. Products can specify a unit of measurement. Accept and preserve all
corresponding fields.

## Checkout lifecycle and controls

### Deferred Subscription creation (`2025-03-31.basil`)

Subscription-mode Checkout Sessions postpone Subscription creation until
payment completes. Do not assume a Subscription exists while checkout is in
progress. This lifecycle permits billing-detail changes after an initial
payment attempt.

### Per-method controls (`2025-09-30.clover`)

Checkout Sessions and PaymentIntents can exclude selected payment methods.
Checkout Sessions can also set capture behavior per payment method. Use these
controls when availability or capture strategy differs by method.

### Mutable Payment Links (`2026-07-29.dahlia`)

Payment Links can be updated with shipping options, consent collection, and
future-usage settings. Do not replace an existing link solely to change these
controls.

## Payment methods and method-specific contracts

### Added payment-method surfaces (`2024-09-30.acacia`)

- Payment Links add Multibanco, Twint, and Zip.
- Billing adds Multibanco.
- PaymentMethodConfiguration adds Twint.
- PaymentMethod brand and network enums add Girocard.

### Basil additions and constraints (`2025-03-31.basil`)

Hosted Invoice Pages add Klarna and configurable saving of payment methods for
one-time payments. Reusable methods add Naver Pay, Billie, Satispay, and New
Zealand BECS Direct Debit. Naver Pay fields become immutable after PaymentMethod
creation. The WeChat Pay client parameter is optional until confirmation.

### MB WAY (`2025-09-30.clover`, `2026-07-29.dahlia`)

MB WAY is available across Checkout and additional payment surfaces, and Hosted
Invoice Pages also support it. Payment-method configuration, invoice payment
selection, and fulfillment logic must recognize the method on those surfaces.

### Samsung Pay and PAYCO reuse intent (`2026-07-29.dahlia`)

Samsung Pay and PAYCO accept `setup_future_usage=none` to state that a payment
method will not be reused. Send this value when reuse is not intended rather
than implying future use.

### FPX and CHAPS (`2026-07-29.dahlia`)

FPX adds supported banks; treat the bank set as extensible. Funding instructions
support CHAPS, so network validation and rendering must accept it.

### Intent allowlists (`2026-07-29.dahlia`)

PaymentIntents and SetupIntents accept `allowed_payment_method_types`. Use it to
constrain methods on an individual Intent rather than relying only on broader
PaymentMethod configuration.

### Crypto currency values (`2025-09-30.clover`)

The crypto token currency enum adds `cash`. Accept it even though it represents
cash rather than a blockchain token.

## Confirmation, capture, and payment outcomes

### ConfirmationToken additions (`2024-09-30.acacia`)

Confirmation Tokens can expose CVC tokens through payment-method options and
include the Customer ID in the payment-method preview. Preview inspection and
confirmation-time CVC handling must accept both.

### Method-specific reporting (`2024-09-30.acacia`)

BLIK adds a unique payer identifier, Affirm adds transaction IDs, Charges add
`authorization_code`, Klarna Charge payer details add country, and Amazon Pay
Disputes add dispute type. Generated types and exhaustive handling must allow
the expanded values.

### Capture and cancellation semantics (`2025-03-31.basil`)

Partial capture and payment cancellation no longer create Refunds. Reconcile
from payment objects rather than waiting for a Refund. Interac card payments no
longer support manual capture. Vault and Forward upstream timeouts return HTTP
402.

### Error cases (`2024-09-30.acacia`)

Error codes add a transaction-limit failure and an invalid
mandate-reference-prefix failure for Bacs Direct Debit and SEPA Direct Debit.
Handle them distinctly and retain an unknown branch.

### Changed outcome values (`2025-09-30.clover`)

Decline-code behavior changes for Alma, Amazon Pay, Billie, Satispay, and South
Korean payment methods. Submitted stablecoin payments add a processing status,
and Klarna disputes add a documented chargeback-loss reason. Status, reason,
and decline-code handling needs an unknown-value path.

### 3D Secure results (`2026-07-29.dahlia`)

3D Secure authentication results add `data_share_only`. Accept it without
treating it as an unknown authentication failure.

## Refunds, disputes, top-ups, and records

### Refund attribution (`2026-07-29.dahlia`)

Refunds expose Customer and PaymentMethod details. Preserve those fields rather
than resolving all attribution through the original payment.

### Dispute network details (`2026-07-29.dahlia`)

Disputes expose card network under payment-method details. Use the returned
network directly when needed and preserve the expanded nested shape.

### Payment Record listing (`2026-07-29.dahlia`)

Payment Records support listing. Enumerate them through the API when identifiers
are not already known.

### Top-up funding and attribution (`2026-07-29.dahlia`)

Top-ups add `initiated_by` and can use PaymentMethods. Preserve initiator
attribution and accept PaymentMethod-backed creation and response models.

## PaymentIntent line items

### Base contract

PaymentIntents accept up to 200 entries under `amount_details[line_items]` for
cards, Klarna, and PayPal. Every item requires `product_name`, a nonnegative
`unit_cost`, and a positive `quantity`. Put transaction references in
`payment_details`; put shipping, tax, and discounts in `amount_details`.

Line items are omitted from responses by default. Request
`expand[]=amount_details.line_items` when they are needed:

```sh
curl https://api.stripe.com/v1/payment_intents \
  -u "${STRIPE_SECRET_KEY}:" \
  -d amount=2000 \
  -d currency=usd \
  -d "amount_details[line_items][0][product_name]=Widget" \
  -d "amount_details[line_items][0][unit_cost]=2000" \
  -d "amount_details[line_items][0][quantity]=1" \
  -d "expand[0]=amount_details.line_items"
```

### Method-specific data and capture timing

A line can contain card `commodity_code`; Klarna product, image, and reference
data; or PayPal description, category, and seller data. Fields for multiple
candidate methods can coexist even when only one method is used.

Line items supplied at confirmation persist in either capture mode. If omitted
at confirmation, they can be supplied at capture, when `amount_details` can also
be updated. Surcharge, multi-capture, overcapture, and authorization-adjustment
flows remain compatible. PayPal does not support capture-time line items.

### Arithmetic validation

By default, line items must reconcile with the PaymentIntent amount after
shipping, discounts, and tax; otherwise the request fails with HTTP 400. Do not
mix top-level and per-line tax, or top-level and per-line discounts.

`amount_details[enforce_arithmetic_validation]=false` allows a mismatched request
to proceed and exposes details in `amount_details.error`. Erroneous card line
items are not sent to networks and cannot qualify for L2 or L3 savings.

### L2, L3, and Product 3 qualification

L2 requires transaction tax and `payment_details[order_reference]`. L3 or
Product 3 also requires every line's product name, unit cost, quantity, product
code, unit of measure, and either line-level or transaction-level tax.

The programs cover US-domestic and intra-EU Visa, Mastercard, and American
Express transactions. American Express requires a direct agreement and receives
only the first four items. Visa L2 ended in April 2026. API acceptance alone
does not prove that MCC or tax rules qualify a payment for a reduced rate.
