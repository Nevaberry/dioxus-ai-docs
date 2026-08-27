# Storage and Databases

Topic-organized compatibility guidance for AWS CDK.

## AWS Backup

### Backup schedule time zones (`2025-07`)

Backup constructs support `ScheduleExpressionTimezone`.

### Token-safe Backup and Lambda validation (`2026-07`)

Backup lifecycle and vault-lock durations can be tokenized. Lambda validation also accepts tokenized provisioned-concurrency and asynchronous-invoke configuration values.

## Amazon DocumentDB

### DocumentDB credentials and maintenance windows (`2026-08`)

DocumentDB constructs support managed passwords; `DatabaseCluster` also supports per-instance maintenance windows.

### DocumentDB serverless clusters (`2025-09`)

DocumentDB constructs support serverless clusters.

## Amazon DynamoDB

### Compound GSI keys (`2025-11`)

DynamoDB constructs support compound keys for global secondary indexes.

### Cross-account DynamoDB global-table replication (`2026-02`)

DynamoDB constructs support cross-account replication for global tables.

### DynamoDB contributor-insights modes (`2025-08`)

DynamoDB constructs now support `ContributorInsightsMode` for configuring contributor insights.

### DynamoDB grant validation (`2026-03`)

DynamoDB grant operations now throw when the grantee is an unsupported `ServicePrincipal`.

### DynamoDB index permissions (`2026-03`)

DynamoDB resource policies now include index ARNs when indexes are added after permissions have already been granted.

### DynamoDB point-in-time recovery specification (`2025-02`)

DynamoDB adds a point-in-time recovery specification and deprecates the older recovery setting.

### DynamoDB stream resource policies (`2026-05`)

DynamoDB stream constructs support resource policies.

### DynamoDB TableV2 MRSC (`2025-08`)

`TableV2` supports MRSC configuration.

## Amazon OpenSearch Service

### OpenSearch 3.1 (`2025-10`)

The OpenSearch engine-version catalog includes version 3.1.

### OpenSearch automatic-update opt-out (`2026-03`)

`enableAutoSoftwareUpdate: false` is now reflected in the synthesized CloudFormation template.

### OpenSearch domain node options (`2025-03`)

The OpenSearch `Domain` construct supports node options.

### OpenSearch gp3 throughput (`2026-07`)

OpenSearch accepts gp3 EBS throughput values up to 2000 MiB/s.

### OpenSearch I8G storage validation (`2025-10`)

OpenSearch validation recognizes I8G nodes as not requiring EBS volumes.

### OpenSearch nodes without EBS (`2025-01`)

OpenSearch validation recognizes I4I and R7GD nodes as not requiring EBS volumes.

### OpenSearch OI2 local storage (`2026-02`)

OpenSearch Service constructs support the OI2 instance type with local NVMe storage.

### OpenSearch S3 Vectors engine (`2026-03`)

OpenSearch Service constructs support the S3 Vectors engine.

### OpenSearch TLS default (`2025-06`)

OpenSearch domains now default to the TLS 1.2 security policy.

## Amazon RDS and Aurora

### Added Aurora MySQL versions (`2025-05`)

The RDS catalog adds Aurora MySQL `2.11.6`, `2.12.5`, and `3.04.4`.

### Added database engine versions (`2025-04`)

The database engine catalog adds SQL Server `15.00.4430.1.v1` and `16.00.4185.3.v1`, plus Aurora MySQL `2.12.4` and `3.08.2`.

### Added RDS engine versions (`2025-01`)

The RDS catalog adds PostgreSQL `11.22-rds.20241121` and MariaDB `11.4.4`, `10.11.10`, `10.6.20`, and `10.5.27`.

### Added RDS engine versions (`2025-03`)

The RDS catalog adds MySQL `5.7.44` (patch), `8.0.41`, and `8.4.4`, plus MariaDB `10.5.28`, `10.6.21`, `10.11.11`, and `11.4.5`.

### Additional RDS log exports (`2025-11`)

RDS constructs support the `instance` and `iam-db-auth-error` CloudWatch log exports.

### Aurora Database Insights (`2025-02`)

RDS constructs support Database Insights for Aurora databases.

### Aurora instance availability zones (`2025-03`)

RDS constructs allow an Availability Zone to be specified for an Aurora instance.

### Aurora Limitless PostgreSQL 16.6 (`2025-02`)

RDS constructs support PostgreSQL 16.6 for Aurora Limitless Database.

### Aurora Serverless v2 auto-pause (`2025-06`)

