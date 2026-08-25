# SDK v6 Components and Types

## Non-null message content

`PayPalMessagesSession.fetchContent()` returns `Promise<MessageContent>`, not
`Promise<MessageContent | null>`.

API failures produce an empty `MessageContent` sentinel with no
`messageItems`, causing `<paypal-message>` to collapse. `null` checks are dead
code.

## Apple Pay button enablement

`ApplePayOneTimePaymentButton` no longer has a `disabled` prop because
`<apple-pay-button>` ignored the attribute and manages availability through
`canMakePayments()`.

Merchants must control any additional presentation state themselves.

## Basic Card buyer country

In JSX, `<paypal-basic-card-button>` takes the kebab-case `buyer-country`
attribute, not `buyerCountry`.

```tsx
<paypal-basic-card-button buyer-country="US" />
```

React versions before 19 lowercase the camel-case form to an attribute that
the element does not observe.

## Google Pay script requirement

The React Google Pay component raises an error when it mounts without the
Google Pay script loaded, rather than continuing without an explicit failure.

## Custom-element DOM types

Non-React TypeScript users receive `HTMLElementTagNameMap` types for the
PayPal, Venmo, Pay Later, Credit, Basic Card, messages, and Apple Pay custom
elements.

```ts
const button = document.createElement("paypal-pay-later-button");
button.countryCode = "US";
button.productCode = "PAYLATER";
```

## v6 subpath resolution

The `@paypal/paypal-js` `./sdk-v6` export has a `default` condition. Bundlers
and tracers without a more specific matching condition can resolve the v6
entry instead of falling back to v5.

## Venmo vault-without-purchase approval data

The v6 `OnApproveData` type includes `vaultSetupToken`. The
`createVaultSetupToken` and `onApprove` contracts cover Venmo save-payment
flows that do not make a purchase.
