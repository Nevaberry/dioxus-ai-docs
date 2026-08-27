# API and Security

## API versions

### Sequential versions and defaults

Paddle increments its sequential API version only for breaking changes. The
current version is `1`. Older versions are not automatically upgraded and are
not currently deprecated.

New accounts default to the latest API version. Requests that do not specify a
version use the account default.

### Per-request version selection

The `Paddle-Version` header overrides the account default for a request. It may
select a later version to test it before changing the account default, but it
cannot select a version earlier than the account default.

```sh
curl https://api.paddle.com/event-types \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Paddle-Version: 1"
```

Notification destinations have separate version behavior; see
[Webhooks and operations](webhooks-and-operations.md#notification-destination-versions).

## OAuth apps and hosted MCP access

Apps can connect to Paddle with OAuth instead of API keys. Merchants can manage
connected third-party apps in the dashboard.

The hosted Paddle MCP server uses browser-based OAuth for live accounts. It
continues to require an API key for sandbox. Its remote codemode interface
exposes the API through three tools.

## API key controls

Enhanced API keys use a standardized format and support:

- permissions;
- expiry dates;
- usage tracking.

Paddle can detect exposed keys in public GitHub repositories and alert or
disable them. Its AWS Secrets Manager integration can rotate keys on a schedule
without downtime.

## Client-side tokens

Paddle.js authenticates with client-side tokens instead of seller IDs. Paddle
Retain can use the same token rather than requiring a separate Retain API key.

Client-side tokens can be created and managed through API operations. Those
operations have corresponding webhooks.

## Paginated list totals

For large datasets, the estimated total in paginated list responses is capped
rather than exact. Consumers must not interpret the estimate as the complete
result count.
