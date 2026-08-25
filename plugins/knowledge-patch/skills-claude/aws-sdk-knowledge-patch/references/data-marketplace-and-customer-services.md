# Data, marketplace, and customer-facing services

## Amazon Connect and customer experience

### Connect

- **Connect recording import and analytics (`2026-06`).** `CreateAttachedFile`
  imports call recordings; `StartContactConversationalAnalyticsJob` runs
  conversational analytics.
- **Connect Health validation (`2026-06`).** Input validation accepts Unicode
  characters and Markdown table syntax.
- **Connect contact-data deletion (`2026-07`).** `DeleteContactData` deletes
  contact PII including the customer endpoint, additional email recipients,
  and email subject.
- **Connect authorization and session APIs (`2026-07`).** The client adds
  `CreateAuthCode` and `DeleteSession`.
- **Connect outbound web notifications (`2026-07`).**
  `SendOutboundWebNotification` targets end-customer chat-widget sessions and
  can be called only by the Connect Outbound Campaigns service principal.
- **Connect email attachment limit (`2026-07-2`).** Customer emails accept up
  to 50 attachments rather than 10. Each remains limited to 20 MB and the
  whole email to 25 MB.
- **Connect extraction definitions (`2026-08`).** The client adds create,
  describe, update, delete, and list operations for extraction definitions,
  Rules event sources for after-contact work, and an Extract Information
  action.
- **Connect assistant contacts and WebRTC errors (`2026-08`).**
  `StartAssistantContact` starts an AI-agent-handled chat.
  `StartWebRTCContact` accepts `SegmentAttributes` and reports access denial as
  `AccessDeniedException` rather than an internal server error.
- **Connect custom metrics (`2026-08`).** Seven operations create, describe,
  update, delete, and otherwise manage custom analytics metrics with
  thresholds, filters, and calculations.
- **Malay automated contact evaluations (`2026-08`).** Automated evaluation
  forms accept Malay as a language.
- **Connect in-progress task templates (`2026-08`).**
  `UpdateContactTaskTemplate` changes the template on an in-progress task
  contact without creating a replacement task.

### Cognito, profiles, and messaging

- **Cognito provisioned API limits (`2026-07`).** `GetProvisionedLimit` and
  `UpdateProvisionedLimit` read and change provisioned User Pools API limits.
- **Cognito SMS delivery and factor inspection (`2026-07-2`).**
  `SmsConfigurationType` accepts `EumsSms` to use AWS End User Messaging for
  MFA and verification. `AdminGetUserAuthFactors` returns configured password,
  SMS, email, and TOTP factors.
- **Customer Profiles recommendation diversity and model rollback (`2026-07`).**
  `recommenderConfig` accepts `diversityConfig`; rolling trained models now
  have versions that can be rolled back.
- **WhatsApp Conversions APIs (`2026-08`).** The Social Messaging client
  supports WhatsApp Conversions APIs.

### AppConfig

- **AppConfig experiments (`2026-06`).** AppConfig supports A/B tests,
  multivariate tests, and gradual feature-rollout experiments.
- **AppConfig experiment conflict errors (`2026-07`).** Experiment Run APIs
  can return `ConflictException`.

## DataZone, Clean Rooms, and Glue

### DataZone

- **DataZone Snowflake connections (`2026-06`).** `CreateConnection` accepts
  type `SNOWFLAKE` and `snowflakeProperties`, including connection details, a
  Secrets Manager secret, an Athena spill bucket, and identity mapping.
- **DataZone subscription-grant scope (`2026-08`).** `GetSubscriptionGrant`
  returns the materialized asset scope name used to map Lake Formation
  data-cell filters or Redshift views to a grant.

### Clean Rooms

- **Clean Rooms intermediate tables (`2026-06`).** Collaboration models
  support intermediate tables.
- **Clean Rooms CR.8X workers (`2026-07-2`).** Clean Rooms and Clean Rooms ML
  support `CR.8X` SQL workers with 32 vCPUs.
- **Clean Rooms custom-rule controls (`2026-08`).** Custom analysis rules
  support minimum aggregation thresholds and comparison controls.
- **Clean Rooms redacted query logs (`2026-08`).** Clean Rooms can export
  redacted query-execution logs.

### Glue

- **Glue Data Catalog asset updates (`2026-06`).** `UpdateAsset` changes the
  business name and description of a Data Catalog asset.
