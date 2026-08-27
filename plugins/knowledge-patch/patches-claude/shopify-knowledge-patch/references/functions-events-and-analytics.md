# Functions, Events, and Analytics

## External-call response headers and JSON

Use `HttpResponse.header(name: ...)` for a case-insensitive single-header
lookup. The all-header `headers` field remains but is deprecated.

For JSON responses, use `JSON_body` without `body`. `body` wins if both are
present, and a missing `Content-Type` is filled as `application/json`.

## Function-readable data

Shopify Functions can read `Customer.createdAt` and Shop User metafields.

## Function variable validation

Across Function APIs, malformed metafield input-query variables raise
`InvalidVariableValueError` instead of being treated as empty.

## Analytics surfaces

Shop Campaigns performance data is queryable through ShopifyQL. Analytics
metric targets are exposed by the GraphQL Admin API. App Events adds app-usage
and performance data to the Dev Dashboard.

## Metafield event triggers

Events adds metafield triggers and additional topics.

## Next Generation Events

The developer preview adds field-level trigger control, custom GraphQL
payloads, and query-based delivery filters to webhooks.
