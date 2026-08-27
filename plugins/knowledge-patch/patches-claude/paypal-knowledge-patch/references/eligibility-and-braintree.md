# Eligibility and Braintree

## Server eligibility export

The v6 server helper is the plain async `fetchEligibleMethods` export from
`@paypal/react-paypal-js/sdk-v6/server`. It replaces the deprecated
`useFetchEligibleMethods` name.

`UseEligibleMethodsOptions` and `UseEligibleMethodsResult` replace the
deprecated `UseFetchEligibleMethodsOptions` and
`UseFetchEligibleMethodsResult` aliases.

```ts
import { fetchEligibleMethods } from "@paypal/react-paypal-js/sdk-v6/server";

const response = await fetchEligibleMethods({
  environment: "production", // or "sandbox"
  headers,
  payload,
});
```

`environment` is required. Omitting it throws instead of silently querying
sandbox.

Server requests can carry the merchant origin. Their response can hydrate the
v6 `PayPalProvider`, so the client skips a duplicate eligibility request.

## Braintree PayPal Messages

`useBraintreePayPalMessages` creates Braintree-backed `<paypal-message>`
content and returns `error`, `isReady`, `isLoading`, and
`handleFetchContent(options)`.

The fetched content exposes `update({ amount })`, allowing the displayed
amount to change without another fetch.

## Pay Later and funding-source eligibility

`useBraintreePayPalPayLaterSession` manages the v6 Pay Later flow through
`error`, `isPending`, and `handleClick`.

`useBraintreeEligibleMethods` fetches and caches funding-source eligibility.
`BraintreePayPalPayLaterButton` renders `<paypal-pay-later-button>` using that
provider eligibility.

Pay Later and Credit buttons require eligibility to be fetched first with
`useEligibleMethods` on the client or `fetchEligibleMethods` on the server.

## Braintree session options

The one-time-payment, Pay Later, and checkout-with-vault session types accept
`shippingCallbackUrl`, `shippingAddressOverride`, and `contactPreference`.

`shippingAddressOverride` uses `BraintreeShippingAddressOverride`.
`BraintreeEligibilityResult.getDetails()` is typed per funding source.
