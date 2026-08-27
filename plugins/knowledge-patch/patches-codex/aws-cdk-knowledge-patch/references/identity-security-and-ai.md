# Identity, security, and AI services

Use this reference for identity, security, and ai services compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## Amazon Cognito

### Cognito choice-based authentication

**Batch:** `2025-02`

Cognito constructs support choice-based authentication, including passwordless and passkey sign-in.

### Cognito client analytics

**Batch:** `2025-02`

Cognito user-pool clients accept analytics configuration.

### Cognito managed login

**Batch:** `2025-01`

Cognito constructs gained support for managed login.

### Cognito pre-token trigger event v3

**Batch:** `2025-04`

Cognito constructs support version 3.0 of the pre-token-generation trigger event.

### Cognito refresh-token rotation

**Batch:** `2025-09`

Cognito constructs support refresh-token rotation.

### Stable Cognito identity pools

**Batch:** `2025-03`

Cognito Identity Pool constructs graduated from experimental to stable.

## Amazon Bedrock and AgentCore

### Added Bedrock models

**Batch:** `2025-04`

The Bedrock model catalog adds Amazon Nova Sonic 1.0 and Nova Reel 1.1.

### Added Bedrock models

**Batch:** `2026-03`

The Bedrock foundation-model catalog adds MiniMax and GLM identifiers.

### AgentCore Cognito authorizers

**Batch:** `2025-11`

`RuntimeAuthorizerConfiguration.usingCognito()` now accepts `IUserPool` and `IUserPoolClient` constructs instead of string identifiers and supports multiple clients.

### AgentCore gateway IAM credential targets

**Batch:** `2026-07`

Bedrock AgentCore gateway-target IAM credential providers can specify the target service and region.

### AgentCore L2 constructs

**Batch:** `2025-10`

AgentCore now provides L2 constructs for runtimes and first-party tools.

### AgentCore memory

**Batch:** `2025-11`

AgentCore provides an L2 construct for memory.

### AgentCore Memory stream delivery

**Batch:** `2026-08`

Bedrock AgentCore Memory L2 constructs support `StreamDeliveryResources`.

### AgentCore metric-dimension changes

**Batch:** `2026-08`

Gateway per-gateway metric helpers now emit `{ Operation, Protocol, Resource }` instead of `{ Resource }`; `RuntimeBase` per-resource helpers emit `{ Operation, Name, Resource }`, and aggregate helpers emit `{ AggregateOperation }` instead of `{ Resource: 'All' }`. Update alarms and dashboards that depend on the previous dimensions.

### Bedrock agent prompt management

**Batch:** `2025-07`

Bedrock agent constructs support prompt management.

### Bedrock DeepSeek R1

**Batch:** `2025-03`

Bedrock constructs support the DeepSeek R1 model.

### Bedrock model-customization jobs

**Batch:** `2025-05`

Step Functions task integrations support Bedrock `CreateModelCustomizationJob`.

### Deprecated Bedrock models

**Batch:** `2025-01`

Bedrock model entries for Claude 2, Claude 2.1, and Claude Instant are deprecated.

### Inference profiles

**Batch:** `2025-08`

Inference-profile constructs support inference and cross-region inference profiles.

### Ray2 model support

**Batch:** `2025-02`

The Bedrock model catalog includes the Ray2 visual model.

### Required AgentCore reference getters

**Batch:** `2026-02`

AgentCore interface implementors must now provide `gatewayRef`, `gatewayTargetRef`, `memoryRef`, `runtimeRef`, `runtimeEndpointRef`, `browserCustomRef`, or `codeInterpreterCustomRef` on the corresponding `IGateway`, `IGatewayTarget`, `IMemory`, `IBedrockAgentRuntime`, `IRuntimeEndpoint`, `IBrowserCustom`, and `ICodeInterpreterCustom` interfaces.

### Stable Bedrock AgentCore constructs

**Batch:** `2026-05`

Bedrock AgentCore has graduated to stable.

## IAM, KMS, Secrets, and access control

### Encrypted SNS notification policies

**Batch:** `2025-05`

Under its feature flag, S3 notifications to a KMS-encrypted SNS topic add a key policy that trusts S3.

### Grants for imported KMS aliases

**Batch:** `2025-06`

Under its feature flag, aliases imported with `Alias.fromAliasName()` support grant methods.

### IAM and RDS lookups

**Batch:** `2025-04`

`Role.fromLookup()` and `DatabaseInstance.fromLookup()` can resolve existing IAM roles and RDS database instances.

### KMS alias behavior

**Batch:** `2025-09`

`Alias` references resolve to the alias instead of its underlying key. Aliases imported with `Alias.fromAliasName()` expose `aliasTargetKey`.

### KMS-encrypted AppConfig hosted configurations

**Batch:** `2025-06`

AppConfig hosted configurations support encryption with a customer-managed key.

### Literal secret dynamic-reference keys

**Batch:** `2025-11`

`SecretValue` and Secrets Manager `Secret` provide methods for obtaining a literal dynamic-reference key that CloudFormation does not resolve.

### Narrower encrypted-resource interface

**Batch:** `2026-02`

`IEncryptedResource` now extends `IEnvironmentAware` rather than `IResource`, and `GrantableResources.isEncryptedResource()` now accepts `IEnvironmentAware` rather than `IConstruct`. Code that still needs an `IResource` must use `IEncryptedResource & IResource` or guard with `Resource.isResource()`.

### Native EKS OIDC providers

**Batch:** `2026-02`

EKS provides `OidcProviderNative`, backed by the native L1 resource, and deprecates the custom-resource-based `OpenIdConnectProvider`.

### Native OIDC providers

**Batch:** `2025-06`

IAM provides `OidcProviderNative`, which uses the native CloudFormation OIDC-provider resource rather than a custom resource.

### Optional KMS account-identity trust

**Batch:** `2026-02`

`trustAccountIdentities` is now optional in `KeyGrants`.

### Synthesized security behavior

**Batch:** `2025-09`

`BucketNotificationsHandler` scopes IAM permissions to specific bucket ARNs, and ECS patterns keep `openListener` false when given a custom security group. The EKS kubectl provider uses the `AmazonEC2ContainerRegistryPullOnly` managed policy.

## Certificates and managed inference

### Exportable public certificates

**Batch:** `2025-09`

ACM constructs support exportable public certificates.

### SageMaker serverless inference

**Batch:** `2025-11`

SageMaker constructs support serverless inference endpoints.
