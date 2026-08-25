# React and Braintree Reference

## Server eligibility

### Fetching eligible methods

The v6 server helper is the plain async `fetchEligibleMethods` export from
`@paypal/react-paypal-js/sdk-v6/server`. It replaces the deprecated
`useFetchEligibleMethods` name.

```ts
import { fetchEligibleMethods } from "@paypal/react-paypal-js/sdk-v6/server";

const response = await fetchEligibleMethods({
  environment: "production", // or "sandbox"
  headers,
  payload,
});
```

`UseEligibleMethodsOptions` and `UseEligibleMethodsResult` replace the
deprecated `UseFetchEligibleMethodsOptions` and
`UseFetchEligibleMethodsResult` aliases.

`environment` is required. Omitting it throws instead of silently querying
sandbox.

### Merchant origin and provider hydration

Server requests can carry the merchant origin. Their response can hydrate the
v6 `PayPalProvider` so the client skips a duplicate eligibility request.

## PayPal Messages

### Braintree-backed messages

`useBraintreePayPalMessages` creates Braintree-backed `<paypal-message>`
content. It returns `error`, `isReady`, `isLoading`, and
`handleFetchContent(options)`.

Fetched content exposes `update({ amount })`, allowing the displayed amount to
change without another fetch.

### Non-null message content

`PayPalMessagesSession.fetchContent()` returns `Promise<MessageContent>`, not
`Promise<MessageContent | null>`.

API failures produce an empty `MessageContent` sentinel without
`messageItems`. This causes `<paypal-message>` to collapse, and `null` checks
are dead code.

## Pay Later and funding eligibility

### Braintree Pay Later session

`useBraintreePayPalPayLaterSession` manages the v6 Pay Later flow through
`error`, `isPending`, and `handleClick`.

### Eligibility hook and button

`useBraintreeEligibleMethods` fetches and caches funding-source eligibility.
`BraintreePayPalPayLaterButton` renders `<paypal-pay-later-button>` using that
provider eligibility.

Pay Later and Credit buttons require eligibility to be fetched first with
`useEligibleMethods` on the client or `fetchEligibleMethods` on the server.

## Session configuration

### Shared options

The one-time-payment, Pay Later, and checkout-with-vault session types accept
`shippingCallbackUrl`, `shippingAddressOverride`, and `contactPreference`.

`shippingAddressOverride` uses `BraintreeShippingAddressOverride`.
`BraintreeEligibilityResult.getDetails()` is typed per funding source.

## Wallet button behavior

### Apple Pay button availability

`ApplePayOneTimePaymentButton` no longer has a `disabled` prop because
`<apple-pay-button>` ignored the attribute and manages availability through
`canMakePayments()`.

Merchants must control any additional presentation state themselves.

### Missing Google Pay script

The React Google Pay component raises an error when it mounts without the
Google Pay script loaded, rather than continuing without an explicit failure.
