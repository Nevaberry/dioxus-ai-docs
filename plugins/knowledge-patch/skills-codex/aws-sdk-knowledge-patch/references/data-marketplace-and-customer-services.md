# Data, marketplace, and customer-facing services

Use this reference for request and response changes in analytics, catalogs,
data movement, billing, Marketplace, Partner Central, Connect, location,
communications, and media services.

## DataZone, Glue, and Clean Rooms

### DataZone Snowflake connections (2026-06)

DataZone `CreateConnection` accepts the `SNOWFLAKE` connection type and
`snowflakeProperties`, including connection details, a Secrets Manager secret,
an Athena spill bucket, and identity mapping.

### Clean Rooms intermediate tables (2026-06)

Clean Rooms collaboration models support intermediate tables. Preserve them in
collaboration request and response handling.

### Glue Data Catalog asset updates (2026-06)

Glue `UpdateAsset` changes the business name and description of an existing
Data Catalog asset.

### Clean Rooms CR.8X workers (2026-07-2)

Clean Rooms and Clean Rooms ML support the `CR.8X` worker type for SQL
workloads, providing 32 vCPUs.

### Glue connector and data-quality controls (2026-07-2)

Glue REST API connectors support filtering, partitioning, and VPC connectivity.
Data-quality APIs add batch retrieval of evaluation runs, anomaly
`ObservationScope` and `ObservationMode`, Data Catalog result tables, and custom
recommendation log-group paths.

### DataZone subscription-grant scope (2026-08)

`GetSubscriptionGrant` returns the materialized asset scope name used to map
Lake Formation data-cell filters or Redshift views to a subscription grant.

### Glue glossary terms on iterable items (2026-08)

Glue Data Catalog forms can associate glossary terms with iterable form items
such as table columns.

### Clean Rooms custom-rule controls (2026-08)

Custom analysis rules support minimum aggregation thresholds and comparison
controls.

### Clean Rooms redacted query logs (2026-08)

Clean Rooms can export redacted query-execution logs.

### Glue Data Catalog exports (2026-08)

`PutDataCatalogExportConfiguration` configures Glue Data Catalog metadata
exports to system tables stored in S3 Tables.

## AppConfig, Feature Store, OpenSearch, and QuickSight

### AppConfig experiments (2026-06)

AppConfig supports A/B tests, multivariate tests, and gradual feature-rollout
experiments.

### Feature Store batch and list operations (2026-06)

The SageMaker Feature Store runtime provides `ListRecords` and
`BatchWriteRecord`.

### AppConfig experiment conflict errors (2026-07)

Experiment Run APIs can return `ConflictException`. Add it to retry and
concurrency handling where an experiment state transition can race.

### OpenSearch saved-object migration (2026-07)

OpenSearch APIs migrate dashboards, visualizations, index patterns, and other
saved objects from a data source into an application workspace, with export
filters and conflict-resolution strategies.

### OpenSearch optimized domains (2026-07)

Creating a Mustang domain requires `EngineMode=OPTIMIZED` together with
`UseCase=OBSERVABILITY` or `MIXED`. Omitting that pairing creates a regular
`GENERAL` domain.

### OpenSearch Insights feedback (2026-07)

The OpenSearch Insights Feedback API submits feedback about Insight API
results.

### QuickSight file-source tables (2026-07)

QuickSight supports `FileSource` physical tables, allowing file-backed datasets.

### QuickSight knowledge bases and TopicV2 (2026-07-2)

QuickSight adds `CreateKnowledgeBase` and `UpdateKnowledgeBase`, plus TopicV2
management APIs whose topics can be used in analyses.

## Redshift, HealthLake, data movement, and databases

### Redshift Serverless restore preservation (2026-07-2)

Restoring a snapshot to a Redshift Serverless namespace can preserve
data-sharing, zero-ETL, and S3 event integrations.

### Redshift generated-model additions (2026-07-2)

`CreateCluster`, `ModifyCluster`, and `ResizeCluster` accept `rg.large` and
`rg.12xlarge` node types. Redshift Data `workgroupArn` validation accepts the
EUSC partition.

### HealthLake source-to-FHIR transformation (2026-07-2)

HealthLake preview support converts CSV and C-CDA input to FHIR R4 through
reusable mapping profiles, synchronous or asynchronous jobs, provenance
tracking, and drift detection.

### Omics task identifiers (2026-07-2)

`GetRunTask` and `ListRunTasks` return the task UUID, allowing callers to
identify individual run tasks by UUID.

### Autonomous Database Secrets Manager integration (2026-07-2)

Autonomous Database admin and wallet passwords can come from customer-managed
Secrets Manager secrets. `InitializeService` controls the OCI IAM service role
used for the integration.

### Redshift Query Editor V2 Identity Center apps (2026-07-2)