- **Glue connector and data-quality controls (`2026-07-2`).** Glue REST API
  connectors support filtering, partitioning, and VPC connectivity.
  Data-quality APIs add batch evaluation-run retrieval, anomaly
  `ObservationScope` and `ObservationMode`, Data Catalog result tables, and
  custom recommendation log-group paths.
- **Glue glossary terms on iterable items (`2026-08`).** Data Catalog forms
  can associate glossary terms with iterable items such as table columns.
- **Glue Data Catalog exports (`2026-08`).**
  `PutDataCatalogExportConfiguration` exports metadata to system tables stored
  in S3 Tables.

## QuickSight and OpenSearch

### QuickSight

- **QuickSight file-source tables (`2026-07`).** `FileSource` physical tables
  allow datasets backed by file sources.
- **QuickSight knowledge bases and TopicV2 (`2026-07-2`).** The client adds
  `CreateKnowledgeBase`, `UpdateKnowledgeBase`, and TopicV2 management APIs;
  TopicV2 topics can be used in analyses.
- **QuickSight permission controls (`2026-07-2`).** Custom permissions govern
  trigger scheduling, inbound email, and Quick Event triggers. Governance
  fields support deny-by-default behavior, and profiles control Amazon Quick
  browser-extension and Microsoft Office add-in access.
- **QuickSight governance APIs (`2026-08`).** APIs manage Microsoft Purview DLP
  configuration, approval policies for asset sharing, and limit profiles for
  index storage and per-user agent hours.

### OpenSearch

- **OpenSearch saved-object migration (`2026-07`).** APIs migrate dashboards,
  visualizations, index patterns, and other saved objects from a data source
  into an application workspace with export filters and conflict resolution.
- **OpenSearch optimized domains (`2026-07`).** A Mustang domain requires
  `EngineMode=OPTIMIZED` with `UseCase=OBSERVABILITY` or `MIXED`; omission
  creates a regular `GENERAL` domain.
- **OpenSearch Insights feedback (`2026-07`).** The client adds an Insights
  Feedback API for feedback on Insight API results.

## Redshift, RDS, and database services

### Entity Resolution

- **Entity Resolution delete-not-found behavior (`2026-08`).**
  `DeleteSchemaMapping`, `DeleteMatchingWorkflow`, `DeleteIdMappingWorkflow`,
  and `DeleteIdNamespace` now return a 404 `ResourceNotFoundException` for a
  missing target rather than 200 success. Idempotent deletion must handle the
  exception.

### Redshift

- **Redshift Serverless restore preservation (`2026-07-2`).** Snapshot restore
  to a namespace can preserve data-sharing, zero-ETL, and S3 event
  integrations.
- **Redshift generated-model additions (`2026-07-2`).** `CreateCluster`,
  `ModifyCluster`, and `ResizeCluster` accept `rg.large` and `rg.12xlarge`.
  Redshift Data `workgroupArn` validation accepts the EUSC partition.
- **Redshift Query Editor V2 Identity Center apps (`2026-07-2`).** The client
  adds `CreateQev2IdcApplication`, `DescribeQev2IdcApplications`,
  `ModifyQev2IdcApplication`, and `DeleteQev2IdcApplication`.
- **Redshift Data long polling and sessions (`2026-07-2`).** Five operations
  accept `wait-time-seconds`, `ListSessions` exposes sessions, and
  `BatchExecuteStatement` accepts `execution-mode`.
- **Redshift password-update unlock behavior (`2026-08`).** Updating an admin
  password through `ModifyCluster` or Serverless `UpdateNamespace` unlocks the
  admin and resets failed-login count when lockout security is enabled.

### RDS, Timestream, DSQL, and Oracle

- **RDS lifecycle, role, and storage controls (`2026-07-2`).**
  `ModifyDBInstance` and `ModifyDBCluster` can change
  `EngineLifecycleSupport`. Cluster create and restore accept
  `AssociatedRoles`; `DescribeDBInstances` returns `StorageOperationStatus`
  and `StorageOperationPercentProgress`.
- **Timestream for InfluxDB plugins and data protection (`2026-07-2`).**
  InfluxDB 3 Core and Enterprise parameter groups accept a plugin repository
  URL and optional Secrets Manager secret for Python plugins. New databases
  and clusters support customer-managed KMS keys and restore from
  customer-managed backups.
- **DSQL peer-removal authorization (`2026-07-2`).** `UpdateCluster` checks
  `RemovePeerCluster` against the particular removed cluster rather than a
  wildcard resource.
