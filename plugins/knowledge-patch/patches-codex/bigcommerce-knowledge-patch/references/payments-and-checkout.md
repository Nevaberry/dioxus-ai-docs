# Payments and checkout

## Payment-method and shipment fields

`Site.paymentMethods` is a new connection of payment methods enabled for the
store and channel. Its `PaymentMethod` nodes expose `entityId` and `name`.

`OrderShipment.shippingProviderDisplayName` provides a human-readable
shipping-provider label.

Both fields are alpha, deprecated, and not for production.

## Delete a stored payment instrument

Authenticated customers can use the alpha
`CustomerMutations.deleteStoredPaymentInstrument` mutation. Pass the
instrument token as `DeleteStoredPaymentInstrumentInput.token`.

The result exposes typed `errors`; an empty list indicates success.

The schema marks the mutation deprecated because it is not production-ready.

## Update a stored payment instrument

The alpha `CustomerMutations.updateStoredPaymentInstrument` mutation accepts
a token and optional `billingAddress` and `setAsDefault` values.

`setAsDefault` can promote an instrument, but it cannot unset the existing
default.

The result includes the updated instrument, the resulting default token, and
typed errors. The mutation is not intended for production use.

## Diagnose Catalyst session sync

Checkout session sync can fail with `Invalid JWT token` or `404` under any of
these conditions:

- checkout routes use the edge runtime;
- login-token routes use the edge runtime;
- `BIGCOMMERCE_STOREFRONT_TOKEN` contains an OAuth token;
- the channel and custom domain do not match;
- the domain is not primary;
- the domain is not fully propagated and verified;
- the redirect exceeds the JWT's 30-second lifetime.

Inspect the JWT's `channel_id`, `redirect_to`, and `eat` claims when diagnosing
configuration mismatches.
