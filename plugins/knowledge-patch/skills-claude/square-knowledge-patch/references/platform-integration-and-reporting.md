# Platform integration and reporting

## Webhook retries

The final retry policy is at most 11 retries over 24 hours for webhook
subscriptions on every Square API version. It supersedes the January policy of
19 retries over 48 hours.

## Webhook SDK objects

As of June, every webhook payload has a corresponding SDK object.

## JWT OAuth access tokens

The OAuth API adds a `use_jwt` parameter for authenticating with a JSON Web
Token. The token behaves like a standard access token.

## Reporting API

The Beta, cube-based Reporting API uses:

- `GET /v1/meta` to discover views, cubes, measures, dimensions, and segments.
- `POST /v1/load` to run analytical queries.

The API supports automatic joins across cubes. Authenticate with a personal
access token or an OAuth token carrying `REPORTING_READ`.

## Channels API

The Channels API retrieves the marketing, sales, and fulfillment channels
through which catalog items are sold and delivered.

## App Marketplace eligibility

Since March 27, 2025, an application needs at least five active Square sellers
before it is eligible for Square App Marketplace listing.

## Square MCP server

Square provides an MCP server through which compatible AI assistants can
control and interact with a Square account.
