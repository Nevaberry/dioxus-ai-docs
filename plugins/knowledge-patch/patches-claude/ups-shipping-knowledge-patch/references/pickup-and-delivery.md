# Pickup and Delivery

## Smart Pickup surfaces

The Smart Pickup API can trigger Smart Pickups independently of a merchant's
platform integration.

The embeddable Smart Pickup Widget owns authentication, scheduling logic, and
UPS API communication.

The separate Pickup Notification Preferences API manages notification settings
at account level.

## Lab Logistics pickup points

UPS Lab Logistics Pickup Points lets clinics and laboratories schedule daily
or date-specific Smart Pickups through a centralized API.

## Delivery controls

### Protected Delivery Token

Protected Delivery Token lets a shipper require a PIN before package release.
It tokenizes the shipper-generated PIN rather than exposing it directly.

### Delivery Intercept eligibility

Delivery Intercept supports automated intercept requests. Its eligibility
endpoint lets an application determine which intercept type is valid before
submitting a request.

The API can be added through the standard application add/edit flow.
