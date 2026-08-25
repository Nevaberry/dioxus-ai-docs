# Accounts and permissions

## Registration-state privacy (3.21.0)

`accountRegister` no longer returns the user's `ID`. `accountRegister`,
`confirmAccount`, `requestPasswordReset`, and `setPassword` no longer reveal
whether an email is registered. For non-staff users, `requestPasswordReset`
does not fail merely because `channel` was omitted.

## JWKS signing algorithm (3.21.0)

Keys returned by `/.well-known/jwks.json` include the JWK `alg` member, so
consumers can identify the intended signing algorithm from the key.

## Password authentication modes (3.23.0)

`PasswordLoginMode.DISABLED` makes `tokenCreate`, `setPassword`,
`passwordChange`, `requestPasswordReset`, and `tokenRefresh` return errors.
`CUSTOMERS_ONLY` strips staff permissions from staff users authenticating by
password.

Google OIDC refresh tokens require `access_type=offline`. The first OIDC claim
of an existing user invalidates that user's old password.

## Staff deletion with order history (3.23.0)

`staffDelete` always deletes the staff user, including when the account has
orders. It no longer merely clears `is_staff` for such accounts. Callers that
relied on order history to preserve a user must add their own safeguard.

## Apps cannot receive `MANAGE_APPS`

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

App installation is rejected when it requests `MANAGE_APPS`, even though an
app with that permission previously could not act as an admin app. Audit
installed apps and remove the permission before upgrading.

## Reconfirming an account is rejected

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`confirmAccount` rejects an already-confirmed account. Callers must not depend
on repeated confirmation succeeding.

## Attribute mutation permissions

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Attribute value and bulk mutations require
`MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES`, `MANAGE_PAGE_TYPES_AND_ATTRIBUTES`, or
`MANAGE_CUSTOMER_TYPES_AND_ATTRIBUTES` for the corresponding attribute type.
A bulk request spanning types requires every matching permission.

`MANAGE_PRODUCTS` no longer permits `attributeValueCreate`. Bulk create or
update rejects an unmapped attribute type rather than falling back to the
page-type permission.

## App permission input semantics

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

For `appCreate`, missing or `null` `permissions` creates an app without
permissions. For `appUpdate`, missing or `null` preserves existing
permissions, while an empty list clears them.
