# Transfers and settlements

## Draft Transfers API

The Draft Transfers API is available again and is generally available.

Integrations must satisfy all of the following requirements:

- Use `pending-review` instead of `awaiting-initiation`.
- Limit account-holder names to 70 characters.
- Provide valid debtor IBANs.
- Provide valid creditor IBANs.

## Settlement cost and revenue subtotal methods

The `method` field on settlement cost and revenue subtotals can be either of
these values:

- `refund`
- `chargeback`

Integrations using closed enums must accept both values.

## Open-settlement convenience endpoint

The `id` field returned by the open-settlement convenience endpoint is the
literal `open`, rather than a normal settlement identifier.

## Next-settlement convenience endpoint

The `id` field returned by the next-settlement convenience endpoint is the
literal `next`, rather than a normal settlement identifier.
