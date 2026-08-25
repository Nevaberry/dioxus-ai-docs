# API values and terminal behavior

## Balance-transaction type values

Balance-transaction `type` parsers and enums must accept:

- `application-fee`; and
- `payment-fee`.

The API was already returning these values even though they were previously
omitted from the documentation. Closed parsing logic must not reject them.

## Locale values

The `locale` field accepts both of these values:

- `en_BE`; and
- `en_NL`.

## Payment-detail card fee-region value

Payment-detail card fee-region parsers must accept
`visa-credit-consumer-inter`.

## Pairing-code eligibility

Requesting a terminal pairing code returns `403` when the organization is
ineligible.

## Pairing-code retention and deletion

Revoked and expired terminal pairing codes are retained for one month.

After a code is permanently deleted, the two retrieval surfaces behave as
follows:

- fetching the code returns `404`; and
- list responses omit the code.

## API rate limits and usage visibility

Mollie is introducing API rate limits, so integrations should account for
limits.

Mollie is also introducing a Mollie Web App section that exposes usage
visibility. Integrations should monitor their usage there.
