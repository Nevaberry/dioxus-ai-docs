# Connectors and integrations

This reference covers connector availability, prerequisites, type mappings,
connector-specific configuration, and pushdown. Lakehouse-format connectors
are documented separately.

## Connector availability and prerequisites

### Added connectors

- DuckDB was added in 470. The Docker image can initialize it correctly from
  472.
- Loki was added in 470 and can connect to Loki releases higher than 3.2.0
  from 472.
- Lakehouse was added in 477; see the lakehouse reference.

### Removed connectors

- Kinesis was removed in 470.
- Kudu and Phoenix were removed in batch 473-474. Before removal, Kudu gained
  unpartitioned-table support and Phoenix exposed
  `phoenix.server-scan-page-timeout` (469).
- Vertica was removed in 480.

### Minimum versions and JVM options

- ClickHouse requires ClickHouse 24.3 or newer, or Altinity 22.3 or newer
  (469).
- PostgreSQL requires version 12 or newer (470).
- BigQuery and Snowflake require
  `--sun-misc-unsafe-memory-access=allow` (476).
- Ignite requires `--add-opens=java.base/java.util=ALL-UNNAMED` (483).

## Relational database writes

### MERGE and nullable updates

Ignite supports `MERGE` (469), MySQL supports `MERGE` (470), and PostgreSQL
supports `MERGE` when `retry_policy` is `TASK` (475).

Updates that assign `NULL` work with ClickHouse, MariaDB, MySQL, Oracle,
PostgreSQL, Redshift, SingleStore, Snowflake, SQL Server, and Vertica (469).
Vertica was subsequently removed in 480.

### Table definition

MariaDB and MySQL support positioned column additions with `FIRST`, `AFTER`,
and `LAST` (469). MySQL can create tables with a primary key (475).

### Correctness

- MySQL rejects invalid negative date writes (470).
- SQL Server `LIKE` is correct for case-insensitive collations (475).
- MySQL and PostgreSQL return correct `IS NOT DISTINCT FROM` results (479).
- MySQL and SingleStore no longer expose `BIT(n)` where `n > 1`, because the
  earlier mapping was incorrect (480).

## Database type mappings

- ClickHouse supports its `bool` type (475) and can read every ClickHouse
  `DECIMAL` column (481).
- Exasol supports `hashtype` (477) and `timestamp` (482).
- PostgreSQL supports `array(uuid)` (475). PostGIS `geometry` works even when
  PostGIS is installed outside `public` (477), and PostgreSQL `point` reads
  and writes as Trino `geometry` (482).
- SQL Server supports `json` (481).
- MariaDB and MySQL read `DECIMAL(p, s)` where `p > 38`; PostgreSQL reads all
  `NUMERIC` and `DECIMAL` columns; Oracle reads all `NUMBER` columns (480).
- MongoDB, MySQL, Pinot, PostgreSQL, and SingleStore preserve JSON decimal
  portions longer than 16 significant digits (481).

## Pushdown and character semantics

The ClickHouse, Druid, DuckDB, Exasol, Ignite, MariaDB, MySQL, Oracle,
PostgreSQL, Redshift, SingleStore, Snowflake, SQL Server, and Vertica
connectors renamed `join-pushdown.with-expressions` to
`deprecated.join-pushdown.with-expressions` (479). The replacement is itself
temporary and scheduled for removal.

MySQL and SQL Server do not push down character inequality or range predicates
(482), preventing wrong results from trailing-space differences. On SQL
Server, a `DELETE` or `UPDATE` that requires such pushdown fails. Oracle
pushdown trims blank padding when casting `char` to `varchar`.

Connector expression pushdown can handle `COALESCE` (481) and lambdas (482);
implementers should also read the SPI reference.

## BigQuery

The gRPC channel pool is configurable (469). Limit maximum parallelism with
`bigquery.max-parallelism` (475). The connector also needs the JVM
unsafe-memory option listed above (476).

## Faker

- Views and generated sequences are supported (469).
- Column constraints use the `min`, `max`, and `options` column properties;
  constraint syntax in `WHERE` clauses is no longer supported (469).
- `CREATE TABLE ... AS SELECT` derives constraints from source data (470).
- `row` is supported, while generated `array`, `map`, and `json` values are
  empty (472).

## Google Sheets

Delegate authentication to a user with (476):

```properties
gsheets.delegated-user-email=analyst@example.com
```

Potential failures with this setting are fixed in 478.

## Kafka connector

Partitions can be filtered by timestamp offset without failure (478).
Kafka event-listener properties are distinct from the Kafka connector and are
documented in the operations reference.

## MongoDB

Tables with case-sensitive name conflicts no longer fail (471). High-precision
JSON decimal content is preserved (481).

## Redis

TLS connections are supported through the `redis.tls.*` catalog properties
(482). Configure the appropriate trust and client-authentication material for
the deployment.

## Druid

`druid.execution-timeout` cancels connector queries that exceed the configured
duration (483).

## Oracle

`oracle.connection-pool.wait-timeout` limits how long a query waits for a
pooled connection (480). Oracle reads every `NUMBER` column, and its character
pushdown trims blank padding as described above.

## TPC-DS

The TPC-DS connector uses generator version 1.7 (482). Generated data and table
statistics differ from earlier generator output; refresh golden results or
statistics-based expectations deliberately.

## JMX

The JMX connector includes metric values even when coordinator and worker
MBeans differ (470). Server-side `blockedQueries` and other operational
metrics are described in the observability reference.

## Textual AI functions

SQL functions can apply textual AI tasks to data using OpenAI, Anthropic, or
other language models served through Ollama (471). These are functions rather
than a connector; operational use still requires provider or service
configuration and appropriate data-governance controls.
