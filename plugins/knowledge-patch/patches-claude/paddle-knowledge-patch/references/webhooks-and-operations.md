# Webhooks and Operations

## Notification destination versions

Webhook notification destinations do not use the account's default API
version. Choose the API version when creating each destination.

For request and account version behavior, see
[API and security](api-and-security.md#api-versions).

## Webhook simulation

The webhook simulator supports:

- individual events;
- predefined scenarios;
- configurable options;
- existing Paddle IDs;
- custom or partial payloads;
- scenario data.

## Replay and retention

Notifications can be replayed.

Events and notifications older than 90 days are unavailable through the API.

## Sandbox behavior

Sandbox emails originate from `@paddle.com`.

Messages addressed to unregistered domains are forwarded to the account email.

Sandbox refunds are approved automatically every ten minutes.

## Paddle Classic migration

The dashboard can map a Paddle Classic catalog and migrate its subscription
data into Paddle Billing.
