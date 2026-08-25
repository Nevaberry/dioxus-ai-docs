# Payment Methods and Processing

## Card funding-source responses

`CardInfo.cardFundingSource` reports the selected card as one of:

- `UNKNOWN`
- `CREDIT`
- `DEBIT`
- `PREPAID`

This lets pricing, discount, or surcharge logic distinguish the underlying
funding type.

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

## Callback-integration feature parity

Web integrations using `authorizePayments` or Dynamic Price Updates callback
intents receive the non-callback payment-sheet UX except where incompatible,
such as `OFFER` callbacks.

Liability shift and processor test cards are also available to these callback
integrations.

## ECv2 direct-integration keys

For `DIRECT` integrations, ECv2 permits a static, long-lived Google signing
key that only needs updating every ten years.
