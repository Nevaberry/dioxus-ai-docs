# Commerce and documents

## Payments

### Re-payment honors `afterOrderEnabled` (since 6.7.13.0)

`POST /store-api/order/payment` rejects a method whose `afterOrderEnabled`
(“Allow payment change after checkout”) is false. It returns
`CHECKOUT__ORDER_PAYMENT_METHOD_NOT_CHANGEABLE` with HTTP 403, so a custom
payment button cannot bypass the setting.

### Unified plugin payment handler

Plugins should extend `AbstractPaymentHandler` rather than the deprecated sync,
async, prepared, refund, and recurring interfaces. `supports()` advertises
optional refund and recurring capabilities. Payment calls receive the
transaction ID, request data when applicable, and `Context`. Sync and async
`pay()` return an optional redirect; prepared-payment `capture()` is replaced
by `pay()`.

### App payment calls

App manifests use `manifest-3.0.xsd` and `pay-url`, not `capture-url`. Async
`pay` / `finalize` calls no longer set payment states automatically. Finalize
query parameters arrive under `requestData`. `CheckoutGatewayRoute` always
filters availability because `onlyAvailable` was removed.

### Technical names

Payment and shipping API writes and plugin installers must provide
`technicalName`; the database columns become non-nullable. Migration assigns
`temporary_<method-id>` when a name is missing, so merchants and extensions
must replace placeholders with stable names.

### Customer default payment

The customer default-payment association is removed in favor of the last-used
or current method. Existing `customerDefaultPaymentMethod` rules migrate to
`paymentMethod`, `checkout.customer.changed-payment-method` flows are disabled,
and Direct Debit no longer advances an order to “in progress” automatically.

## Customers and addresses

### Recovery links

`ChangeEmailRoute` deletes outstanding customer recovery links after the email
address changes. Integrations must not expect an old recovery URL to stay
valid.

### VAT IDs

VAT validation is case-sensitive and normally requires uppercase. Company
customers are revalidated at checkout.

## Rules and cart behavior

### Purchase-price rule shape (since 6.7.13.0)

`LineItemPurchasePriceRule` (`cartLineItemPurchasePrice`) persists
`type: gross|net` instead of the `isNet` boolean. Code that creates or reads
this rule configuration must use `type`.

### Rule helper contracts

`CustomerBirthdayRule::match()` handles a null birthday through the
negative-operator guard. An unknown `LineItemCustomFieldRule` operator throws
`RuleException::unsupportedOperator()` instead of
`CartException::unsupportedOperator()`.

`RuleComparison` is deprecated for inheritance and becomes final in 6.8,
where `date()` and `datetime()` accept `DateTime|string|array` rule values.

### Cart persistence permissions

`CartBehavior::isRecalculation()` is deprecated. For an in-memory calculation,
set `CheckoutPermissions::SKIP_CART_PERSISTENCE` through
`SalesChannelContext::withPermissions()`. Any `CartVerifyPersistEvent`
override must respect it.

## Orders and deliveries

### Primary associations

Use `order.primaryOrderDelivery` and `order.primaryOrderTransaction`, not
positional delivery and transaction collection entries. Existing orders are
backfilled, and `OrderConverter` keeps the primary delivery first for
compatibility. `ORIGINAL_PRIMARY_ORDER_DELIVERY` and
`ORIGINAL_PRIMARY_ORDER_TRANSACTION` cart extensions are read-only snapshots.

### Tax-provider priority (since 6.7.13.0)

An app manifest's tax-provider `priority` applies only during initial
installation. App updates preserve the merchant's chosen ordering.

## Document rendering

### Sales-channel business timezone (since 6.7.13.0)

An optional sales-channel business timezone controls document rendering. In
6.7, an unset value retains entry-point-dependent behavior. In 6.8, it
consistently falls back to `twig.date.timezone`, which is UTC unless configured.
Set the sales-channel value when document timestamps must be stable.

### Return and company address switches

Document configuration has separate switches for “Display return address”
above the recipient and “Display company address” below the header.

### Custom PDF renderers

An `AbstractDocumentRenderer` implementation should render the PDF and call
`RenderedDocument::setContent()`. The constructor no longer receives HTML, and
the `html` property is removed in the next major.

```php
$document = new RenderedDocument($number, $name, $fileType, $config);
$document->setContent($this->pdfRenderer->render($document, $html));
```

## ZUGFeRD

### Correction shipping semantics (since 6.7.13.0)

A manually constructed `ZugferdDocument` should call
`withDocumentInformation()` before adding deliveries. Correction documents
then emit refunded shipping as an allowance, charged return shipping as a
charge, and omit zero-value shipping.

### Price override

`ZugferdDocument::getPrice()` is deprecated. Call and override
`getPriceWithFallback()` because Core no longer invokes `getPrice()` overrides.

## Units

Store API context and product responses convert stored kg/mm values to the
sales-channel domain's measurement system. Admin API clients can choose units
with `sw-measurement-weight-unit` and `sw-measurement-length-unit`. Twig can
convert arbitrary values using `sw_convert_unit(from: ..., to: ..., precision:
...)`.
