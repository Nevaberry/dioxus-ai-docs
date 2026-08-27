# REST and catalogs

Use this reference to implement or configure REST clients and servers,
remote scan planning, mutation safety, views, SQL UDFs, and catalog behavior.

## Endpoint and discovery contracts

Default REST routes stop including namespace, table, and view `HEAD`
endpoints in 1.9.0. Clients and servers must not assume these endpoints are
registered by default.

The 1.11.0-guides protocol adds several discovery and response details:

- Servers can advertise their namespace separator.
- `/v1/config` returns 404 for a nonexistent warehouse.
- `loadTable` can return a `referenced-by` list of dependencies.
- `LoadTableResult` can advertise `scan-planning-mode`.
- S3 signing moves into the main OpenAPI specification.

Interpret each signal narrowly: a missing warehouse is not the same as a
missing endpoint, and table-level scan-planning policy can differ from the
catalog default.

## Remote scan planning

The REST API adds scan-planning request and response models and parsers in
1.10.0.

In 1.11.0-guides, REST catalogs can plan:

- Ordinary table scans.
- Incremental scans.
- Metadata-table scans.

A per-table override can opt out of catalog-level planning. Planning responses
can include storage credentials when `include-credentials` is requested.
Apply the table override first, parse the advertised planning mode, and scope
returned credentials to the intended storage operation.

## Cache freshness and concurrent changes

REST clients can revalidate cached table metadata with ETags in
1.11.0-guides. A server can return `304 Not Modified`, avoiding an unnecessary
metadata transfer. `CommitTableResponse` carries an ETag that clients can use
to detect concurrent changes.

Keep the ETag paired with the exact table state it represents. On a conflict,
reload and re-plan instead of replaying a mutation against stale metadata.
GCP catalog integration also adds ETag conflict detection in this batch.

## Idempotent mutations

Mutating catalog operations accept an `Idempotency-Key` header as of
1.11.0-guides. Send a stable, unique key when retrying commits, creates, and
drops so the server does not execute the same logical mutation twice.

The key complements concurrency checks; it does not replace ETags or table
requirements. Reuse a key only for retries of the same logical request.

## Retry policy

The REST retry semantics change in 1.10.0:

- HTTP 503 is marked non-retryable.
- Retries stop on HTTP 502 and 504.
- Selected status-code retries are permitted for idempotent requests.

Do not implement a blanket "retry every gateway or service error" policy.
First establish idempotence, then apply only the selected retry statuses and
operation rules.

## Client transport and authentication

The 1.10.0 REST client can configure:

- HTTP user agent.
- TLS settings.
- HTTP proxy.
- Whether authentication refresh disables token exchange.

Core enables the Auth Manager API in 1.9.0 for authentication integrations.
Use that integration point instead of embedding authentication state into
unrelated catalog operations.

The REST specification documents configuration for cross-region S3 access as
of 1.8.0. Coordinate that setting with the REST client's signing and the
storage endpoint behavior.

## View registration and operations

The 1.11.0-guides protocol supports optional view registration that attaches
existing view metadata. A separate `/register-view` endpoint can be authorized
independently.

REST catalogs can inject custom `TableOperations` and `ViewOperations`
implementations. Keep injected operations consistent with the REST
concurrency, refresh, and authorization contracts.

Catalogs also have a view-override property as of 1.9.0 for controlling view
behavior.

## Partition-statistics updates

`TableUpdate` includes `SetPartitionStatisticsUpdate` and
`RemovePartitionStatisticsUpdate` in 1.11.0-guides. Clients that round-trip
table updates must preserve these variants even if they do not directly
compute partition statistics.

## Catalog-managed SQL UDFs

The SQL UDF specification introduced in 1.11.0-guides stores versioned,
portable functions in Iceberg catalogs. One logical UDF can carry multiple
SQL-dialect representations.

Select the representation matching the executing engine and retain the
versioned function identity. Do not flatten multiple dialect bodies into one
engine-neutral SQL string.

## Catalog location and registration behavior

Catalogs can enable unique table locations through a catalog property in
1.11.0. This prevents reuse of a location derived from the same identifier
across multiple table creations.

The Content and Partition Stats APIs in 1.11.0-guides allow table registration
to explicitly overwrite. Treat explicit overwrite as distinct from accidental
name collision.

Hive catalog behavior in that batch is stricter:

- Replacing a view updates its query in the Hive Metastore.
- Table registration fails when a view already occupies the name rather than
  overwriting it.

## Encryption in the REST model

The table and REST specifications add encryption keys in 1.10.0, with
table-metadata keys represented in the API. Clients must preserve encryption
metadata through load, commit, and registration operations even when key
material is managed by a separate `KeyManagementClient`.

## Implementation checklist

1. Discover namespace, warehouse, view, and planning capabilities without
   assuming default `HEAD` routes.
2. Honor table-level remote-planning overrides.
3. Pair cached metadata with its ETag and handle `304 Not Modified`.
4. Supply stable idempotency keys for retried mutations.
5. Apply the restricted status-code retry policy.
6. Keep returned storage credentials scoped and refreshable.
7. Preserve every known `TableUpdate` variant and `referenced-by` dependency.
8. Authorize view registration separately where the deployment requires it.
9. Resolve SQL UDF dialect representations for the executing engine.

