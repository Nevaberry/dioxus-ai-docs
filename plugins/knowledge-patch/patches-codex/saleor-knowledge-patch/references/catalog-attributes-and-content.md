# Catalog, Attributes, and Content

## Product pricing and translation fields expand

Since 3.21.0, prior-price fields are available on `VariantPricingInfo`,
`ProductPricingInfo`, and `CheckoutLine`; `TaxableObjectDiscount` gains `type`.
`Product.productVariants` replaces deprecated `Product.variants`. Product,
category, collection, and page translations gain slugs that can be used in
queries.

## Models support single and constrained references

Since 3.22.0, `SINGLE_REFERENCE` attributes hold exactly one related entity,
while `REFERENCE` remains multi-valued. Reference attributes can restrict
selectable objects to allowed product types or model types.
`AttributeEntityType` supports `CATEGORY` and `COLLECTION`. Dashboard calls
Pages and Page Types Models and Model Types, while the GraphQL API retains the
old names.

## Attribute filters support models and referenced products

Since 3.22.0, Pages can be filtered by numeric, boolean, date, and reference
attributes, including `containsAll` and `containsAny`. Product filters can
match a `REFERENCE` or `SINGLE_REFERENCE` target by ID, slug, or SKU without
naming the attribute slug. Category filtering includes subcategories. Model
attribute filters are API-only in this release and are not yet available in
Dashboard.

## Stock availability can use direct warehouse-channel links

Since 3.23.0, `Shop.useLegacyShippingZoneStockAvailability` and its settings
input select legacy address/shipping-zone filtering or direct warehouse-channel
availability. Existing installations default to legacy behavior. Setting it to
`false` changes stock validation, reservation, allocation, fulfillment,
product availability, and relevant webhook warehouse selection. The `address`
argument on `ProductVariant.stocks`, `ProductVariant.quantityAvailable`, and
`Product.isAvailable` is deprecated and ignored in direct-link mode.

## External product media is eventually available

Since 3.23.0, `productMediaCreate` and `productBulkCreate` download images from
external URLs in background tasks. An image request returns HTTP 503 while its
download is in progress; clients must tolerate and retry that state.

## EditorJS input and links are stricter

Since 3.23.0, the EditorJS parser rejects unknown or extra fields, and rendered
links default to `rel="noopener noreferrer"`.
`UNSAFE_EDITOR_JS_ALLOWED_URL_SCHEMES` can no longer extend accepted URL
schemes. Deployments relying on permissive rich-text payloads or custom schemes
must clean up that content before upgrading.

## Product-type and export interfaces are deprecated

Since 3.23.0, `ProductType.hasVariants` is deprecated. Products may have
multiple variants regardless of its value, and it no longer prevents assigning
variant attributes. `exportProducts`, `exportGiftCards`, and
`exportVoucherCodes` are deprecated in favor of fetching GraphQL data for
external export tooling.

## Legacy digital-content API is removed

Since 3.23.0, the undocumented legacy digital-content API is removed, while
supported digital-product flows remain available.

## Attribute presentation flags are removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`filterableInStorefront`, `filterableInDashboard`, `availableInGrid`, and
`storefrontSearchPosition` are removed from attribute fields, create/update and
filter inputs, and related sort enum values. Storefront or Dashboard
presentation logic must live in the client or in attribute metadata. The
unused database columns remain temporarily.

## Empty attribute filters match nothing

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

For page, product, and product-variant `where` filters, `attributes: null`,
`attributes: []`, or a no-op condition such as
`reference: { pageSlugs: {} }` returns no objects instead of silently matching
everything.

## Product variants support stock filters

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The `productVariants` query's `where` input supports `stockAvailability` and
`stocks`, allowing filtering by stock status or quantity for a channel.

## Duplicate channel listings return a structured error

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

When `productVariantBulkUpdate.channelListings.create` names a channel where
the variant is already listed, the mutation returns `DUPLICATED_INPUT_ITEM`,
recommends using `update`, and honors the selected `errorPolicy` instead of
failing with an unhandled server error.

## The top-level variant query replaces `Product.variant`

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`Product.variant` is removed in favor of the top-level `variant` query.

## Remaining legacy digital-content surfaces are removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The `DIGITAL_LINKS` order-email event, `DIGITAL_LINK_DOWNLOADED` customer event,
and always-empty fulfillment-notification `digital_lines` key are removed. Use
`physical_lines` for all fulfillment lines. GraphQL product-type `isDigital`
fields, inputs, filters, and sorting are removed, as is the ORM field
`ProductType.is_digital`.

## Digital-content database cleanup leaves media files

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The legacy `product_digitalcontent` and `product_digitalcontenturl` tables and
related site-settings columns are dropped, but uploaded files are not deleted
from media storage. Operators may remove the `digital_contents/` directory
manually. The remaining `ProductType.is_digital` database column is scheduled
for removal in 3.25.
