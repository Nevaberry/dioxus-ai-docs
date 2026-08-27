# Web Configuration and Testing

## CSP nonces for injected elements

`PaymentOptions` accepts a `nonce`. When provided, that CSP nonce is applied
to every dynamically injected `<style>` and `<script>` element.

```js
const paymentOptions = {
  nonce: cspNonce,
};
```

## Supported button border configuration

`ButtonOptions` passed to `createButton()` accepts `borderButtonType`, exposing
border selection through the supported button configuration.

## Multi-market gateway test cards

Gateway test cards in the `TEST` environment support billing addresses from
27 markets rather than only the US. This enables country-specific end-to-end
billing tests.

Examples include:

- UK
- France
- Germany
- Spain
- Japan
- Hong Kong
- Brazil
