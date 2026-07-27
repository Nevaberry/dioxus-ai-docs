# Semantic Conventions: Protocols and Data Services

## Generative AI

All `gen_ai.*` attributes, metrics, events, and spans formerly defined in the
main semantic-conventions repository are deprecated there, including its
provider-specific and MCP areas. Instrumentations must use the corresponding
definitions and `schema_url` from the dedicated Generative AI repository.

## RPC

### Names, units, and metadata

- Required duration metrics are `rpc.client.call.duration` and
  `rpc.server.call.duration`, measured in seconds.
- `rpc.method` is fully qualified and absorbs the former `rpc.service`.
- Common request and response metadata names are `rpc.request.metadata` and
  `rpc.response.metadata`.
- Response status is `rpc.response.status_code`.
- `rpc.system` is renamed to `rpc.system.name`.
- Normalized `rpc.system.name` values include `connectrpc` and `dubbo`.

### Stability and system-specific metrics

Core RPC, gRPC, and Apache Dubbo conventions are Release Candidate. JSON-RPC,
gRPC, and Connect RPC each have system-specific metric sections.

### Removed and deprecated fields

- RPC spans and metrics no longer include `network.type`,
  `network.protocol.name`, `network.protocol.version`, or
  `network.transport`.
- RPC server spans no longer include `client.address` or `client.port`.
- Request- and response-size metrics are deprecated.
- `rpc.message` is deprecated.
- `server.address` is only conditionally required.

## Exceptions move from spans to logs

Generic exception recording as span events is deprecated. During migration,
`OTEL_SEMCONV_EXCEPTION_SIGNAL_OPT_IN` enables the exception-log path.

Domain-specific exception events include:

- `db.client.operation.exception`.
- `rpc.client.call.exception`.
- `rpc.server.call.exception`.
- `http.client.request.exception`.
- `http.server.request.exception`.
- `faas.invocation.exception`.
- The corresponding messaging-operation exception variants.

Treat `exception.message` as potentially sensitive. `error.type` or
`exception.type` may unwrap an uninformative wrapper type to identify the
meaningful underlying error.

## HTTP

### Declarative configuration

HTTP conventions add declarative configuration for:

- Overriding the known-method set.
- Identifying sensitive query parameters.

`QUERY` is a recognized method. Intentional client cancellation is not an
error.

### Metric cardinality

`network.peer.address` is Opt-In on `http.client.open_connections` and
`http.client.connection.duration`. Including peer addresses can create
unbounded cumulative metric streams.

## GraphQL

`graphql.document` is Opt-In rather than Recommended because a document can
contain sensitive, unbounded, high-cardinality user input. Sanitize the
document whenever capture is enabled.

## Browser document identity

The `browser.document` entity keeps navigation-varying document identity
separate from immutable browser runtime attributes. Its
`browser.document.url.full` attribute is Recommended, Development stability,
and contains the current RFC 3986 URL.

## Oracle database identity

`db.namespace` for Oracle contains only the database's unique identifier.
Move the other identity dimensions to:

| Dimension | Attribute |
| --- | --- |
| Pluggable database | `oracle.db.pdb` |
| Instance | `oracle.db.instance.name` |
| Service | `oracle.db.service` |
| Domain | `oracle.db.domain` |

The Oracle client span and its connection attributes are Release Candidate.

## Database operations and propagation

`db.operation.batch.size` explicitly covers:

- Multi-operand operations.
- Parameterized batch APIs.
- Empty batches.

Database context-propagation guidance includes SQL commenter, SQL Server
`SET CONTEXT_INFO`, and Oracle `V$SESSION.ACTION`.
