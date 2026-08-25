# Storage, databases, and search

Use this reference for storage, databases, and search compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## Amazon S3 and EFS

### Auto-delete mixins

**Batch:** `2026-03`

ECR adds `RepositoryAutoDeleteImages`, and S3's `BucketAutoDeleteObjects` mixin graduates into `aws-cdk-lib`.

### Custom S3 replication roles

**Batch:** `2025-04`

S3 bucket replication configuration accepts a custom IAM role.

### Feature-flagged S3 public-access defaults

**Batch:** `2025-05`

Under its feature flag, `blockPublicAccess` now enables settings whose defaults are `true`.

### Imported EFS subnets

**Batch:** `2025-04`

EFS constructs support imported subnets.

### KMS encryption for S3 Tables

**Batch:** `2025-05`

The S3 Tables `TableBucket` L2 construct supports KMS encryption.

### OpenSearch S3 Vectors engine

**Batch:** `2026-03`

OpenSearch Service constructs support the S3 Vectors engine.

### S3 attribute-based access control

**Batch:** `2026-03`

S3 constructs support attribute-based access control.

### S3 blocked encryption types

**Batch:** `2026-03`

`Bucket` accepts `blockedEncryptionTypes` for configuring encryption types that must not be used.

### S3 bucket naming properties

**Batch:** `2026-05`

S3 constructs support `bucketNamePrefix` and `bucketNamespace`.

### S3 Files Lambda integration

**Batch:** `2026-04`

S3 Files now has a Lambda L1 integration.

### S3 object replication

**Batch:** `2025-01`

S3 constructs gained support for configuring object replication, including replication-rule filters.

### S3 Tables and namespaces

**Batch:** `2025-08`

S3 Tables provides L2 constructs for `Table` and `Namespace` resources.

### S3 Tables L2 constructs

**Batch:** `2025-04`

Amazon S3 Tables has L2 constructs.

## Amazon RDS, Aurora, and DocumentDB

### Added Aurora MySQL versions

**Batch:** `2025-05`

The RDS catalog adds Aurora MySQL `2.11.6`, `2.12.5`, and `3.04.4`.

### Added database engine versions

**Batch:** `2025-04`

The database engine catalog adds SQL Server `15.00.4430.1.v1` and `16.00.4185.3.v1`, plus Aurora MySQL `2.12.4` and `3.08.2`.

### Added RDS engine versions

**Batch:** `2025-01`

The RDS catalog adds PostgreSQL `11.22-rds.20241121` and MariaDB `11.4.4`, `10.11.10`, `10.6.20`, and `10.5.27`.

### Added RDS engine versions

**Batch:** `2025-03`

The RDS catalog adds MySQL `5.7.44` (patch), `8.0.41`, and `8.4.4`, plus MariaDB `10.5.28`, `10.6.21`, `10.11.11`, and `11.4.5`.

### Additional RDS log exports

**Batch:** `2025-11`

RDS constructs support the `instance` and `iam-db-auth-error` CloudWatch log exports.

### Aurora Database Insights

**Batch:** `2025-02`

RDS constructs support Database Insights for Aurora databases.

### Aurora instance availability zones

**Batch:** `2025-03`

RDS constructs allow an Availability Zone to be specified for an Aurora instance.

### Aurora Limitless PostgreSQL 16.6

**Batch:** `2025-02`

RDS constructs support PostgreSQL 16.6 for Aurora Limitless Database.

### Aurora Serverless v2 auto-pause

**Batch:** `2025-06`

RDS constructs support configuring auto-pause for Aurora Serverless v2 clusters.

### Database Insights for RDS instances

**Batch:** `2025-07`

RDS instance constructs support Database Insights, extending the earlier Aurora support.

### Deferred RDS modifications

**Batch:** `2025-02`

RDS constructs can schedule modifications for the next maintenance window instead of applying them immediately.

### DocumentDB credentials and maintenance windows

**Batch:** `2026-08`

DocumentDB constructs support managed passwords; `DatabaseCluster` also supports per-instance maintenance windows.

### DocumentDB serverless clusters

**Batch:** `2025-09`

DocumentDB constructs support serverless clusters.

