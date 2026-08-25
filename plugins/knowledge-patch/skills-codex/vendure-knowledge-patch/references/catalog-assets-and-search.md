# Catalog, Assets, and Search

## Asset MIME allow-lists

The unreleased line upgrades `file-type` to `^21.3.1` and adopts these IANA
names:

- `audio/flac`
- `video/matroska`
- `application/vnd.apache.arrow.file`
- `application/vnd.apache.parquet`

Replace the former `x-` names in explicit `assetOptions.permittedFileTypes`
lists. The default wildcard list is unaffected.

## Channel-aware catalog behavior

### Product lookup and assignment

Product lookup by slug is channel-scoped. `assignProductsToChannel` assigns
the Product as well as its variants, and new variants inherit every channel of
their Product.

### Variant stock behavior

Assigning a variant to a channel seeds a `StockLevel`. Numeric `stockOnHand`
writes target the active channel's stock location.

## Shared product options

In 3.6, `ProductOptionGroup` and `ProductOption` become shared, channel-aware
entities. CSV import supports shared option groups, and the Dashboard gains an
Option Groups management page.

## Public catalog APIs

The Admin API adds:

- `updateProductVariant`.
- Single `facetValue` lookup.
- Single facet-value create and update mutations.

`CreateProductVariantInput` exposes the previously missing `enabled` field.

## Search and list filtering

### Default search and collections

DefaultSearchPlugin accepts `collectionIds` and `collectionSlugs`. Collection
queries expose `productVariantCount`.

### Tax, SKU, and Elasticsearch filters

Tax-rate lists can filter by `zoneId` and `categoryId`. Product and variant
tooling supports SKU filtering, while Elasticsearch can `groupBySKU` for
multi-vendor stores.

## Custom-field controls

Custom fields can:

- Be deprecated in GraphQL with `@deprecated`.
- Be hidden from Dashboard forms with the `dashboard` option.
- Have defaults that apply during entity creation.

Non-public OrderLine custom fields remain available in the Admin API.
ProductVariantPrice custom fields have Dashboard inputs.

## Asset behavior and management

`AssetStorageStrategy` may specify an encoding. Dashboard asset management
adds tags and focal-point editing.

## Translation fallback behavior

Server-side translatable fields fall back when a translated value is empty.
Facets and facet values follow channel language fallbacks. Dashboard language
and currency choices are derived dynamically from the schema.

_Source batch: `official-changelog-2025-current`._