- **Stricter DSQL Kinesis ARN validation (`2026-08`).** DSQL rejects Kinesis
  stream ARNs containing characters outside the valid ARN character set.
- **Autonomous Database Secrets Manager integration (`2026-07-2`).** Admin and
  wallet passwords can come from customer-managed Secrets Manager secrets;
  `InitializeService` controls the OCI IAM service role used for integration.
- **Oracle Exadata Exascale resources (`2026-08`).** The ODB client supports
  Exadata on Exascale Infrastructure (`ExaDB-XS`), including storage vaults
  and VM clusters.

## Health and scientific data

- **HealthLake source-to-FHIR transformation (`2026-07-2`).** Preview support
  converts CSV and C-CDA to FHIR R4 using reusable mapping profiles,
  synchronous or asynchronous jobs, provenance tracking, and drift detection.
- **HealthLake import provenance (`2026-08`).** `StartFHIRImportJob` accepts
  `provenanceEnabled` to retain provenance for imported FHIR data.
- **Omics task identifiers (`2026-07-2`).** `GetRunTask` and `ListRunTasks`
  return a task UUID for identifying individual run tasks.

## Marketplace, partners, and procurement

### Partner Central

- **Partner Central Marketplace associations (`2026-06`).** `Associate` and
  `Disassociate` accept `AwsMarketplaceSolutions` and
  `AwsMarketplaceProducts`; `GetOpportunity` returns them, and `ListSolutions`
  adds `AwsMarketplaceSolutionArn`.
- **Partner Central revenue measurement (`2026-07`).** The Revenue Measurement
  client creates, manages, and tracks revenue attributions and Marketplace
  revenue-share allocations.
- **Partner Central qualification and lead workflows (`2026-07-2`).** A
  subsidiary account's qualifications can be associated with a primary
  account to share qualifications and consolidate scorecards. Leads require
  five fields, accept free text elsewhere, and return propensity and readiness
  enrichment.
- **Partner Central headquarters validation (`2026-07-2`).**
  `StartProfileUpdateTask` accepts a headquarters location using ISO 3166
  country and subdivision codes; when supplied, both are required.

### Marketplace Catalog and assessments

- **Marketplace Catalog reseller-role filtering (`2026-07`).** `ListEntities`
  accepts `ResellerRole` for `ResaleAuthorization` entities.
- **Marketplace Catalog offer filters (`2026-07-2`).** `ListEntities` accepts
  `TargetAgreementId`, `TargetAgreementIntent`, and `CreatedBySource` for
  `Offer` entities.
- **Marketplace resource assessments (`2026-08`).** `DescribeAssessment` and
  `ListAssessments` expose validation issues on Marketplace resources through
  Assessment resources.

### Metering and identity

- **Marketplace metering window (`2026-07`).** `BatchMeterUsage` accepts
  records for 24 hours after an event; the six-hour grace period at the end of
  a billing cycle still applies.
- **Marketplace metering identity migration (`2026-07-2`).** For new SaaS
  integrations, `ResolveCustomer` does not populate `CustomerIdentifier` and
  `BatchMeterUsage` does not support it. Use `CustomerAWSAccountId` and
  `LicenseArn`.
- **Marketplace net-payment terms (`2026-08`).** Marketplace Agreement
  `GetAgreementTerms` returns `AcceptedTerm.netPaymentTerm`; Marketplace
  Discovery `GetOfferTerms` returns its offer equivalent. `paymentDuePeriod`
  is an ISO 8601 duration such as `P30D`.

### Billing, support, and procurement

- **Billing credits and preferences (`2026-07`).** Billing APIs retrieve
  credit details and monthly allocation history, redeem promotional codes,
  and configure credit sharing and billing preferences.
- **Procurement portal OTP validation (`2026-07-2`).**
  `SendProcurementPortalValidation` and `VerifyProcurementPortalValidation`
  activate invoicing procurement-portal preferences with a one-time passcode.
- **Compressed BCM data exports (`2026-07-2`).** Billing and Cost Management
  data exports can deliver CSV reports in ZIP archives.
- **Enterprise Support billing APIs (`2026-07-2`).**
  `GetEnterpriseSupportChargeSummary`, `GetEnterpriseSupportContractDetails`,
  and `ListEnterpriseSupportLinkedAccountCharges` expose charges formerly
  available only through Concierge or Support.
