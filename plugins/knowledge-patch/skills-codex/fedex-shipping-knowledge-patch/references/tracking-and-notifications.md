# Tracking and Notifications

## Account-scoped tracking webhooks

The Tracking Account Number Webhook API pushes near-real-time events for every
shipment associated with a subscribed account. Its scope includes inbound,
outbound, and third-party-billed shipments.

A subscription can send:

- The full tracking history.
- Only the current event.

It can also push changes to the estimated delivery date or time window.

## Basic Integrated Visibility

Basic Integrated Visibility, formerly the Track API, is pull-based and limited
to 100,000 calls per day.

Current response fields include:

- `scanEvents.eventType`: `AE` for early or `AO` for on-time.
- `deliveryOptionEligibilityDetails.option`: `DISPUTE_DELIVERY`,
  `RETURN_TO_SHIPPER`, or `SUPPLEMENT_ADDRESS`.
- Estimated-window start:
  `estimatedDeliveryTimeWindow.window.begins`.
- Estimated-window end:
  `estimatedDeliveryTimeWindow.window.ends`.

## Date-only webhook timestamps

Advanced Integrated Visibility events without a time component use
`00:00:00+00:00`. Consumers should interpret that value as UTC midnight rather
than local time.

## Shipment email notifications

Ship can send exception and delivery notifications to the recipient and as many
as six additional email addresses.

## Pickup email notifications

Pickup notifications cover:

- Create or modify confirmation.
- Day-before reminders.
- Morning-of reminders.
- Successful pickup.
- Unsuccessful pickup.

`pickupNotificationDetail\emailDetails\locale` rejects invalid locale values.
