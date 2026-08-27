# Orders, Commissions, and Returns

## Multi-vendor carts and orders (0.9.0)

Mercur supports multi-vendor cart completion and order processing, including
promotions during cart splitting. Sellers can work with their orders from the
Vendor panel. Some multi-vendor order edge cases remained under testing in
this release.

## Order format and supported countries (1.0.0)

The order format changed in 1.0. Integrations that consume order data should
not assume the 0.9 representation remains compatible.

The set of supported countries also changed. Revalidate country-dependent
marketplace configuration during an upgrade.

## Order-set operations (1.0.0)

Order sets are listable, include statuses, and can be filtered by an order ID.
Operators can directly find and inspect the marketplace grouping associated
with an individual order.

## Cart shipping selection and completion (1.0.0)

A selected shipping method can be removed from a cart, allowing delivery
selection to be cleared before checkout.

Creating shipping marks the order as completed. Code reacting to order status
should account for that automatic transition.

## Commissions, tax, and payout integration (0.9.0)

Marketplace commissions are built in. A zero-percent commission is valid, and
commission is included in order payouts.

Stripe Connect provides payout integration, and Stripe Tax is supported. Some
currency-specific commission cases still needed testing in this release.

## Commission administration and payout reversals (1.0.0)

Commissions have a dedicated API and Admin dashboard, exposing their
management separately from their application to payouts.

Payout-reversal creation is available, providing a compensating operation for
an already-created payout.

## Pluggable marketplace payouts (2.0.0)

`@mercurjs/payout-stripe-connect` is the bundled Stripe Connect provider
rather than a fixed payment implementation. It covers:

- seller account creation and onboarding;
- automatic order-to-payout processing;
- payout webhooks;
- KYC/KYB data; and
- idempotent processing.

It can be replaced with another payout provider.

## Vendor fulfillment and returns (0.9.0 and 1.0.0)

Vendors can manage fulfillments and returns, while the order flow supports
return requests. These are marketplace-layer capabilities added on top of
Medusa rather than Medusa core behavior.

Return flows provide seller-specific return shipping options, preserving
seller boundaries when return delivery is selected.

## Review and return-request constraints (1.0.0)

Mercur enforces one review per order and prevents duplicate return requests
for an order. Both customer actions are single-instance operations.
