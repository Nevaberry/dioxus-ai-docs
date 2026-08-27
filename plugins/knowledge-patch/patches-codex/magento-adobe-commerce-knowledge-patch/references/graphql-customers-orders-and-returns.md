# GraphQL Customers, Orders, Gifts, and Returns

## Customer account flows

Adobe Commerce (`2.4.8-adobe-commerce`) adds the
`resendConfirmationEmail` mutation and paginated `customer.addressesV2`.

## Customer order fields and filters

`CustomerOrders` adds `date_of_first_order` and these filters:

- `created_at`
- `status`
- `grand_total`

`CustomerOrder` adds:

- `is_virtual`
- `available_actions`
- `customer_info`
- `order_status_change_date`

Order addresses can return custom attributes. `OrderItemPrices` supplies
detailed pre-discount prices.

## Order lookup, cancellation, and reordering

Guest order lookup uses `lastname` instead of `postcode`.

`cancelOrder` is registered-customer-only.

`requestGuestOrderCancel` requires an order token, and `confirmCancelOrder`
completes guest cancellation.

Partially shipped orders cannot be canceled.

When reordering is disabled, the `REORDER` action is suppressed.

Matching guest orders are associated with a customer account by email.

## Order totals and tax display

Order totals expose store-credit and reward-point values.

`customerOrders` can return `applied_gift_cards`.

`OrderTotal.subtotal` is deprecated in favor of `subtotal_excl_tax` and
`subtotal_incl_tax`.

`StoreConfig` exposes Admin tax-display settings.

## Gift fields

Gift APIs add:

- `printed_card_priceV2`
- `gift_wrapping_available`
- the price-object field `gift_wrapping_price`

## Returns

Guest orders can use `requestReturn`.

`OrderItemInterface.quantity_return_requested` distinguishes pending return
quantity from completed return quantity.

Past returns remain queryable when RMA is disabled.

Return eligibility excludes items already in a return process.
