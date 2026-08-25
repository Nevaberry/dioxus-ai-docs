# Observability, security, and governance

Use this reference for telemetry, alarms, log management, identity, security
services, certificate flows, compliance, resilience, and organization-level
controls.

## CloudWatch and telemetry

### Observability Admin telemetry rules (2026-06)

The Observability Admin client manages account- and organization-level
telemetry rules and CloudWatch pipelines for metrics.

### Wall-clock CloudWatch alarm windows (2026-06)

CloudWatch alarms can use wall-clock-aligned daily or weekly evaluation windows
with optional time-zone support, rather than only sliding windows.

### CloudWatch Logs-query alarms (2026-06)

`PutLogAlarm` creates alarms directly from CloudWatch Logs query results.

### CloudWatch Logs intelligent-tiering policy (2026-07)

`PutStorageTierPolicy` and `GetStorageTierPolicy` configure account-level
Intelligent Tiering that moves infrequently accessed logs to lower-cost tiers.

### CloudWatch anomaly-detector identifiers (2026-07-2)

`PutAnomalyDetector` and `DescribeAnomalyDetectors` return an
`AnomalyDetectorId`. Use it to identify a specific detector for describe and
delete operations.

### Observability Admin telemetry-rule extensions (2026-07-2)

Account- and organization-level telemetry rules can enable ALB and Bedrock
Knowledge Base logs and can use customer-managed KMS keys.

### AMP collector destinations (2026-07-2)

Amazon Managed Service for Prometheus collectors can send datasets to
CloudWatch and can use an Amazon OpenSearch Service exporter.

### CloudWatch Logs alarm inputs (2026-07-2)

`LogGroupIdentifiers` is optional for CloudWatch log alarms. Do not require it
in local schemas.

### CloudWatch Logs lookup tables (2026-07-2)

CloudWatch Logs can create or update lookup tables from a query by passing its
`queryId`. A lookup table can also be a scheduled-query destination that
refreshes after every run.

### Observability Admin tag propagation (2026-08)

CloudWatch Logs centralization rules accept `TagPropagationConfiguration` to
synchronize source log-group tags to destination groups with configurable
conflict resolution.

### CloudWatch Logs index categories (2026-08)

`DescribeFieldIndexes` can filter field indexes by `DEFAULT`, `CUSTOM`, `AUTO`,
and `INACTIVE` categories.

## Certificates, encryption, and web protection

### ACM ACME certificate issuance (2026-06)

ACM can use ACME to issue public certificates for customer-managed
infrastructure such as on-premises servers and Kubernetes clusters.

### WAF protection for AgentCore Gateway (2026-06)

WAF `AssociateWebACL`, `DisassociateWebACL`, `GetWebACLForResource`, and
`ListResourcesForWebACL` support Bedrock AgentCore Gateway resources.

### Synthetics canary environment encryption (2026-07)

CloudWatch Synthetics canaries can use a customer-managed KMS key to encrypt
their Lambda environment variables at rest.

### WAF pre-parse transformations (2026-07-2)

WAF can normalize raw query strings before parsing rules whose `FieldToMatch`
is `SingleQueryArgument` or `AllQueryArguments`. Ten additional text
transformations include options matching ModSecurity v3 behavior.

### ACM email-to-DNS validation migration (2026-08)

ACM can change an existing email-validated certificate to DNS validation. Use
this migration rather than replacing the certificate solely to change method.

### Private CA RSASSA-PSS signing (2026-08)

AWS Private CA supports the RSASSA-PSS certificate-signing algorithm. Accept it
in signing-algorithm selections and generated models.

## IAM and Identity Center

### IAM Identity Center replication metadata (2026-06)

SSO Admin `ListInstances` returns `PrimaryRegion` and `Regions` for replicated
instances.

### IAM Policy Simulator SCP semantics (2026-07-2)

The IAM Policy Simulator evaluates SCP conditions and resource scoping, returns
`explicitDeny` for explicit SCP denials, and reports cross-account decisions
more accurately. Update expected decisions in policy tests.

### DSQL peer-removal authorization (2026-07-2)

DSQL `UpdateCluster` checks `RemovePeerCluster` permission against the specific
cluster being removed rather than a wildcard resource. Scope IAM policies to
the peer cluster ARN.

### Organization-level Identity Center instances (2026-07-2)

IAM Identity Center can create an organization-level instance without enabling
multi-account permissions. Permissions can be enabled during creation or later;
the required service-linked roles are provisioned when enabled.

### IAM account access manager client (2026-08)

