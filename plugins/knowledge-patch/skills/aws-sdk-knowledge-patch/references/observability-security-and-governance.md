# Observability, security, and governance

## Telemetry and alarms

### Observability Admin

Observability Admin supports organization- and account-level telemetry rules and CloudWatch pipelines for metrics (since `2026-06`). Choose rule scope deliberately when centralizing telemetry across accounts.

### CloudWatch alarms

CloudWatch adds `PutLogAlarm` for alarms evaluated directly from CloudWatch Logs query results (since `2026-06`). Alarm evaluation windows can align to wall-clock boundaries and optionally use a time zone for daily or weekly periods.

### CloudWatch Logs storage tiers

`PutStorageTierPolicy` and `GetStorageTierPolicy` manage the account-level Intelligent Tiering policy that moves infrequently accessed logs to lower-cost storage tiers (since `2026-07`). The scope is the account policy, not an individual log group's standalone setting.

### Synthetics environment encryption

CloudWatch Synthetics can use a customer-managed KMS key to encrypt a canary Lambda function's environment variables at rest (since `2026-07`). Grant both canary execution and service paths the required KMS permissions.

## Inventory and organization governance

### Resource Explorer metadata

Resource Explorer `Search` and `ListSupportedResourceTypes` responses include CloudFormation resource-type fields, and `ServiceView` includes `SLRec` (since `2026-06`). Update strict response decoders and use the CloudFormation fields for type-aware tooling.

### Identity Center replicated instances

SSO Admin `ListInstances` returns `PrimaryRegion` and `Regions` for replicated instances (since `2026-06`). Use these fields instead of assuming an instance has only the endpoint Region through which it was listed.

### AWS Config

- `PutConnector`, `GetConnector`, `DeleteConnector`, and `ListConnectors` manage third-party cloud connectors (since `2026-07`). `PutThirdPartyServiceLinkedConfigurationRecorder` enables recording of connected providers' resources.
- `PutOrganizationConfigRule` and `PutOrganizationConformancePack` support tag-on-create for organization-managed rules and conformance packs (since `2026-07`). Include required governance tags in the creation call rather than relying on a follow-up operation.

### Inspector2

Inspector2 vulnerability management covers Azure virtual machines, container registries, and function apps (since `2026-07`). It also supports per-member-account scan configuration, so delegated-administrator automation should not assume one uniform scan setting.

## Detection, authorization, and compliance

### GuardDuty

GuardDuty detector schemas add the `AI Analyst` enum value (since `2026-07`). Ensure exhaustive enum handling preserves or recognizes this value.

### IAM-authenticated Sign-In OAuth

AWS Sign-In adds three IAM-authenticated operations (since `2026-07`):

- `CreateOAuth2TokenWithIAM` implements the OAuth 2.0 client-credentials flow.
- `IntrospectOAuth2TokenWithIAM` inspects a token.
- `RevokeOAuth2TokenWithIAM` revokes a token.

Sign these calls with IAM credentials; do not substitute the non-IAM OAuth operations when the IAM-authenticated contract is required.

### WAF and AgentCore

WAF web ACL association APIs accept Bedrock AgentCore Gateway resources (since `2026-06`), including association, disassociation, lookup, and resource-listing operations.

AgentCore Gateway inbound authorizers can map allowed scopes to separate advertised scopes (since `2026-07`). Keep authorization enforcement scopes distinct from scopes published to tool clients when configuring this mapping.

### Artifact Assurance Assistant

AWS Artifact provides Assurance Assistant APIs for creating and managing compliance inquiries, with tagging support (since `2026-07`). Include tag permissions in automation that creates inquiries.

## Resilience Hub v2

Resilience Hub v2 adds the following assessment controls (since `2026-07`):

- Filter and sort assessments by failure mode.
- Filter `ListResources` by resource type.
- Represent cross-Region and cross-account topology edges.
- Report data-recovery achievability status.
- Report dependency-discovery progress at finer granularity.
