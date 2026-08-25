# Catalog, attributes, and search

## Product pricing and translation fields (3.21.0)

Prior-price fields are available on `VariantPricingInfo`,
`ProductPricingInfo`, and `CheckoutLine`. `TaxableObjectDiscount` gains
`type`. `Product.productVariants` replaces deprecated `Product.variants`.
Product, category, collection, and page translations gain slugs usable in
queries.

## Single and constrained references (3.22.0)

`SINGLE_REFERENCE` attributes hold exactly one related entity;
`REFERENCE` remains multi-valued. Reference attributes can restrict selectable
objects to allowed product types or model types. `AttributeEntityType`
supports `CATEGORY` and `COLLECTION`. Dashboard calls Pages and Page Types
Models and Model Types, while the GraphQL API keeps the old names.

## Attribute filters for models and products (3.22.0)

Pages can be filtered by numeric, boolean, date, and reference attributes,
including `containsAll` and `containsAny`. Product filters can match a
`REFERENCE` or `SINGLE_REFERENCE` target by ID, slug, or SKU without naming
the attribute slug. Category filtering includes subcategories. Model
attribute filters are API-only in this release and unavailable in Dashboard.

## `where`, `search`, and expanded filtering (3.22.0)

`where` and `search` replace deprecated `filter` arguments. Orders and draft
orders gain voucher, invoice, fulfillment, payment-method, total, product-type,
and address filters, plus relevance-ranked search and status sorting.
Customers gain filters and search across customer and address-book data. Pages
migrate their filters to the new system. Dashboard supports the order filters,
but not yet the new draft-order or customer filters.

## Direct warehouse-channel stock availability (3.23.0)

`Shop.useLegacyShippingZoneStockAvailability` and its settings input select
legacy address/shipping-zone filtering or direct warehouse-channel
availability. Existing installations default to legacy behavior. Setting it
to `false` changes stock validation, reservation, allocation, fulfillment,
product availability, and relevant webhook warehouse selection.

The `address` argument on `ProductVariant.stocks`,
`ProductVariant.quantityAvailable`, and `Product.isAvailable` is deprecated
and ignored in direct-link mode.

## External product media downloads (3.23.0)

`productMediaCreate` and `productBulkCreate` download images from external
URLs in background tasks. Requests for an image return HTTP 503 while the
download is in progress, so clients must tolerate and retry that state.

## Shared search grammar and relevance (3.23.0)

Search across products, orders, gift cards, checkouts, pages, and users
supports prefix matching, Boolean `AND`, `OR`, and `-`, quoted exact phrases,
accent-insensitive matching, and default relevance ordering. Search filters
can use `RANK` to request relevance ordering explicitly.

## Product-type and export deprecations (3.23.0)

`ProductType.hasVariants` is deprecated. Products may have multiple variants
regardless of its value, and it no longer prevents assigning variant
attributes. `exportProducts`, `exportGiftCards`, and `exportVoucherCodes` are
deprecated in favor of fetching GraphQL data for external export tooling.
Draft-order inputs should replace deprecated `voucher` with `voucherCode`.

## Attribute presentation flags removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`filterableInStorefront`, `filterableInDashboard`, `availableInGrid`, and
`storefrontSearchPosition` are removed from attribute fields, create/update and
filter inputs, and related sort enum values. Storefront or Dashboard
presentation logic must live in the client or attribute metadata. The unused
database columns remain temporarily.

## Empty attribute filters match nothing

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

For page, product, and product-variant `where` filters, `attributes: null`,
`attributes: []`, or a no-op condition such as
`reference: { pageSlugs: {} }` returns no objects instead of matching
everything.

## Product variant stock filters

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The `productVariants` query's `where` input supports `stockAvailability` and
`stocks`, allowing filtering by stock status or quantity for a channel.

## Duplicate channel listing errors

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

When `productVariantBulkUpdate.channelListings.create` names a channel where
the variant is already listed, the mutation returns `DUPLICATED_INPUT_ITEM`,
recommends using `update`, and honors the selected `errorPolicy` instead of
failing with an unhandled server error.