The IAM account access manager client maps IAM roles to IAM Identity Center
users and groups. Use it for centrally managed account-access assignments.

## Config, Inspector, GuardDuty, and Security Hub

### GuardDuty AI Analyst detectors (2026-07)

GuardDuty detector models include an AI Analyst enum value. Treat detector enums
as open to this value.

### AWS Config third-party cloud connectors (2026-07)

AWS Config adds `PutConnector`, `GetConnector`, `DeleteConnector`, and
`ListConnectors` for third-party cloud providers, plus
`PutThirdPartyServiceLinkedConfigurationRecorder` for their service-linked
recorders.

### Inspector2 Azure coverage and member scan settings (2026-07)

Inspector2 extends vulnerability management to Azure VMs, container registries,
and function apps, and adds per-member-account scan configuration.

### AWS Config tags on organization resources (2026-07)

`PutOrganizationConfigRule` and `PutOrganizationConformancePack` support tags at
creation time.

### GuardDuty AI Protection findings (2026-07-2)

GuardDuty AI Protection findings expose Bedrock guardrail, model, observation,
and continuous-scan details. `GuardrailArn` and `GuardrailVersion` are
deprecated; consume the `guardrails` list instead.

### GuardDuty filter lifecycle metadata (2026-07-2)

`GetFilter` returns `createdAt`, `updatedAt`, and a version number incremented
on every update, allowing revision tracking and optimistic comparisons.

### Security Hub V2 free-trial status (2026-08)

`ListFreeTrialStatusesV2` reports free-trial states for Security Hub and each
opt-in feature.

## Resilience, compliance, and advisory services

### Resource Explorer CloudFormation metadata (2026-06)

Resource Explorer `Search` and `ListSupportedResourceTypes` responses contain
CloudFormation resource-type fields. `ServiceView` also exposes `SLRec`.

### Resilience Hub v2 assessment controls (2026-07)

Resilience Hub v2 supports failure-mode assessment filtering and sorting,
resource-type filtering in `ListResources`, cross-Region and cross-account
topology edges, data-recovery achievability status, and finer-grained
dependency-discovery progress.

### Artifact Assurance Assistant (2026-07)

Artifact provides Assurance Assistant APIs for managing compliance inquiries,
including tags.

### License Manager usage resets (2026-07-2)

`CreateLicenseVersion` accepts `ResetUsage`. `true` resets entitlement usage to
zero; `false` or omission preserves it. Set it explicitly when reset semantics
matter.

### Systems Manager Automation warnings (2026-07-2)

Systems Manager Automation responses expose `WarningMessage`. Surface these
non-fatal warnings instead of treating success as warning-free.

### Trusted Advisor resource recommendations (2026-07-2)

`ListRecommendationsForResource` retrieves recommendations for a resource ARN.
`CheckSummary` exposes `resourceArnQueryable`, `awsResourceTypes`,
`checkGranularity`, and `recommendationId`.

### Security Agent repository branch overrides (2026-07-2)

Security Agent integrated-repository configuration accepts a branch override,
and task responses include active task hours.

### Security Agent budgets and revalidation (2026-08)

Security Agent penetration tests and code reviews can set a maximum task-hour
budget. Use the `REVALIDATION` job type to re-check previously reported
findings.

### Security Agent email MFA (2026-08)

Security Agent actors accept `enableEmailMfa`. When enabled, responses supply
`mfaForwardingAddress` for forwarding login codes during penetration tests.

### Device Farm generated insights (2026-08)

Device Farm models expose service-generated insights for runs, jobs, and tests.
Treat these insights as additional response data rather than client-computed
results.

## Account governance and limits

### Cognito provisioned API limits (2026-07)

Cognito User Pools provides `GetProvisionedLimit` and `UpdateProvisionedLimit`
for reading and changing provisioned API rate limits.

### Cognito SMS delivery and factor inspection (2026-07-2)

`SmsConfigurationType` accepts `EumsSms` to send MFA and verification messages
through AWS End User Messaging instead of SNS. `AdminGetUserAuthFactors`
returns configured password, SMS, email, and TOTP factors.

### QuickSight permission controls (2026-07-2)

QuickSight custom permissions can govern trigger scheduling, inbound email, and
Quick Event triggers, with deny-by-default governance fields. Profiles can
control Amazon Quick access through browser extensions and Microsoft Word,
Outlook, Excel, and PowerPoint add-ins.

### QuickSight governance APIs (2026-08)

QuickSight provides APIs for Microsoft Purview DLP configuration, approval
policies on asset sharing, and limit profiles for index storage and per-user
agent hours.
