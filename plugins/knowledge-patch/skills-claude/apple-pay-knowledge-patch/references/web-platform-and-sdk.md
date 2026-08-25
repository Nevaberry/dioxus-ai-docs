# Web Platform and SDK

## Web API platform boundaries

### Outside China

Apple Pay JS supports:

- iOS 10 or later.
- macOS 10.12 or later.

Payment Request supports:

- iOS 11.3 or later.
- macOS 10.12.6 or later with Safari 11.1 or later.

### China

Apple Pay JS requires iOS 11.2 or later.

Payment Request requires iOS 11.3 or later.

Neither API is available on macOS in China.

On iOS in China, both Safari and `SFSafariViewController` support Apple Pay.

## Apple Pay JS SDK delivery

Sites can load either the latest autoupdating Apple Pay JS SDK or a chosen
version.

## Apple Pay button behavior

`ApplePayButton` can start a payment or prompt the customer to set up a card.

## Sandbox environment behavior

Apple Pay JS 1.3.5 added sandbox environment configuration.

In sandbox mode:

- The UI shows a “Sandbox Mode” banner.
- The console reports the environment.
- `applePayCapabilities` returns `paymentCredentialStatusUnknown` in supported
  browsers.

Do not treat `paymentCredentialStatusUnknown` as proof that Apple Pay is
unavailable.

## Pinned 1.3.8 asset

The versioned 1.3.8 SDK has a published CDN URL and Subresource Integrity hash.
To pin that release with SRI, load it as follows:

```html
<script src="https://applepay.cdn-apple.com/jsapi/v1.3.8/apple-pay-sdk.js"
        integrity="sha384-u/9mOkmShCO0v+dqCAZFhiutJuORfzvuyM5i+676iy7mLSWS6rlllHrIt15f/mqH"
        crossorigin="anonymous"></script>
```
