# Benefits, events, and meters

## Feature Flag benefits

The Feature Flag benefit exposes entitlement state through the API and
webhooks. Its JSON metadata is hidden from customers.

## Benefit revocation

Canceling a subscription automatically revokes its benefits.

After a failed payment, benefit revocation can happen immediately or after the
payment-retry grace window.

## License keys

License-key list operations can filter keys by status. Activation rejects a
license key after its `expires_at` value.

## Event hierarchy and idempotency

Events accept `parent_id` to create hierarchies. Use `external_id` as an
idempotency key.

## Event types and metadata

Event names create event types. Event types support display names and a
statistics endpoint. Events can include cost metadata.

Built-in events cover:

- paid and refunded orders;
- customer creation and updates; and
- subscription cycling, cancellation, and past-due transitions.

## Meter units

A meter can define a unit label and a value multiplier. This allows raw tokens,
requests, or bytes to be priced in larger units.

## Meter time zones and archival

Meter quantity queries accept `timezone` for grouping outside UTC.

A meter cannot be archived while it is attached to an active product or
referenced by an active benefit.

## Webhook delivery

Webhook payloads include a Standard Webhooks timestamp.

By default, Polar automatically disables a webhook endpoint after 10
consecutive failures and notifies organization members. After the receiver is
fixed, the endpoint must be manually re-enabled.
