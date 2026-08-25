# Events, Destinations, and API Releases

## API release lifecycle

Stripe API versions use twice-yearly, plant-named major releases that may
contain breaking changes. Monthly releases retain the current major's plant
name and add backward-compatible features.

Every API release has directly associated SDK releases for supported languages,
but SDK packages continue to use semantic versions. Track both the SDK version
and its mapped API release during an upgrade.

`2025-09-30.clover` is the first Clover release and the breaking migration
boundary. Later Clover releases are additive; do not treat every Clover-dated
upgrade as breaking.

## Snapshot and thin events

### Thin Event retrieval (`2024-09-30.acacia`)

API v2 supports retrieving thin Events. Retrieve the Event resource when the
delivered notification is insufficient.

### API v1 thin-event preview

Thin events for API v1 resources are in private preview. This extends a format
that previously supported only API v2 resources and lets preview integrations
adopt unversioned typed notifications without replacing webhook configuration
during upgrades.

### Contract differences

Snapshot events can originate from API v1 or v2. They carry an eventually
consistent object snapshot and `previous_attributes`, and their schema follows
the API version configured on the destination.

Thin notifications carry Event and related-object identifiers. Retrieve the
latest related object for current resource state. Retrieve the complete v2 Event
when `data` context or `changes` are needed.

### Typed processing

SDKs type the initial notification as `{EventType}EventNotification` and the
result of `fetchEvent()` as `{EventType}Event`. Parse and verify the notification
with the endpoint secret. Then use `fetchRelatedObject()` for current state or
`fetchEvent()` for Event context and previous values.

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

## Permissions and retention

### Retrieval permissions

Workbench Event viewing requires the Admin or Developer role. API retrieval can
use a secret key. A restricted key needs `Read` access to the Event type's
underlying resource—for example, PaymentIntent read access for
`payment_intent.succeeded`—rather than a generic Event-read permission.

### Retention windows

Workbench exposes Events for 13 months:

- Less than 15 days old: full payload, delivery attempts, and manual resend.
- 16–30 days old: full payload without attempts or resend.
- Older: a truncated summary only.

Retrieve Event and List Events return full payloads only for the past 30 days.

## Destination constraints

Each livemode or sandbox account can register at most 16 Event Destinations. If
a snapshot destination's API version differs from the merchant default, only
three uniquely versioned destinations can be registered.

## List API migration (`2025-03-31.basil`)

List APIs remove both expanded `total_count` and the `page` parameter. Do not
use either for pagination or collection sizing.
