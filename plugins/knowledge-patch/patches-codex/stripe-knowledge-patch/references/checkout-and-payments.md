# Checkout and Payments

## Checkout and Elements migrations

### Custom Checkout and initialization (`2025-03-31.basil`)

Checkout Sessions accept `ui_mode=custom`, allowing an Elements-based checkout
backed by the Session. Use the new Checkout initialization flow rather than the
hosted-page flow. The Payment Element's default layout also changes; configure
the layout explicitly when preserving the previous rendering matters.

### Removed entry points and synchronous initialization (`2025-09-30.clover`)

`redirectToCheckout` and deprecated messaging and bank Elements are removed.
Migrate callers to their replacement Checkout flow or replacement Elements.

`initCheckout` is synchronous. Use its return value directly instead of
awaiting it; Elements can mount without waiting for an initialization promise.

### Saved methods and client-secret validation (`2025-09-30.clover`)

Elements with Checkout Sessions no longer requires saved payment methods to be
enabled both on the Session and in the initialization call. Remove the duplicate
opt-in. Do not reuse an Intent client secret in a state rejected by the new
initialization check as capable of producing a broken payment form.

### Postal codes and Adaptive Pricing (`2025-09-30.clover`)

Checkout and the Payment Element no longer automatically collect card postal
codes in Canada, the United Kingdom, or Puerto Rico. Collect them explicitly
when required. Checkout Sessions remove `currency_conversion`; use
`presentment_details` for Adaptive Pricing.

## Checkout Session and Payment Link contracts

### Customer Session, metadata, and optional fields (`2024-09-30.acacia`)

Customer Sessions can enable the Payment Element, Checkout Sessions gain a
metadata update method, and Checkout `LineItem.description` becomes optional.
Product creation accepts `custom_unit_amount`.

Checkout Sessions and Payment Links can require customer tax-ID collection,
not merely enable it. Customer tax IDs add Swiss UID and Croatian OIB.

### Shipping, permissions, and optional items (`2025-03-31.basil`)

Checkout Sessions remove their shipping-details contract but allow
shipping-option updates. Sessions gain a permissions parameter, and Checkout
Sessions and Payment Links gain optional items. Payment Link custom fields also
gain a default value.

### Method controls, identity, and branding (`2025-09-30.clover`)

Checkout Sessions and PaymentIntents can exclude selected payment methods.
Checkout Sessions can also set per-method capture behavior. Use these controls
when method availability or capture strategy differs instead of applying one
Session-wide assumption.

Checkout Sessions add business-name and individual-name collection and
configurable branding. Products add a unit of measurement. Preserve the new
fields in response models and generated types.

### Mutable Payment Links (`2026-07-29.dahlia`)

Payment Links can be updated with shipping options, consent collection, and
future-usage settings. An existing link need not be replaced solely to change
these checkout controls.

## Payment-method contracts

### Method-specific reporting (`2024-09-30.acacia`)

BLIK adds a unique payer identifier, Affirm adds transaction IDs, Charges expose
`authorization_code`, Klarna Charge payer details add country, and Amazon Pay
Disputes add dispute type. Confirmation Tokens can expose CVC tokens through
payment-method options and include the customer ID in their payment-method
preview. Accept all additions in generated types and preview handling.

### Method availability (`2024-09-30.acacia`)

Payment Links add Multibanco, Twint, and Zip; the PaymentMethodConfiguration API
adds Twint; PaymentMethod brand and network enums add Girocard. Billing's
Multibanco surface is described in [billing.md](billing.md).

### Reuse, mutability, and capture (`2025-03-31.basil`)

Reusable Naver Pay, Billie, Satispay, and New Zealand BECS Direct Debit are
added. Naver Pay fields are immutable after PaymentMethod creation, while the
WeChat Pay client parameter is optional until confirmation. Interac card
payments no longer support manual capture.

### Newer payment methods and outcomes (`2025-09-30.clover`)