RDS constructs support configuring auto-pause for Aurora Serverless v2 clusters.

### Database Insights for RDS instances (`2025-07`)

RDS instance constructs support Database Insights, extending the earlier Aurora support.

### Deferred RDS modifications (`2025-02`)

RDS constructs can schedule modifications for the next maintenance window instead of applying them immediately.

### IAM and RDS lookups (`2025-04`)

`Role.fromLookup()` and `DatabaseInstance.fromLookup()` can resolve existing IAM roles and RDS database instances.

### Native RDS Secrets Manager integration (`2026-07`)

RDS cluster and instance constructs support the service-native Secrets Manager integration for credentials.

### RDS cluster scalability spelling (`2025-01`)

Use `clusterScalabilityType`; the earlier `clusterScailabilityType` spelling was erroneous.

### RDS cluster-snapshot restores (`2025-06`)

`DatabaseInstanceFromSnapshot` accepts `clusterSnapshotIdentifier` for restoring an instance from a DB cluster snapshot.

### RDS engine lifecycle (`2025-04`)

RDS constructs support engine-lifecycle configuration.

### RDS Performance Insights disablement (`2026-03`)

`enablePerformanceInsights: false` is now honored even when other Performance Insights properties are supplied.

### RDS Proxy default authentication schemes (`2026-01`)

RDS Proxy constructs support configuring a default authentication scheme.

### RDS proxy, backup, and lookup support (`2025-09`)

RDS adds a `DatabaseProxyEndpoint` L2 construct, and database clusters can retain automated backups. Instances returned by `DatabaseInstance.fromLookup()` can use `connections`.

### RDS replication sources (`2025-03`)

`DatabaseCluster` accepts `replicationSourceIdentifier`.

### Standalone RDS parameter groups (`2026-03`)

RDS `ParameterGroup` supports standalone resource creation.

## Amazon S3

### Custom S3 replication roles (`2025-04`)

S3 bucket replication configuration accepts a custom IAM role.

### Empty S3 deployment data (`2025-10`)

S3 Deployment's `Source.data()` accepts an empty string.

### Encrypted SNS notification policies (`2025-05`)

Under its feature flag, S3 notifications to a KMS-encrypted SNS topic add a key policy that trusts S3.

### Feature-flagged S3 public-access defaults (`2025-05`)

Under its feature flag, `blockPublicAccess` now enables settings whose defaults are `true`.

### Firehose destination time zones (`2025-07`)

Kinesis Data Firehose S3 destinations support custom time-zone settings.

### Firehose output integrations (`2025-04`)

Kinesis Data Firehose supports S3 file-extension formats, and CloudWatch Logs destination constructs can target Amazon Data Firehose.

### Firehose record-format conversion (`2025-10`)

Kinesis Data Firehose `DeliveryStream` constructs support record-format conversion for S3 bucket destinations.

### Lambda stream failures to S3 (`2025-03`)

Lambda event sources for Kinesis and DynamoDB streams support S3 as an on-failure destination.

### Opt-in JSON escaping (`2025-04`)

`Source.jsonData()` no longer escapes JSON automatically. Pass `{ escape: true }` as its third argument when special characters require the former behavior: `Source.jsonData("config.json", data, { escape: true })`.

### S3 attribute-based access control (`2026-03`)

S3 constructs support attribute-based access control.

### S3 blocked encryption types (`2026-03`)

`Bucket` accepts `blockedEncryptionTypes` for configuring encryption types that must not be used.

### S3 bucket naming properties (`2026-05`)

S3 constructs support `bucketNamePrefix` and `bucketNamespace`.

### S3 object replication (`2025-01`)

S3 constructs gained support for configuring object replication, including replication-rule filters.

### Source.jsonData list-token resolution (`2025-08`)

S3 Deployment's `Source.jsonData()` now resolves tokens contained in lists.

### VPC-enabled bucket deployments (`2025-11`)

S3 `BucketDeploymentProps` accepts security groups.

## Other Storage and Databases

### Imported EFS subnets (`2025-04`)

EFS constructs support imported subnets.

## S3 Tables and S3 Files

### KMS encryption for S3 Tables (`2025-05`)

The S3 Tables `TableBucket` L2 construct supports KMS encryption.

### S3 Tables and namespaces (`2025-08`)

S3 Tables provides L2 constructs for `Table` and `Namespace` resources.

### S3 Tables L2 constructs (`2025-04`)

Amazon S3 Tables has L2 constructs.
