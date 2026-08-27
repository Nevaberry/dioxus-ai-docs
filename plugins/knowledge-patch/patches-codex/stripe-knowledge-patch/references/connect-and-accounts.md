# Connect, Accounts, and Financial Data

## Accounts v2 (`billing-and-payments-v2`)

### Configuration and identity model

Accounts v2 uses `/v2/core/accounts` and is documented with
`Stripe-Version: 2026-07-29.preview`. One Account can add `merchant`, `customer`,
and `recipient` configurations to accept payments, be charged as a customer, or
receive transfers without recollecting identity.

Capabilities live under their configurations. `merchant` includes
`card_payments` and `stripe_balance.payouts`; `recipient` includes
`stripe_balance.stripe_transfers` for indirect charges.

### Include-dependent responses

Some properties return their values while others return `null` regardless of
their stored values. Request paths such as `configuration.merchant`, `identity`,
and `requirements` with `include`. Never interpret an include-dependent `null`
as proof that a property is unset.

### Customer use and v1 interoperability

Where a request accepts a Customer through `customer`, use
`customer_account=<acct_id>` for an Accounts v2 object with customer
configuration.

A v2 Account ID can be passed to Accounts v1 endpoints. Those endpoints return
a v1-shaped object while updating corresponding v2 properties. Accounts v1 is
still required for OAuth, recipient service agreements, Treasury or Issuing
capabilities, and certain deprecated or preview payment-method capabilities.

## Connect accounts and onboarding

### Risk details and Account Link defaults (`2024-09-30.acacia`)

Connected accounts expose additional risk-verification details. Account Link
API v1 also applies additional defaults; revalidate the resulting link
configuration when code depends on omitted values.

Connect embedded components add tax settings and registration support.

### Verification and Person identity (`2025-03-31.basil`)

Connect adds required-verification error codes and exposes more Account KYC
data. The Person political-exposure property changes from a free-form string to
an enum. Update generated types and keep enum handling tolerant.

### Validation and balance settings (`2025-09-30.clover`)

Connect adds a distinct business-type-validation error code and a Balance
Settings API for account balance and payout configuration. Accept the validation
case and use the API when managing those settings.

Customers can store business and individual names. Preserve both in customer
schemas and synchronization rather than assuming one personal-name shape.

### Singapore fields and embedded disputes (`2026-07-29.dahlia`)

Account address schemas add Singapore compliance fields in Accounts v1 and v2.
Preserve them across either API generation.

Account Session embedded components add Smart Disputes management. Platforms
can expose it through Account Session component configuration.

### Rejection lifecycle (`2026-07-29.dahlia`)

Platforms can reject connected accounts with non-zero balances and control
whether rejection pauses payouts. A reversal operation can undo a platform
rejection; do not model rejection as irreversible.

## Financial Connections

### Collection filters (`2024-09-30.acacia`)

Financial Connections adds account-subcategory filtering and expands Session
filters. Constrain returned accounts during collection instead of filtering only
after retrieval when those filters apply.

### PaymentMethod creation failures (`2025-09-30.clover`)

Creating PaymentMethods from Financial Connections Accounts adds failure error
codes. Keep error handling forward-compatible with the new creation failures.

### Session configuration and deactivation (`2026-07-29.dahlia`)

Financial Connections Sessions add explicit configuration options, allowing
creation to declare the intended configuration rather than depend entirely on
implicit behavior.

Deactivation notifications are available for both accounts and authorizations.
React to these lifecycle events instead of discovering deactivation only during
a later API call.

## Balances and top-ups

### Balance transaction classifications (`2025-03-31.basil`)

Balance Transactions add types for paying with a Stripe balance, and customer
balance transactions gain new types. Exhaustive transaction-type handling must
accept the added classifications.

### Top-up attribution and Payment Methods (`2026-07-29.dahlia`)

Top-ups add `initiated_by`; retain the initiator rather than assuming every
top-up starts the same way. Top-ups can also use Payment Methods, so creation and
response models must allow Payment Method-backed top-ups in addition to earlier
funding contracts.
