# Paddle.js and Client-Side Flows

## Updating an open checkout

Paddle.js can update items, discounts, customer information, and custom data on
an already-open checkout.

## Checkout error handling

Checkout events distinguish invalid or missing input from payment errors such
as having no valid payment method. This enables separate frontend fallback
handling.

## Client-side tokens

Paddle.js authenticates with client-side tokens instead of seller IDs. Paddle
Retain can use the same token instead of a separate Retain API key.

Client-side tokens can be created and managed through API operations with
corresponding webhooks.

## Price and transaction previews

Price previews return localized, formatted prices with tax and discount
calculations. Paddle.js can preview complete transaction totals without a
server call.

## Payment-method control

Preview responses can report valid payment methods. Checkout can be restricted
to a selected set.
