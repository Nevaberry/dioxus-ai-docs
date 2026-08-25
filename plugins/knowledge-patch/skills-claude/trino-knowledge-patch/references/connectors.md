# Other Connectors

Use this reference for connectors other than Delta Lake, Hive, Hudi, Lakehouse,
and Iceberg.

## Connector lifecycle and compatibility

- DuckDB and Loki connectors were added in 470. DuckDB initializes in the Docker
  image (472), and Loki accepts versions newer than 3.2.0 (472).
- ClickHouse now requires ClickHouse 24.3+ or Altinity 22.3+ (469).
  PostgreSQL requires version 12+ (470).
- The Kinesis connector was removed in 470. Kudu and Phoenix were removed in
  473-474, and Vertica was removed in 480. Do not retain those catalogs during
  an upgrade. Before its removal, Kudu supported unpartitioned tables and
  Phoenix exposed `phoenix.server-scan-page-timeout` (469).
- The deprecated `glue-v1` metastore type was removed from Delta Lake, Hive, and
  Hudi, and the deprecated Databricks Unity Catalog integration was removed from
  Delta Lake and Hive (473-474).

## Relational database connectors

- `MERGE` is supported by Ignite (469), MySQL (470), and PostgreSQL under
  fault-tolerant `retry_policy=TASK` (475). Updates assigning `NULL` work for
  ClickHouse, MariaDB, MySQL, Oracle, PostgreSQL, Redshift, SingleStore,
  Snowflake, SQL Server, and Vertica (469).
- MySQL prevents negative date writes (470) and supports primary keys in table
  creation (475). PostgreSQL supports `array(uuid)` (475).
- ClickHouse reads `bool` (475) and all ClickHouse `DECIMAL` columns (481).
- MariaDB and MySQL read `DECIMAL(p,s)` above precision 38; PostgreSQL reads all
  `NUMERIC`/`DECIMAL`; Oracle reads all `NUMBER` columns (480).
- MySQL and SingleStore no longer expose `BIT(n)` for `n > 1`, because the prior
  mapping was incorrect (480).
- `oracle.connection-pool.wait-timeout` limits pooled-connection wait time
  (480).
- SQL Server supports `json` (481). Exasol supports `hashtype` (477) and
  `timestamp` (482). PostgreSQL maps PostGIS `point` to Trino `geometry` (482)
  and discovers PostGIS geometry types outside `public` (477).
- SQL Server case-insensitive-collation `LIKE` results were corrected (475).
  MySQL and SQL Server no longer push down character inequality/range predicates
  that could violate trailing-space semantics; SQL Server `DELETE`/`UPDATE`
  requiring that pushdown can fail. Oracle trims blank padding when pushing a
  `char`-to-`varchar` cast (482).
- `IS NOT DISTINCT FROM` correctness was fixed for MySQL and PostgreSQL (479).
- Connector JSON reads through MySQL, PostgreSQL, MongoDB, Pinot, and SingleStore
  preserve decimals beyond 16 significant digits (481). MongoDB also handles
  case-sensitive table-name conflicts correctly (471).

## BigQuery, Snowflake, and Google Sheets

- BigQuery gRPC channel-pool sizing is configurable (469), and
  `bigquery.max-parallelism` caps parallelism (475).
- BigQuery and Snowflake require JVM option
  `--sun-misc-unsafe-memory-access=allow` when running with Trino (476).
- Google Sheets delegated-user authentication uses
  `gsheets.delegated-user-email` (476); reliability with this setting was fixed
  in 478.

## Faker, JMX, Kafka, Redis, and specialized connectors

- Faker supports views and generated sequences (469). Constraints now use the
  `min`, `max`, and `options` column properties, not `WHERE` clauses (469).
  CTAS derives constraints from source data (470), and Faker supports `row` while
  producing empty values for `array`, `map`, and `json` (472).
- JMX exports complete metric values even when coordinator and worker MBeans
  differ (470).
- Kafka supports timestamp-offset partition filtering (478).
- Redis supports TLS through `redis.tls.*` properties (482).
- `druid.execution-timeout` cancels overlong Druid queries (483).
- The TPC-DS connector moved to generator 1.7, changing generated rows and table
  statistics (482).
- The Ignite connector requires
  `--add-opens=java.base/java.util=ALL-UNNAMED` (483).

## Temporary join-pushdown migration

ClickHouse, Druid, DuckDB, Exasol, Ignite, MariaDB, MySQL, Oracle, PostgreSQL,
Redshift, SingleStore, Snowflake, SQL Server, and Vertica renamed
`join-pushdown.with-expressions` to
`deprecated.join-pushdown.with-expressions` (479). The replacement is temporary
and should not become a long-lived configuration dependency.