Redshift provides `CreateQev2IdcApplication`, `DescribeQev2IdcApplications`,
`ModifyQev2IdcApplication`, and `DeleteQev2IdcApplication` for Query Editor V2
IAM Identity Center applications.

### Redshift Data long polling and sessions (2026-07-2)

Five Redshift Data operations accept `wait-time-seconds` for long polling.
`ListSessions` exposes sessions, and `BatchExecuteStatement` accepts
`execution-mode`.

### DataSync Enhanced mode expansion (2026-07-2)

Enhanced mode works agentlessly with EFS and FSx for Lustre, and with an agent
for HDFS with TDE, Azure Blob, and object-storage locations. HDFS can use
multiple NameNodes for high availability, and Enhanced-mode agents can run on
Hyper-V.

### Redshift password-update unlock behavior (2026-08)

Updating an admin password through Redshift `ModifyCluster` or Redshift
Serverless `UpdateNamespace` unlocks the admin and resets the failed-login
counter when account-lockout security is enabled.

### HealthLake import provenance (2026-08)

HealthLake `StartFHIRImportJob` accepts `provenanceEnabled` to retain provenance
for imported FHIR data.

## Marketplace, billing, and partner operations

### Partner Central Marketplace associations (2026-06)

Partner Central `Associate` and `Disassociate` accept
`AwsMarketplaceSolutions` and `AwsMarketplaceProducts`; `GetOpportunity`
returns them, and `ListSolutions` adds `AwsMarketplaceSolutionArn`.

### Partner Central revenue measurement (2026-07)

The Partner Central Revenue Measurement client creates, manages, and tracks
revenue attributions and Marketplace revenue-share allocations.

### Marketplace Catalog reseller-role filtering (2026-07)

Marketplace Catalog `ListEntities` accepts a `ResellerRole` filter for
`ResaleAuthorization` entities.

### Marketplace metering window (2026-07)

`BatchMeterUsage` accepts usage records for 24 hours after the metered event.
The six-hour grace period at the end of a billing cycle still applies.

### Billing credits and preferences (2026-07)

Billing APIs retrieve credit details and monthly allocation history, redeem
promotional codes, and configure credit sharing and billing preferences.

### Marketplace metering identity migration (2026-07-2)

For new SaaS integrations, `ResolveCustomer` does not populate
`CustomerIdentifier` and `BatchMeterUsage` does not support it. Use
`CustomerAWSAccountId` and `LicenseArn`.

### Procurement portal OTP validation (2026-07-2)

`SendProcurementPortalValidation` and `VerifyProcurementPortalValidation`
activate invoicing procurement-portal preferences through a one-time passcode.

### Partner Central qualification and lead workflows (2026-07-2)

Partners can associate a subsidiary account's qualifications with a primary
account, sharing qualifications and consolidating scorecards. Leads require
only five fields, accept free text elsewhere, and return enrichment such as
propensity scores and lead readiness.

### Partner Central headquarters validation (2026-07-2)

`StartProfileUpdateTask` accepts an optional headquarters location using ISO
3166 country and subdivision codes. When supplied, both codes are required.

### Compressed BCM data exports (2026-07-2)

Billing and Cost Management data exports can deliver CSV reports in ZIP
archives.

### Enterprise Support billing APIs (2026-07-2)

`GetEnterpriseSupportChargeSummary`, `GetEnterpriseSupportContractDetails`, and
`ListEnterpriseSupportLinkedAccountCharges` expose Enterprise Support billing
data formerly available only through Concierge or Support.

### Marketplace Catalog offer filters (2026-07-2)

Marketplace Catalog `ListEntities` accepts `TargetAgreementId`,
`TargetAgreementIntent`, and `CreatedBySource` filters for `Offer` entities.

### Marketplace resource assessments (2026-08)

Marketplace Catalog adds `DescribeAssessment` and `ListAssessments` for
validation issues exposed through Assessment resources.

### Marketplace net-payment terms (2026-08)

Marketplace Agreement `GetAgreementTerms` returns
`AcceptedTerm.netPaymentTerm`; Marketplace Discovery `GetOfferTerms` returns
the corresponding offer term. `paymentDuePeriod` is an ISO 8601 duration such
as `P30D`.

### Deadline persistent-volume costs (2026-08)

Deadline Cloud usage data reports persistent-volume costs separately from
compute and license costs for per-fleet analysis.

## Amazon Connect and customer engagement

### Connect recording import and analytics (2026-06)

Connect adds `CreateAttachedFile` for importing call recordings and
`StartContactConversationalAnalyticsJob` for conversational analytics.

### Connect Health validation (2026-06)

Connect Health input validation accepts Unicode characters and Markdown table
syntax. Do not reject either with older local validators.

### Connect contact-data deletion (2026-07)

`DeleteContactData` deletes contact PII including the customer endpoint,
additional email recipients, and email subject.

### Connect authorization and session APIs (2026-07)

