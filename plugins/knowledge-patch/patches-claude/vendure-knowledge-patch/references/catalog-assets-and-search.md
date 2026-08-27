# Catalog, assets, and search

Source batch: `official-changelog-2025-current`.

## Asset MIME allow-lists

The unreleased line upgrades `file-type` to `^21.3.1` and adopts these IANA
names:

- `audio/flac`
- `video/matroska`
- `application/vnd.apache.arrow.file`
- `application/vnd.apache.parquet`

Replace the former `x-` names in explicit
`assetOptions.permittedFileTypes` lists. The default wildcard list is
unaffected.

## Channel-aware products and stock

- Product lookup by slug is channel-scoped.
- `assignProductsToChannel` assigns the Product as well as its variants.
- Assigning a variant to a channel seeds a `StockLevel`.
- New variants inherit every channel of their Product.
- Numeric `stockOnHand` writes target the active channel's stock location.

## Shared product options

In 3.6, `ProductOptionGroup` and `ProductOption` become shared, channel-aware
entities. CSV import supports shared option groups, and the Dashboard gains an
Option Groups management page.

## Search and list filtering

- DefaultSearchPlugin accepts `collectionIds` and `collectionSlugs`.
- Tax-rate lists can filter by `zoneId` and `categoryId`.
- Collection queries expose `productVariantCount`.
- Product and variant tooling supports SKU filtering.
- Elasticsearch can `groupBySKU` for multi-vendor stores.

## Custom-field controls

- Custom fields can be deprecated in GraphQL with `@deprecated`.
- The `dashboard` option can hide custom fields from Dashboard forms.
- Custom-field defaults apply during entity creation.
- Non-public OrderLine custom fields remain available in the Admin API.
- ProductVariantPrice custom fields have Dashboard inputs.

## Asset capabilities

`AssetStorageStrategy` may specify an encoding. Dashboard asset management
adds tags and focal-point editing.

## Variant and facet Admin APIs

The Admin API adds:

- `updateProductVariant`;
- single `facetValue` lookup; and
- single facet-value create and update mutations.

`CreateProductVariantInput` also exposes the previously missing `enabled`
field.

## Translation fallbacks

Server-side translatable fields fall back when a translated value is empty.
Facets and facet values follow channel language fallbacks.
