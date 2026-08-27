# Subscriptions, Members, and Benefits

## Subscription creation

Subscriptions can be created through the API without Checkout.

## Existing subscription mutation

An existing subscription can move from an archived price to the current price
of the same product with proration.

Its discount can be added, changed, or removed. Its current billing-period end
can be changed unless the subscription is already canceled.

## Scheduled product, price, and seat changes

Product, price, and seat changes can use the `next_period` proration behavior.
The pending update is returned on subscription objects and webhooks.

## Pause and resume

Pausing takes effect at period end. It stops billing and revokes benefits
without deleting the subscription or payment method.

Resuming starts a new period and charges immediately. An automatic resume date
is optional.

The transitions emit `subscription.paused` and `subscription.resumed`.

## B2B member listing and roles

The paginated `GET /v1/members` endpoint supports customer filtering. Polar
automatically creates an owner member.

Roles are:

- `owner`.
- `billing_manager`.
- `member`.

Ownership transfer demotes the former owner to billing manager.

## Member sessions, benefits, and events

Member sessions use the `polar_mst_` prefix. Benefits can be member-specific.
Events accept `member_id` or `external_member_id`.

## Seat assignment and proration

Seats can be assigned by API. Customer seat changes are automatically
prorated.

## Feature Flag benefits

The Feature Flag benefit exposes entitlement state through the API and
webhooks while hiding its JSON metadata from customers.

## Benefit revocation

Cancellation automatically revokes subscription benefits.

Failed-payment revocation can be immediate or follow the payment-retry grace
window.

## License keys

License-key lists can filter by status. Activation rejects keys past
`expires_at`.