- **Deadline persistent-volume costs (`2026-08`).** Deadline Cloud usage data
  reports persistent-volume costs separately from compute and license costs.

## Location, IoT, payments, and licensing

- **IoT Wireless multicast defaults (`2026-07`).** Multicast Group APIs store
  default session downlink transmission parameters, so FUOTA multicast
  sessions need not pass them explicitly at start.
- **Places V2 address and mobility fields (`2026-07`).** APIs add
  `AddressNamesMode`, `AddressNameTranslations`, `MobilityMode`,
  `PostalCodeMode`, `SecondaryAddresses`, and `DriveThrough` for formatting,
  translation, travel-aware search, multi-city postal codes, and unit-level
  addresses.
- **Dynamic-map POI controls (`2026-08`).** Location Maps
  `GetStyleDescriptor` accepts `PoiDensity` from `Off` through `VeryDense` and
  up to nine `PoiCategories` for HERE and Grab styles.
- **UnionPay session-key derivation (`2026-07-2`).** Payment Cryptography Data
  supports UnionPay derivation in `GenerateAuthRequestCryptogram`,
  `VerifyAuthRequestCryptogram`, `GenerateMac`, and `VerifyMac`.

## Media and gaming

### MediaTailor and MediaPackage

- **MediaTailor dual-stack response fields (`2026-07`).** SSAI and Channel
  Assembly responses include dual-stack IPv4/IPv6 endpoint fields.
- **MediaTailor decision-server controls (`2026-07-2`).** Playback
  configurations accept ad-decision-server timeout and concurrency fields.
- **MediaPackage non-epoch-locked CMAF ingest (`2026-07-2`).** MediaPackageV2
  channels support CMAF ingest that is not epoch-locked.
- **MediaPackage stream-name output mode (`2026-08`).** V2 origin endpoints
  accept `StreamNameOutputMode` to use encoder-assigned stream names instead
  of numeric indexes in egress manifests.
- **MediaTailor VAST Ad Buffet sequencing (`2026-08`).** Playback
  configurations accept `AdSequencingMode` for ordered VAST Ad Buffet
  insertion, using standalone ads when a sequenced ad is unavailable.
- **Concurrent MediaTailor functions (`2026-08`).** The Concurrent Executor
  function type runs independent child functions in parallel within one
  lifecycle hook.

### Video and audio services

- **IVS post-roll ad configuration (`2026-07`).** Ad-configuration resources
  accept `postRollConfiguration`.
- **MediaConvert output controls (`2026-07`).** MediaConvert adds
  integer-second duration normalization and an option to disable explicit
  weighted prediction.
- **MediaConvert archive output (`2026-07-2`).** Outputs can target S3 Glacier
  Instant Retrieval, and Kantar server URL validation accepts the Fifty5Blue
  domain.
- **Transcribe streaming transcript form (`2026-07-2`).** Streaming
  Transcribe accepts `TranscriptFormat` to select spoken or written numeric
  and formatted output.
- **MediaLive SCTE-35 passthrough (`2026-08`).** MediaLive can pass SCTE-35
  markers without adding an IDR frame for CMAF Ingest, MediaPackage V2, and
  transport-stream outputs.
- **MediaLive multicast source addresses (`2026-08`).** MediaLive Anywhere
  multicast destinations accept `VirtualSourceAddress` for networks that
  filter multicast traffic by source.
- **MediaConnect recovery-latency tuning (`2026-08`).** Router inputs and
  outputs can trade stream quality for end-to-end latency by tuning internal
  recovery latency.
- **Elemental Inference fixture search (`2026-08`).** `SearchFixtures` and
  `DataSourceConfiguration` map fixture event data onto clipping outputs.

### GameLift Streams and Servers

- **GameLift Streams admin shell (`2026-07`).**
  `CreateStreamSessionAdminShell` opens a secure terminal to a live stream
  session for troubleshooting.
- **GameLift managed-fleet expiration (`2026-07-2`).** A managed fleet expires
  one year after creation, enters `EXPIRED`, emits `FLEET EXPIRED`, and scales
  to zero; it cannot host new sessions or scale up.
- **GameLift Streams session controls (`2026-07-2`).** Sessions can assume an
  IAM role and choose landscape, portrait, or square aspect ratios.
  `CreateStreamUrl`, `GetStreamUrl`, `ListStreamUrls`, and `RevokeStreamUrl`
  manage temporary unauthenticated browser access.
