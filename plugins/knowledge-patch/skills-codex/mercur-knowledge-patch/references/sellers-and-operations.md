# Sellers and marketplace operations

## Seller onboarding and team access (0.9.0)

Sellers can register and onboard, then organize team members through invitations and
role-based access. Mercur also provides extended seller information, team-member email
handling, and vendor file uploads.

## Seller lifecycle administration (1.0.0)

Mercur provides a seller-management API, platform-level seller invitations, and
seller-suspension logic. These allow operators to administer sellers beyond each
seller's onboarding and team-management flows.

When a seller has no email address, Mercur uses the member email instead, preserving
a recipient for email-dependent seller flows.

## Multi-vendor carts and orders (0.9.0)

Mercur supports multi-vendor cart completion and order processing, including
promotions during cart splitting. Sellers can work with their orders from the Vendor
panel. Some multi-vendor order edge cases remained a known limitation in this
release.

## Order sets and format (1.0.0)

Order sets are listable, include statuses, and can be filtered by an order ID. This
allows an operator to find and inspect the marketplace grouping associated with an
individual order.

The order format changed in 1.0. Integrations that consume order data should not
assume the 0.9 representation remains compatible.

The supported-country set also changed. Revalidate country-dependent marketplace
configuration during an upgrade.

## Shipping, fulfillment, and returns (0.9.0, 1.0.0)

Vendors can manage fulfillments and returns, and the marketplace order flow supports
return requests. These marketplace-layer capabilities are added on top of Medusa,
rather than being Medusa core behavior.

A selected shipping method can be removed from a cart, allowing delivery selection to
be cleared before checkout. Return flows provide seller-specific return shipping
options. Creating shipping marks an order as completed, so order-status consumers
must account for the automatic transition.

Mercur prevents duplicate return requests for an order.

## Commissions and payout operations (0.9.0, 1.0.0)

Marketplace commissions are built in. A zero-percent commission is valid, and
commission is included in order payouts. Stripe Connect provides the payout
integration and Stripe Tax is supported, although some currency-specific commission
cases still needed testing in 0.9.0.

Commissions have a dedicated API and Admin dashboard. Payout-reversal creation covers
the compensating operation for an already-created payout.

## Pluggable payout provider (2.0.0)

`@mercurjs/payout-stripe-connect` is the bundled Stripe Connect provider rather than
a fixed payment implementation. It covers:

- seller account creation and onboarding;
- automatic order-to-payout processing;
- payout webhooks;
- KYC/KYB data;
- idempotent processing.

It can be replaced with another payout provider.

## Seeded configuration rules (1.0.0)

Mercur's seed process creates default configuration rules, so a seeded environment
starts with the marketplace's baseline rule configuration.
