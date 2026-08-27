# Semantic Conventions: Protocols and Data Services

## Generative AI

### Dedicated convention repository (`semantic-conventions`)

All `gen_ai.*` attributes, metrics, events, and spans formerly in the main
semantic-conventions repository—including its provider-specific and MCP
areas—are deprecated there and live in the dedicated GenAI repository.
Instrumentations must use that repository's corresponding `schema_url`.

## RPC

### Names and duration metrics (`semantic-conventions`)

Use the required, seconds-based `rpc.client.call.duration` and
`rpc.server.call.duration` metrics. `rpc.method` is fully qualified and
absorbs the former `rpc.service`. Use `rpc.request.metadata`,
`rpc.response.metadata`, and `rpc.response.status_code`. Rename `rpc.system`
to `rpc.system.name`; normalized values include `connectrpc` and `dubbo`.

### Stability, addressing, and retirements (`semantic-conventions`)

Core RPC, gRPC, and Apache Dubbo conventions are Release Candidate. JSON-RPC,
gRPC, and Connect RPC have system-specific metric sections. RPC spans and
metrics no longer include `network.type`, `network.protocol.name`,
`network.protocol.version`, or `network.transport`; server spans also drop
`client.address` and `client.port`. Request/response size metrics and
`rpc.message` are deprecated. `server.address` is only conditionally required.

## Exceptions, HTTP, and GraphQL

### Exception telemetry in logs (`semantic-conventions`)

Generic exception recording as span events is deprecated.
`OTEL_SEMCONV_EXCEPTION_SIGNAL_OPT_IN` supports migration to logs. Use domain
events such as `db.client.operation.exception`, `rpc.client.call.exception`,
`rpc.server.call.exception`, `http.client.request.exception`,
`http.server.request.exception`, `faas.invocation.exception`, and the
messaging-operation variants. Treat `exception.message` as potentially
sensitive. `error.type` or `exception.type` may unwrap uninformative wrapper
types.

### HTTP configuration and cardinality (`semantic-conventions`)

HTTP declarative configuration can override known methods and identify
sensitive query parameters. `QUERY` is recognized. Intentional client
cancellation is not an error. `network.peer.address` is Opt-In on
`http.client.open_connections` and `http.client.connection.duration` because
it can create unbounded cumulative metric streams.

### GraphQL document capture (`semantic-conventions`)

`graphql.document` is Opt-In rather than Recommended because it can contain
sensitive, unbounded, high-cardinality user input. Sanitize it whenever
capture is enabled.

## Browser telemetry

### Browser document identity (`semantic-conventions`)

The `browser.document` entity uses Recommended, Development-stability
`browser.document.url.full` for the current RFC 3986 URL. This keeps
navigation-varying document identity separate from immutable browser-runtime
attributes.

### Web Vitals event attributes (`2026-08-stable`)

Semantic Conventions 1.44 moves Web Vital `name`, `value`, `delta`, and `id`
out of the `browser.web_vital` event body into `browser.web_vital.*`
attributes and adds attributes used by current instrumentation.

## Database telemetry

### Oracle identity (`semantic-conventions`)

Oracle `db.namespace` contains only the database's unique identifier. Put PDB,
instance, service, and domain in `oracle.db.pdb`, `oracle.db.instance.name`,
`oracle.db.service`, and `oracle.db.domain`. The Oracle client span and its
connection attributes are Release Candidate.

### Batching and context propagation (`semantic-conventions`)

`db.operation.batch.size` covers multi-operand operations, parameterized
batch APIs, and empty batches. Supported database context-propagation
approaches include SQL commenter, SQL Server `SET CONTEXT_INFO`, and
`V$SESSION.ACTION`.

## Messaging

### Operation spans (`2026-08-stable`)

Model distinct spans for create, send, receive, process, and settle operations,
then apply the relevant messaging-system refinements. Kafka spans may carry
`messaging.kafka.cluster.id` to identify the connected cluster.
