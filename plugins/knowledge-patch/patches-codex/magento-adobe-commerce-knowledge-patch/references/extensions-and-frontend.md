# Extensions and Frontend

## Adobe Commerce bundled Braintree extension

For Adobe Commerce (`2.4.8-adobe-commerce`), the bundled extension moves
shipping-method selection into the PayPal and Google Pay modals and makes the
review page optional.

Apple Pay and Google Pay modals can show line items, discounts, shipping, and
tax.

The extension uses Braintree PHP SDK 6.21.0 and JavaScript SDK 3.112.0.

Sofort and Giropay are removed.

The extension sends PayPal carrier and tracking details when an order ships.

## Adobe Commerce frontend build output

A critical-head block places critical CSS before other assets.

Developer-mode server-side LESS compilation emits source maps.

Grunt-generated source-map paths no longer carry the `/pub` prefix.

Static deployment excludes CSS belonging to disabled modules.

## Magento Open Source legacy JavaScript assets

For Magento Open Source (`2.4.8-magento-open-source`), the jQuery/fileUploader
and ExtJS folders are removed after migration to Uppy and jsTree. Extensions
must stop importing those legacy assets.

## Magento Open Source TinyMCE

Magento Open Source migrates TinyMCE 5.10.2 to 7.3.0, including its Page Builder
integration.

Custom editor integrations must target TinyMCE 7.

Plugin widget functions are again callable through the returned widget object
for backward compatibility.

## Extension compatibility repairs

`Magento\Catalog\Model\ProductRepository` restores the Initialization Helper as
its second constructor parameter so existing subclasses retain their prior
contract.

`setup:di:compile` generates interceptor methods correctly for plugins
configured through virtual types, matching runtime compilation behavior.
