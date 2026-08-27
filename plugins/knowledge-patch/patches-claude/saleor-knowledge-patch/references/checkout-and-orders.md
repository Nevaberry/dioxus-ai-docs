# Checkout and orders

## Checkout address persistence (3.21.0)

`saveBillingAddress` and `saveShippingAddress` are supported by
`checkoutCreate`, both checkout address-update mutations, `draftOrderCreate`,
and `draftOrderUpdate`. They matter when completing a checkout or draft order
for a signed-in customer and must accompany a valid address input. A shipping
address is not saved for Click & Collect. Without an override, checkouts save
addresses and draft orders do not.

## Read queries do not invoke tax or shipping integrations (3.21.0)

`checkouts`, `checkoutLines`, and `me.checkouts` do not run
`CHECKOUT_CALCULATE_TAXES`, `SHIPPING_LIST_METHODS_FOR_CHECKOUT`, or
`CHECKOUT_FILTER_SHIPPING_METHODS`. `orders`, `draftOrders`, and `me.orders`
do not run `ORDER_CALCULATE_TAXES` or `ORDER_FILTER_SHIPPING_METHODS`.
Integrations must not rely on these read-query side effects.

## Checkout notes, metadata, and subscriptions (3.21.0)

`Checkout.customerNote` and `CheckoutCustomerNoteUpdate` expose checkout
customer notes. `CheckoutCreateInput` accepts `metadata` and
`privateMetadata`; `CheckoutLinesUpdate` accepts per-line `metadata`.
Filterable subscriptions are available for `checkoutCreated`,
`checkoutUpdated`, `checkoutFullyPaid`, and `checkoutMetadataUpdated`.

## Shipping method currency behavior (3.21.0)

`Checkout.shippingMethods` and `Checkout.availableShippingMethods` omit
external methods whose currency differs from the checkout currency.
`checkoutShippingAddressUpdate` can update a checkout that does not require
shipping without raising an error.

## Order, draft-order, and gift-card input context (3.21.0)

`draftOrderCreate`, `draftOrderUpdate`, and `orderUpdate` can write metadata
and private metadata. `GiftCardCreate` and `GiftCardUpdate` can do the same
through their input types. `DraftOrderInput`, `DraftOrderCreateInput`, and
`OrderUpdateInput` accept `languageCode`.

## Metadata merge and permission behavior (3.21.0)

`transactionUpdate` merges supplied `metadata` and `privateMetadata` into
existing maps instead of replacing them. Updating metadata on an `Order` or
`OrderLine` requires `MANAGE_ORDERS`.

## Discount fields and voucher propagation (3.21.0)

`OrderLine.discounts` returns `OrderLineDiscount` entries.
`OrderDiscount.total` replaces deprecated `OrderDiscount.amount`.
`draftOrderInput.discount` is deprecated. `useLegacyLineVoucherPropagation`
lets specific voucher types keep the old line-propagation behavior.

## Shipping-related mutation events (3.21.0)

Changing a draft order's shipping method with `orderUpdateShipping` emits
`DRAFT_ORDER_UPDATED`, not `ORDER_UPDATED`. For an editable order, clearing
the method with `null` emits `ORDER_UPDATED`. Updating variant metadata emits
both `PRODUCT_VARIANT_METADATA_UPDATED` and `PRODUCT_VARIANT_UPDATED` when
subscribed.

## Draft and unconfirmed order base prices (3.21.0)

Order updates use denormalized base prices. `UNCONFIRMED` orders never refresh
them. `DRAFT` orders refresh them after a default of 24 hours.

## Explicit delivery-option calculation (3.23.0)

Storefronts can call `deliveryOptionsCalculate` to deliberately run
`SHIPPING_LIST_METHODS_FOR_CHECKOUT` and
`CHECKOUT_FILTER_SHIPPING_METHODS` and receive `Delivery` objects.
`Checkout.delivery` replaces deprecated `shippingMethod` and
`deliveryMethod`. Pass a `CheckoutDelivery` ID to
`checkoutDeliveryMethodUpdate.deliveryMethodId`.

`Checkout.problems` reports non-blocking
`CheckoutProblemDeliveryMethodStale`, which calculation or completion
revalidates. A blocking `CheckoutProblemDeliveryMethodInvalid` requires a
valid delivery assignment before completion.

## GraphQL nullability and input contracts (3.23.0)

`RefundSettingsUpdate.refundSettings` becomes nullable on errors.
`Attribute.name`, `Attribute.slug`, and `Attribute.type` become non-null.
Federation `_entities` requires `representations: [_Any!]!`, and
`AppInstallInput` makes `appName` and `manifestUrl` schema-required.
`NonNegativeInt` underlies `Minute`, `Hour`, and `Day`, so negative time values
fail GraphQL validation instead of producing mutation error code `INVALID`.

## Shipping-method metadata snapshots (3.23.0)

Checkout-to-order conversion and draft-order finalization copy shipping method
metadata and private metadata into dedicated order fields. Later edits or
deletion of the source shipping method do not change the order's
`shippingMethod.metadata` view.

## Checkout mutation contract changes

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`checkoutShippingAddressUpdate` and `checkoutBillingAddressUpdate` replace
`checkoutId` with `id`. `checkoutLineDelete` is replaced by
`checkoutLinesDelete`, which accepts `linesIds` and only the checkout `id`.
`checkoutCreate.lines` is optional; omitting it creates an empty checkout.

## Removed order, product, and checkout fields

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`orderAddNote` is replaced by `orderNoteAdd`,
`Order.availableShippingMethods` by `shippingMethods`, `Product.variant` by the
top-level `variant` query, and `Checkout.note` by `customerNote`.

## Bulk delete input limit

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Every bulk delete mutation accepts at most 100 IDs by default and returns an
`INVALID` error above the limit. Deployments can change the cap with:

```env
BULK_DELETE_LIMIT=250
```
