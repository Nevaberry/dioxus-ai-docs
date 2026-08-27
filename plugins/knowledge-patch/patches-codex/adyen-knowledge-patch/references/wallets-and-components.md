# Wallets and components

Use this reference for Apple Pay, Google Pay, Affirm, Giving, and Riverty. Items
come from `adyen-web-releases-current` and `adyen-web-releases-history`.

## Apple Pay

### Browser support (since v6.10.0)

Apple Pay supports third-party browsers.

### Store-pickup address editing (since v6.13.0)

Apple Pay accepts `shippingContactEditingMode` to prevent address editing for
store pickup.

### Iframe merchant-validation domain (since v6.23.0)

Apple Pay accepts `domainName` to identify the domain performing merchant
validation when the component is embedded in an iframe.

### Coupon codes (since v6.33.0)

Apple Pay supports coupon codes, so coupon-enabled Apple Pay flows no longer
require treating the capability as unsupported by the Web SDK.

## Google Pay

### Merchant ID validation (since v6.10.0)

Google Pay throws an error when the merchant ID is missing, so integrations
must provide it explicitly.

### Issuer-country filters (since v6.32.0)

Google Pay accepts `allowedIssuerCountryCodes` and
`blockedIssuerCountryCodes` component properties for filtering cards by issuer
country.

### Environment fallback (since v6.32.0)

An unrecognized Google Pay environment string falls back to `PRODUCTION`, not
`TEST`. Validate configuration values explicitly to avoid unintentionally
initializing the production environment.

## Affirm countries (since v6.40.0)

Affirm components accept `allowedCountries`. The supported country codes are
`CA`, `US`, and `GB`.

```js
{ allowedCountries: ["CA", "US", "GB"] }
```

## Riverty redirect flow (since v6.14.0)

Riverty is implemented as a Redirect component.
