# API, Authentication, and Search

## Account registration and recovery conceal state

Since 3.21.0, `accountRegister` no longer returns the user's `ID`.
`accountRegister`, `confirmAccount`, `requestPasswordReset`, and `setPassword`
no longer reveal whether an email is registered. For non-staff users,
`requestPasswordReset` also no longer fails merely because `channel` was
omitted.

## Order metadata updates require order permission

Since 3.21.0, updating metadata on `Order` or `OrderLine` requires
`MANAGE_ORDERS`.

## Order, customer, and Page filters move to `where` and `search`

Since 3.22.0, `where` and `search` replace deprecated `filter` arguments.
Orders and draft orders add filters for vouchers, invoices, fulfillment,
payment methods, totals, product types, and addresses, plus relevance-ranked
search and status sorting. Customers add filters and search across customer and
address-book data, and Pages move their existing filters to the new system.
Dashboard supports the order filters, but not yet the new draft-order or
customer filters.

## Password authentication supports restricted modes

Since 3.23.0, `PasswordLoginMode.DISABLED` makes `tokenCreate`, `setPassword`,
`passwordChange`, `requestPasswordReset`, and `tokenRefresh` return errors.
`CUSTOMERS_ONLY` strips staff permissions from staff users who authenticate by
password. Google OIDC refresh tokens require `access_type=offline`, and the
first OIDC claim of an existing user invalidates that user's old password.

## GraphQL nullability and input contracts tighten

Since 3.23.0, `RefundSettingsUpdate.refundSettings` is nullable on errors;
`Attribute.name`, `Attribute.slug`, and `Attribute.type` are non-null;
federation `_entities` requires `representations: [_Any!]!`; and
`AppInstallInput.appName` and `AppInstallInput.manifestUrl` are schema-required.
The new `NonNegativeInt` scalar underlies `Minute`, `Hour`, and `Day`, so
negative time values fail GraphQL validation instead of producing mutation
error code `INVALID`.

## Search uses a shared grammar and relevance ranking

Since 3.23.0, search across products, orders, gift cards, checkouts, pages, and
users supports prefix matching, `AND`/`OR`/`-` Boolean operators, quoted exact
phrases, accent-insensitive matching, and default relevance ordering. Search
filters can explicitly request relevance ordering through the `RANK` sort
field.

## Apps cannot receive `MANAGE_APPS`

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

App installation is rejected when it requests `MANAGE_APPS`, even though an
app with that permission previously could not act as an admin app. Audit
installed apps and remove the permission before upgrading.

## Reconfirming an account fails

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`confirmAccount` no longer allows an already-confirmed account to be confirmed
again. Callers must not depend on repeated confirmation succeeding.

## Attribute mutation permissions depend on attribute type

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Attribute value and bulk mutations require
`MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES`, `MANAGE_PAGE_TYPES_AND_ATTRIBUTES`, or
`MANAGE_CUSTOMER_TYPES_AND_ATTRIBUTES` for the corresponding attribute type. A
bulk request spanning types requires every matching permission.
`MANAGE_PRODUCTS` no longer permits `attributeValueCreate`, and bulk create or
update rejects an unmapped attribute type instead of falling back to the
page-type permission.

## App permission inputs distinguish omission from clearing

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

For `appCreate`, a missing or null `permissions` value creates an app without
permissions. For `appUpdate`, missing or null preserves existing permissions,
while an empty list clears them.
