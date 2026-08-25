# GraphQL carts and catalog

## Adobe Commerce cart price fields

In Adobe Commerce 2.4.8 (`2.4.8-adobe-commerce`), `CartItemPrices` adds:

- `original_item_price`, explicitly pre-discount
- `original_row_total`
- `row_total_including_catalog_discounts_only`

`CartPrices` adds `grand_total_excluding_tax`. `CartItemInterface` adds
`not_available_message`.

## Cart addresses, errors, and checkout

Cart addresses gain an address-book identifier. `ShippingCartAddress` adds
`same_as_billing`.

`updateCartItems` returns a successful response containing mapped error details,
including `InsufficientStockError`, instead of throwing. Clients must inspect
the returned errors.

Zero-total checkout exposes only the Free payment method. `StoreConfig` exposes
per-store terms-and-conditions settings.

## Adobe Commerce catalog and runtime behavior

`ProductInterface.quantity` returns available stock or `null` according to
Admin settings.

`StoreConfig` exposes grouped- and configurable-product image selection.
`recaptchaV3Config` adds `theme`. `trackViewedProduct` is callable by both
guests and customers.

The framework supports custom scalar implementations. The default maximum query
complexity rises from 300 to 1000. Requests made with expired customer tokens
return HTTP 401.

## Magento Open Source catalog API behavior

In Magento Open Source 2.4.8 (`2.4.8-magento-open-source`), OAuth1 REST product
GET requests work for SKUs containing `/`.

GraphQL category filtering by `category_uid` with
`includeDirectChildrenOnly` returns only direct children. Multi-field product
sorting works when sort fields are supplied through variables. Product-search
`total_count` is no longer capped at 10,000 matches.

## Magento Open Source cart inputs

`addProductsToCart` matches SKUs case-insensitively.

`setShippingAddressesOnCart` accepts `pickup_location_code` without a customer
address ID or address object.

`customerCart` creates an empty cart when no quote exists.

In multi-website installations, customer-info and cart queries verify that the
customer exists on the requested non-default website.
