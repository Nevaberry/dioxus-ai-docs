# Terminals and API operations

## Terminal pairing-code eligibility

Requesting a terminal pairing code returns `403` when the organization is
ineligible.

## Terminal pairing-code retention and deletion

Revoked and expired pairing codes are retained for one month.

After a pairing code is permanently deleted:

- Fetching it returns `404`.
- List responses omit it.

## API rate limits and usage visibility

Mollie is introducing API rate limits and a Mollie Web App section that
exposes usage visibility.

Integrations should account for the limits and monitor their usage in that
Mollie Web App section.

## Generated SDK support for payment-method operations

The profile ID path parameter for enabling or disabling payment methods and
payment-method issuers no longer uses a union schema.

This allows all four operations to be generated in language SDKs:

- Enable payment methods.
- Disable payment methods.
- Enable payment-method issuers.
- Disable payment-method issuers.
