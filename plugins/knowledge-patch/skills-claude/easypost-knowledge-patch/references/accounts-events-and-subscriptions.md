# Accounts, events, sessions, and subscriptions

## Carrier-account lifecycle

Carrier-account APIs cover registration, available platform-account types and
configuration, and team-authorized status updates. Platform account
availability endpoints expose access and setup options.

BYOCA support extends to all users. Most carrier accounts no longer require a
separate manual registration step.

## Group management

Group management supports creating, viewing, listing, and deleting subgroups,
as well as assigning sub-accounts to them. Sub-account list responses can
include group information.

## Webhook events

The `shipment.invoice.updated` event reports billed-shipment disputes.

The `payment.created` and `payment.failed` events are again emitted for bank
and credit-card charges.

## JWT sessions and invitation redirects

Embeddable components and customer portals can create JWT-authenticated
sessions.

SAML invitation flows accept `return_to_url`. After an invitation is
successfully accepted, this can return users to an application-selected
location.

## Subscription controls

The API can cancel Advanced Tracking subscriptions and synchronize Advanced
Tracking brand customization.

Subscription plans can be charged immediately when they are created.
