# Observability, security, and governance

## CloudWatch and telemetry

### Alarms and telemetry rules

- **Observability Admin telemetry rules (`2026-06`).** The client manages
  organization- and account-level telemetry rules and CloudWatch metrics
  pipelines.
- **Wall-clock CloudWatch alarm windows (`2026-06`).** Alarms support
  wall-clock-aligned daily or weekly evaluation windows with optional time
  zones, rather than only sliding windows.
- **CloudWatch Logs-query alarms (`2026-06`).** `PutLogAlarm` creates alarms
  directly from CloudWatch Logs query results.
- **CloudWatch anomaly-detector identifiers (`2026-07-2`).**
  `PutAnomalyDetector` and `DescribeAnomalyDetectors` return
  `AnomalyDetectorId`, which can target a detector for describe and delete.
- **Observability Admin telemetry-rule extensions (`2026-07-2`).** Account and
  organization rules can enable ALB and Bedrock Knowledge Base logs and use
  customer-managed KMS keys.
- **CloudWatch Logs alarm inputs (`2026-07-2`).** `LogGroupIdentifiers` is
  optional for CloudWatch log alarms.
- **Observability Admin tag propagation (`2026-08`).** Logs centralization
  rules accept `TagPropagationConfiguration` to copy source log-group tags to
  destinations with configurable conflict resolution.

### Logs, metrics, and automation

- **CloudWatch Logs intelligent-tiering policy (`2026-07`).**
  `PutStorageTierPolicy` and `GetStorageTierPolicy` manage account-level
  Intelligent Tiering for infrequently accessed logs.
- **AMP collector destinations (`2026-07-2`).** Managed Service for Prometheus
  collectors can send datasets to CloudWatch and use an OpenSearch Service
  exporter.
- **CloudWatch Logs lookup tables (`2026-07-2`).** Create or update a lookup
  table from a query by passing `queryId`; scheduled queries can use a lookup
  table as a destination and refresh it after every run.
- **Systems Manager Automation warnings (`2026-07-2`).** Automation responses
  expose `WarningMessage` for non-fatal warnings.
- **CloudWatch Logs index categories (`2026-08`).** `DescribeFieldIndexes`
  filters by `DEFAULT`, `CUSTOM`, `AUTO`, or `INACTIVE`.

### Resource discovery and recommendations

- **Resource Explorer CloudFormation metadata (`2026-06`).** `Search` and
  `ListSupportedResourceTypes` responses include CloudFormation resource-type
  fields; `ServiceView` adds `SLRec`.
- **Trusted Advisor resource recommendations (`2026-07-2`).**
  `ListRecommendationsForResource` queries by resource ARN. `CheckSummary`
  exposes `resourceArnQueryable`, `awsResourceTypes`, `checkGranularity`, and
  `recommendationId`.

## GuardDuty, Inspector, and Security Hub

### GuardDuty

- **GuardDuty AI Analyst detectors (`2026-07`).** Detector models include an
  AI Analyst enum value.
- **GuardDuty AI Protection findings (`2026-07-2`).** AI Protection is
  generally available. Findings expose Bedrock guardrail, model, observation,
  and continuous-scan details; `GuardrailArn` and `GuardrailVersion` are
  deprecated in favor of the `guardrails` list.
- **GuardDuty filter lifecycle metadata (`2026-07-2`).** `GetFilter` returns
  `createdAt`, `updatedAt`, and a version incremented on every update.

### Inspector

- **Inspector2 Azure coverage and member scan settings (`2026-07`).**
  Inspector2 scans Azure VMs, container registries, and function apps and
  supports per-member-account scan configuration.
- **Inspector scan and API-model changes (`2026-07-2`).** Inspector2 supports
  three- and seven-day ECR rescan durations, Windows deep-inspection paths,
  Azure SBOM export, and corrected tag propagation for connector CloudFormation
  stacks. `Tags` was removed from `ListCodeSecurityIntegration` and
  `ListCodeSecurityScanConfiguration`; do not consume it.

### Security Hub and Resilience Hub

- **Resilience Hub v2 assessment controls (`2026-07`).** Version 2 adds
  failure-mode assessment filtering and sorting, resource-type filters in
  `ListResources`, cross-Region and cross-account topology edges,
  data-recovery achievability, and finer dependency-discovery progress.
