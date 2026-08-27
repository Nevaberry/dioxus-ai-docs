# Payments, checkout, and risk

## Consolidated Web Payments tokenization

In Beta, `Card.tokenize()` supports a consolidated flow for payment processing,
buyer verification, and storing, charging, or both charging and storing a card
on file.

## Refund update-time filters

`ListPaymentRefunds` adds `updated_at_begin_time`, `updated_at_end_time`, and
`sort_field` for filtering and sorting results by the refund's `updated_at`
timestamp.

## Disputes API and Dashboard state

Evidence submitted through the Disputes API cannot be viewed or managed in
Square Dashboard. Managing a dispute through the API does not update its
Dashboard status.

## Card decline metadata and ZIP+4

`Card` has the read-only Beta fields `hsa_fsa`, `issuer_alert`, and
`issuer_alert_at`. For supported Mastercard cards, the alert can report
`ISSUER_ALERT_CARD_CLOSED`.

`CreateCard` also accepts a billing-address `postal_code` in ZIP+4 form, such
as `12345-6789`.

## Invoice creator, attachments, and hosted links

`Invoice.creator_team_member_id` identifies a logged-in team member who
created an invoice in Dashboard or the Invoices app.

Sandbox allows only 1 KB of total attachments per invoice; production allows
25 MB.

After an invoice is published and reaches any scheduled date, `public_url`
points to a temporary hosted payment link. Retrieving the invoice refreshes an
aging link. Link expiry or regeneration does not emit an `invoice.updated`
webhook.

## Subscription checkout identifiers

For subscription checkout, `CreatePaymentLink.subscription_plan_id` must
contain a subscription plan variation ID, not a subscription plan ID.

## Terminal defaults and regional capabilities

`PaymentOptions.autocomplete` defaults to `true`.

Linked-order Terminal checkouts expanded to Canada, the UK, and Australia.
Localized order receipts became generally available in Japan and the EU.

Terminal checkout support for app fees, delayed capture, statement
descriptors, team-member IDs, and tip money expanded to Australia, Canada,
Japan, and the UK.

## Gift-card insufficient funds

A failed Square gift-card payment always returns
`GIFT_CARD_AVAILABLE_AMOUNT` with `INSUFFICIENT_FUNDS`, even without partial
authorization. This behavior applies to every Square API version.

## Digital wallets for Japanese sellers

In-App Payments SDK supports Apple Pay and Google Pay for Japanese sellers.
Both wallets are available in every region where Square operates.

## Completed subscriptions

Fixed-phase subscriptions can enter the non-billing, non-resumable `COMPLETED`
status, expose their expected `completed_date`, and receive a
`SubscriptionAction` of type `COMPLETE`.

Plans containing any non-fixed-length phase have no defined completion date,
so `completed_date` is unset.

## Order charges and card surcharges

`OrderLineItem.blocked_service_charges` can block ad hoc service charges per
line item.

The following fields add charge classification metadata:

- `OrderLineItemAppliedTax.auto_applied`
- `OrderReturnServiceCharge.type`
- `OrderCardSurchargeTreatmentType`

Payments report seller-added card surcharges. The Terminal API can add
credit-card surcharges in the US.

## Payment-source diagnostics

`Payment.BuyNowPayLaterDetails.errors` and
`Payment.DigitalWalletDetails.errors` expose source-specific failures. The
card nested under `CardPaymentDetails` adds `created_at` and `disabled_at`.

New error codes are:

- `PARTIAL_PAYMENT_DELAY_CAPTURE_NOT_SUPPORTED`
- `PAYMENT_SOURCE_NOT_ENABLED_FOR_TARGET`
- `AMOUNT_TOO_LOW`

## Multi-party application fees and refunds

`Payment.app_fee_allocations` can distribute one application fee among up to
three parties. When refunding a payment that used allocations, set
`PaymentRefund.app_fee_allocations` to control how much each party contributes.

## Wallet and Japanese e-money details

`CardPaymentDetails.wallet_type` identifies Apple Pay payments. The new
`ElectronicMoneyDetails` represents Japanese e-money payments and exposes
`felica_details` for FeliCa.
