# Events, Meters, and Metrics

## Event hierarchy and idempotency

Events accept `parent_id` for hierarchies and `external_id` as an idempotency
key.

## Event types and statistics

Event types are created from event names. They support display names and a
statistics endpoint. Events can carry cost metadata.

Built-in events cover:

- Paid and refunded orders.
- Customer creation and updates.
- Subscription cycling, cancellation, and past-due transitions.

## Meter units

Meters can define a unit label and value multiplier so raw tokens, requests,
or bytes can be priced in larger units.

## Meter quantity time zones

Meter quantity queries accept `timezone` for non-UTC grouping.

## Meter archive restrictions

A meter cannot be archived while attached to an active product or referenced
by an active benefit.

## Metrics selection

The Metrics API selects requested values with the `metrics` query parameter.
The deprecated `focus_metrics` parameter has been removed.

## Included order states

Metrics calculations exclude pending and unpaid orders. They include only paid
and refunded orders.
