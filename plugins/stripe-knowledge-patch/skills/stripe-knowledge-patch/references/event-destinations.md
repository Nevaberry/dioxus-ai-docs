# Event Destinations API

Unified API for webhook endpoints, Amazon EventBridge, and Azure Event Grid. Supports thin events (unversioned, ID-only) and snapshot events.

```ts
// Create a webhook event destination
const destination = await stripe.v2.core.eventDestinations.create({
  type: 'webhook_endpoint',
  url: 'https://example.com/webhook',
  enabled_events: ['payment_intent.succeeded'],
});

// Ping to test connectivity
await stripe.v2.core.events.ping({ destination: destination.id });
```

## Destination Types

| Type | Description |
|------|-------------|
| `webhook_endpoint` | Standard HTTPS webhook |
| `amazon_eventbridge` | AWS EventBridge integration |
| `azure_event_grid` | Azure Event Grid integration |

## Event Formats

- **Thin events**: Unversioned, contain only the event ID -- you fetch the full object yourself
- **Snapshot events**: Full object snapshot included in the event payload
