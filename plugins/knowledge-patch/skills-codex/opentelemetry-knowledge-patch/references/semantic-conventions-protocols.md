# Semantic Conventions: Protocols and Data Services

## Generative AI

All `gen_ai.*` attributes, metrics, events, and spans formerly defined in the
main semantic-conventions repository—including its OpenAI and MCP areas—are
deprecated there and have moved to the dedicated GenAI repository.
Instrumentation must use that repository's corresponding `schema_url`.

## RPC

### Names, duration, and status

- Required duration metrics are `rpc.client.call.duration` and
  `rpc.server.call.duration`, measured in seconds.
- `rpc.method` is fully qualified and absorbs the former `rpc.service`.
- Metadata attributes are `rpc.request.metadata` and
  `rpc.response.metadata`.
- Status is `rpc.response.status_code`.
- `rpc.system.name` replaces `rpc.system`; normalized values include
  `connectrpc` and `dubbo`.

Core RPC, gRPC, and Apache Dubbo conventions are Release Candidate. JSON-RPC,
gRPC, and Connect RPC have system-specific metric sections.

### Addressing and retirements

- RPC spans and metrics omit `network.type`, `network.protocol.name`,
  `network.protocol.version`, and `network.transport`.
- Server spans also omit `client.address` and `client.port`.
- Request/response size metrics and `rpc.message` are deprecated.
- `server.address` is conditionally required rather than unconditionally
  required.

## Exception telemetry

Generic exception span events are deprecated. Use exception log records and
domain events while migrating. `OTEL_SEMCONV_EXCEPTION_SIGNAL_OPT_IN` supports
the transition.

Domain-specific events include:

- `db.client.operation.exception`
- `rpc.client.call.exception` and `rpc.server.call.exception`
- `http.client.request.exception` and `http.server.request.exception`
- `faas.invocation.exception`
- the messaging-operation exception variants

Treat `exception.message` as potentially sensitive. `error.type` or
`exception.type` may unwrap wrapper exceptions that do not identify the real
failure.

## HTTP

- Declarative configuration can override known methods and identify sensitive
  query parameters.
- `QUERY` is a recognized method.
- Intentional client cancellation is not an error.
- `network.peer.address` is Opt-In on `http.client.open_connections` and
  `http.client.connection.duration` because it can produce unbounded
  cumulative metric streams.

## GraphQL

`graphql.document` is Opt-In rather than Recommended because documents can
contain sensitive, unbounded, high-cardinality user input. Sanitize any value
captured after explicit enablement.

## Browser telemetry

### Document identity

The `browser.document` entity uses Recommended, Development-stability
`browser.document.url.full` for the current RFC 3986 URL. This keeps identity
that varies during navigation separate from immutable browser-runtime
attributes.

### Web Vitals

Web Vital `name`, `value`, `delta`, and `id` belong in
`browser.web_vital.*` attributes, not in the `browser.web_vital` event body.
The schema also includes attributes used by current instrumentation (batch
`2026-08-stable`).

## Messaging

Messaging conventions distinguish create, send, receive, process, and settle
operation spans and refine each operation per messaging system. Kafka spans
may carry `messaging.kafka.cluster.id` for the connected cluster.

## Database conventions

### Oracle identity

For Oracle, `db.namespace` contains only the database's unique identifier.
Move other identity dimensions to:

- `oracle.db.pdb`
- `oracle.db.instance.name`
- `oracle.db.service`
- `oracle.db.domain`

The Oracle client span and its connection attributes are Release Candidate.

### Batch operations and propagation

`db.operation.batch.size` covers multi-operand operations, parameterized batch
APIs, and empty batches. Database context-propagation guidance covers SQL
commenter, SQL Server `SET CONTEXT_INFO`, and `V$SESSION.ACTION`.
