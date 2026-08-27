# Customers and subscriptions

## External customer IDs

Customers have an `external_id` with dedicated get, update, and delete
operations. Customer lists can be filtered by external ID.

When a checkout supplies `external_customer_id`, that value is copied to the
customer created after payment.

## Customer State

Customer State returns active subscriptions and granted benefits in one API
call or webhook. It correctly represents trialing subscriptions.

## Creating and mutating subscriptions

Create a subscription through the API without using Checkout.

For an existing subscription, Polar supports these changes:

- move from an archived price to the current price of the same product with
  proration;
- add, change, or remove its discount; and
- change its current billing-period end unless it is already canceled.

## Scheduled updates

Set the `next_period` proration behavior for a product, price, or seat change
that should take effect in the next period. The pending update is returned on
subscription objects and webhooks.

## Pause and resume

Pausing a subscription takes effect at the end of its period. It stops billing
and revokes benefits, but does not delete the subscription or payment method.

Resuming starts a new period and charges immediately. An automatic resume date
is optional.

Pause and resume transitions emit:

- `subscription.paused`
- `subscription.resumed`

## Members

The paginated `GET /v1/members` endpoint supports filtering by customer. Polar
automatically creates an owner member.

Available roles are:

- `owner`
- `billing_manager`
- `member`

Transferring ownership demotes the former owner to billing manager.

Member-session tokens use the `polar_mst_` prefix. Benefits can be scoped to a
member, and events accept `member_id` or `external_member_id`.

## Seat assignment and proration

Seats can be assigned through the API. Customer seat changes are automatically
prorated.
