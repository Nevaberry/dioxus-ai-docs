# Identity, Security, and AI

Topic-organized compatibility guidance for AWS CDK.

## Bedrock and AgentCore

### Added Bedrock models (`2025-04`)

The Bedrock model catalog adds Amazon Nova Sonic 1.0 and Nova Reel 1.1.

### Added Bedrock models (`2026-03`)

The Bedrock foundation-model catalog adds MiniMax and GLM identifiers.

### AgentCore Cognito authorizers (`2025-11`)

`RuntimeAuthorizerConfiguration.usingCognito()` now accepts `IUserPool` and `IUserPoolClient` constructs instead of string identifiers and supports multiple clients.

### AgentCore gateway IAM credential targets (`2026-07`)

Bedrock AgentCore gateway-target IAM credential providers can specify the target service and region.

### AgentCore interface endpoints (`2025-10`)

`InterfaceVpcEndpointAwsService` includes `BEDROCK_AGENTCORE` and `BEDROCK_AGENTCORE_GATEWAY`.

### AgentCore L2 constructs (`2025-10`)

AgentCore now provides L2 constructs for runtimes and first-party tools.

### AgentCore memory (`2025-11`)

AgentCore provides an L2 construct for memory.

### AgentCore Memory stream delivery (`2026-08`)

Bedrock AgentCore Memory L2 constructs support `StreamDeliveryResources`.

### AgentCore metric-dimension changes (`2026-08`)

Gateway per-gateway metric helpers now emit `{ Operation, Protocol, Resource }` instead of `{ Resource }`; `RuntimeBase` per-resource helpers emit `{ Operation, Name, Resource }`, and aggregate helpers emit `{ AggregateOperation }` instead of `{ Resource: 'All' }`. Update alarms and dashboards that depend on the previous dimensions.

### Bedrock agent prompt management (`2025-07`)

Bedrock agent constructs support prompt management.

### Bedrock DeepSeek R1 (`2025-03`)

Bedrock constructs support the DeepSeek R1 model.

### Bedrock model-customization jobs (`2025-05`)

Step Functions task integrations support Bedrock `CreateModelCustomizationJob`.

### Deprecated Bedrock models (`2025-01`)

Bedrock model entries for Claude 2, Claude 2.1, and Claude Instant are deprecated.

### Inference profiles (`2025-08`)

Inference-profile constructs support inference and cross-region inference profiles.

### Ray2 model support (`2025-02`)

The Bedrock model catalog includes the Ray2 visual model.

### Stable Bedrock AgentCore constructs (`2026-05`)

Bedrock AgentCore has graduated to stable.

## Certificates and Security Services

### ACM interface endpoints (`2025-12`)

EC2 constructs provide interface VPC endpoint services for ACM and ACM Private CA.

### Exportable public certificates (`2025-09`)

ACM constructs support exportable public certificates.

## Cognito

### Cognito choice-based authentication (`2025-02`)

Cognito constructs support choice-based authentication, including passwordless and passkey sign-in.

### Cognito client analytics (`2025-02`)

Cognito user-pool clients accept analytics configuration.

### Cognito managed login (`2025-01`)

Cognito constructs gained support for managed login.

### Cognito pre-token trigger event v3 (`2025-04`)

Cognito constructs support version 3.0 of the pre-token-generation trigger event.

### Cognito refresh-token rotation (`2025-09`)

Cognito constructs support refresh-token rotation.

### Stable Cognito identity pools (`2025-03`)

Cognito Identity Pool constructs graduated from experimental to stable.

## IAM, KMS, and Secrets

### Grants for imported KMS aliases (`2025-06`)

Under its feature flag, aliases imported with `Alias.fromAliasName()` support grant methods.

### KMS alias behavior (`2025-09`)

`Alias` references resolve to the alias instead of its underlying key. Aliases imported with `Alias.fromAliasName()` expose `aliasTargetKey`.

### KMS-encrypted AppConfig hosted configurations (`2025-06`)

AppConfig hosted configurations support encryption with a customer-managed key.

### Literal secret dynamic-reference keys (`2025-11`)

`SecretValue` and Secrets Manager `Secret` provide methods for obtaining a literal dynamic-reference key that CloudFormation does not resolve.

### Native OIDC providers (`2025-06`)

IAM provides `OidcProviderNative`, which uses the native CloudFormation OIDC-provider resource rather than a custom resource.

### Optional KMS account-identity trust (`2026-02`)

`trustAccountIdentities` is now optional in `KeyGrants`.
