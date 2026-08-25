---
name: google-pay-knowledge-patch
description: Google Pay
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Google Pay Knowledge Patch

Use this skill when implementing or reviewing Google Pay Web merchant
integrations that involve payment-sheet behavior, callback intents, address
formats, card or payment-method configuration, test cards, button styling,
content security policy nonces, or direct-integration signing keys.

## How to use this skill

1. Start with the quick reference for the relevant integration surface.
2. Open the indexed reference file for the complete guidance on that topic.
3. Preserve the documented property names, enum values, labels, and scope.
4. Do not infer unlisted configuration values or behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Web configuration and testing](references/web-configuration-and-testing.md) | CSP nonces, supported button borders, multi-market gateway test cards |
| [Addresses and checkout](references/addresses-and-checkout.md) | ISO 3166 administrative areas, checkout labels, payment-sheet promo codes |
| [Payment methods and processing](references/payment-methods-and-processing.md) | Card funding sources, INTERAC, PayPal, callback parity, ECv2 direct-integration keys |

## Quick reference

### Apply a CSP nonce to injected elements

`PaymentOptions` accepts a `nonce`. When it is present, the CSP nonce is
applied to every dynamically injected `<style>` and `<script>` element.

```js
const paymentOptions = {
  nonce: cspNonce,
};
```

See
[Web configuration and testing](references/web-configuration-and-testing.md)
for the web-configuration details.

### Request full ISO 3166 administrative-area data

Set `BillingAddressParameters.format` to `FULL-ISO3166`.

```js
const billingAddressParameters = {
  format: "FULL-ISO3166",
};
```

`ShippingAddressParameters` also has a `format` property. Returned `Address`
and `IntermediateAddress` objects include
`iso3166AdministrativeArea`.

See [Addresses and checkout](references/addresses-and-checkout.md) for the
address-format details.

### Select the payment-sheet checkout label

Set `TransactionInfo.checkoutOption` according to the label the payment sheet
should display.

| Value | Displayed label |
| --- | --- |
| `DEFAULT` | “Continue” |
| `CONTINUE_TO_REVIEW` | “Review Order” |
| `COMPLETE_IMMEDIATE_PURCHASE` | “Pay” |

```js
const transactionInfo = {
  checkoutOption: "CONTINUE_TO_REVIEW",
};
```

See [Addresses and checkout](references/addresses-and-checkout.md) for related
payment-sheet guidance.

### Read the selected card's funding source

`CardInfo.cardFundingSource` reports one of these values:

| Value |
| --- |
| `UNKNOWN` |
| `CREDIT` |
| `DEBIT` |
| `PREPAID` |

The value lets pricing, discount, or surcharge logic distinguish the selected
card's underlying funding type.

See
[Payment methods and processing](references/payment-methods-and-processing.md)
for card and payment-method details.

### Request INTERAC

`CardParameters.allowedCardNetworks` supports `INTERAC`.

```js
const cardParameters = {
  allowedCardNetworks: ["INTERAC"],
};
```

### Request PayPal

The `type` property of a `PaymentMethod` request supports PayPal as a payment
method.

See
[Payment methods and processing](references/payment-methods-and-processing.md)
for both request options.

### Use callback integrations with payment-sheet feature parity

Web integrations using `authorizePayments` or Dynamic Price Updates callback
intents receive the non-callback payment-sheet UX except where incompatible,
such as `OFFER` callbacks.

Liability shift and processor test cards are also available to these callback
integrations.

See
[Payment methods and processing](references/payment-methods-and-processing.md)
for the callback-integration scope.

### Manage ECv2 direct-integration keys

For `DIRECT` integrations, ECv2 permits a static, long-lived Google signing
key that only needs updating every ten years.

See
[Payment methods and processing](references/payment-methods-and-processing.md)
for the direct-integration guidance.

### Configure a supported button border

`ButtonOptions` passed to `createButton()` accepts `borderButtonType`. This
exposes border selection through the supported button configuration.

See
[Web configuration and testing](references/web-configuration-and-testing.md)
for button configuration.

### Display and update promo codes

The `OfferInfo` API lets merchants update and display promo codes on the
payment sheet.

See [Addresses and checkout](references/addresses-and-checkout.md) for
payment-sheet offer guidance.

### Test billing addresses across markets

Gateway test cards in the `TEST` environment support billing addresses from
27 markets rather than only the US. This enables country-specific end-to-end
billing tests.

Supported examples include:

- UK
- France
- Germany
- Spain
- Japan
- Hong Kong
- Brazil

See
[Web configuration and testing](references/web-configuration-and-testing.md)
for the testing details.

## Integration review checklist

- If injected styles or scripts must carry a CSP nonce, provide
  `PaymentOptions.nonce`.
- If administrative-area values need ISO 3166 formatting, use
  `FULL-ISO3166` and read `iso3166AdministrativeArea` from returned address
  objects.
- If the payment-sheet button label matters, select the matching
  `TransactionInfo.checkoutOption` value.
- If pricing, discount, or surcharge logic depends on funding type, read
  `CardInfo.cardFundingSource`.
- If the request needs the INTERAC network, include `INTERAC` in
  `allowedCardNetworks`.
- If the payment method is PayPal, use the supported `PaymentMethod` request
  type.
- If the integration uses `authorizePayments` or Dynamic Price Updates
  callback intents, account for the stated callback feature parity and the
  `OFFER` incompatibility example.
- If the integration is `DIRECT`, account for the ECv2 static signing-key
  update interval.
- If the button needs a supported border selection, use `borderButtonType` in
  the `ButtonOptions` passed to `createButton()`.
- If promo codes appear on the payment sheet, use `OfferInfo` to update and
  display them.
- If billing behavior varies by country, gateway test cards in `TEST` support
  billing addresses across 27 markets.
