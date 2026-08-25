# GraphQL Cart and Checkout

## Adobe Commerce cart prices

In Adobe Commerce (`2.4.8-adobe-commerce`), `CartItemPrices` adds:

- `original_item_price`, explicitly the pre-discount price
- `original_row_total`
- `row_total_including_catalog_discounts_only`

`CartPrices` adds `grand_total_excluding_tax`.

`CartItemInterface` adds `not_available_message`.

## Cart addresses

Cart addresses gain an address-book identifier and
`ShippingCartAddress.same_as_billing`.

## Cart-item update errors

`updateCartItems` returns a successful response containing mapped error
details, including `InsufficientStockError`, instead of throwing. Clients must
inspect the returned errors.

## Checkout configuration and payment visibility

Zero-total checkout exposes only the Free payment method.

`StoreConfig` exposes per-store terms-and-conditions settings.

## Magento Open Source cart inputs

In Magento Open Source (`2.4.8-magento-open-source`), `addProductsToCart`
matches SKUs case-insensitively.

`setShippingAddressesOnCart` accepts `pickup_location_code` without a customer
address ID or address object.

`customerCart` creates an empty cart when no quote exists.

## Multi-website scope

In multi-website installations, customer-info and cart queries verify that the
customer exists on the requested non-default website.
