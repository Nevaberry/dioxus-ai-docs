# GraphQL customers and orders

## Customer account operations

In Adobe Commerce 2.4.8 (`2.4.8-adobe-commerce`), customers gain the
`resendConfirmationEmail` mutation and paginated `customer.addressesV2`.

## Order collection fields and filters

`CustomerOrders` gains `date_of_first_order` and these filters:

- `created_at`
- `status`
- `grand_total`

`CustomerOrder` gains:

- `is_virtual`
- `available_actions`
- `customer_info`
- `order_status_change_date`

Order addresses can return custom attributes. `OrderItemPrices` supplies
detailed pre-discount prices.

## Guest lookup and cancellation

Guest order lookup uses `lastname` instead of `postcode`.

`cancelOrder` is registered-customer-only. `requestGuestOrderCancel` requires
an order token, and `confirmCancelOrder` completes guest cancellation.

Partially shipped orders cannot be canceled.

## Reordering and guest association

When reordering is disabled, the `REORDER` action is suppressed.

Matching guest orders are associated with a customer account by email.
