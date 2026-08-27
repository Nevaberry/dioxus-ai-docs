# API values

## Balance-transaction types

Balance-transaction `type` parsers and enums must accept:

- `application-fee`
- `payment-fee`

The API was already returning these values despite their previous omission
from the documentation.

## Locale values

The `locale` field accepts:

- `en_BE`
- `en_NL`

## Payment-detail card fee regions

Payment-detail card fee-region parsers must accept:

- `visa-credit-consumer-inter`