- **Security Hub V2 free-trial status (`2026-08`).**
  `ListFreeTrialStatusesV2` reports trial state for Security Hub and opt-in
  features.

## AWS Config and organizational governance

### AWS Config

- **AWS Config third-party cloud connectors (`2026-07`).** `PutConnector`,
  `GetConnector`, `DeleteConnector`, and `ListConnectors` manage third-party
  cloud connectors; `PutThirdPartyServiceLinkedConfigurationRecorder` creates
  their service-linked recorder.
- **AWS Config tags on organization resources (`2026-07`).**
  `PutOrganizationConfigRule` and `PutOrganizationConformancePack` accept tags
  at creation.

### Organizations and License Manager

- **License Manager usage resets (`2026-07-2`).** `CreateLicenseVersion`
  accepts `ResetUsage`; `true` resets entitlement usage to zero, while `false`
  or omission preserves it.
- **Organizations free-text validation (`2026-07-2`).** Free-text inputs are
  checked for common cross-site-scripting patterns; previously accepted
  membership-operation values can raise `InvalidInputException`.
- **Organizations handshake-party inputs (`2026-08`).** For
  `InviteAccountToOrganization`, `HandshakePartyType` accepts only `ACCOUNT`
  and `EMAIL`; `ORGANIZATION` is response-only.

## Identity, authorization, and policy

### IAM Identity Center

- **IAM Identity Center replication metadata (`2026-06`).** SSO Admin
  `ListInstances` returns `PrimaryRegion` and `Regions` for replicated
  instances.
- **Organization-level Identity Center instances (`2026-07-2`).** An
  organization-level instance can be created without multi-account
  permissions. Enabling them during creation or later provisions the required
  service-linked roles.
- **IAM account access manager client (`2026-08`).** The client maps IAM roles
  to IAM Identity Center users and groups.

### OAuth, policies, and credentials

- **IAM-authenticated Sign-In OAuth operations (`2026-07`).** The Sign-In
  client adds `CreateOAuth2TokenWithIAM`, `IntrospectOAuth2TokenWithIAM`, and
  `RevokeOAuth2TokenWithIAM` for client-credentials tokens, inspection, and
  revocation.
- **IAM Policy Simulator SCP semantics (`2026-07-2`).** The simulator evaluates
  SCP conditions and resource scoping, reports explicit SCP denials as
  `explicitDeny`, and improves cross-account decisions.
- **Roles Anywhere trust-anchor certificate inputs (`2026-07-2`).** Trust
  anchor source data accepts longer certificate strings, matching adjustable
  trust-anchor limits.

## WAF, certificates, and encryption

### WAF

- **WAF protection for AgentCore Gateway (`2026-06`).** `AssociateWebACL`,
  `DisassociateWebACL`, `GetWebACLForResource`, and `ListResourcesForWebACL`
  support Bedrock AgentCore Gateway resources.
- **WAF pre-parse transformations (`2026-07-2`).** WAF can normalize raw query
  strings before parsing `SingleQueryArgument` or `AllQueryArguments` fields.
  Ten new text transformations include ModSecurity v3-compatible options.

### Certificate authorities and TLS assets

- **ACM ACME certificate issuance (`2026-06`).** ACM uses ACME to issue public
  certificates for customer-managed infrastructure such as on-premises
  servers and Kubernetes clusters.
- **ACM email-to-DNS validation migration (`2026-08`).** An existing
  email-validated certificate can be changed to DNS validation.
- **Private CA RSASSA-PSS signing (`2026-08`).** AWS Private CA supports the
  RSASSA-PSS certificate-signing algorithm.

### Encryption and assurance

- **Synthetics canary environment encryption (`2026-07`).** Canaries can use a
  customer-managed KMS key for Lambda environment variables at rest.
- **Artifact Assurance Assistant (`2026-07`).** Artifact adds Assurance
  Assistant APIs for compliance inquiries, including tagging.

## Security Agent

- **Security Agent repository branch overrides (`2026-07-2`).** Integrated
  repository configuration accepts a branch override; task responses expose
  active task hours.
- **Security Agent budgets and revalidation (`2026-08`).** Penetration tests
  and code reviews accept maximum task-hour budgets; the `REVALIDATION` job
  type re-checks reported findings.
- **Security Agent email MFA (`2026-08`).** Actors accept `enableEmailMfa`;
  when enabled, responses include `mfaForwardingAddress` for forwarding login
  codes during penetration tests.
