# Lakehouses and connectors

Use this reference for DuckLake, Delta, Iceberg, ODBC, and Teradata integration.
The lakehouse and connector details are drawn from batches `1.2-1.4` and
`1.5.0`.

## DuckLake changes

DuckLake moves to specification 0.4, adding:

- macros;
- sorted tables;
- deletion inlining; and
- partial delete files.

Validate the catalog and client combination before assuming that an older
DuckLake consumer understands these capabilities.

DuckLake supports DuckDB `VARIANT` values in 1.5.0.

## Delta behavior

Delta integration adds improved Unity Catalog writes, idempotent writes, and
table checkpoints. Use the idempotent-write path when retry behavior can repeat
a logical operation, and configure checkpointing according to the table's
operational needs.

Delta supports DuckDB `VARIANT` values in 1.5.0.

## Iceberg table creation and catalog headers

Iceberg `CREATE TABLE` accepts table properties in `WITH`. `format-version` and
`location` are promoted to dedicated fields rather than being left as generic
properties:

```sql
CREATE TABLE test_create_table (a INTEGER)
WITH (
    'format-version' = '2',
    'location' = 's3://path/to/data',
    'property1' = 'value1'
);
```

Iceberg catalog attachments accept `EXTRA_HTTP_HEADERS`. This enables catalogs
that require additional request headers, including BigLake access. Keep header
values in an appropriate credential source rather than committed SQL.

Iceberg support for DuckDB `VARIANT` begins in 1.5.1. DuckDB 1.5.0 can use the
other Iceberg features in this reference but must not assume `VARIANT` support.

## Database-wide Iceberg copies

Copying an entire Iceberg database into DuckDB or DuckLake works directly:

```sql
COPY FROM DATABASE iceberg_datalake TO duckdb_db;
```

The reverse direction has a setup requirement: create the destination schemas
before copying from DuckDB into Iceberg:

```sql
CREATE SCHEMA iceberg_datalake.main;
COPY FROM DATABASE duckdb_db TO iceberg_datalake;
```

Preserve this directionality in generated migration procedures. A successful
Iceberg-to-DuckDB copy does not prove that the reverse operation auto-creates
schemas.

## ODBC scanner

The shipped `odbc_scanner` extension queries remote ODBC endpoints through a
connection object:

```sql
LOAD odbc_scanner;

SET VARIABLE conn = odbc_connect(
  'Driver={Oracle Driver};DBQ=//127.0.0.1:1521/XE;UID=scott;PWD=tiger;'
);

SELECT *
FROM odbc_query(
  getvariable('conn'),
  'SELECT SYSTIMESTAMP FROM dual;'
);
```

Keep real credentials outside checked-in SQL. Confirm that the operating system
has the required ODBC driver and that its driver name matches the connection
string.

## Teradata connector

DuckDB 1.4 adds a connector for querying Teradata systems. Treat it as a
connector-specific integration: confirm extension availability and the target
authentication and network requirements before generating a query workflow.

## Integration checklist

1. Identify the catalog or connector and its exact extension version.
2. Confirm whether the operation reads, writes, or copies a whole database.
3. For Iceberg destinations, create schemas before a database-wide copy.
4. Keep ODBC connection strings and extra HTTP header values out of source.
5. Do not use Iceberg `VARIANT` with DuckDB 1.5.0; require 1.5.1 or later.
6. Test idempotent Delta writes under the actual retry mechanism.
7. Confirm that all DuckLake consumers understand specification 0.4 features.
