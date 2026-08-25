# SDK generation and Mollie Components

## Generated payment-method operations

For operations that enable or disable payment methods and payment-method
issuers, the profile ID path parameter no longer uses a union schema.

This allows all four operations to be generated in language SDKs:

- enable payment methods;
- disable payment methods;
- enable payment-method issuers; and
- disable payment-method issuers.

## Mollie Components type deprecations

The old `ComponentType` values for Card and Express components in the
private-beta Mollie.js v2 are deprecated.

Those component types are being renamed ahead of public release. The new
component type names are not specified in this guidance.
