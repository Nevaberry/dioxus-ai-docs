# Orders and Payment Sources

## Billing usage pattern

`charge_pattern` is deprecated in favor of `usage_pattern`. Orders accepts
`usage_pattern` in billing requests and returns it in billing responses.

## Wallet experience context

Orders supports experience context for Apple Pay and Google Pay payment
sources.

## Server-side shipping callback

Orders supports a server-side shipping callback.

## Trustly email address

Trustly payment sources require `email_address`.

## Stored credentials

Orders responses include `stored_credentials`.

## Item description length

The Orders item `description` field supports up to 2,048 characters.

## Card risk attributes

Card payment sources support risk-related attributes.

## PUI buyer-specific ID

PUI payment-source requests accept a buyer-specific ID.

## EFTPOS network

The Orders network enum includes EFTPOS.

## Wallet business name

PayPal Wallet responses include `business_name`.

## Card merchant customer ID

The card object includes `merchant_customer_id`.

## Content type on order actions

The Confirm, Capture, and Authorize endpoints include a `Content-Type` header.

## Billing-agreement description length

The billing-agreement `description` field supports up to 255 characters.
