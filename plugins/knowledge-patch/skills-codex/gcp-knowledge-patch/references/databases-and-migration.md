# Databases and Migration

Use this reference for databases and migration compatibility details and current behavior.

## Federation, external datasets, and reverse ETL

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


### RAG Engine deployment modes (2026-04)

Public-Preview RAG Engine Serverless mode provides a fully managed database for RAG resources without database provisioning or scaling. Deployments can switch between Serverless mode and Spanner mode, which uses dedicated, isolated database instances.


### Reverse ETL to AlloyDB (2026-04)

Preview `EXPORT DATA` statements can reverse-ETL BigQuery data to AlloyDB.


## Transfers, assessment, and metadata migration

### BigQuery Migration Service billing-account requirement (2026-06)

New users have required a Cloud Billing account for BigQuery Migration Service since March 9, 2026, and all users have required one since May 18, even though the service remains without charge.


### Data-service remote MCP servers (2026-03)

Preview remote MCP servers let agents manage Pub/Sub topics, subscriptions, and snapshots and publish messages; create, manage, and run BigQuery data transfers; and use BigQuery Migration Service to translate SQL to GoogleSQL, generate DDL, and explain translations.


### External catalog metadata migration (2026-04)

Preview migration tooling can move metadata from Apache Hive Metastore or an Apache Iceberg REST Catalog into BigLake tables for Apache Iceberg.


### Hadoop and Cloudera migration assessment (2025-06)

In Preview, BigQuery migration assessment can assess workflows that use Cloudera and Apache Hadoop.


### Hadoop migration workflows (2025-07)

Preview migration tooling can use `dwh-migration-dumper` to capture metadata, translate permissions from Hadoop, Hive, and Ranger HDFS to BigQuery, and move tables from an HDFS data lake to Google Cloud.


### Impala and GoogleSQL translation (2025-11)

In Preview, the interactive, API, and batch SQL translators accept Apache Impala SQL for Cloudera or Hadoop migrations and GoogleSQL for iterative rewrites of already-translated queries, including YAML-configured customizations.


### Informatica migration assessment (2025-09)

Preview BigQuery migration assessment can assess the complexity of moving an Informatica platform to BigQuery.


### Migration-service organization policies (2025-11)

Preview custom organization policies can allow or deny specific BigQuery migration operations, including disabling AI suggestions during a migration.


### Redshift Serverless migration assessment (2025-04)

Preview BigQuery migration assessment can assess Amazon Redshift Serverless environments.


### Snowflake migration assessment (2026-03)

BigQuery migration assessment for estimating the complexity of a Snowflake-to-BigQuery migration is GA.


### Snowflake SQL translation mapping (2026-04)

BigQuery Migration Service translation from Snowflake SQL to GoogleSQL is GA and now maps Snowflake `INTEGER` and zero-scale `NUMERIC` values with precision up to 38 to GoogleSQL `INT64` by default.


### SQL translation metadata caching (2025-03)

Preview metadata caching for BigQuery SQL translation can reduce latency on later translation requests.


### Teradata migration schema mappings (2025-05)

In Preview, a Teradata transfer can use BigQuery translation-engine output as its schema mapping.


## SQL translation and schema conversion

### Gemini-enhanced SQL translation (2025-06)

GA SQL translation features can create Gemini-based configuration YAML for AI suggestions and review batch output in code and configuration tabs. Preview interactive translation rules can customize SQL inputs.


### SQL translation optimization files (2025-04)

GA BigQuery SQL translation accepts configuration YAML files that optimize translated queries.
