# Addresses and Checkout

## ISO 3166 administrative-area formatting

`BillingAddressParameters.format` accepts `FULL-ISO3166`.

```js
const billingAddressParameters = {
  format: "FULL-ISO3166",
};
```

`ShippingAddressParameters` also has a `format` property. Returned `Address`
and `IntermediateAddress` objects include
`iso3166AdministrativeArea`.

## Payment-sheet checkout labels

Set `TransactionInfo.checkoutOption` to `CONTINUE_TO_REVIEW` for a “Review
Order” button.

```js
const transactionInfo = {
  checkoutOption: "CONTINUE_TO_REVIEW",
};
```

The other documented values display these labels:

| Value | Displayed label |
| --- | --- |
| `DEFAULT` | “Continue” |
| `COMPLETE_IMMEDIATE_PURCHASE` | “Pay” |

## Payment-sheet promo codes

The `OfferInfo` API lets merchants update and display promo codes on the
payment sheet.
