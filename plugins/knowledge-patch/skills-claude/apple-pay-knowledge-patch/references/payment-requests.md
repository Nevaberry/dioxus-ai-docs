# Payment Requests

## Specialized payment schedules

PassKit provides a distinct request for each of these payment shapes:

| Payment shape | Request |
| --- | --- |
| Subscription | `PKRecurringPaymentRequest` |
| Reload, such as a prepaid-account top-up | `PKAutomaticReloadPaymentRequest` |
| Charge, such as a hotel booking or preorder | `PKDeferredPaymentRequest` |

## Multimerchant payment tokens

`PKPaymentTokenContext` defines the context for one payment token in a
multimerchant payment request.

## Merchant-validation sheet updates

`PKPaymentRequestMerchantSessionUpdate` updates a payment request with merchant
validation.

## Merchant category codes

`PKPaymentRequest.merchantCategoryCode` optionally attaches an MCC to categorize
the merchant's goods or services for the payment transaction.
