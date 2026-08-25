---
name: aws-sdk-knowledge-patch
description: AWS SDK
version: null
license: MIT
metadata:
  author: Nevaberry
---


# AWS SDK Knowledge Patch

Use this skill when upgrading an AWS SDK or CLI, changing a supported runtime,
configuring shared SDK behavior, or implementing one of the service APIs in the
reference index. Identify the language, SDK major version, runtime, service,
and deployment environment before applying the guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [lifecycle-runtimes-and-packaging.md](references/lifecycle-runtimes-and-packaging.md) | SDK and tool lifecycle, runtime support, JavaScript packaging, removed clients |
| [client-configuration-auth-and-retries.md](references/client-configuration-auth-and-retries.md) | STS endpoints, retries, authentication, credentials, checksums, tracing, protocols, TLS |
| [compute-deployment-and-networking.md](references/compute-deployment-and-networking.md) | CloudFormation, compute, containers, databases, networking, migration, and recovery |
| [observability-security-and-governance.md](references/observability-security-and-governance.md) | CloudWatch, Config, Inspector, GuardDuty, IAM, WAF, certificates, security, governance |
| [data-marketplace-and-customer-services.md](references/data-marketplace-and-customer-services.md) | Analytics, data, customer experience, Marketplace, billing, location, and media APIs |
| [serverless-ai-storage-and-cdk.md](references/serverless-ai-storage-and-cdk.md) | Lambda, AgentCore, Bedrock, SageMaker, vector storage, backups, and CDK Mixins |

## Apply the patch

1. Inspect manifests and lockfiles to identify the exact SDK and runtime line.
2. Resolve lifecycle, runtime, and packaging requirements before editing code.
3. Preserve explicit endpoint, retry, authentication, and backoff overrides.
4. Open the task-specific reference before constructing service request shapes,
   consuming response fields, or matching enums and errors.
5. Treat service-side validation changes and removed fields as compatibility
   work even when no SDK method name changed.
6. Test generated clients against the selected runtime and the intended Region.

## Breaking changes and migrations

### Migrate retired SDK and tool lines

- AWS SDK for .NET v3 reached end of support on June 1, 2026. Upgrade all
  `AWSSDK.*` packages together to 4.0.0 or later; v3 and v4 packages cannot
  coexist.
- AWS Tools for PowerShell v4 reached end of support on June 1, 2026. Move to
  v5.
- AWS CLI v1 is in its Maintenance Announcement phase. Prefer CLI v2 for new
  deployments and upgrades.

### Handle .NET v4 null collections

Request and response collection properties default to `null` in v4 rather
than to empty collections. Null-check before iteration and preserve the
difference between an unset collection and an explicitly empty collection.

```csharp
if (response.Items is not null)
{
    foreach (var item in response.Items) { /* ... */ }
}
```

During migration only, this switch restores v3-style initialization:

```csharp
Amazon.AWSConfigs.InitializeCollections = true;
```

### Update JavaScript v3 packaging and clients

- Bundlers must consume `dist-es`; bundler support was removed from `dist-cjs`.
- IoT Events, IoT Events Data, Panorama, and SimSpace Weaver clients were
  removed in `2026-06`.
- Node.js 18 and pre-ES2023 support ended in January 2026. Node.js 20 and
  pre-ES2024 support are scheduled to end in January 2027.
- Pinning an older release can retain runtime compatibility, but does not
  retain support, service updates, or fixes.

### Update deprecated or restricted service integrations

- Stop building new Amazon Cloud Directory integrations; the public CLI
  reference marks the service end-of-support.
- Chime SDK Voice proxy-session and Voice Connector proxy operations are
  deprecated.
- Amazon A2I is in maintenance mode; `StartHumanLoop` rejects accounts that
  are not recognized as existing customers.
- Marketplace SaaS metering integrations must use `CustomerAWSAccountId` and
  `LicenseArn`; new integrations cannot rely on `CustomerIdentifier`.
- Entity Resolution delete calls now raise a 404 `ResourceNotFoundException`
  for a missing target. Make idempotent deletion handle that exception.

## Shared defaults

### Regional STS endpoints

Python, PHP, C++, and .NET SDKs and AWS Tools for PowerShell default to
Regional STS endpoints. AWS CLI v1 remains the exception among generally
available SDKs and CLIs. Do not assume implicit STS traffic uses the global
endpoint or routes through `us-east-1`.

### Retry rollout

Supporting releases can opt into the updated `standard` and `adaptive`
behavior before it becomes the default in November 2026:

```sh
export AWS_NEW_RETRIES_2026=true
```

- Explicit `legacy`, maximum-attempt, and backoff settings remain unchanged.
- Updated standard retries use a 500-token quota: transient errors cost 14
  tokens and throttling errors cost 5.
- Transient errors use a 50 ms base delay; throttling uses 1,000 ms.
- DynamoDB and DynamoDB Streams use a 25 ms base delay and four attempts.
- Long-polling operations delay before returning an error after quota
  exhaustion, preventing hot loops.
