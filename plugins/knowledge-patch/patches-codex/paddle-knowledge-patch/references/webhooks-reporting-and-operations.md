# Webhooks, Reporting, and Operational Limits

## Reporting and metrics APIs

Paddle added reports for subscriptions, checkouts, balance, catalog, and
transaction or adjustment line items. It also added seven API operations for
account time-series metrics.

Reports can be created and downloaded through the API. Webhooks are available
for report workflows.

## Capped totals for large list operations

For large datasets, the estimated total in paginated list responses is capped
rather than exact. Consumers must not interpret that estimate as the complete
result count.

## Report and preview limits

Report creation is limited to 100 per day. Price and transaction preview
operations allow 1,000 requests per minute per IP address.

## Webhook simulation

The webhook simulator supports single events and predefined scenarios,
configurable options, existing Paddle IDs, custom or partial payloads, and
scenario data.

## Replay and retention

Notifications can be replayed. Events and notifications older than 90 days are
unavailable through the API.
