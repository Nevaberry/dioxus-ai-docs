# Storage, Build, and Artifacts

Use this reference for storage, build, and artifacts compatibility details and current behavior.

## Cloud Storage transfers and data movement

### BigLake metastore Iceberg REST catalog (2025-06)

The Preview Apache Iceberg REST catalog in BigLake metastore lets open-source query engines access Iceberg data in Cloud Storage through a shared catalog.


### Dataplex automatic discovery (2025-04)

GA Dataplex automatic discovery scans Cloud Storage data, extracts and catalogs metadata, and creates BigLake, external, or object tables.


### Event-driven Cloud Storage transfers (2025-05)

GA event-driven transfers from Cloud Storage to BigQuery can start automatically when objects are added or modified in a bucket.


### Iceberg REST catalog credential vending (2025-09)

In Preview, Lakehouse runtime's Iceberg REST catalog can vend credentials so catalog users do not need direct access to the underlying Cloud Storage buckets.


## Lakehouse storage and Iceberg

### BigLake Iceberg REST catalog federation (2025-10)

The BigLake metastore Iceberg REST catalog is GA and adds BigQuery catalog federation and catalog management in the Google Cloud console.


### BigLake Iceberg table partitioning (2025-11)

BigLake tables for Apache Iceberg in BigQuery support partitioning in Preview.


### BigLake Iceberg transactions (2025-08)

In Preview, BigLake Iceberg tables in BigQuery support multi-statement transactions.


### BigLake product transitions (2025-06)

BigQuery metastore is renamed BigLake metastore and is GA, while the previous BigLake metastore is renamed BigLake metastore (classic). BigQuery tables for Apache Iceberg are renamed BigLake tables for Apache Iceberg in BigQuery and are also GA.


### Conversational analytics over lakehouse catalogs (2026-04)

Preview BigQuery conversational analytics can query lakehouse tables connected to an Apache Iceberg REST catalog or federated to an external catalog.


### Data product renames (2026-04)

Dataproc is now Managed Service for Apache Spark; BigLake is Google Cloud Lakehouse; BigLake metastore is Lakehouse runtime catalog; Dataplex Universal Catalog is Knowledge Catalog; and Looker Studio is Data Studio. API, client-library, CLI, and IAM names remain unchanged, but Data Studio moves from `lookerstudio.google.com` to `datastudio.google.com`, so proxy ACLs might require the new domain.


### Dataform-managed BigLake Iceberg tables (2025-11)

At GA, Dataform can automate creation of BigLake tables for Apache Iceberg in BigQuery.


### Iceberg external-table time travel (2025-09)

GA BigQuery queries can read snapshots retained in an Iceberg external table's metadata with `FOR SYSTEM_TIME AS OF`.

```sql
SELECT * FROM `project.dataset.iceberg_table`
FOR SYSTEM_TIME AS OF TIMESTAMP '2025-09-15 12:00:00+00';
```


### Iceberg merge-on-read (2025-03)

GA Iceberg external tables support merge-on-read, including queries over position deletes and equality deletes.


### Iceberg version 3 external tables (2026-04)

Preview BigQuery Apache Iceberg external tables support Iceberg version 3, including binary deletion vectors.
