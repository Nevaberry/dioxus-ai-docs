# Checkout and Payments

## Stripe.js and Elements breaking changes

### Removed and renamed entry points

- `redirectToCheckout` and the superseded messaging and bank Elements are removed in `2025-09-30.clover`.
- Deprecated Stripe.js PaymentIntent, SetupIntent, and Sources methods are removed in `2026-03-25.dahlia`; migrate to their current replacements before upgrading.
- `stripe.initCheckout(...)` is renamed to `stripe.initCheckoutElements(...)`.
- `stripe.initEmbeddedCheckout(...)` is renamed to `stripe.createEmbeddedCheckoutPage(...)`.

### Initialization and updates

- The custom Checkout UI introduced in `2025-03-31.basil` pairs custom `ui_mode` with `initCheckout` for an Elements-based Checkout experience.
- In `2025-09-30.clover`, `initCheckout` is synchronous. Do not await it:

```js
const checkout = stripe.initCheckout(options);
```

- In `2026-03-25.dahlia`, `elements.update()` returns a Promise. Await it before work that depends on the update:

```js
await elements.update(options);
```

- `options.layout.radios` no longer accepts booleans; use a supported non-boolean layout configuration.
- Checkout Session `ui_mode` enum values change. Update validators and exhaustive switches.

### Defaults and state safety

- The Payment Element default layout changes in `2025-03-31.basil`. Configure the intended layout explicitly instead of depending on the former implicit default.
- Elements blocks reuse of Intent client secrets in states that could render a broken payment form (`2025-09-30.clover`).
- With Checkout Sessions, enabling saved payment methods on the Session is sufficient; do not also enable them in the initialization call.
- The Address Element state value returned by `getValue()` and change events defaults to Latin-formatted characters in `2026-03-25.dahlia`. Do not assume native-script state text.
- Payment Element future-usage configuration changes, including its interaction with payment-method options and Customer Sessions. Revalidate existing future-usage setup.

## Checkout Session contracts

### Session fields and updates

- Customer Sessions can enable the Payment Element (`2024-09-30.acacia`).
- Checkout Sessions support metadata updates, and `LineItem.description` becomes optional.
- Product creation accepts `custom_unit_amount`.
- In `2025-03-31.basil`, Checkout Sessions remove shipping details, allow shipping-option updates, and add a permissions parameter.
- Checkout Sessions and Payment Links add optional items.
- Session updates use new semantics; update clients rather than assuming create-time behavior applies unchanged.
- Payment Links custom fields can specify a default value.

### Postal code, branding, and names

- Checkout and the Payment Element no longer automatically collect postal codes for card payments in Canada, the United Kingdom, or Puerto Rico (`2025-09-30.clover`). Collect them explicitly if required.
- Checkout Sessions add branding settings and collection of business or individual names.
- Customer objects can store those business or individual names.
- Product data can specify a unit of measurement.

### Payment-method controls

- Checkout Sessions can exclude selected payment methods and set capture behavior per payment method (`2025-09-30.clover`).
- PaymentIntents also support payment-method exclusion.
- Treat an unavailable method as potentially intentional, and honor method-specific capture settings.

### Adaptive Pricing

- Checkout adds `presentment_details` in `2025-03-31.basil`, exposing customer-facing currency presentation for Adaptive Pricing.
- Checkout Sessions remove `currency_conversion` in `2025-09-30.clover`; read the existing `presentment_details` field instead.
- Adaptive Pricing Subscriptions later expose their own presentment details; see [billing.md](billing.md).

### Subscription tracking

In `2026-03-25.dahlia`, Checkout Session creation adds:

- an integration identifier for grouping and tracking Sessions; and
- a pending-invoice-item interval for subscription payments.

## PaymentIntent line items

### Availability and limits

PaymentIntents accept line items for cards, Klarna, and PayPal.

- Supply at most 200 items.
- American Express receives only the first four items.
- Automatic and manual capture are supported, including multicapture and overcapture.
- Card line items are incompatible with partial or decrement authorization and with airline, lodging, car-rental, and other industry-specific metadata.

### Required fields and program data

Every `amount_details.line_items` entry requires:

- `product_name`;
- nonnegative `unit_cost` in the smallest currency unit; and
- a positive integer `quantity`.

Put transaction identifiers under `payment_details`.

- Level 2 card data requires `payment_details.order_reference` and transaction-level tax.
- Level 3 adds per-line tax, `product_code`, and `unit_of_measure`.
- Transaction-level and line-level tax are mutually exclusive.
- Transaction-level and line-level discounts are mutually exclusive.

