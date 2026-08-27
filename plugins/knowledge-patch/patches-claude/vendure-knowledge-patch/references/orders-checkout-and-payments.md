# Orders, checkout, and payments

Source batch: `official-changelog-2025-current`.

## Cart and checkout schema

The Shop API adds `addItemsToOrder` for adding multiple lines and a mutation
for changing the active order's currency.

`AddPaymentToOrderResult` can return `CouponRemovedDuringCheckoutError` when
checkout invalidates a coupon.

## Order calculation strategies

- `OrderTaxCalculationStrategy` makes order-level tax calculation
  configurable.
- `OrderLineDiscountDistributionStrategy` controls discount proration.
- `OrderMergeStrategy` may be asynchronous.

## Coupon and promotion semantics

From 3.7, promotion coupon matching is case-insensitive. This is breaking for
stores that treated case variants as distinct codes.

Usage limits apply to auto-applied promotions and concurrent checkout races.
Draft and seller orders are excluded from the corresponding counts.

## Atomic order operations

`OrderService.mergeOrders()` is atomic and concurrency-safe. State-machine
transitions roll back atomically when a hook fails.

## Interceptors and update events

`removeAllItemsFromOrder` calls `OrderInterceptor.willRemoveItemFromOrder`.
Update events contain the post-update entity.

## Tax and shipping behavior

- Tax-zone selection uses only the shipping address.
- Tax-inclusive shipping cancellation is used when `pricesIncludeTax` is
  enabled.
- Free-shipping tax calculation is corrected.

## Payment-method eligibility

A payment method must be enabled to qualify.

## Public Shop APIs

The Shop API exposes `activePaymentMethods` and `activeShippingMethods`,
including their custom fields.
