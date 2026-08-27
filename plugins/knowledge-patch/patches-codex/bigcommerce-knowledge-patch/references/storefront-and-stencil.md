# Storefront GraphQL and Stencil

## Stencil category custom-field visibility

The redundant `is_visible` property on custom-field overrides in Stencil's
`category_content` resource is deprecated and will stop being returned.

Remove theme references to `is_visible`. There is no replacement field.

## Country address requirements

`Country.stateRequired` reports whether addresses for a country require a
state or province.

## Currency codes

The `currencyCode` enum includes `MRU` and `STN`.

## Fields graduated from alpha

The following fields have graduated from alpha and are no longer deprecated,
so they are production-ready:

- `Locale.fullPath`;
- `Locale.path`;
- `Product.featuredPromotions`.
