# Apple Pay JS SDK

## Sandbox environment behavior

Apple Pay JS 1.3.5 added sandbox environment configuration.

In sandbox mode:

- The UI shows a “Sandbox Mode” banner.
- The console reports the environment.
- `applePayCapabilities` returns
  `paymentCredentialStatusUnknown` in supported browsers.

The `paymentCredentialStatusUnknown` status must not be treated as proof that
Apple Pay is unavailable.

## Pinned Apple Pay JS 1.3.8 asset

The versioned 1.3.8 SDK has a published CDN URL and Subresource Integrity hash.
To pin that release with SRI, load it as follows:

```html
<script src="https://applepay.cdn-apple.com/jsapi/v1.3.8/apple-pay-sdk.js"
        integrity="sha384-u/9mOkmShCO0v+dqCAZFhiutJuORfzvuyM5i+676iy7mLSWS6rlllHrIt15f/mqH"
        crossorigin="anonymous"></script>
```
