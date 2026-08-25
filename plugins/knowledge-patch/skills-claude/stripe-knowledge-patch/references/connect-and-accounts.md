# Connect, Accounts, and Financial Data

## Accounts v2

### Configuration and identity model

Accounts v2 uses `/v2/core/accounts` and is documented with
`Stripe-Version: 2026-07-29.preview`. One Account can add `merchant`, `customer`,
and `recipient` configurations so it can accept payments, be charged as a
Customer, or receive transfers without recollecting identity.

Capabilities live below configurations. `merchant` includes `card_payments`
and `stripe_balance.payouts`; `recipient` includes
`stripe_balance.stripe_transfers`, which is required for indirect charges.

### Include-dependent values

Some response properties contain values while others return `null` regardless
of their actual values. Request needed paths such as
`configuration.merchant`, `identity`, and `requirements` with `include`. Never
interpret an include-dependent `null` as proof that the property is unset.

### Customer accounts and v1 interoperability

Where a request accepts a Customer as `customer`, an Accounts v2 object with
customer configuration can be supplied as `customer_account=<acct_id>`.

A v2 Account ID can be passed to Accounts v1 endpoints. Those endpoints return
a v1-shaped object while updating the corresponding v2 properties. Continue to
use v1 for OAuth, recipient service agreements, Treasury or Issuing
capabilities, and specified deprecated or preview payment-method capabilities.

## Connect account contracts

### Risk details and Account Link defaults (`2024-09-30.acacia`)

Connected Accounts expose additional risk-verification details. Account Link
API v1 applies additional defaults; revalidate the resulting link configuration
when code previously depended on omitted values.

### Verification and identity (`2025-03-31.basil`)

Connect adds error codes for required verifications and exposes more Account
KYC data. The Person object's political-exposure property changes from a
free-form string to an enum. Update generated types and keep enum handling
tolerant.

### Business validation and balance settings (`2025-09-30.clover`)

Connect adds a distinct business-type validation error. It also adds a Balance
Settings API for Account balance and payout settings. Accept the validation case
and use the API when configuring those settings.

### Singapore address fields (`2026-07-29.dahlia`)

Account address schemas expand for Singapore compliance in both Accounts v1 and
Accounts v2. Synchronization and validation must preserve the additions across
either API generation.

### Smart Disputes components (`2026-07-29.dahlia`)

Account Session embedded components add Smart Disputes management. Platforms
can expose it through component configuration.

### Rejection and reversal (`2026-07-29.dahlia`)

Platforms can reject Connected Accounts that retain non-zero balances and can
control whether rejection pauses payouts. A reversal operation can undo a
platform rejection, so do not model rejection as irreversible.

## Financial Connections

### Collection filters (`2024-09-30.acacia`)

Financial Connections supports account-subcategory filtering and expands
Session filters. Constrain returned Accounts during collection instead of
filtering only after retrieval when appropriate.

### PaymentMethod creation failures (`2025-09-30.clover`)

Creating PaymentMethods from Financial Connections Accounts adds failure error
codes. Error handling must be forward-compatible with those creation failures.

### Explicit Session configuration (`2026-07-29.dahlia`)

Financial Connections Sessions add explicit configuration options. Declare the
intended configuration at creation instead of relying entirely on implicit
behavior.

### Deactivation events (`2026-07-29.dahlia`)

Deactivation notifications cover both Accounts and Authorizations. Integrations
can react to those lifecycle changes instead of discovering them only through a
later API call.

## Balances and transactions

### Transaction classifications (`2025-03-31.basil`)

Balance Transactions add types for payments made with a Stripe balance, and
Customer balance transactions add types. Exhaustive handling must accept the
new classifications.

## Customer identity

### Business and individual names (`2025-09-30.clover`)

Customers can store business and individual names. Preserve both in Customer
schemas and synchronization instead of assuming a single personal-name shape.

### Verification Session attribution (`2024-09-30.acacia`)

Identity Verification Sessions can be linked to Customers. Preserve that
association when ingesting or creating Sessions.

## Treasury attribution and failures

### Wires and received debits (`2024-09-30.acacia`)

Treasury outbound wires expose CHIPS tracking details. ReceivedDebit failures
add a value for international-transaction failures. Preserve the tracking data
and accept the expanded failure enum.
