# Catalog APIs and GraphQL Runtime

## Adobe Commerce product and store configuration

In Adobe Commerce (`2.4.8-adobe-commerce`), `ProductInterface.quantity` returns
available stock or `null` according to Admin settings.

`StoreConfig` exposes grouped-product and configurable-product image selection.

`recaptchaV3Config` adds `theme`.

`trackViewedProduct` is callable by both guests and customers.

## GraphQL runtime

The framework supports custom scalar implementations.

The default maximum query complexity rises from 300 to 1000.

Requests made with expired customer tokens return HTTP 401.

## Magento Open Source product layouts

In Magento Open Source (`2.4.8-magento-open-source`), frontend product layouts
can be selected by attribute set. This supplements the existing SKU-based and
product-type-based layout choices.

## REST product lookup

OAuth1 REST product GET requests work for SKUs containing `/`.

## Catalog GraphQL behavior

Category filtering by `category_uid` with `includeDirectChildrenOnly` returns
only direct children.

Multi-field product sorting works when sort fields are supplied through
variables.

Product-search `total_count` is no longer capped at 10,000 matches.
