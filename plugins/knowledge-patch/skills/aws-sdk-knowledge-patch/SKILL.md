---
name: aws-sdk-knowledge-patch
description: AWS SDK rolling coverage. Use for AWS SDK work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# AWS SDK Knowledge Patch

Baseline: AWS SDK for JavaScript v3, boto3/botocore, AWS SDK for Java 2.x, Go v2, .NET v3, and pre-2025/2026 shared SDK defaults and lifecycle state. Covered range: lifecycle and shared behavior through July 2026, plus service changes in `2026-06` and `2026-07`.

Coverage identifiers: `sdk-lifecycle-and-eol`, `shared-defaults-and-runtime-support`, `crypto-auth-and-rust-runtime`, and `service-client-launches`.

## Reference index

| Reference | Topics |
| --- | --- |
| [lifecycle-runtimes-and-packaging.md](references/lifecycle-runtimes-and-packaging.md) | Major-version lifecycle, migrations, .NET collection semantics, Python and Node.js support, JavaScript packaging, removed APIs |
| [client-configuration-auth-and-retries.md](references/client-configuration-auth-and-retries.md) | Regional STS, 2026 retry behavior, authentication-scheme selection, SigV4a, W3C tracing, CBOR, post-quantum TLS |
| [compute-deployment-and-networking.md](references/compute-deployment-and-networking.md) | CloudFormation, CodeBuild, EKS, ECS, EC2, Auto Scaling, VPC, Route 53, MSK, ACM, EVS, PCS |
| [observability-security-and-governance.md](references/observability-security-and-governance.md) | CloudWatch, Config, Inspector, GuardDuty, Resource Explorer, IAM-authenticated OAuth, WAF, Artifact, Resilience Hub |
| [data-marketplace-and-customer-services.md](references/data-marketplace-and-customer-services.md) | DataZone, Clean Rooms, AppConfig, Connect, OpenSearch, Places, billing, Marketplace, Partner Central, media APIs |
| [serverless-ai-storage-and-cdk.md](references/serverless-ai-storage-and-cdk.md) | Lambda storage and durable execution, AgentCore, S3 Vectors, CDK Mixins |

## Apply this patch

1. Identify the SDK language, major version, runtime, service client, and deployment environment.
2. Check lifecycle and runtime support before changing dependencies or build targets.
3. Check shared endpoint, retry, authentication, and transport defaults before relying on implicit configuration.
4. Read the task-specific reference before generating service request shapes or enum values.
5. Preserve explicit retry settings and other intentional compatibility overrides during migrations.

## Breaking changes and required migrations

### Retired major versions

| Line | Lifecycle state | Required action |
| --- | --- | --- |
| AWS SDK for .NET v3 | Maintenance began March 1, 2026; support ended June 1, 2026 | Upgrade every `AWSSDK.*` package to 4.0.0 or later together; v3 and v4 packages cannot coexist |
| AWS SDK for Go v1 | Support ended July 31, 2025 | Perform the one-time source migration to Go v2 |
| AWS SDK for JavaScript v2 | Support ended September 8, 2025 | Move to modular v3; use the automated migration tool where useful |
| AWS SDK for Java 1.x | End of support | Move to Java 2.x |
| AWS Tools for PowerShell 4.x | End of support | Move to PowerShell 5.x |
| AWS CLI 1.x | Maintenance announced | Prefer CLI 2.x for the current GA line |

Maintenance lines receive only critical bug and security fixes: they do not gain new services, APIs, or Regions. End-of-support lines receive no releases.

### .NET v4 collection semantics

Request and response collections now default to `null`, not empty collections. Null-check before iterating and preserve the distinction between unset and explicitly empty values.

```csharp
if (response.Items is not null)
{
    foreach (var item in response.Items) { /* ... */ }
}
```

`Amazon.AWSConfigs.InitializeCollections = true` temporarily restores v3-style initialization, at the cost of the new semantics and performance benefit.

### JavaScript packaging and removed clients

- IoT Events, IoT Events Data, Panorama, and SimSpace Weaver clients were removed in `2026-06`.
- Bundler support was removed from `dist-cjs`; configure bundlers to consume `dist-es`.
- JavaScript v3 ended Node.js 18 and pre-ES2023 support in January 2026. Node.js 20 and pre-ES2024 support are scheduled to end in January 2027.
- Cloud9's public EC2-environment creation API removed Amazon Linux 2 from accepted AMI options in `2026-07`.
- Outposts site requests now enforce a stricter `ContactPhoneNumber` pattern; previously accepted values can fail client-side or service validation.

## Shared defaults

### Regional STS endpoints

Since July 31, 2025, Python, PHP, C++, and .NET SDKs and AWS Tools for PowerShell default to Regional STS endpoints. AWS CLI v1 remains the exception among generally available SDKs and CLIs. Do not assume implicit STS traffic routes through `us-east-1`.

### Retry rollout

The planned July 2025 default switch was postponed. Supporting releases can opt into updated `standard` and `adaptive` behavior now; it becomes the default in November 2026.

