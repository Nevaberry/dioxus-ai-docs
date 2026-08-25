---
name: apple-pay-knowledge-patch
description: Apple Pay
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Apple Pay Knowledge Patch

Use this skill for Apple Pay work involving web platform support, Apple Pay JS
SDK delivery, sandbox behavior, web merchandising or order tracking, and
PassKit payment-request fields and request types.

## Reference index

| Reference | Topics |
| --- | --- |
| [Web integration](references/web-integration.md) | Apple Pay JS and Payment Request platform boundaries, SDK delivery, `ApplePayButton`, merchandising, and order tracking |
| [PassKit payment requests](references/passkit-payment-requests.md) | Recurring, reload, and deferred schedules; multimerchant token contexts; merchant validation; merchant category codes |
| [Apple Pay JS SDK](references/apple-pay-js-sdk.md) | Sandbox behavior and the pinned Apple Pay JS 1.3.8 CDN asset with Subresource Integrity |

## Start here

Choose the reference by task:

- For browser and operating-system boundaries, open
  [Web integration](references/web-integration.md).
- For SDK loading choices and Apple Pay button behavior, open
  [Web integration](references/web-integration.md).
- For sandbox capability checks or a pinned 1.3.8 script, open
  [Apple Pay JS SDK](references/apple-pay-js-sdk.md).
- For subscriptions, automatic reloads, deferred charges, multimerchant
  tokens, merchant validation, or MCCs, open
  [PassKit payment requests](references/passkit-payment-requests.md).

## Quick reference: web platform boundaries

### Outside China

| API | iOS | macOS and Safari |
| --- | --- | --- |
| Apple Pay JS | iOS 10 or later | macOS 10.12 or later |
| Payment Request | iOS 11.3 or later | macOS 10.12.6 or later with Safari 11.1 or later |

### In China

| API | iOS | macOS |
| --- | --- | --- |
| Apple Pay JS | iOS 11.2 or later | Not available |
| Payment Request | iOS 11.3 or later | Not available |

On iOS, Safari and `SFSafariViewController` both support Apple Pay.

## Quick reference: sandbox capability status

Apple Pay JS 1.3.5 added sandbox environment configuration.

In sandbox mode:

- The UI displays a “Sandbox Mode” banner.
- The console reports the environment.
- `applePayCapabilities` returns
  `paymentCredentialStatusUnknown` in supported browsers.

Do not treat `paymentCredentialStatusUnknown` as proof that Apple Pay is
unavailable.

## Quick reference: SDK delivery

A site can load either:

- The latest, autoupdating Apple Pay JS SDK.
- A chosen Apple Pay JS SDK version.

For the published, pinned 1.3.8 asset with Subresource Integrity, use:

```html
<script src="https://applepay.cdn-apple.com/jsapi/v1.3.8/apple-pay-sdk.js"
        integrity="sha384-u/9mOkmShCO0v+dqCAZFhiutJuORfzvuyM5i+676iy7mLSWS6rlllHrIt15f/mqH"
        crossorigin="anonymous"></script>
```

See [Apple Pay JS SDK](references/apple-pay-js-sdk.md) for the sandbox and
pinned-asset details together.

## Quick reference: Apple Pay button behavior

`ApplePayButton` can do either of the following:

- Start a payment.
- Prompt the customer to set up a card.

## Quick reference: payment schedules

Use the PassKit request type that matches the payment schedule:

| Payment schedule | PassKit type | Stated example |
| --- | --- | --- |
| Subscription | `PKRecurringPaymentRequest` | Subscriptions |
| Automatic reload | `PKAutomaticReloadPaymentRequest` | Prepaid-account top-ups |
| Deferred charge | `PKDeferredPaymentRequest` | Hotel bookings or preorders |

## Quick reference: multimerchant payments

`PKPaymentTokenContext` defines the context for one payment token in a
multimerchant payment request.

## Quick reference: merchant validation

`PKPaymentRequestMerchantSessionUpdate` updates a payment request with merchant
validation.

## Quick reference: merchant category code

`PKPaymentRequest.merchantCategoryCode` optionally attaches an MCC to categorize
the merchant's goods or services for the payment transaction.

## Quick reference: merchandising

The Apple Pay Merchandising web component displays:

- Installment-payment options.
- Related merchandising information.

It displays that information on a seller's site.

## Quick reference: web order tracking

A website can configure and style a Track with Apple Wallet button to match the
rest of the site.

## Task map

### Checking whether a web API fits the target platform

1. Distinguish Apple Pay JS from Payment Request.
2. Distinguish deployment outside China from deployment in China.
3. Apply the matching iOS requirement.
4. For macOS, apply the API-specific availability and Safari requirement.

The complete matrix is in
[Web integration](references/web-integration.md#web-api-platform-boundaries).

### Choosing SDK delivery

Choose between the latest autoupdating SDK and a chosen version. If the chosen
version is 1.3.8, the published CDN URL and SRI hash are recorded in
[Apple Pay JS SDK](references/apple-pay-js-sdk.md#pinned-apple-pay-js-138-asset).

### Handling sandbox capability results

When the sandbox environment returns
`paymentCredentialStatusUnknown` from `applePayCapabilities`, do not interpret
that status as proof that Apple Pay is unavailable.

### Modeling a specialized payment schedule

Match the intended schedule to `PKRecurringPaymentRequest`,
`PKAutomaticReloadPaymentRequest`, or `PKDeferredPaymentRequest`. Consult
[PassKit payment requests](references/passkit-payment-requests.md#specialized-payment-schedules)
for the stated mapping and examples.

### Adding transaction context

Use the PassKit reference for the exact role stated for:

- `PKPaymentTokenContext` in a multimerchant request.
- `PKPaymentRequestMerchantSessionUpdate` in merchant validation.
- `PKPaymentRequest.merchantCategoryCode` in attaching an MCC.

### Adding customer-facing web components

Use the web integration reference for:

- The Apple Pay Merchandising web component and the information it displays.
- The configurable, styleable Track with Apple Wallet button.

## Fidelity rule

Keep Apple Pay guidance within the behavior and platform boundaries recorded in
the references. When a task needs details beyond those references, obtain those
details from the task's own project sources or authoritative product material.
