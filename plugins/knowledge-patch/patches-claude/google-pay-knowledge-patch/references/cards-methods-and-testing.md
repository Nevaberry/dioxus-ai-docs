# Cards, payment methods, and testing

Use this reference for card funding responses, card-network requests,
payment-method requests, and gateway test cards.

## Card funding-source responses

`CardInfo.cardFundingSource` reports the selected card as one of:

- `UNKNOWN`
- `CREDIT`
- `DEBIT`
- `PREPAID`

This response lets pricing, discount, or surcharge logic distinguish the
underlying funding type.

## INTERAC card-network requests

`CardParameters.allowedCardNetworks` supports `INTERAC`.

```js
const cardParameters = {
  allowedCardNetworks: ["INTERAC"],
};
```

## PayPal payment-method requests

The `type` property of a `PaymentMethod` request supports PayPal as a payment
method.

No literal PayPal `type` value is specified here.

## Multi-market gateway test cards

In the `TEST` environment, gateway test cards support billing addresses from
27 markets rather than only the US. This enables country-specific end-to-end
billing tests.

Examples of supported markets include:

- UK
- France
- Germany
- Spain
- Japan
- Hong Kong
- Brazil

These markets are examples, not a complete list of all 27.

## Implementation checklist

- Handle all four documented `cardFundingSource` responses.
- Use the funding-source response for pricing, discount, or surcharge logic
  that distinguishes the underlying funding type.
- Add `INTERAC` to `allowedCardNetworks` when requesting that card network.
- Account for PayPal support through the `PaymentMethod` request `type`
  property without inventing an unspecified literal value.
- Use gateway test cards in `TEST` for country-specific billing tests across
  the expanded set of markets.
