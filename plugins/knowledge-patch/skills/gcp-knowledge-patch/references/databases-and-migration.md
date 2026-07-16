# Databases and Migration

Use this reference for Spanner and AlloyDB integration, CDC, database transfers, SQL translation, migration assessment, and migration-service behavior.

## Contents

- [Federation, reverse ETL, and database integration](#federation-reverse-etl-and-database-integration)
- [Migration assessment and SQL translation](#migration-assessment-and-sql-translation)
- [Database transfers, metadata, and CDC](#database-transfers-metadata-and-cdc)

## Federation, reverse ETL, and database integration

### Authorized Spanner external datasets (2025-06)

GA Spanner external datasets can be used with authorized views, authorized routines, and Cloud resource connections.

### BigQuery and Spanner integration (2025-03)

GA `EXPORT DATA` statements can reverse-ETL BigQuery data into Spanner, and a BigQuery external dataset can link to an existing Spanner database.

### Cloud resource connections for Spanner exports (2026-03)

GA `EXPORT DATA` statements can use Cloud resource connections when reverse-ETLing BigQuery data to Spanner.

### Continuous-query export to Spanner (2025-07)

In Preview, a BigQuery continuous query can export data to Spanner in real time.

### Continuous-query export to Spanner reaches GA (2026-03)

BigQuery continuous queries can stream data to Spanner in real time at GA.

### Cross-region Spanner federation (2025-05)

In Preview, BigQuery can issue federated queries against Spanner tables in a different region; Spanner network egress charges are waived during the Preview.

### Materialized views over Spanner (2025-09)

Preview BigQuery non-incremental materialized views can periodically cache results over Spanner data.

### Materialized views over Spanner reach GA (2026-03)

GA BigQuery non-incremental materialized views can periodically cache results over Spanner data.

### PostgreSQL-dialect Spanner federation (2025-09)

At GA, BigQuery external datasets can use GoogleSQL to run same-region or cross-region federated queries against PostgreSQL-dialect Spanner databases.

### Reverse ETL to AlloyDB (2026-04)

Preview `EXPORT DATA` statements can reverse-ETL BigQuery data to AlloyDB.


## Migration assessment and SQL translation

### Gemini-enhanced SQL translation (2025-06)

GA SQL translation features can create Gemini-based configuration YAML for AI suggestions and review batch output in code and configuration tabs. Preview interactive translation rules can customize SQL inputs.

### Hadoop and Cloudera migration assessment (2025-06)

In Preview, BigQuery migration assessment can assess workflows that use Cloudera and Apache Hadoop.

### Hadoop migration workflows (2025-07)

Preview migration tooling can use `dwh-migration-dumper` to capture metadata, translate permissions from Hadoop, Hive, and Ranger HDFS to BigQuery, and move tables from an HDFS data lake to Google Cloud.

### Impala and GoogleSQL translation (2025-11)

In Preview, the interactive, API, and batch SQL translators accept Apache Impala SQL for Cloudera or Hadoop migrations and GoogleSQL for iterative rewrites of already-translated queries, including YAML-configured customizations.

### Informatica migration assessment (2025-09)

Preview BigQuery migration assessment can assess the complexity of moving an Informatica platform to BigQuery.

### Redshift Serverless migration assessment (2025-04)

Preview BigQuery migration assessment can assess Amazon Redshift Serverless environments.

### Snowflake migration assessment (2026-03)

BigQuery migration assessment for estimating the complexity of a Snowflake-to-BigQuery migration is GA.

### Snowflake SQL translation mapping (2026-04)

BigQuery Migration Service translation from Snowflake SQL to GoogleSQL is GA and now maps Snowflake `INTEGER` and zero-scale `NUMERIC` values with precision up to 38 to GoogleSQL `INT64` by default.

### SQL translation metadata caching (2025-03)

Preview metadata caching for BigQuery SQL translation can reduce latency on later translation requests.

### SQL translation optimization files (2025-04)

GA BigQuery SQL translation accepts configuration YAML files that optimize translated queries.

### Teradata migration schema mappings (2025-05)

In Preview, a Teradata transfer can use BigQuery translation-engine output as its schema mapping.


## Database transfers, metadata, and CDC

### BigQuery database transfers (2025-12)

BigQuery Data Transfer Service sources for Oracle, MySQL, and PostgreSQL are GA, while Microsoft SQL Server is in Preview.

### CDC custom ordering (2025-03)

GA BigQuery change data capture can use `_CHANGE_SEQUENCE_NUMBER` to control the ordering of streaming `UPSERT` operations.

### Change data capture naming (2026-01)

BigQuery change data capture is now named **BigQuery change data capture ingestion**.

### Database metadata transfers to Knowledge Catalog (2026-06)

In Preview, the BigQuery Data Transfer Service can transfer Oracle and MySQL metadata into Knowledge Catalog.

### External catalog metadata migration (2026-04)

Preview migration tooling can move metadata from Apache Hive Metastore or an Apache Iceberg REST Catalog into BigLake tables for Apache Iceberg.

### Hive transfer resource status (2026-03)

Preview resource-level status reporting for Hive managed-table transfers shows per-table progress and granular errors in BigQuery Data Transfer Service.

### Incremental database transfers (2026-04)

In Preview, BigQuery Data Transfer Service can run incremental transfers from MySQL, Oracle, PostgreSQL, ServiceNow, and Microsoft SQL Server.

### Materialized views over active CDC tables (2026-04)

At GA, BigQuery materialized views can be created over tables with active change data capture ingestion.

### MySQL and PostgreSQL transfers (2025-01)

The BigQuery Data Transfer Service can ingest from MySQL and PostgreSQL sources in Preview.

### PostgreSQL and SQL Server metadata transfers (2026-07)

Preview BigQuery Data Transfer Service support can transfer PostgreSQL and Microsoft SQL Server metadata into Knowledge Catalog, expanding the existing database-metadata transfer sources.
