# Commerce, Orders, Payments, and Documents

## Orders, customers, and addresses

### Re-payment method enforcement (6.7.13.0)

`POST /store-api/order/payment` rejects a method whose `afterOrderEnabled` ("Allow payment change after checkout") flag is false. It returns `CHECKOUT__ORDER_PAYMENT_METHOD_NOT_CHANGEABLE` with HTTP 403, so custom payment buttons cannot bypass the setting.

### Primary delivery and transaction associations

Use `order.primaryOrderDelivery` and `order.primaryOrderTransaction` instead of positional access to delivery and transaction collections. Existing orders are backfilled. `OrderConverter` keeps the primary delivery first for compatibility. `ORIGINAL_PRIMARY_ORDER_DELIVERY` and `ORIGINAL_PRIMARY_ORDER_TRANSACTION` cart extensions are read-only informational snapshots.

### Customer email recovery links

`ChangeEmailRoute` deletes outstanding customer recovery links after an address change. Integrations must not expect old recovery URLs to remain valid.

### Registration address validation and limits

Malformed billing or shipping values during registration return HTTP 400 validation errors instead of a server error. Customer and order address first and last names support 255 characters. Custom validators and schemas should match these contracts.

### VAT IDs

VAT validation is case-sensitive and normally requires uppercase. Company customers are revalidated at checkout.

## Cart, rules, and pricing

### Rule helper contracts

`CustomerBirthdayRule::match()` handles a null birthday through the negative-operator guard. An unknown `LineItemCustomFieldRule` operator throws `RuleException::unsupportedOperator()`, not `CartException::unsupportedOperator()`. `RuleComparison` is deprecated for inheritance and becomes final in 6.8, where `date()` and `datetime()` accept `DateTime|string|array` rule values.

### Digital-product legacy state repair

The update post-finish subscriber rebuilds missing legacy `product.states` so product-state rules and digital-delivery flows work. It runs automatically once per installation and records completion in `app_config`.

### Filterable price definitions

Custom price definitions intended to be filterable must implement `Shopware\Core\Checkout\Cart\Price\Struct\FilterableInterface` and `getFilter()`.

### Recalculation and persistence permissions

`CartBehavior::isRecalculation()` is deprecated. For an in-memory calculation, set `CheckoutPermissions::SKIP_CART_PERSISTENCE` through `SalesChannelContext::withPermissions()` and ensure any `CartVerifyPersistEvent` override respects it.

### Variant price sorting

Product-listing min/max price logic uses `MIN()` instead of selecting an arbitrary grouped variant row. Sorting a variant product by price reflects its cheapest variant.

## Payment and shipping migrations

### Customer default-payment removal

The customer default payment association is removed in favor of the last-used/current method. Existing `customerDefaultPaymentMethod` rules migrate to `paymentMethod`. `checkout.customer.changed-payment-method` flows are disabled. Direct Debit no longer moves an order to “in progress” automatically.

### Required method technical names

Payment and shipping API writes and plugin installers must provide `technicalName`; the database columns become non-nullable. Migration uses `temporary_<method-id>` for missing values, so merchants and extensions must replace placeholders with stable names.

### Unified payment handler contract

Plugins should extend `AbstractPaymentHandler` instead of deprecated sync, async, prepared, refund, and recurring interfaces. `supports()` declares optional refund and recurring capabilities. Payment calls receive the transaction ID, request data when applicable, and `Context`. Sync and async `pay()` return an optional redirect. Prepared-payment `capture()` is replaced by `pay()`.

### App payment calls

App manifests use `manifest-3.0.xsd` and `pay-url` rather than `capture-url`. Async `pay` and `finalize` calls do not set payment states automatically. Finalize query parameters arrive under `requestData`. `CheckoutGatewayRoute` always filters availability because `onlyAvailable` is removed.

### Tax-provider priorities (6.7.13.0)

An app manifest tax-provider `priority` is applied only on initial installation. App updates preserve merchant-selected ordering.

## Documents and invoicing

### Sales-channel business timezone (6.7.13.0)

An optional sales-channel business timezone controls document rendering. In 6.7, an unset value retains entry-point-dependent behavior. In 6.8, it consistently falls back to `twig.date.timezone`, UTC unless configured. Set the sales-channel value when document timestamps must be stable.

### Return and company address switches

Document configuration separately controls “Display return address” above the recipient and “Display company address” below the header.

### ZUGFeRD correction shipping (6.7.13.0)

Manually constructed `ZugferdDocument` instances should call `withDocumentInformation()` before adding deliveries. Correction documents then emit refunded shipping as an allowance, charged return shipping as a charge, and omit zero-value shipping.

### ZUGFeRD price fallback

`ZugferdDocument::getPrice()` is deprecated. Call and override `getPriceWithFallback()` because Core no longer invokes `getPrice()` overrides.

### Custom PDF renderers

`AbstractDocumentRenderer` implementations should render the PDF and call `RenderedDocument::setContent()`. The constructor no longer receives HTML, and the `html` property is removed in the next major.

```php
$document = new RenderedDocument($number, $name, $fileType, $config);
$document->setContent($this->pdfRenderer->render($document, $html));
```
