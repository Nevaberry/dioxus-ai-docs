---
name: apple-pay-knowledge-patch
description: Apple Pay
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Apple Pay Knowledge Patch

Use this skill for Apple Pay work involving:

- Apple Pay JS or Payment Request platform availability.
- SDK delivery, sandbox behavior, or a pinned SDK asset.
- Apple Pay button behavior.
- Merchandising and order-tracking components on the web.
- Recurring, automatic-reload, or deferred payment requests.
- Multimerchant token contexts.
- Merchant-validation sheet updates.
- Merchant category codes on payment requests.

## Reference index

| Reference | Topics |
| --- | --- |
| [Web platform and SDK](references/web-platform-and-sdk.md) | Regional platform boundaries, SDK delivery, button behavior, sandbox behavior, and the pinned 1.3.8 asset |
| [Payment requests](references/payment-requests.md) | Specialized schedules, multimerchant token contexts, merchant validation, and merchant category codes |
| [Merchandising and order tracking](references/merchandising-and-order-tracking.md) | Installment merchandising and the Track with Apple Wallet button |

## Apply the guidance

1. Identify the integration surface.
   - For browser and operating-system eligibility, use
     [Web platform and SDK](references/web-platform-and-sdk.md).
   - For payment-request modeling, use
     [Payment requests](references/payment-requests.md).
   - For installment information or order tracking, use
     [Merchandising and order tracking](references/merchandising-and-order-tracking.md).
2. Preserve the regional distinction in web platform checks.
   - Outside China and China have different minimum iOS versions.
   - macOS availability also differs by region.
3. Keep Apple Pay JS and Payment Request requirements separate.
   - Their minimum iOS versions differ.
   - Their minimum macOS requirements differ outside China.
4. Treat sandbox capability results according to the sandbox-specific rule.
   - `paymentCredentialStatusUnknown` is not proof that Apple Pay is
     unavailable.
5. Select only the payment-request primitive that matches the stated payment
   schedule or update.

## Quick reference: web platform boundaries

### Outside China

| API | iOS | macOS and Safari |
| --- | --- | --- |
| Apple Pay JS | iOS 10 or later | macOS 10.12 or later |
| Payment Request | iOS 11.3 or later | macOS 10.12.6 or later with Safari 11.1 or later |

### China

| API | iOS | macOS |
| --- | --- | --- |
| Apple Pay JS | iOS 11.2 or later | Not available |
| Payment Request | iOS 11.3 or later | Not available |

On iOS in China, both Safari and `SFSafariViewController` support Apple Pay.

## Quick reference: SDK and button

### SDK delivery

A site can load either:

- The latest autoupdating Apple Pay JS SDK.
- A chosen Apple Pay JS SDK version.

For the exact versioned 1.3.8 CDN URL and Subresource Integrity hash, use
[Pinned 1.3.8 asset](references/web-platform-and-sdk.md#pinned-138-asset).

### Button behavior

`ApplePayButton` can:

- Start a payment.
- Prompt the customer to set up a card.

### Sandbox behavior

Apple Pay JS 1.3.5 added sandbox environment configuration. In sandbox mode:

- The UI displays a “Sandbox Mode” banner.
- The console reports the environment.
- `applePayCapabilities` returns `paymentCredentialStatusUnknown` in supported
  browsers.

Do not treat that status as proof that Apple Pay is unavailable.

## Quick reference: payment requests

### Specialized schedules

| Payment shape | PassKit request |
| --- | --- |
| Subscription | `PKRecurringPaymentRequest` |
| Reload such as a prepaid-account top-up | `PKAutomaticReloadPaymentRequest` |
| Charge such as a hotel booking or preorder | `PKDeferredPaymentRequest` |

### Multimerchant tokens

`PKPaymentTokenContext` defines the context for one payment token in a
multimerchant payment request.

### Merchant validation

`PKPaymentRequestMerchantSessionUpdate` updates a payment request with merchant
validation.

### Merchant category code

`PKPaymentRequest.merchantCategoryCode` optionally attaches an MCC that
categorizes the merchant's goods or services for the payment transaction.

## Quick reference: web presentation

### Installment merchandising

The Apple Pay Merchandising web component displays:

- Installment-payment options.
- Related merchandising information on a seller's site.

### Order tracking

A website can configure and style a Track with Apple Wallet button to match the
rest of the site.

## Integration checks

### Browser eligibility

- Determine whether the integration is inside or outside China.
- Determine whether the integration uses Apple Pay JS or Payment Request.
- Apply the matching iOS minimum.
- Outside China, apply the matching macOS minimum and the Safari minimum stated
  for Payment Request.
- In China, do not treat either web API as available on macOS.
- On iOS in China, account for support in Safari and
  `SFSafariViewController`.

### SDK selection

- Decide between the latest autoupdating SDK and a chosen version.
- When pinning version 1.3.8 with SRI, copy the published URL, integrity hash,
  and `crossorigin` attribute from the reference.
- When using sandbox environment configuration, expect the banner and console
  report.
- Do not convert `paymentCredentialStatusUnknown` into an unavailable result.
- Choose whether `ApplePayButton` starts payment or prompts card setup.

### Payment-request modeling

- Use `PKRecurringPaymentRequest` for a subscription.
- Use `PKAutomaticReloadPaymentRequest` for a reload such as a prepaid-account
  top-up.
- Use `PKDeferredPaymentRequest` for a charge such as a hotel booking or
  preorder.
- Use one `PKPaymentTokenContext` to define the context for one payment token
  in a multimerchant payment request.
- Use `PKPaymentRequestMerchantSessionUpdate` to update a payment request with
  merchant validation.
- Attach an MCC through `PKPaymentRequest.merchantCategoryCode` when the
  payment request should categorize the merchant's goods or services.

### Customer-facing web elements

- Use the Apple Pay Merchandising web component to display installment-payment
  options and related merchandising information.
- Configure and style the Track with Apple Wallet button to match the site.

## Fidelity rules

- Do not collapse the Apple Pay JS and Payment Request platform minimums into
  one requirement.
- Do not carry the outside-China macOS availability into China.
- Do not interpret sandbox `paymentCredentialStatusUnknown` as proof of
  unavailability.
- Do not replace the exact pinned 1.3.8 asset details with reconstructed
  values.
- Keep each specialized payment request attached to its stated payment shape.
- Keep `PKPaymentTokenContext` scoped to one token context in a multimerchant
  payment request.
- Keep the merchant category code optional.
