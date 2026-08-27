# Payments, gifts, and returns

## Adobe Commerce order totals and tax display

In Adobe Commerce 2.4.8 (`2.4.8-adobe-commerce`), order totals expose store-credit
and reward-point values. `customerOrders` can return `applied_gift_cards`.

`OrderTotal.subtotal` is deprecated in favor of `subtotal_excl_tax` and
`subtotal_incl_tax`.

`StoreConfig` exposes Admin tax-display settings.

## Gift API fields

Gift APIs add:

- `printed_card_priceV2`
- `gift_wrapping_available`
- price-object `gift_wrapping_price`

## Guest returns and eligibility

Guest orders can use `requestReturn`.

`OrderItemInterface.quantity_return_requested` distinguishes pending return
quantity from completed return quantity.

Past returns remain queryable when RMA is disabled. Return eligibility excludes
items already in a return process.

## Bundled Braintree extension

The bundled extension moves shipping-method selection into the PayPal and
Google Pay modals and makes the review page optional.

Apple Pay and Google Pay modals can show line items, discounts, shipping, and
tax.

The extension updates to Braintree PHP SDK 6.21.0 and JavaScript SDK 3.112.0.
It removes Sofort and Giropay. It sends PayPal carrier and tracking details when
an order ships.
