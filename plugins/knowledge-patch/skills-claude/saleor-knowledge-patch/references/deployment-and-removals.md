# Deployment and removals

## Removed plugins and plugin-manager hooks (3.21.0)

The invoicing plugin and deprecated `mirumee.payments.stripe` plugin are
removed. Custom deployments must use an invoice app and migrate Stripe
references to `saleor.payments.stripe`. Plugin-manager methods
`perform_mutation` and `change_user_address` are removed.

## Deployment environment contracts (3.21.0)

GCP private storage uses `GS_MEDIA_PRIVATE_BUCKET_NAME` instead of
`GS_MEDIA_BUCKET_NAME`. Environment parsing accepts numeric and lowercase
boolean values. S3 deployments can set `AWS_S3_URL_PROTOCOL`, and the token
generator class is configurable. Django Debug Toolbar and
`ENABLE_DEBUG_TOOLBAR` are unsupported.

## Removed payment gateways and legacy digital-content API (3.23.0)

The Adyen and NP Atobarai gateway plugins are removed in favor of their apps.
The Adyen-specific `Payment.partial` field is removed. The undocumented legacy
digital-content API is removed, although supported digital-product flows
remain available.

## EditorJS validation and links (3.23.0)

The EditorJS parser rejects unknown or extra fields. Rendered links default to
`rel="noopener noreferrer"`. `UNSAFE_EDITOR_JS_ALLOWED_URL_SCHEMES` can no
longer extend accepted URL schemes. Deployments relying on permissive rich
text payloads or custom schemes must clean up that content before upgrading.

## Removed configuration and management hooks (3.23.0)

`JWT_EXPIRE` can no longer disable JWT expiration. `manage.py
createsuperuser` no longer supports custom `User` database models. Deployment
configuration and account-provisioning automation must remove those
assumptions.

## More legacy payment gateway plugins removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The built-in Authorize.Net, Razorpay, Braintree, Dummy, and Dummy Credit Card
plugins (`mirumee.payments.authorize_net`, `.razorpay`, `.braintree`, `.dummy`,
and `.dummy_credit_card`) are removed. Deployments using them must migrate
before upgrading.

## Shop and order configuration surfaces removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`shopDomainUpdate` is replaced by the `PUBLIC_URL` environment variable.
Order settings move from `orderSettingsUpdate` and the `orderSettings` query
to `channelUpdate(orderSettings: ...)` and `channel.orderSettings`.

The no-op `shopFetchTaxRates` mutation and `ShopFetchTaxRates` type are
removed. Tax configuration should use mutations such as
`taxConfigurationUpdate`.

## Gift-card and voucher exports and webhooks removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`exportGiftCards`, `exportVoucherCodes`, and their input/output types are
removed. Callers must fetch `giftCards` or `voucher` data and format it.
Completion webhook and subscription types for those exports are removed.
Migration deletes existing subscriptions to those events, leaving a webhook
with no other events inactive.

## Remaining legacy digital-content surfaces removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The `DIGITAL_LINKS` order-email event, `DIGITAL_LINK_DOWNLOADED` customer
event, and always-empty fulfillment-notification `digital_lines` key are
removed. Use `physical_lines` for every fulfillment line. GraphQL product-type
`isDigital` fields, inputs, filters, and sorting are removed, as is the ORM
field `ProductType.is_digital`.

## Digital-content database cleanup

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The legacy `product_digitalcontent` and `product_digitalcontenturl` tables and
related site-settings columns are dropped, but uploaded files are not deleted
from media storage. Operators may manually remove the `digital_contents/`
directory. The remaining `ProductType.is_digital` database column is
scheduled for removal in 3.25.