- After rollout, use individual overrides or `AWS_RETRY_MODE=legacy` where
  supported; the opt-in flag is then ignored.

## Authentication and transport

### Choose authentication schemes explicitly

Current SDK lines and CLI v2 accept an ordered preference:

```ini
[default]
auth_scheme_preference=sigv4a,sigv4
sigv4a_signing_region_set=us-east-1,us-west-2
```

The environment equivalents are `AWS_AUTH_SCHEME_PREFERENCE` and
`AWS_SIGV4A_SIGNING_REGION_SET`; the JVM property is
`aws.authSchemePreference`. Valid schemes are `sigv4`, `sigv4a`, and
`httpBearerAuth`. Unsupported preferences fall back to the service default.

### Keep transport dependencies current

- JavaScript v3 propagates W3C trace headers.
- Several clients negotiate Smithy RPC v2 CBOR and prefer the most performant
  supported protocol. Do not force CBOR for Pricing Calculator or BCM
  Recommended Actions; their brief support was rolled back.
- Future hybrid ECDH plus ML-KEM negotiation requires TLS 1.3 or later.
  Existing certificates remain usable because the change affects session-key
  negotiation, not certificate format.

## High-value service guidance

### Deployment and containers

- CloudFormation validates `CreateStack` and `UpdateStack` before deployment.
  Use `DisableValidation` to skip it or `DeploymentConfig` for Express mode.
- EKS supports version rollback timeout, cancellation, and cancellation
  details; it also accepts request context for Pod Identity and control-plane
  component tuning.
- ECS circuit breakers accept a custom failure threshold and counting
  mechanism. Express Mode detects CPU architecture automatically.
- Auto Scaling supports reservations-first distribution and batch instance
  termination.
- Network Firewall container-association polling must handle `UPDATING`.

### Lambda durable execution

Choose durable execution when creating the function; it cannot be enabled
later. Use Node.js 22 or 24 with JavaScript/TypeScript, or Python 3.13 or 3.14.
Bundle the durable SDK and publish production code as versions so suspended
executions replay against their starting version.

```python
from aws_durable_execution_sdk_python import durable_execution, durable_step

@durable_step
def work(step_context, value):
    return {"value": value}

@durable_execution
def lambda_handler(event, context):
    return context.step(work(event["value"]))
```

Use `context.step()` for checkpointed retries, `context.wait()` for
compute-free suspension, `wait_for_condition()` for polling,
`create_callback()` for external completion, and `parallel()` or `map()` for
concurrency. An unhandled exception outside a step terminates the execution.

### Vector search

For S3 Vectors, create vector buckets and indexes separately, use `float32`,
match index dimension to the embedding source, and choose cosine or Euclidean
distance. Each vector supports up to 50 metadata keys, at most 10 of them
non-filterable, and queries return up to 100 results.

```sh
aws s3vectors create-index \
  --vector-bucket-name "$BUCKET_NAME" \
  --index-name "$INDEX_NAME" \
  --data-type float32 \
  --dimension "$DIMENSIONS" \
  --distance-metric "$DISTANCE_METRIC"
```

DynamoDB vector indexes provide approximate-nearest-neighbor search over
embeddings stored in table items. Choose the storage model before generating
requests; the S3 Vectors and DynamoDB APIs are distinct.

### AgentCore

Wrap an agent entry point in `BedrockAgentCoreApp`; local and cloud invocation
use the same payload contract.

```sh
agentcore configure --entrypoint my_agent.py
agentcore launch --local
agentcore invoke --local '{"prompt":"hello"}'
agentcore launch
agentcore status
```

Use Memory for short- and long-term state, Identity for managed credentials,
Gateway for MCP access to Smithy, Lambda, or OpenAPI targets, and CloudWatch
Transaction Search plus execution-role permissions for traces. AgentCore also
supports private networking, bring-your-own storage, gateway schema pinning,
rate limits, customer EC2 runtime capacity, evaluators, and payment resources.

### Observability and governance

- CloudWatch can create alarms from Logs queries and use wall-clock-aligned
  daily or weekly evaluation windows with optional time zones.
- Observability Admin manages organization/account telemetry rules and
  CloudWatch pipelines, including KMS encryption and tag propagation.
- AWS Config can inventory third-party cloud resources; Inspector2 can scan
  supported Azure resources.
- IAM Policy Simulator evaluates SCP conditions and resource scoping and
  reports explicit SCP denials as `explicitDeny`.

### Data and customer services

- AppConfig supports experiments; Experiment Run APIs may return
  `ConflictException`.
- Marketplace `BatchMeterUsage` accepts records for 24 hours after an event,
  while retaining the six-hour billing-cycle grace period.
- OpenSearch optimized domains require `EngineMode=OPTIMIZED` with
  `UseCase=OBSERVABILITY` or `MIXED`.
- Connect, QuickSight, Clean Rooms, Glue, Redshift, Marketplace, and media
  clients have substantial new request and response shapes. Read the indexed
  service reference before implementing them.
