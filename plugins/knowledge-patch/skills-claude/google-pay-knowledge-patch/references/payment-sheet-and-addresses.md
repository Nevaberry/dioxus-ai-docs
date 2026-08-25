# Payment sheet and addresses

Use this reference for address formatting and payment-sheet behavior in web
merchant integrations.

## ISO 3166 administrative-area formatting

`BillingAddressParameters.format` accepts `FULL-ISO3166`.

```js
const billingAddressParameters = {
  format: "FULL-ISO3166",
};
```

`ShippingAddressParameters` also has a `format` property.

Returned `Address` and `IntermediateAddress` objects include
`iso3166AdministrativeArea`.

## Checkout labels

Set `TransactionInfo.checkoutOption` to control the payment-sheet checkout
label.

| `checkoutOption` value | Displayed label |
| --- | --- |
| `DEFAULT` | “Continue” |
| `CONTINUE_TO_REVIEW` | “Review Order” |
| `COMPLETE_IMMEDIATE_PURCHASE` | “Pay” |

```js
const transactionInfo = {
  checkoutOption: "CONTINUE_TO_REVIEW",
};
```

## Promo codes

The `OfferInfo` API lets merchants update and display promo codes on the
payment sheet.

## Callback-integration feature parity

Web integrations using `authorizePayments` or Dynamic Price Updates callback
intents receive the non-callback payment-sheet UX except where incompatible.
`OFFER` callbacks are an example of an incompatibility.

Liability shift and processor test cards are also available to these callback
integrations.

## Implementation checklist

- For billing administrative areas, set `format` to `FULL-ISO3166`.
- Account for the `format` property on `ShippingAddressParameters`.
- Read `iso3166AdministrativeArea` from `Address` and `IntermediateAddress`.
- Select `DEFAULT`, `CONTINUE_TO_REVIEW`, or
  `COMPLETE_IMMEDIATE_PURCHASE` according to the required checkout label.
- Use `OfferInfo` when updating and displaying payment-sheet promo codes.
- When using `authorizePayments` or Dynamic Price Updates callback intents,
  preserve the documented incompatibility exception.