```sh
curl https://api.stripe.com/v1/payment_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -d amount=2100 \
  -d currency=usd \
  -d "payment_method_types[]=card" \
  -d "payment_details[order_reference]=order_123" \
  -d "amount_details[line_items][0][product_name]=Widget" \
  -d "amount_details[line_items][0][unit_cost]=2000" \
  -d "amount_details[line_items][0][quantity]=1" \
  -d "amount_details[line_items][0][tax][total_tax_amount]=100" \
  -d "amount_details[line_items][0][product_code]=SKU001" \
  -d "amount_details[line_items][0][unit_of_measure]=each"
```

### Card eligibility

Card line-item programs cover US domestic and intra-EU Visa, Mastercard, and American Express transactions. Level 2 is limited to business, purchasing, and corporate cards; Level 3/Product 3 is limited to purchasing and corporate cards. Stripe accepts data that misses network MCC or tax requirements, so request success does not establish interchange-rate eligibility.

### Method-specific fields

- Card lines can carry `commodity_code`.
- Klarna lines can carry product and image URLs plus reference fields.
- PayPal lines can carry `description`, `category`, and connected-account `sold_by`.
- Supported method-specific fields may be sent even when another method is ultimately confirmed.
- Klarna derives line amount as `(unit_cost * quantity) - discount_amount + tax.total_tax_amount`; do not send an explicit line amount.

### Confirmation, capture, and retrieval

- Supply line items at confirmation for either capture mode and retain them for later capture.
- Alternatively, first supply or update line items during capture.
- Capture-time line items are not supported for PayPal.
- Responses omit line items by default. Request `expand[]=amount_details.line_items` to retrieve them.

### Arithmetic validation

A line-item arithmetic mismatch returns HTTP 400 by default. Setting `amount_details[enforce_arithmetic_validation]=false` permits processing and exposes the mismatch in `amount_details.error`. Erroneous card line items are not sent to the networks and cannot qualify for Level 2 or Level 3 rates.

```sh
-d "amount_details[enforce_arithmetic_validation]=false" \
-d "expand[]=amount_details.line_items"
```

## Payment Records and reporting

- Card properties on Payment Records have revised requirements in `2026-03-25.dahlia`.
- Payment Records expose 3D Secure authentication properties.
- Update readers and validators for the revised card shape instead of assuming earlier requirements.

## Confirmation Tokens and payment details

In `2024-09-30.acacia`:

- Confirmation Tokens can return CVC tokens on request and expose a Customer ID in the payment-method preview.
- BLIK exposes its unique payer.
- Affirm exposes transaction IDs.
- Charges expose `authorization_code`.
- Klarna exposes payer country.
- Amazon Pay disputes expose a dispute type.

## Cards, wallets, and local payment methods

### In-person card details

- Interac is supported as an in-person PaymentMethod (`2024-09-30.acacia`).
- `card_present` Charges and PaymentMethods expose wallet details.
- Girocard appears as a PaymentMethod brand and network.
- Interac card-present payments no longer support manual capture in `2025-03-31.basil`.

### Added and changed methods

- Payment Links add Multibanco, Twint, and Zip; Billing adds Multibanco; and PaymentMethodConfiguration can configure Twint (`2024-09-30.acacia`).
- Naver Pay PaymentMethods become reusable in `2025-03-31.basil`, but their Naver Pay fields are immutable after creation.
- Billie, Satispay, and New Zealand BECS Direct Debit are added.
- WeChat Pay no longer requires its client parameter before confirmation.
- MB WAY is added in `2025-09-30.clover`.
- UPI supports one-time and recurring payments in India in `2026-03-25.dahlia`.

### Crypto and stablecoins

- Submitted stablecoin payments expose a processing status (`2025-09-30.clover`).
- The crypto token currency enum adds `cash`; do not assume every enum member denotes cryptocurrency.
- Checkout can configure future usage at the crypto-payment-method level (`2026-03-25.dahlia`).
- Crypto payments accept `Tempo` as a network value.

## Tax IDs and payment errors

### Customer tax IDs

Customer tax IDs add Switzerland UID and Croatia OIB types in `2024-09-30.acacia`. Checkout and Payment Links can require Customer tax-ID collection.

### Errors and classifications

- Bacs Direct Debit and SEPA Direct Debit add distinct errors for exceeded transaction limits and invalid mandate-reference prefixes (`2024-09-30.acacia`).
- Vault and Forward return HTTP 402 for upstream request timeouts (`2025-03-31.basil`).
- SetupIntents add an error for mobile-wallet failures.
- Decline-code sets change for Alma, Amazon Pay, Billie, Satispay, and South Korean payment methods in `2025-09-30.clover`; preserve an unknown-code path.
- BalanceTransaction adds types for Stripe-balance payments, and Customer balance transactions add transaction types (`2025-03-31.basil`).