MB WAY is available across Checkout and additional payment surfaces. Decline
code behavior changes for Alma, Amazon Pay, Billie, Satispay, and South Korean
payment methods. Submitted stablecoin payments gain a processing status, and
Klarna disputes gain a chargeback-loss reason. Status, reason, and decline-code
handling needs an unknown-value path.

The crypto token currency enum adds `cash`; accept it even though it represents
cash rather than a blockchain token.

### Intent constraints and non-reuse (`2026-07-29.dahlia`)

Payment Intents and Setup Intents add `allowed_payment_method_types`, allowing
eligible methods to be constrained per Intent rather than only through broader
configuration. Samsung Pay and PAYCO accept `setup_future_usage=none`; send it
when reuse is explicitly not intended.

FPX supports additional banks. Treat the bank set as extensible. Funding
instructions support CHAPS, so network validation and rendering must accept it.

### Authentication and Radar context (`2026-07-29.dahlia`)

3D Secure results add `data_share_only`. Accept it without treating it as an
unknown authentication failure. Payment Intent Radar options add `referrer`;
preserve it in Intent builders and serializers.

## Errors, refunds, disputes, and records

### Error-code growth (`2024-09-30.acacia`)

The error-code surface adds transaction-limit failure and invalid
mandate-reference-prefix failure cases for Bacs Direct Debit and SEPA Direct
Debit. Handle them distinctly and retain an unknown branch.

### Classification additions (`2024-09-30.acacia`)

Credit Notes add email types, and card Disputes add case-type classification.
Accept the new values in deserializers and exhaustive switches.

### Refund and dispute attribution (`2026-07-29.dahlia`)

Refunds expose customer and payment-method details. Preserve them rather than
resolving every attribution through the original payment. Disputes expose the
card network inside payment-method details; preserve the expanded nested shape
and use the returned network directly when needed.

### Payment Record listing (`2026-07-29.dahlia`)

Payment Records have a list operation, allowing integrations to enumerate them
without relying only on individually known identifiers.

## List API migration (`2025-03-31.basil`)

List APIs no longer support expanding `total_count`, and the `page` parameter is
removed. Do not use either as a pagination or collection-size mechanism.

## PaymentIntent line items (`billing-and-payments-v2`)

### Request and response shape

PaymentIntents accept up to 200 entries under `amount_details[line_items]` for
cards, Klarna, and PayPal. Every entry requires `product_name`, a nonnegative
`unit_cost`, and a positive `quantity`. Put transaction references in
`payment_details`, and shipping, tax, and discounts in `amount_details`.

Line items are omitted from responses by default. Expand
`amount_details.line_items` when they are needed:

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

### Payment-method data and capture timing

Each line can carry card `commodity_code`; Klarna product, image, and reference
data; and PayPal description, category, and seller data. Method-specific fields
for multiple candidate methods may be supplied together even when not all are
used.

Lines supplied at confirmation persist for either capture mode. If omitted at
confirmation, they can be supplied at capture and `amount_details` can be
updated then. Surcharge, multi-capture, overcapture, and authorization-adjustment
flows remain compatible. PayPal does not support capture-time line items.

### Arithmetic validation

By default, line items must reconcile with the PaymentIntent amount after
shipping, discounts, and tax; otherwise the request fails with HTTP 400.
Top-level and per-line tax are mutually exclusive, as are top-level and per-line
discounts.

`amount_details[enforce_arithmetic_validation]=false` lets a mismatched request
proceed and exposes details in `amount_details.error`. Erroneous card lines are
not sent to networks and cannot qualify for L2 or L3 savings.

### L2, L3, and Product 3

L2 requires transaction tax and `payment_details[order_reference]`. L3 or
Product 3 additionally requires each line's product name, unit cost, quantity,
product code, unit of measure, and line-level or transaction-level tax.

The programs cover US-domestic and intra-EU Visa, Mastercard, and American
Express transactions. American Express requires a direct agreement and
receives only the first four items. Visa L2 ended in April 2026. API acceptance
does not prove that MCC or tax rules qualify the payment for a reduced rate.
