---
name: paypal-knowledge-patch
description: PayPal
version: null
license: MIT
metadata:
  author: Nevaberry
---


# PayPal Knowledge Patch

Use this skill when implementing or reviewing PayPal Orders integrations,
PayPal React integrations, Braintree-backed PayPal flows, or v6 SDK custom
elements and module imports.

## How to use this skill

1. Identify whether the task concerns Orders API data, React and Braintree
   integration, or v6 custom elements and package resolution.
2. Read the matching reference file from the index.
3. Apply the exact current property, export, type, and custom-element names.
4. Check the breaking changes and deprecations below before adapting existing
   code.

## Reference index

| Reference | Topics |
| --- | --- |
| [Orders and API](references/orders-api.md) | Orders billing fields, payment-source data, field limits, networks, and action headers |
| [React and Braintree](references/react-and-braintree.md) | Server eligibility, provider hydration, PayPal Messages, Pay Later, session options, and button behavior |
| [v6 elements and modules](references/v6-elements-and-modules.md) | DOM types, custom-element attributes, package resolution, and Venmo approval data |

## Breaking changes and deprecations

### Use `usage_pattern` instead of `charge_pattern`

`charge_pattern` is deprecated. Orders accepts `usage_pattern` in billing
requests and returns `usage_pattern` in billing responses.

### Use the renamed server eligibility API

Import the plain async `fetchEligibleMethods` export from
`@paypal/react-paypal-js/sdk-v6/server`.

```ts
import { fetchEligibleMethods } from "@paypal/react-paypal-js/sdk-v6/server";

const response = await fetchEligibleMethods({
  environment: "production", // or "sandbox"
  headers,
  payload,
});
```

The deprecated name is `useFetchEligibleMethods`. The corresponding current
types are `UseEligibleMethodsOptions` and `UseEligibleMethodsResult`; they
replace the deprecated `UseFetchEligibleMethodsOptions` and
`UseFetchEligibleMethodsResult` aliases.

The `environment` option is required. Omitting it throws instead of silently
querying sandbox.

### Remove obsolete message-content null checks

`PayPalMessagesSession.fetchContent()` returns
`Promise<MessageContent>`, not `Promise<MessageContent | null>`.

On API failure it produces an empty `MessageContent` sentinel without
`messageItems`. That makes `<paypal-message>` collapse, so a `null` check is
dead code.

### Do not pass `disabled` to `ApplePayOneTimePaymentButton`

`ApplePayOneTimePaymentButton` no longer has a `disabled` prop. The underlying
`<apple-pay-button>` ignored that attribute and manages availability through
`canMakePayments()`.

Control any additional presentation state in merchant code.

### Use the kebab-case basic-card attribute

In JSX, pass `buyer-country` to `<paypal-basic-card-button>`:

```tsx
<paypal-basic-card-button buyer-country="US" />
```

Do not use `buyerCountry`. React versions before 19 lowercase that camel-case
form to an attribute the element does not observe.

## Eligibility and client hydration

### Avoid duplicate eligibility requests

Server eligibility requests can carry the merchant origin. Their response can
hydrate the v6 `PayPalProvider`, allowing the client to skip a duplicate
eligibility request.

### Fetch eligibility before Pay Later and Credit buttons

Pay Later and Credit buttons require eligibility to be fetched first. Use
`useEligibleMethods` on the client or `fetchEligibleMethods` on the server.

`BraintreePayPalPayLaterButton` renders `<paypal-pay-later-button>` using the
provider eligibility.

### Treat a missing Google Pay script as an error

The React Google Pay component raises an error when mounted without the Google
Pay script loaded. It no longer continues without an explicit failure.

## Braintree-backed flows

### PayPal Messages

`useBraintreePayPalMessages` creates Braintree-backed `<paypal-message>`
content and returns:

- `error`
- `isReady`
- `isLoading`
- `handleFetchContent(options)`

The fetched content exposes `update({ amount })`, which changes the displayed
amount without another fetch.

### Pay Later sessions and eligibility

`useBraintreePayPalPayLaterSession` manages the v6 Pay Later flow through
`error`, `isPending`, and `handleClick`.

`useBraintreeEligibleMethods` fetches and caches funding-source eligibility.

### Session options

The one-time-payment, Pay Later, and checkout-with-vault session types accept:

- `shippingCallbackUrl`
- `shippingAddressOverride`
- `contactPreference`

`shippingAddressOverride` uses `BraintreeShippingAddressOverride`.
`BraintreeEligibilityResult.getDetails()` is typed per funding source.

## Orders quick reference

### Required Trustly buyer data

Trustly payment sources require `email_address`.

### Current field limits

- An Orders item `description` supports up to 2,048 characters.
- A billing-agreement `description` supports up to 255 characters.

### Current response fields

- Orders responses include `stored_credentials`.
- PayPal Wallet responses include `business_name`.
- The card object includes `merchant_customer_id`.

### Current payment-source capabilities

- Orders supports experience context for Apple Pay and Google Pay payment
  sources.
- Orders supports a server-side shipping callback.
- Card payment sources support risk-related attributes.
- PUI payment-source requests accept a buyer-specific ID.
- The Orders network enum includes EFTPOS.

### Order-action response headers

The Confirm, Capture, and Authorize endpoints include a `Content-Type` header.

## v6 SDK quick reference

### Custom-element DOM types

Non-React TypeScript users receive `HTMLElementTagNameMap` types for PayPal,
Venmo, Pay Later, Credit, Basic Card, messages, and Apple Pay custom elements.

```ts
const button = document.createElement("paypal-pay-later-button");
button.countryCode = "US";
button.productCode = "PAYLATER";
```

### v6 entry resolution

The `@paypal/paypal-js` `./sdk-v6` export has a `default` condition. Bundlers
and tracers without a more specific matching condition can resolve the v6
entry instead of falling back to v5.

### Venmo vault-without-purchase data

The v6 `OnApproveData` type includes `vaultSetupToken`. The
`createVaultSetupToken` and `onApprove` contracts cover Venmo save-payment
flows that do not make a purchase.
