# Security, buttons, and direct integration

Use this reference for CSP nonces, supported button borders, and ECv2 keys in
direct integrations.

## CSP nonces for injected elements

`PaymentOptions` accepts a `nonce`.

```js
const paymentOptions = {
  nonce: cspNonce,
};
```

When the nonce is provided, it is applied to every dynamically injected
`<style>` and `<script>` element.

## Supported button border configuration

`ButtonOptions` passed to `createButton()` accepts `borderButtonType`. This
exposes border selection through the supported button configuration.

No `borderButtonType` values are specified here.

## ECv2 direct-integration keys

For `DIRECT` integrations, ECv2 permits a static, long-lived Google signing
key. The key only needs updating every ten years.

## Implementation checklist

- Put the CSP nonce in `PaymentOptions.nonce`.
- Account for the nonce on every dynamically injected `<style>` and `<script>`
  element.
- Pass `borderButtonType` through the `ButtonOptions` supplied to
  `createButton()`.
- Do not invent border values that are not documented here.
- For a `DIRECT` integration using ECv2, preserve the documented ten-year
  signing-key update interval.