Connect provides `CreateAuthCode` and `DeleteSession`.

### Customer Profiles recommendation diversity and model rollback (2026-07)

Customer Profiles adds `diversityConfig` to `recommenderConfig` and model
versioning for rolling trained models back.

### Connect outbound web notifications (2026-07)

`SendOutboundWebNotification` sends notifications to end-customer chat-widget
sessions. It can be invoked only by the Connect Outbound Campaigns service
principal.

### Connect extraction definitions (2026-08)

Connect provides create, describe, update, delete, and list operations for
extraction definitions, plus Rules event sources for after-contact work and an
Extract Information action.

### Connect assistant contacts and WebRTC errors (2026-08)

`StartAssistantContact` starts an AI-agent-handled chat. `StartWebRTCContact`
accepts `SegmentAttributes` and models access denial as
`AccessDeniedException` instead of an internal server error.

### Connect custom metrics (2026-08)

Connect provides seven operations for creating, describing, updating, deleting,
and otherwise managing custom analytics metrics with thresholds, filters, and
calculations.

### Malay automated contact evaluations (2026-08)

Connect automated evaluation forms support Malay.

### Connect in-progress task templates (2026-08)

`UpdateContactTaskTemplate` changes the task template on an in-progress Connect
task contact without creating a replacement task.

## Location and wireless services

### IoT Wireless multicast defaults (2026-07)

Multicast Group APIs can store default session downlink transmission parameters,
so starting a multicast session during FUOTA need not provide them explicitly.

### Places V2 address and mobility fields (2026-07)

Places V2 adds `AddressNamesMode`, `AddressNameTranslations`, `MobilityMode`,
`PostalCodeMode`, `SecondaryAddresses`, and `DriveThrough` for formatting,
translations, travel-aware search, multi-city postal codes, and unit-level
addresses.

### Dynamic-map POI controls (2026-08)

Location Maps `GetStyleDescriptor` accepts `PoiDensity` from `Off` through
`VeryDense`, and `PoiCategories` with up to nine categories for HERE and Grab
styles.

## Media, transcription, and social messaging

### IVS post-roll ad configuration (2026-07)

IVS ad-configuration resources support `postRollConfiguration`.

### MediaTailor dual-stack response fields (2026-07)

MediaTailor SSAI and Channel Assembly responses include dual-stack IPv4 and
IPv6 endpoint fields.

### MediaConvert output controls (2026-07)

MediaConvert supports integer-second duration normalization and an option to
disable explicit weighted prediction.

### MediaTailor decision-server controls (2026-07-2)

MediaTailor playback configurations can set ad-decision-server timeout and
concurrency fields.

### MediaPackage non-epoch-locked CMAF ingest (2026-07-2)

MediaPackageV2 channels support CMAF ingest that is not epoch-locked.

### Transcribe streaming transcript form (2026-07-2)

Streaming Transcribe accepts `TranscriptFormat` to select spoken or written
forms for numeric and formatted output.

### MediaConvert archive output (2026-07-2)

MediaConvert outputs can target S3 Glacier Instant Retrieval. Kantar server URL
validation also accepts the Fifty5Blue domain.

### MediaLive SCTE-35 passthrough (2026-08)

MediaLive can pass SCTE-35 markers through without inserting an IDR frame for
CMAF Ingest, MediaPackage V2, and transport-stream outputs.

### MediaConnect recovery-latency tuning (2026-08)

MediaConnect Router inputs and outputs can tune internal recovery latency to
trade stream quality against end-to-end latency.

### MediaLive multicast source addresses (2026-08)

MediaLive Anywhere multicast destinations accept `VirtualSourceAddress` to set
the source IP when downstream networks filter multicast traffic by source.

### Elemental Inference fixture search (2026-08)

Elemental Inference adds `SearchFixtures` and `DataSourceConfiguration` for
mapping fixture event data onto clipping outputs.

### MediaPackage stream-name output mode (2026-08)

MediaPackage V2 origin endpoints accept `StreamNameOutputMode` to use
encoder-assigned stream names in egress manifests instead of numeric stream
indexes.

### MediaTailor VAST Ad Buffet sequencing (2026-08)

MediaTailor playback configurations accept `AdSequencingMode` for ordered VAST
Ad Buffet insertion, with standalone ads as fallbacks when a sequenced ad is
unavailable.

### WhatsApp Conversions APIs (2026-08)

The Social Messaging client supports WhatsApp Conversions APIs.

### Concurrent MediaTailor functions (2026-08)

MediaTailor's Concurrent Executor function type runs independent child
functions in parallel within one lifecycle hook.

## Payments and other customer data

### UnionPay session-key derivation (2026-07-2)

Payment Cryptography Data supports UnionPay session-key derivation in
`GenerateAuthRequestCryptogram`, `VerifyAuthRequestCryptogram`, `GenerateMac`,
and `VerifyMac`.
