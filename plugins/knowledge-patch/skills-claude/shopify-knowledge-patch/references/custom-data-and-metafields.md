# Custom Data and Metafields

## Nullable fields and bulk-operation errors

`DiscountAutomaticBasic.minimumRequirement` and
`DiscountAutomaticFreeShipping.minimumRequirement` can be `null`.

`ReverseFulfillmentOrder.order` can be `null` without a GraphQL error when
`read_all_orders` is absent, the order is more than 60 days old, or the order
no longer exists.

`BulkOperationUserError` is public. Errors returned by
`bulkOperationRunQuery` now include `code`.

## Localized fields and Function validation

`localizationExtensions` became `localizedFields` on `DraftOrderInput` and
`OrderUpdate` input. `HasLocalizedFields` supports locally required tax-field
validation.

Function `Cart.localizedFields` returns values only for server-side
`purchase.validation.run`. Across Function APIs, malformed metafield
input-query variables raise `InvalidVariableValueError` instead of being
treated as empty.

## App-owned custom-data permissions

`PrivateMetafield` is gone from the public Admin API. Use app-data metafields
for app storage or app-reserved namespaces for per-resource data.

App-reserved metafield and metaobject mutations no longer accept `PRIVATE`,
`PUBLIC_READ`, `PUBLIC_READ_WRITE`, or `LEGACY_LIQUID_ONLY`.
`MetafieldAccessInput.admin` and `MetafieldAccessUpdateInput.admin` are
optional.

## Storefront access and capabilities

The `MetafieldStorefrontVisibility` object, its queries and mutations, and the
`visibleToStorefrontApi` fields were removed. Read
`MetafieldDefinition.access` and change it with `metafieldDefinitionUpdate`.

`MetafieldDefinitionInput.useAsCollectionCondition` was replaced by
`capabilities.smartCollectionCondition`. Standard-definition enable mutations
now accept `capabilities`.

## Conditional and unique definitions

Create inputs accept `constraints`, and update inputs accept
`constraintsUpdates`. In `2025-01`, product metafield definitions support
product-category constraints, product updates provide
`deleteConflictingConstrainedMetafields`, and
`VariantOptionValueInput.linkedMetafieldValue` is available.

`MetafieldCapabilityUniqueValues` can enforce uniqueness only before a
definition has metafields, and only for `single_line_text_field`,
`number_integer`, `url`, and `id` values.

## Delete metafields by identifier fields

`metafieldDelete(gid)` was removed in favor of `metafieldsDelete`. Each array
entry identifies a metafield with `ownerId`, `namespace`, and `key`; a
metafield GID is not accepted.

## Custom IDs and upserts

Custom IDs, formerly called external keys, are metafield-backed identifiers
available to any metafield-capable resource. Lookup by custom ID is limited to
products and customers.

`productSet` and unstable `customerSet` provide matching-key upserts, but a
custom ID cannot yet be the matching key.

## Metafield query errors

Invalid metafield queries now return GraphQL Admin API errors.
