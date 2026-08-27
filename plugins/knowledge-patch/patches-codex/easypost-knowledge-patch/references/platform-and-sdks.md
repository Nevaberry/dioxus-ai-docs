# Platform APIs and SDKs

## Node.js SDK compatibility

The Node.js SDK now uses `fetch` instead of `superagent`, drops Node 16
support, renames `superagentMiddleware` to `httpMiddleware`, renames
`fetchClient` to `httpClient`, and returns API resources as plain
JSON-compatible objects instead of model-class instances.

## Generic requests

The C#, Java, Node.js, PHP, and Ruby SDKs expose a generic request interface
for arbitrary API endpoints, including endpoints that do not yet have typed
resource wrappers.

## Webhook events

The `shipment.invoice.updated` event reports billed-shipment disputes.
`payment.created` and `payment.failed` are again emitted for bank and
credit-card charges.

## Index endpoint throttling

Index endpoints have request-per-second rate limiting. Integrations that
enumerate resources must tolerate throttling instead of assuming unrestricted
pagination.

## Carrier-account lifecycle

Carrier-account APIs cover registration, available platform-account types and
configuration, and team-authorized status updates. Platform account
availability endpoints expose access and setup options.

BYOCA support extends to all users. Most carrier accounts no longer require a
separate manual registration step.

## Group management

Group management supports creating, viewing, listing, and deleting subgroups,
and assigning sub-accounts to them. Sub-account list responses can include
group information.

## JWT sessions and invitation redirects

Embeddable components and customer portals can create JWT-authenticated
sessions. SAML invitation flows accept `return_to_url`, allowing successful
invitation acceptance to return users to an application-selected location.

## Subscription controls

The API can cancel Advanced Tracking subscriptions and synchronize Advanced
Tracking brand customization. Subscription plans can be charged immediately
when created.