```sh
export AWS_NEW_RETRIES_2026=true
```

- An explicitly selected `legacy` mode remains unchanged.
- Explicit maximum-attempt and backoff settings remain preserved.
- Updated standard retries charge 14 quota tokens for transient errors and 5 for throttling against a 500-token budget.
- Transient errors use a 50 ms base delay; throttling uses 1,000 ms.
- DynamoDB and DynamoDB Streams use a 25 ms base delay and four attempts by default.
- Long-polling operations delay before returning an error after quota exhaustion, avoiding hot loops.

Before the rollout, unset `AWS_NEW_RETRIES_2026` to revert. Afterward, set individual retry options or use `AWS_RETRY_MODE=legacy` where supported.

### Runtime cadence

| Runtime | Current boundary |
| --- | --- |
| Python for Boto3, Botocore, CLI v1 | Python 3.9 support ended April 2026; 3.10 ends April 2027; 3.11 ends April 2028 |
| Node.js for JavaScript v3 | Current LTS majors plus the most recently retired major for about eight months |
| AWS CLI v2 | No local Python dependency |

Pinning an older JavaScript v3 release may retain runtime compatibility, but does not restore support, service updates, or fixes.

## Authentication and transport

Set a priority order for supported authentication schemes in shared configuration:

```ini
[default]
auth_scheme_preference=sigv4a,sigv4
sigv4a_signing_region_set=us-east-1,us-west-2
```

Equivalent settings are `AWS_AUTH_SCHEME_PREFERENCE`, `AWS_SIGV4A_SIGNING_REGION_SET`, and `aws.authSchemePreference` on the JVM. Valid preferences are `sigv4`, `sigv4a`, and `httpBearerAuth`; if none is available, use the service default. SigV4a signs more slowly but remains valid across the configured Region set.

JavaScript v3 now propagates W3C trace headers. Mail Manager can negotiate Smithy RPC v2 CBOR or AWS JSON 1.0 and automatically prioritizes the most performant supported protocol.

For future hybrid ECDH plus ML-KEM negotiation, keep TLS 1.3 enabled and keep SDK, CLI, and TLS dependencies up to date. Existing certificates remain usable for the planned ELB, API Gateway, and CloudFront rollout.

## Lambda Durable Functions

Select durable execution when creating a function; it cannot be enabled later. Supported launch runtimes are Node.js 22 or 24 with JavaScript/TypeScript and Python 3.13 or 3.14. Bundle the durable SDK and publish production functions as versions so suspended executions replay against their starting version.

```python
from aws_durable_execution_sdk_python import durable_execution, durable_step

@durable_step
def work(step_context, value):
    return {"value": value}

@durable_execution
def lambda_handler(event, context):
    return context.step(work(event["value"]))
```

Use `context.wait()` for compute-free suspension, `wait_for_condition()` for polling, and `parallel()` or `map()` for concurrency. Keep retryable work inside steps: an unhandled exception outside a step terminates the execution.

## S3 Vectors

Create vector buckets and indexes separately. Match the index dimension to the embedding source, use `float32`, and choose cosine or Euclidean distance.

```sh
aws s3vectors create-index \
  --vector-bucket-name "$BUCKET_NAME" \
  --index-name "$INDEX_NAME" \
  --data-type float32 \
  --dimension "$DIMENSIONS" \
  --distance-metric "$DISTANCE_METRIC"
```

Each vector supports up to 50 metadata keys; up to 10 may be non-filterable. Query filters operate on filterable metadata, while responses can include metadata and distances.

## AgentCore

Wrap any agent framework in `BedrockAgentCoreApp`, then use the starter toolkit for matching local and cloud payload contracts:

```sh
agentcore configure --entrypoint my_agent.py
agentcore launch --local
agentcore invoke --local '{"prompt":"hello"}'
agentcore launch
agentcore status
```

At GA, every AgentCore service supports VPC connectivity, PrivateLink, CloudFormation, and tags. Use Memory for short- or long-term state, Identity for workload identities and vaulted credentials, Gateway for MCP access to Smithy, Lambda, or OpenAPI targets, and CloudWatch Transaction Search plus execution-role permissions for trace delivery.

## High-impact service changes

- CloudFormation now validates `CreateStack` and `UpdateStack` before deployment; use `DisableValidation` to skip or `DeploymentConfig` for Express mode.
- EKS supports version rollback, rollback timeouts, cancellation, and cancellation details.
- ECS deployment circuit breakers accept a custom threshold and failure-counting mechanism.
- EC2 fleet launch-template overrides now include user data, key name, instance profile, and metadata options.
- CloudWatch supports Logs-query alarms and wall-clock-aligned daily or weekly windows with time zones.
- AWS Config can inventory third-party cloud resources; Inspector2 can scan supported Azure resources.
- AppConfig supports experiments, and experiment APIs can return `ConflictException`.
- Marketplace metering accepts records for 24 hours after an event while retaining the six-hour billing-cycle grace period.

Read the indexed reference for complete request fields, response fields, constraints, and examples before implementing any of these APIs.
