# Orders and API Reference

## Billing data

### Usage-pattern migration

`charge_pattern` is deprecated in favor of `usage_pattern`. Orders accepts
`usage_pattern` in billing requests and returns it in billing responses.

### Stored credentials

Orders responses include `stored_credentials`.

### Billing-agreement descriptions

The billing-agreement `description` field supports up to 255 characters.

## Payment-source requests and responses

### Apple Pay and Google Pay experience context

Orders supports experience context for Apple Pay and Google Pay payment
sources.

### Server-side shipping callback

Orders supports a server-side shipping callback.

### Trustly email address

Trustly payment sources require `email_address`.

### Card risk attributes

Card payment sources support risk-related attributes.

### PUI buyer-specific ID

PUI payment-source requests accept a buyer-specific ID.

### PayPal Wallet business name

PayPal Wallet responses include `business_name`.

### Card merchant customer ID

The card object includes `merchant_customer_id`.

## Items and networks

### Item description length

The Orders item `description` field supports up to 2,048 characters.

### EFTPOS network

The Orders network enum includes EFTPOS.

## Order actions

### Content type

The Confirm, Capture, and Authorize endpoints include a `Content-Type` header.
