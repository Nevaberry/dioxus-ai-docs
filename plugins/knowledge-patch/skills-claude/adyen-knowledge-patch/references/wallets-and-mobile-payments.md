# Wallets and Mobile Payments

Source batches: `adyen-web-releases-current`,
`adyen-web-releases-history`.

## UPI Collect removal

From v6.30.0, UPI Collect is no longer supported. The default UPI flow is QR
code on desktop and Intent on mobile.

## Required UPI mandate end time

From v6.34.1, the UPI Autopay mandate type requires `endsAt`. TypeScript
integrations must provide it rather than treating it as optional.

## Apple Pay browser and configuration support

Version 6.10.0 adds support for third-party browsers.

Version 6.13.0 accepts `shippingContactEditingMode` to prevent address editing
for store pickup.

Version 6.23.0 accepts `domainName` to identify the domain performing merchant
validation when the component is embedded in an iframe.

## Apple Pay coupon codes

From v6.33.0, Apple Pay supports coupon codes. Coupon-enabled Apple Pay flows
no longer need to treat the capability as unsupported by the web SDK.

## Google Pay issuer-country filters

From v6.32.0, Google Pay accepts `allowedIssuerCountryCodes` and
`blockedIssuerCountryCodes` component properties for filtering cards by
issuer country.

## Google Pay environment fallback

From v6.32.0, an unrecognized Google Pay environment string falls back to
`PRODUCTION`, not `TEST`. Validate configuration values explicitly to avoid
unintentionally initializing the production environment.

## Google Pay merchant validation

From v6.10.0, Google Pay throws an error when the merchant ID is missing, so
integrations must provide it explicitly.
