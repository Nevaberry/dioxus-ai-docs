# PassKit payment requests

## Specialized payment schedules

PassKit provides these request types:

| Request type | Purpose stated for the request |
| --- | --- |
| `PKRecurringPaymentRequest` | Subscriptions |
| `PKAutomaticReloadPaymentRequest` | Reloads such as prepaid-account top-ups |
| `PKDeferredPaymentRequest` | Charges such as hotel bookings or preorders |

## Multimerchant payment tokens

`PKPaymentTokenContext` defines the context for one payment token in a
multimerchant payment request.

## Merchant-validation sheet updates

`PKPaymentRequestMerchantSessionUpdate` updates a payment request with merchant
validation.

## Merchant category codes

`PKPaymentRequest.merchantCategoryCode` optionally attaches a merchant category
code (MCC) to categorize the merchant's goods or services for the payment
transaction.