### Native RDS Secrets Manager integration

**Batch:** `2026-07`

RDS cluster and instance constructs support the service-native Secrets Manager integration for credentials.

### RDS cluster scalability spelling

**Batch:** `2025-01`

Use `clusterScalabilityType`; the earlier `clusterScailabilityType` spelling was erroneous.

### RDS cluster-snapshot restores

**Batch:** `2025-06`

`DatabaseInstanceFromSnapshot` accepts `clusterSnapshotIdentifier` for restoring an instance from a DB cluster snapshot.

### RDS engine lifecycle

**Batch:** `2025-04`

RDS constructs support engine-lifecycle configuration.

### RDS Performance Insights disablement

**Batch:** `2026-03`

`enablePerformanceInsights: false` is now honored even when other Performance Insights properties are supplied.

### RDS Proxy default authentication schemes

**Batch:** `2026-01`

RDS Proxy constructs support configuring a default authentication scheme.

### RDS proxy, backup, and lookup support

**Batch:** `2025-09`

RDS adds a `DatabaseProxyEndpoint` L2 construct, and database clusters can retain automated backups. Instances returned by `DatabaseInstance.fromLookup()` can use `connections`.

### RDS replication sources

**Batch:** `2025-03`

`DatabaseCluster` accepts `replicationSourceIdentifier`.

### Standalone RDS parameter groups

**Batch:** `2026-03`

RDS `ParameterGroup` supports standalone resource creation.

## Amazon OpenSearch Service

### OpenSearch 3.1

**Batch:** `2025-10`

The OpenSearch engine-version catalog includes version 3.1.

### OpenSearch automatic-update opt-out

**Batch:** `2026-03`

`enableAutoSoftwareUpdate: false` is now reflected in the synthesized CloudFormation template.

### OpenSearch domain node options

**Batch:** `2025-03`

The OpenSearch `Domain` construct supports node options.

### OpenSearch gp3 throughput

**Batch:** `2026-07`

OpenSearch accepts gp3 EBS throughput values up to 2000 MiB/s.

### OpenSearch I8G storage validation

**Batch:** `2025-10`

OpenSearch validation recognizes I8G nodes as not requiring EBS volumes.

### OpenSearch nodes without EBS

**Batch:** `2025-01`

OpenSearch validation recognizes I4I and R7GD nodes as not requiring EBS volumes.

### OpenSearch OI2 local storage

**Batch:** `2026-02`

OpenSearch Service constructs support the OI2 instance type with local NVMe storage.

### OpenSearch TLS default

**Batch:** `2025-06`

OpenSearch domains now default to the TLS 1.2 security policy.

## Amazon DynamoDB

### Compound GSI keys

**Batch:** `2025-11`

DynamoDB constructs support compound keys for global secondary indexes.

### Cross-account DynamoDB global-table replication

**Batch:** `2026-02`

DynamoDB constructs support cross-account replication for global tables.

### DynamoDB contributor-insights modes

**Batch:** `2025-08`

DynamoDB constructs now support `ContributorInsightsMode` for configuring contributor insights.

### DynamoDB grant validation

**Batch:** `2026-03`

DynamoDB grant operations now throw when the grantee is an unsupported `ServicePrincipal`.

### DynamoDB index permissions

**Batch:** `2026-03`

DynamoDB resource policies now include index ARNs when indexes are added after permissions have already been granted.

### DynamoDB point-in-time recovery specification

**Batch:** `2025-02`

DynamoDB adds a point-in-time recovery specification and deprecates the older recovery setting.

### DynamoDB stream resource policies

**Batch:** `2026-05`

DynamoDB stream constructs support resource policies.

### DynamoDB TableV2 MRSC

**Batch:** `2025-08`

`TableV2` supports MRSC configuration.

## Other data stores

### ElastiCache engine type classes

**Batch:** `2026-06`

ElastiCache replaces the `CacheEngine` and `UserEngine` enums with enum-like classes, changing the public type contract for code that consumes them.

### Kendra template configuration type

**Batch:** `2025-07`

In the experimental Kendra L1 bindings, `CfnDataSource.TemplateConfigurationProperty.template` changed from `string` to `json`.
