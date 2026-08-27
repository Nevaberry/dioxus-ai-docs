# API Versions, Security, and Integrations

## Sequential API versions and account defaults

Paddle increments its sequential API version only for breaking changes. The
current version is `1`; older versions are not automatically upgraded and are
not currently deprecated.

New accounts default to the latest version. Requests without an explicit
version use the account default.

## Per-request version selection

The `Paddle-Version` header overrides the account default. It may select a
later version for testing before the account default changes, but it cannot
select a version earlier than the default.

```sh
curl https://api.paddle.com/event-types \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Paddle-Version: 1"
```

## Notification destination versions

Webhook notification destinations do not use the account default. Choose the
API version when creating each destination.

## OAuth apps and remote MCP authentication

Apps can connect to Paddle with OAuth instead of API keys. Merchants can manage
connected third-party apps in the dashboard.

The hosted Paddle MCP server uses browser-based OAuth for live accounts but
continues to require an API key for sandbox. Its remote codemode interface
exposes the API through three tools.

## API key controls and automatic rotation

Enhanced API keys use a standardized format and support permissions, expiry
dates, and usage tracking. Paddle can detect exposed keys in public GitHub
repositories and alert or disable them.

An AWS Secrets Manager integration can rotate keys on a schedule without
downtime.

## Paddle UI

Paddle UI provides customizable React components for checkout, pricing, and
subscription management. It is based on shadcn/ui and installed with the
shadcn CLI.

## External purchase flows for iOS

An iOS app can direct users to an external hosted checkout or to a web checkout
deployed to Vercel, with RevenueCat used for fulfillment.

## Paddle Classic migration

The dashboard can map a Paddle Classic catalog and migrate its subscription
data into Paddle Billing.
