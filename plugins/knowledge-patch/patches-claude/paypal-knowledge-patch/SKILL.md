---
name: paypal-knowledge-patch
description: PayPal
version: null
license: MIT
metadata:
  author: Nevaberry
---


# PayPal Knowledge Patch

Use this skill when implementing or reviewing PayPal Orders API behavior,
PayPal JavaScript SDK v6 integration, Braintree-backed PayPal components,
payment-method eligibility, or PayPal custom elements.

Apply the quick-reference guidance below first. Open the topic reference that
matches the code being changed for the complete set of relevant details.

## Reference index

| Reference | Topics |
| --- | --- |
| [Orders and payment sources](references/orders-and-payment-sources.md) | Orders billing fields, experience context, shipping callbacks, payment-source requirements, response fields, enums, headers, and length limits |
| [Eligibility and Braintree](references/eligibility-and-braintree.md) | Server eligibility fetching, provider hydration, Braintree messages, Pay Later, funding-source eligibility, and session options |
| [SDK v6 components and types](references/sdk-v6-components-and-types.md) | Message content, Apple Pay, Basic Card, Google Pay, custom-element DOM types, subpath resolution, and Venmo vault approval data |

## Breaking changes and deprecations

### Replace `charge_pattern` with `usage_pattern`

`charge_pattern` is deprecated. Use `usage_pattern` in Orders billing requests.
Orders billing responses also return `usage_pattern`.

### Use the renamed server eligibility helper

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

The old `useFetchEligibleMethods` name is deprecated. The related type aliases
are also replaced:

| Deprecated | Replacement |
| --- | --- |
| `useFetchEligibleMethods` | `fetchEligibleMethods` |
| `UseFetchEligibleMethodsOptions` | `UseEligibleMethodsOptions` |
| `UseFetchEligibleMethodsResult` | `UseEligibleMethodsResult` |

The `environment` option is required. Omitting it throws instead of silently
querying sandbox.

### Remove nullable message-content handling

`PayPalMessagesSession.fetchContent()` returns `Promise<MessageContent>` rather
than `Promise<MessageContent | null>`.

API failures return an empty `MessageContent` sentinel with no `messageItems`.
The `<paypal-message>` element then collapses, so `null` checks are dead code.

### Do not pass `disabled` to the Apple Pay button

`ApplePayOneTimePaymentButton` no longer has a `disabled` prop because the
`<apple-pay-button>` element ignored that attribute and manages availability
through `canMakePayments()`.

Control any additional presentation state separately.

### Use the kebab-case Basic Card attribute

In JSX, pass `buyer-country`, not `buyerCountry`:

```tsx
<paypal-basic-card-button buyer-country="US" />
```

React versions before 19 lowercase the camel-case form to an attribute that
the custom element does not observe.

### Load the Google Pay script before mounting

The React Google Pay component raises an error when it mounts without the
Google Pay script loaded. It no longer continues without an explicit failure.

## Eligibility and provider hydration

Server eligibility requests may include the merchant origin. Their response
can hydrate the v6 `PayPalProvider`, allowing the client to skip a duplicate
eligibility request.

Pay Later and Credit buttons require eligibility to be fetched first. Use
`useEligibleMethods` on the client or `fetchEligibleMethods` on the server.

`useBraintreeEligibleMethods` fetches and caches funding-source eligibility.
`BraintreePayPalPayLaterButton` uses that provider eligibility when rendering
`<paypal-pay-later-button>`.

## Braintree flow reminders

### PayPal Messages

`useBraintreePayPalMessages` creates Braintree-backed `<paypal-message>`
content and returns:

- `error`
- `isReady`
- `isLoading`
- `handleFetchContent(options)`

The fetched content exposes `update({ amount })`, which changes the displayed
amount without another fetch.

### Pay Later

`useBraintreePayPalPayLaterSession` manages the v6 Pay Later flow through
`error`, `isPending`, and `handleClick`.

### Session options

The one-time-payment, Pay Later, and checkout-with-vault session types accept:

- `shippingCallbackUrl`
- `shippingAddressOverride`
- `contactPreference`

`shippingAddressOverride` uses `BraintreeShippingAddressOverride`.
`BraintreeEligibilityResult.getDetails()` is typed per funding source.

## Orders API reminders

### Requests

- Trustly payment sources require `email_address`.
- PUI payment-source requests accept a buyer-specific ID.
- Card payment sources support risk-related attributes.
- Orders supports a server-side shipping callback.
- Apple Pay and Google Pay payment sources support experience context.

### Responses and objects

- Orders responses include `stored_credentials`.
- PayPal Wallet responses include `business_name`.
- The card object includes `merchant_customer_id`.

### Enums, headers, and limits

- The Orders network enum includes EFTPOS.
- Confirm, Capture, and Authorize endpoints include a `Content-Type` header.
- An Orders item `description` supports up to 2,048 characters.
- A billing-agreement `description` supports up to 255 characters.

## SDK v6 integration reminders

Non-React TypeScript users receive `HTMLElementTagNameMap` types for PayPal,
Venmo, Pay Later, Credit, Basic Card, messages, and Apple Pay custom elements.

The `@paypal/paypal-js` `./sdk-v6` export has a `default` condition. Bundlers
and tracers without a more specific matching condition can resolve the v6
entry rather than falling back to v5.

The v6 `OnApproveData` type includes `vaultSetupToken`. The
`createVaultSetupToken` and `onApprove` contracts cover Venmo save-payment
flows that do not make a purchase.
