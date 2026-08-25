# v6 Elements and Modules Reference

## Custom elements

### Basic-card buyer country

In JSX, `<paypal-basic-card-button>` takes the kebab-case `buyer-country`
attribute, not `buyerCountry`.

```tsx
<paypal-basic-card-button buyer-country="US" />
```

React versions before 19 lowercase the camel-case form to an attribute the
element does not observe.

### DOM type maps

Non-React TypeScript users receive `HTMLElementTagNameMap` types for the
PayPal, Venmo, Pay Later, Credit, Basic Card, messages, and Apple Pay custom
elements.

```ts
const button = document.createElement("paypal-pay-later-button");
button.countryCode = "US";
button.productCode = "PAYLATER";
```

## Package resolution

### v6 subpath default condition

The `@paypal/paypal-js` `./sdk-v6` export has a `default` condition. This allows
bundlers and tracers without a more specific matching condition to resolve the
v6 entry instead of falling back to v5.

## Approval data

### Venmo vault without purchase

The v6 `OnApproveData` type includes `vaultSetupToken`. The
`createVaultSetupToken` and `onApprove` contracts cover Venmo save-payment
flows that do not make a purchase.
