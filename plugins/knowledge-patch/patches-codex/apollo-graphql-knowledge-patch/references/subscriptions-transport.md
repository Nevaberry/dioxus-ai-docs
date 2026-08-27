# Subscriptions and Streaming Transport

## Deduplication and identity

### Subscription deduplication can ignore headers (2.3.0)

List non-semantic headers under `subscription.deduplication.ignored_headers` so
their differences do not prevent identical subgraph subscriptions from sharing
a connection.

### Subscription deduplication can ignore JWT context (2.15.0)

Decoded claims participate in identity separately from forwarded headers, so
`ignored_headers` cannot merge authenticated subscriptions. Set
`ignore_auth_context: true` only for non-personalized streams. Deduplication
defaults and overrides can be configured per subgraph.

## Protocol and error handling

### WebSocket handshakes produce valid GraphQL payloads (2.4.0)

Handshake-time subscription responses, including coprocessor responses, contain
the required GraphQL `data` member and pass response validation.

### Subscription errors retain their protocol level (2.6.0)

For multipart HTTP, a GraphQL error immediately before stream end remains a
GraphQL error rather than being serialized as fatal transport failure.

### WebSocket connection errors propagate without an ID (2.7.0)

The Router accepts `graphql-transport-ws` `connection_error` messages containing
a payload but no `id` and propagates their errors to clients.

### WebSocket handshakes propagate trace context (2.11.0)

Trace headers are injected into the initial subgraph HTTP upgrade. Individual
messages on the established WebSocket cannot receive new propagation headers.

### Subscription request builders restore plugin compatibility (2.11.0)

External plugins/crates can use `SubscriptionTaskParams` with
`execution::Request` builders again, including in unit tests.

## Lifecycle and deployment

### Health-check endpoints can be disabled again (2.3.0)

Router 2.3 restores the ability to disable the health endpoint after its 2.0
conversion into a plugin temporarily lost that behavior.

### Self-hosted subscriptions are available on every GraphOS plan (2.11.0)

Free, Developer, Standard, and Enterprise plans may run subscriptions on a
self-hosted Router. Because the feature remains licensed, connect the Router to
GraphOS with API key and graph ref.

### Maximum subscription lifetime (2.15.0)

`subscription.max_lifetime` closes streams after the configured duration and
sends terminal `SUBSCRIPTION_MAX_LIFETIME_EXCEEDED`. Unset means unlimited.

### AWS API Gateway can front multipart subscriptions (2.13.0)

AWS REST API Gateway can proxy HTTP multipart subscriptions when response
transfer mode is configured for streaming.

## Streaming telemetry

### Open-subscription metrics identify the operation (2.4.0)

`apollo.router.opened.subscriptions` includes `graphql.operation.name`.

### Subscription event counter semantics (2.9.0)

`apollo.router.operations.subscriptions.events` counts subscription events but
not ping, pong, or close. The Router relies on WebSocket ping handling and no
longer sends duplicate pong before acknowledgement.

### Streaming termination telemetry (2.14.0)

Router spans expose `apollo.subscription.end_reason` values `server_close`,
`subgraph_error`, `heartbeat_delivery_failed`, `client_disconnect`,
`schema_reload`, or `config_reload`; deferred operations expose
`apollo.defer.end_reason` as `completed` or `client_disconnect`. Counters cover
client termination (`apollo.router.operations.subscriptions.terminated.client`),
subscription rejection (`apollo.router.operations.subscriptions.rejected`), and
per-subgraph WebSocket closure
(`apollo.router.operations.subscriptions.terminated.subgraph`).
