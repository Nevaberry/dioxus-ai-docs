# Payments, cards, and disputes

## Refund filtering and sorting

`ListPaymentRefunds` adds `updated_at_begin_time`, `updated_at_end_time`, and
`sort_field` for filtering and sorting results by the refund's `updated_at`
timestamp.

## API-managed disputes

Evidence submitted through the Disputes API cannot be viewed or managed in
Square Dashboard. Managing a dispute through the API does not update its
Dashboard status.

## Card metadata and postal codes

`Card` has read-only Beta fields `hsa_fsa`, `issuer_alert`, and
`issuer_alert_at`. The alert can report `ISSUER_ALERT_CARD_CLOSED` for supported
Mastercard cards.

`CreateCard` accepts a billing-address `postal_code` in ZIP+4 form, such as
`12345-6789`.

The card nested under `CardPaymentDetails` adds `created_at` and `disabled_at`.

## Gift-card insufficient funds

A failed Square gift-card payment always returns `GIFT_CARD_AVAILABLE_AMOUNT`
with `INSUFFICIENT_FUNDS`, even without partial authorization. This behavior
applies to every Square API version.

## Customer bank accounts

The Bank Accounts API adds:

- `CreateBankAccount` to store a new customer bank account.
- `DisableBankAccount` to disable a customer bank account.

## Service charges and card surcharges

`OrderLineItem.blocked_service_charges` can block ad hoc service charges per
line item. Charge classification metadata is available through:

- `OrderLineItemAppliedTax.auto_applied`
- `OrderReturnServiceCharge.type`
- `OrderCardSurchargeTreatmentType`

Payments report seller-added card surcharges. The Terminal API can add
credit-card surcharges in the US.

## Payment-source diagnostics

`Payment.BuyNowPayLaterDetails.errors` and
`Payment.DigitalWalletDetails.errors` expose source-specific failures.

New error codes are:

- `PARTIAL_PAYMENT_DELAY_CAPTURE_NOT_SUPPORTED`
- `PAYMENT_SOURCE_NOT_ENABLED_FOR_TARGET`
- `AMOUNT_TOO_LOW`

## Multi-party application fees and refunds

`Payment.app_fee_allocations` can distribute one application fee among up to
three parties. When refunding a payment that used allocations, set
`PaymentRefund.app_fee_allocations` to control how much each party contributes.

## Wallet and Japanese e-money details

`CardPaymentDetails.wallet_type` identifies Apple Pay payments.

`ElectronicMoneyDetails` represents Japanese e-money payments and exposes
`felica_details` for FeliCa.
