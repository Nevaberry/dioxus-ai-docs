# Transfers and settlements

## Draft Transfers API

The Draft Transfers API is available again and is generally available.

Integrations must use `pending-review` instead of `awaiting-initiation`.
Account-holder names are limited to 70 characters. Both the debtor IBAN and
the creditor IBAN must be valid.

Use these requirements together when constructing or validating Draft
Transfers requests:

- status value: `pending-review`;
- maximum account-holder name length: 70 characters;
- debtor IBAN: valid; and
- creditor IBAN: valid.

## Settlement cost and revenue subtotal methods

The `method` field on settlement cost subtotals can be either:

- `refund`; or
- `chargeback`.

The `method` field on settlement revenue subtotals can also be either:

- `refund`; or
- `chargeback`.

Integrations that use closed enums for either subtotal context must accept
both values.

## Open-settlement identifier

The open-settlement convenience endpoint returns the literal `open` in its
`id` field. This is not a normal settlement identifier.

Preserve `open` when parsing or validating this endpoint's response.

## Next-settlement identifier

The next-settlement convenience endpoint returns the literal `next` in its
`id` field. This is not a normal settlement identifier.

Preserve `next` when parsing or validating this endpoint's response.
