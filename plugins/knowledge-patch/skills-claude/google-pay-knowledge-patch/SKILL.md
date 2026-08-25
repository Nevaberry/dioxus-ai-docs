---
name: google-pay-knowledge-patch
description: Google Pay
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Google Pay web merchant integration

Use this skill when working on Google Pay web merchant integrations that
configure payment-sheet behavior, addresses, cards, payment methods, injected
elements, buttons, callback intents, test cards, or direct-integration keys.

Keep every implementation claim within the options and behavior documented
here. In particular, do not infer option values that are not shown.

## Reference index

| Reference | Topics |
| --- | --- |
| [Payment sheet and addresses](references/payment-sheet-and-addresses.md) | Administrative-area formatting, checkout labels, promo codes, and callback behavior |
| [Cards, methods, and testing](references/cards-methods-and-testing.md) | Funding sources, gateway test cards, INTERAC, and PayPal requests |
| [Security, buttons, and direct integration](references/security-buttons-and-direct.md) | CSP nonces, button borders, and ECv2 signing keys |

## Quick reference

### Option and response map

| API or object | Field or value | Documented behavior |
| --- | --- | --- |
| `PaymentOptions` | `nonce` | Applies the supplied CSP nonce to every dynamically injected `<style>` and `<script>` element |
| `CardInfo` | `cardFundingSource` | Reports `UNKNOWN`, `CREDIT`, `DEBIT`, or `PREPAID` |
| `BillingAddressParameters` | `format: "FULL-ISO3166"` | Requests the documented ISO 3166 address format |
| `ShippingAddressParameters` | `format` | Makes address formatting available for shipping parameters |
| `Address` | `iso3166AdministrativeArea` | Returns the ISO 3166 administrative area |
| `IntermediateAddress` | `iso3166AdministrativeArea` | Returns the ISO 3166 administrative area |
| `TransactionInfo` | `checkoutOption` | Selects the payment-sheet checkout label |
| `ButtonOptions` | `borderButtonType` | Exposes border selection through supported button configuration |
| `OfferInfo` | promo-code updates | Updates and displays promo codes on the payment sheet |
| `CardParameters` | `allowedCardNetworks: ["INTERAC"]` | Requests the INTERAC network |
| `PaymentMethod` request | `type` | Supports PayPal as a payment method |

### Apply a CSP nonce

`PaymentOptions` accepts `nonce`. When it is provided, the same CSP nonce is
applied to every dynamically injected `<style>` and `<script>` element.

```js
const paymentOptions = {
  nonce: cspNonce,
};
```

For the complete security and button notes, read
[Security, buttons, and direct integration](references/security-buttons-and-direct.md).

### Request ISO 3166 administrative areas

Set `BillingAddressParameters.format` to `FULL-ISO3166` when using the
documented billing-address format.

```js
const billingAddressParameters = {
  format: "FULL-ISO3166",
};
```

`ShippingAddressParameters` also has a `format` property. Returned `Address`
and `IntermediateAddress` objects include `iso3166AdministrativeArea`.

For the related payment-sheet settings, read
[Payment sheet and addresses](references/payment-sheet-and-addresses.md).

### Select the checkout label

Set `TransactionInfo.checkoutOption` according to the label the payment sheet
must display:

| Value | Label |
| --- | --- |
| `DEFAULT` | “Continue” |
| `CONTINUE_TO_REVIEW` | “Review Order” |
| `COMPLETE_IMMEDIATE_PURCHASE` | “Pay” |

```js
const transactionInfo = {
  checkoutOption: "CONTINUE_TO_REVIEW",
};
```

### Branch on card funding source

Read `CardInfo.cardFundingSource` as one of:

- `UNKNOWN`
- `CREDIT`
- `DEBIT`
- `PREPAID`

The response lets pricing, discount, or surcharge logic distinguish the
selected card's underlying funding type.

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

The documented guidance does not supply a literal value or request example;
do not invent one from this skill.

### Display promo codes

Use the `OfferInfo` API to update and display promo codes on the payment sheet.

### Account for callback feature parity

Web integrations using `authorizePayments` or Dynamic Price Updates callback
intents receive the non-callback payment-sheet UX except where that UX is
incompatible. `OFFER` callbacks are an example of an incompatibility.

Liability shift and processor test cards are also available to these callback
integrations.

### Configure a supported button border

Pass `borderButtonType` in the `ButtonOptions` supplied to `createButton()`.
This exposes border selection through the supported button configuration.

The documented guidance does not enumerate border values; do not add values
from this skill.

### Test billing addresses across markets

In the `TEST` environment, gateway test cards support billing addresses from
27 markets rather than only the US. Examples include:

- UK
- France
- Germany
- Spain
- Japan
- Hong Kong
- Brazil

Use [Cards, methods, and testing](references/cards-methods-and-testing.md) for
the complete card and payment-method notes.

### Maintain ECv2 direct-integration keys

For `DIRECT` integrations, ECv2 permits a static, long-lived Google signing
key. That key only needs updating every ten years.

## Task routing

### Editing payment-sheet behavior

1. Use `TransactionInfo.checkoutOption` for the checkout label.
2. Use `OfferInfo` for payment-sheet promo codes.
3. Check callback compatibility when using `authorizePayments` or Dynamic
   Price Updates callback intents.
4. Read
   [Payment sheet and addresses](references/payment-sheet-and-addresses.md)
   for the supported behavior.

### Editing address requests or responses

1. Use `FULL-ISO3166` as the documented billing `format` value.
2. Account for the shipping `format` property.
3. Read `iso3166AdministrativeArea` from returned `Address` and
   `IntermediateAddress` objects.
4. Read
   [Payment sheet and addresses](references/payment-sheet-and-addresses.md)
   for the address notes.

### Editing card or method handling

1. Use `CardInfo.cardFundingSource` for funding-type distinctions.
2. Include `INTERAC` in `allowedCardNetworks` when requesting that network.
3. Account for PayPal support on the `PaymentMethod` request `type` property.
4. Use the expanded gateway test-card billing-address markets in `TEST`.
5. Read [Cards, methods, and testing](references/cards-methods-and-testing.md)
   for the complete notes.

### Editing initialization, buttons, or direct keys

1. Supply `PaymentOptions.nonce` when applying a CSP nonce to injected
   elements.
2. Supply `ButtonOptions.borderButtonType` to expose supported border
   selection in `createButton()`.
3. Account for the documented ECv2 signing-key update interval for `DIRECT`
   integrations.
4. Read
   [Security, buttons, and direct integration](references/security-buttons-and-direct.md)
   for the complete notes.

## Fidelity rules

- Preserve exact identifiers and enum values shown in this skill.
- Preserve the distinction between the `TEST` environment and general
  integration behavior.
- Preserve the callback exception: parity applies except where incompatible,
  with `OFFER` callbacks given as an example.
- Do not turn examples of supported test-card markets into a complete list.
- Do not invent a PayPal `type` literal or `borderButtonType` values.
- Do not shorten the ECv2 key statement into a different rotation schedule.
