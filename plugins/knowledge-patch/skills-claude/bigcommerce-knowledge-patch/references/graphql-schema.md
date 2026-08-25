# GraphQL Schema

## Alpha and deprecated fields

### Payment methods and shipment provider display

`Site.paymentMethods` is a new connection of payment methods enabled for the
store and channel. Its `PaymentMethod` nodes expose `entityId` and `name`.

`OrderShipment.shippingProviderDisplayName` adds a human-readable provider
label.

Both fields are alpha, deprecated, and not for production.

### Delete a stored payment instrument

Authenticated customers can use the alpha
`CustomerMutations.deleteStoredPaymentInstrument` mutation. Its
`DeleteStoredPaymentInstrumentInput` accepts `token`.

The result exposes typed `errors`. An empty error list indicates success. The
schema marks the mutation deprecated because it is not production-ready.

### Update a stored payment instrument

The alpha `CustomerMutations.updateStoredPaymentInstrument` mutation accepts
a token plus optional `billingAddress` and `setAsDefault` values.

`setAsDefault` can promote an instrument, but it cannot unset the existing
default.

The result includes:

- the updated instrument
- the resulting default token
- typed errors

The mutation is not intended for production use.

### Company-address management

Authenticated company users gain the alpha `CompanyMutations.addAddress`,
`CompanyMutations.updateAddress`, and `CompanyMutations.deleteAddress` fields.

`CompanyQueries` and `ActiveCompany` gain single-address lookup by `entityId`.
These mutations and lookups are deprecated and not for production.

Address connections gain `city`, `state`, `country`, and `companyIds` filters.
`CompanyAddress` gains nullable `createdAt` and `updatedAt` fields.

## Removed alpha fields

The alpha `companyUser` query, `updateCompanyUser` mutation, and
`CompanyOrdersFiltersInput.search` filter have been removed.

## Country and currency additions

`Country.stateRequired` reports whether addresses for a country require a
state or province.

The `currencyCode` enum adds:

- `MRU`
- `STN`

## Fields graduated from alpha

These fields are no longer deprecated and are production-ready:

- `Locale.fullPath`
- `Locale.path`
- `Product.featuredPromotions`
