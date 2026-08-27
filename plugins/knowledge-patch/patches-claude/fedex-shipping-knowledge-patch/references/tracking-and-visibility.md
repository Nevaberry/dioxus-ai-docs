# Tracking and visibility

## Account-scoped tracking webhooks

The Tracking Account Number Webhook API pushes near-real-time events for
every shipment associated with a subscribed account. Its account scope
includes:

- Inbound shipments.
- Outbound shipments.
- Third-party-billed shipments.

A subscription can send the full tracking history or only the current event.
It can also push changes to the estimated delivery date or estimated delivery
time window.

## Basic Integrated Visibility limits

Basic Integrated Visibility, formerly the Track API, is pull-based. It is
limited to 100,000 calls per day.

## Basic Integrated Visibility response fields

In `scanEvents.eventType`:

- `AE` reports early.
- `AO` reports on-time.

`deliveryOptionEligibilityDetails.option` can include:

- `DISPUTE_DELIVERY`.
- `RETURN_TO_SHIPPER`.
- `SUPPLEMENT_ADDRESS`.

The estimated delivery time window is returned at:

- `estimatedDeliveryTimeWindow.window.begins` for the beginning.
- `estimatedDeliveryTimeWindow.window.ends` for the end.

## Date-only webhook timestamps

Advanced Integrated Visibility events without a time component use
`00:00:00+00:00`. Consumers should interpret that value as UTC midnight
rather than local time.
