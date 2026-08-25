# Events, Destinations, and API Releases

## API release selection (`api-release-lifecycle`)

Stripe API versions ship as twice-yearly, plant-named major releases that may
include breaking changes. Monthly releases retain the latest major's name and
add only backward-compatible features.

Every API release has directly associated SDK releases for all supported
languages, while SDK packages retain semantic versioning. Track both the SDK
version and its mapped API release during upgrades.

`2025-09-30.clover` is the first Clover release and contains breaking changes;
later Clover releases are additive. Treat that release as the migration
boundary rather than assuming every Clover-dated upgrade is backward-compatible.

## Snapshot and thin event contracts (`event-destinations`)

Snapshot events can originate from API v1 or v2. They carry an eventually
consistent object snapshot and `previous_attributes` and remain tied to the API
version configured on the destination.

Thin notifications carry event and related-object identifiers. Retrieve the
latest related object for current state, or retrieve the complete v2 Event when
`data` context or `changes` are needed.

Thin events for API v1 resources are available in private preview. This extends
a format that previously supported only API v2 resources and lets preview
integrations adopt unversioned typed notifications without replacing webhook
configuration during upgrades.

API v2 supports thin-event retrieval (`2024-09-30.acacia`). Retrieve the event
resource when the delivered thin payload alone is insufficient.

## Typed thin-event processing (`event-destinations`)

SDKs type the initial notification as `{EventType}EventNotification` and the
complete result from `fetchEvent()` as `{EventType}Event`. Parse and verify the
notification with the endpoint secret. Call `fetchRelatedObject()` for current
resource state or `fetchEvent()` for event-specific context and previous values.

```java
com.stripe.model.v2.core.EventNotification notification =
    client.parseEventNotification(payload, signatureHeader, endpointSecret);
if (notification instanceof V1BillingMeterErrorReportTriggeredEventNotification) {
  V1BillingMeterErrorReportTriggeredEventNotification typed =
      (V1BillingMeterErrorReportTriggeredEventNotification) notification;
  Meter latestMeter = typed.fetchRelatedObject();
  com.stripe.model.v2.core.Event completeEvent = typed.fetchEvent();
}
```

## Permissions and retention (`event-destinations`)

Workbench event viewing requires the Admin or Developer role. API retrieval
works with a secret key or with a restricted key granted `Read` access to the
event type's underlying resource—for example, PaymentIntent read access for
`payment_intent.succeeded`. It does not use a generic event-read grant.

Workbench exposes events for 13 months:

- Events less than 15 days old retain full payloads, delivery attempts, and
  manual resend.
- Events 16–30 days old retain full payloads without attempts or resend.
- Older events retain only a truncated summary.

The Retrieve Event and List Events APIs expose full payloads only for the past
30 days.

## Destination limits (`event-destinations`)

Each livemode or sandbox account can register at most 16 event destinations.
For snapshot destinations whose API version differs from the merchant default,
only three uniquely versioned destinations can be registered.
