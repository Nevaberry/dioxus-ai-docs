# Connect, Accounts, and Financial Data

## Accounts v2

### Unified identities

Accounts v2 represents merchant, customer, and recipient roles as configurations of one `/v2/core/accounts` object. Do not maintain parallel mappings between connected-account and Customer objects when a unified Account is appropriate.

Any API that accepts `customer` also accepts `customer_account` with an Account whose customer configuration is active.

```sh
curl https://api.stripe.com/v1/setup_intents \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Version: 2025-09-30.preview" \
  -d customer_account=acct_123 \
  -d "payment_method_types[]=card" \
  -d confirm=true \
  -d usage=off_session
```

### Configurations and capabilities

- The `merchant` configuration carries capabilities such as `card_payments` and `stripe_balance.payouts`.
- The `recipient` configuration carries `stripe_balance.stripe_transfers`.
- `recipient.stripe_balance.stripe_transfers` is required for indirect charges.

### Include-dependent responses

Accounts v2 can return properties as `null` regardless of stored value unless their paths are requested with `include`. Request the data needed by the code, including paths such as:

- `configuration.customer`;
- `configuration.merchant`;
- `identity`; and
- `requirements`.

Treat omitted inclusion and genuinely absent values as different states in clients and tests.

## Connect requirements and balance settings

### Verification and KYC

- Connected Accounts expose risk-verification details in `2024-09-30.acacia`.
- In `2025-03-31.basil`, Connect adds error codes for required verifications and exposes more Account KYC data.
- `Person.political_exposure` changes from free-form text to an enum; update validators and preserve unknown enum handling.
- The Balance Settings API exposes account balance and payout configuration in `2025-09-30.clover`.
- Connect adds a distinct business-type validation error.

### Returned requirements

In `2026-03-25.dahlia`, the Capabilities API exposes risk requirements. Account Sessions no longer require external-account collection for some connected accounts. Onboarding should follow the returned requirements rather than always forcing external-account collection.

### Account Link defaults

Account Link API v1 applies additional defaults when fields are omitted (`2024-09-30.acacia`). Code that must distinguish an explicit choice from a server default should send the desired value.

## Financial Connections

### Filters and session creation

Financial Connections adds Account subcategory filtering and expands filters accepted by Session creation in `2024-09-30.acacia`.

### PaymentMethod creation failures

Creating PaymentMethods from Financial Connections Accounts can return additional failure codes in `2025-09-30.clover`. Surface and branch on these cases rather than reducing them to unknown errors.

## Identity and Treasury

- Identity Verification Sessions can link to Customers (`2024-09-30.acacia`).
- Outbound Treasury wires expose CHIPS tracking details.
- ReceivedDebit failures add a classification for international transactions.

## Payouts

Payout Methods v2 publicly preview foreign-currency payout support in `2026-03-25.dahlia`. Keep preview payout-method schemas separated from stable Connect payout models.
