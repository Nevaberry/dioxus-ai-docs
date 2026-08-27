# Checkout, Orders, and Delivery

## Checkout address persistence is configurable

Since 3.21.0, `saveBillingAddress` and `saveShippingAddress` are supported by
`checkoutCreate`, both checkout address-update mutations, `draftOrderCreate`,
and `draftOrderUpdate`. They apply when completing a checkout or draft order
for a signed-in customer and must accompany a valid address input. Click &
Collect does not save a shipping address. Without an override, checkouts save
addresses and draft orders do not.

## Refund and invoice mutation contracts change

Since 3.21.0, `OrderGrantRefundCreateInput.transactionId` is required.
`invoiceRequest` does not error when an app subscribed to `INVOICE_REQUESTED`
is installed without the removed invoice plugin.

## Read queries do not invoke tax or shipping integrations

Since 3.21.0, `checkouts`, `checkoutLines`, and `me.checkouts` do not run
`CHECKOUT_CALCULATE_TAXES`, `SHIPPING_LIST_METHODS_FOR_CHECKOUT`, or
`CHECKOUT_FILTER_SHIPPING_METHODS`. Likewise, `orders`, `draftOrders`, and
`me.orders` do not run `ORDER_CALCULATE_TAXES` or
`ORDER_FILTER_SHIPPING_METHODS`. Integrations must not rely on read-query side
effects.

## No-op mutations suppress webhook work

Since 3.21.0, `draftOrderUpdate` and `orderUpdate` do not emit update webhooks
when nothing changed. `CHECKOUT_FILTER_SHIPPING_METHODS` and
`ORDER_FILTER_SHIPPING_METHODS` are also skipped when a related mutation
produces no available-method change, including when there is no shipping
address.

## Checkout exposes notes, metadata, and subscriptions

Since 3.21.0, `Checkout.customerNote` and `CheckoutCustomerNoteUpdate` expose
checkout customer notes. `CheckoutCreateInput` accepts `metadata` and
`privateMetadata`; `CheckoutLinesUpdate` accepts per-line `metadata`.
Filterable subscriptions are available for `checkoutCreated`,
`checkoutUpdated`, `checkoutFullyPaid`, and `checkoutMetadataUpdated`.

## Checkout shipping enforces currency compatibility

Since 3.21.0, `Checkout.shippingMethods` and
`Checkout.availableShippingMethods` omit external methods whose currency does
not match the checkout currency. `checkoutShippingAddressUpdate` can update a
checkout that does not require shipping without raising an error.

## Order and draft-order inputs accept metadata and language

Since 3.21.0, `draftOrderCreate`, `draftOrderUpdate`, and `orderUpdate` can
write metadata and private metadata. `DraftOrderInput`,
`DraftOrderCreateInput`, and `OrderUpdateInput` also accept `languageCode`.

## Order-shipping mutations emit events for the actual order type

Since 3.21.0, changing a draft order's shipping method with
`orderUpdateShipping` emits `DRAFT_ORDER_UPDATED`, not `ORDER_UPDATED`. For an
editable order, clearing the method with null emits `ORDER_UPDATED`. Updating
variant metadata emits both `PRODUCT_VARIANT_METADATA_UPDATED` and
`PRODUCT_VARIANT_UPDATED` when subscribed.

## Draft and unconfirmed orders refresh base prices differently

Since 3.21.0, order updates use denormalized base prices. `UNCONFIRMED` orders
never refresh them, while `DRAFT` orders refresh them after a default of 24
hours.

## Delivery-option calculation is explicit

Since 3.23.0, storefronts can call `deliveryOptionsCalculate` to deliberately
run `SHIPPING_LIST_METHODS_FOR_CHECKOUT` and
`CHECKOUT_FILTER_SHIPPING_METHODS` and receive `Delivery` objects.
`Checkout.delivery` replaces deprecated `shippingMethod` and `deliveryMethod`,
and `checkoutDeliveryMethodUpdate.deliveryMethodId` should receive a
`CheckoutDelivery` ID.

`Checkout.problems` reports a non-blocking
`CheckoutProblemDeliveryMethodStale`, which calculation or completion
revalidates, or a blocking `CheckoutProblemDeliveryMethodInvalid`, which
requires assigning a valid delivery before completion.

## Order shipping-method metadata is snapshotted

Since 3.23.0, checkout-to-order conversion and draft-order finalization copy
shipping method metadata and private metadata into dedicated order fields.
Later edits or deletion of the source shipping method no longer change the
order's `shippingMethod.metadata` view.

## Async order events do not pre-fire synchronous webhooks

Since 3.23.0, preparing asynchronous order, draft-order, or fulfillment events
does not invoke synchronous hooks such as `ORDER_CALCULATE_TAXES` or
`ORDER_FILTER_SHIPPING_METHODS`. Those hooks run only when their data is
actually requested. Integrations must not depend on an async event producing
those synchronous side effects.

## Draft-order voucher input changes

Since 3.23.0, draft-order inputs should replace the deprecated `voucher` field
with `voucherCode`.

## Checkout mutation contracts change

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`checkoutShippingAddressUpdate` and `checkoutBillingAddressUpdate` remove
`checkoutId` in favor of `id`. `checkoutLineDelete` is replaced by
`checkoutLinesDelete`, which accepts `linesIds` and only the checkout `id`.
`checkoutCreate.lines` is optional; omitting it creates an empty checkout.

## Shop and order configuration surfaces move

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`shopDomainUpdate` is replaced by the `PUBLIC_URL` environment variable. Order
settings move from `orderSettingsUpdate` and the `orderSettings` query to
`channelUpdate(orderSettings: ...)` and `channel.orderSettings`. The no-op
`shopFetchTaxRates` mutation and `ShopFetchTaxRates` type are removed; tax
configuration should use mutations such as `taxConfigurationUpdate`.

## Deprecated order and checkout fields are removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`orderAddNote` is replaced by `orderNoteAdd`,
`Order.availableShippingMethods` by `shippingMethods`, and `Checkout.note` by
`customerNote`.
