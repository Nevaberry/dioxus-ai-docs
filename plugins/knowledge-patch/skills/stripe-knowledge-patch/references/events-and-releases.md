# Events, Destinations, and API Releases

## API release lifecycle

Stripe uses two coordinated version systems:

- Plant-named major API releases arrive twice yearly and can include breaking changes.
- Monthly API releases retain the latest major release's plant name and add backward-compatible features.
- Every API release has a corresponding SDK release.
- SDK packages use semantic versions, but each package version is associated with a specific API release.

Plan API and SDK upgrades together. Check the SDK pin rather than deriving the API contract from a semantic major number.

## Snapshot and thin event contracts

### Snapshot events

- Snapshot events originate from API v1.
- They deliver an API-versioned resource snapshot with `previous_attributes`.
- The embedded snapshot is eventually consistent.
- Continue to parse snapshot payloads through the SDK's webhook signature and event helper.

### Thin notifications

- Thin notifications normally originate from API v2.
- They contain a small, unversioned notification; fetch the full event or related resource separately when needed.
- Thin notifications are SDK-typed.
- Thin notifications for API v1 resources are available in private preview.
- API v1 can retrieve thin events beginning with `2024-09-30.acacia`.

SDKs generally name the light payload `{EventType}EventNotification` and the retrieved event `{EventType}Event`.

```java
EventNotification notification =
    client.parseEventNotification(payload, signatureHeader, endpointSecret);
Event event = client.v2().core().events().retrieve(notification.getId());
```

## Choosing what to fetch

- Call `fetchEvent()` when event-time `data` or `changes` is needed.
- Call `fetchRelatedObject()` when the related resource's latest state is needed.
- Make no extra request when event type and resource ID are sufficient.
- Do not assume `fetchRelatedObject()` reconstructs event-time state.

## Retrieval authorization

- A secret API key can retrieve every event type by default.
- A restricted API key needs `Read` access to the resource associated with the event type.

## Retention and resend windows

Workbench retains events for 13 months, but available detail and operations narrow over time:

| Event age | Available data and operations |
| --- | --- |
| Less than 15 days | Delivery attempts and manual resend are available. |
| 16-30 days | Full payload remains, but delivery attempts and manual resend are unavailable. |
| Older than 30 days | Workbench exposes only a truncated summary. |

The Retrieve and List Events APIs return full payloads for the most recent 30 days.

## Event destinations

### Limits

- Each livemode or sandbox account can register at most 16 event destinations.
- Snapshot destinations whose API version differs from the merchant default are limited to three uniquely versioned destinations.

### Pagination and source values

- Event Destinations remove the `page` parameter in `2025-03-31.basil`.
- List APIs generally no longer support expanding total count in that release.
- In `2026-03-25.dahlia`, Event Destination `events_from` accepts string values; widen serializers and input schemas.

### Azure Event Grid

Event destinations publicly preview direct delivery to Azure Event Grid in `2026-03-25.dahlia`.

## Batch API operations

The public-preview Batch Jobs v2 API can run API operations in batches (`2026-03-25.dahlia`), including:

- bulk Customer creation;
- Subscription migration; and
- large dataset updates.

Treat batch execution, error handling, and preview schemas separately from ordinary synchronous request logic.
