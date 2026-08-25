---
name: aws-sdk-knowledge-patch
description: AWS SDK
version: null
license: MIT
metadata:
  author: Nevaberry
---


# AWS SDK Knowledge Patch

Use this skill when working with AWS SDK or CLI lifecycle changes, shared client
defaults, recently added service operations, or changed request and response
models. Identify the language, SDK major line, runtime, service client, and
deployment environment before applying guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [lifecycle-runtimes-and-packaging.md](references/lifecycle-runtimes-and-packaging.md) | SDK and tool lifecycle, runtime support, packaging, removed clients, and deprecated APIs |
| [client-configuration-auth-and-retries.md](references/client-configuration-auth-and-retries.md) | Endpoints, retries, authentication, checksums, protocols, tracing, and compatibility-sensitive validation |
| [compute-deployment-and-networking.md](references/compute-deployment-and-networking.md) | CloudFormation, compute, containers, databases, networking, streaming infrastructure, and disaster recovery |
| [observability-security-and-governance.md](references/observability-security-and-governance.md) | Monitoring, logs, IAM, security services, compliance, certificates, and organization controls |
| [data-marketplace-and-customer-services.md](references/data-marketplace-and-customer-services.md) | Analytics, data platforms, billing, Marketplace, Connect, media, and customer-facing APIs |
| [serverless-ai-storage-and-cdk.md](references/serverless-ai-storage-and-cdk.md) | Lambda, AgentCore, Bedrock, SageMaker, vector storage, backup access, and CDK Mixins |

## Breaking changes and migrations

### Move .NET SDK v3 applications to v4

The .NET SDK v3 is unsupported. Upgrade every `AWSSDK.*` dependency together
to 4.0.0 or later because v3 and v4 core and service packages cannot coexist.

.NET v4 collection properties default to `null` rather than empty collections.
Null-check before iteration and preserve the difference between unset and
explicitly empty request collections.

```csharp
if (response.Items is not null)
{
    foreach (var item in response.Items) { /* ... */ }
}
```

During a staged migration, this compatibility switch temporarily restores the
old initialization behavior:

```csharp
Amazon.AWSConfigs.InitializeCollections = true;
```

### Retire unsupported tools and APIs

- Move AWS Tools for PowerShell v4 installations to v5.
- Prefer AWS CLI v2 for upgrades and new deployments; CLI v1 is in maintenance.
- Do not build new integrations on Amazon Cloud Directory.
- Treat Amazon A2I `StartHumanLoop` as restricted to recognized existing
  customers.
- Replace deprecated Chime SDK Voice proxy-session and voice-connector proxy
  operations.

### Update JavaScript v3 packaging and clients

- Bundlers must consume `dist-es`; `dist-cjs` is no longer a bundler target.
- IoT Events, IoT Events Data, Panorama, and SimSpace Weaver clients were
  removed. Migrate or hold the prior release deliberately.
- Node.js 18 and pre-ES2023 targets are unsupported. Plan to leave Node.js 20
  and pre-ES2024 before their scheduled support end.

### Handle changed response and validation behavior

- Entity Resolution delete operations now raise a 404
  `ResourceNotFoundException` for missing resources; idempotent deletion must
  catch it.
- Inspector2 list responses no longer contain `Tags` on code-security
  integrations or scan configurations.
- New Marketplace metering integrations must use `CustomerAWSAccountId` and
  `LicenseArn`, not `CustomerIdentifier`.
- Outposts phone numbers, Organizations free text, DSQL Kinesis ARNs, and
  headquarters country/subdivision pairs have stricter validation.
- Connect WebRTC access denial is now `AccessDeniedException`, not an internal
  server error.

Read the lifecycle and client-configuration references before changing pinned
dependencies, runtime targets, generated models, or exception handling.

## Shared client defaults

### Regional STS endpoints

Python, PHP, C++, and .NET SDKs and AWS Tools for PowerShell now default to
Regional STS endpoints. AWS CLI v1 remains the exception among generally
available SDKs and CLIs. Do not assume implicit STS traffic routes through
`us-east-1` after an upgrade.

### Retry rollout

Supporting releases can opt into revised `standard` and `adaptive` behavior:

```sh
export AWS_NEW_RETRIES_2026=true
```

The revised behavior becomes the default in November 2026. Explicit `legacy`,
maximum-attempt, and backoff settings remain unchanged. Before rollout, unset
the flag to revert; afterward, configure individual retry options or use
`AWS_RETRY_MODE=legacy` where supported.

Updated standard retries use a 500-token quota. Transient retries cost 14
tokens and start at 50 ms; throttling retries cost 5 and start at 1,000 ms.
DynamoDB and DynamoDB Streams start at 25 ms and use four attempts by default.
Long-poll operations delay before surfacing quota exhaustion to prevent hot
loops.

### Authentication-scheme preference

Current SDK lines and CLI v2 can prioritize supported signing schemes:

```ini
[default]
auth_scheme_preference=sigv4a,sigv4
sigv4a_signing_region_set=us-east-1,us-west-2
```

Environment equivalents are `AWS_AUTH_SCHEME_PREFERENCE` and
`AWS_SIGV4A_SIGNING_REGION_SET`; the JVM property is
`aws.authSchemePreference`. Valid preferences are `sigv4`, `sigv4a`, and
`httpBearerAuth`. Unsupported legacy SDK lines keep their service defaults.

### Transport and tracing

- Keep TLS 1.3 enabled and SDK, CLI, and TLS dependencies updatable for hybrid
  ECDH plus ML-KEM negotiation. Existing certificates remain usable.
- JavaScript v3 propagates W3C trace headers.
- Protocol-capable clients may prefer Smithy RPC v2 CBOR over JSON. Do not
  assume every service retained CBOR; Pricing Calculator and BCM Recommended
  Actions rolled it back.
- The checksum implementation set includes CRC32C and SHA-1.

## High-value service features

### Lambda durable execution

Choose durable execution when creating the function; it cannot be enabled
later. Supported launch runtimes are Node.js 22 or 24 and Python 3.13 or 3.14.
Bundle the durable SDK and publish production code as versions so replay uses
the code version that began the execution.

Use `context.step()` for checkpointed retryable work, `context.wait()` for
compute-free suspension, `wait_for_condition()` for polling,
`create_callback()` for external completion, and `parallel()` or `map()` for
concurrency. An unhandled exception outside a step terminates the execution.

### S3 Vectors

Create vector buckets and indexes separately. Match the index dimension to the
embedding source, use `float32`, and choose cosine or Euclidean distance.

```sh
aws s3vectors create-index \
  --vector-bucket-name "$BUCKET_NAME" \
  --index-name "$INDEX_NAME" \
  --data-type float32 \
  --dimension "$DIMENSIONS" \
  --distance-metric "$DISTANCE_METRIC"
```

Each vector supports up to 50 metadata keys, with at most 10 non-filterable.
Queries filter only filterable metadata and can return up to 100 results with
metadata and distances.

### AgentCore runtime and gateway

Wrap a framework in `BedrockAgentCoreApp`, keep local and cloud invocation
payloads identical, and use the starter toolkit for roles, ECR, deployment, and
status:

```sh
agentcore configure --entrypoint my_agent.py
agentcore launch --local
agentcore invoke --local '{"prompt":"hello"}'
agentcore launch
agentcore status
```

Use Memory for short- and long-term state, Identity for workload identities and
vaulted credentials, and Gateway for MCP access to Smithy, Lambda, OpenAPI, and
managed connector targets. Configure Transaction Search and execution-role
permissions for CloudWatch trace delivery.

### CloudFormation and deployment controls

`CreateStack` and `UpdateStack` validate before deployment. Set
`DisableValidation` only when validation must be skipped; use `DeploymentConfig`
for Express mode. Also account for EKS version rollback and cancellation, ECS
circuit-breaker thresholds, and EC2 fleet override fields before generating
deployment request shapes.

### Observability and governance

- CloudWatch supports Logs-query alarms and wall-clock-aligned daily or weekly
  windows with optional time zones.
- AWS Config supports third-party cloud connectors; Inspector2 extends scanning
  to supported Azure resources.
- Observability Admin manages account and organization telemetry rules and can
  propagate or encrypt centralized telemetry configuration.
- IAM Policy Simulator now evaluates SCP conditions and resource scope more
  accurately; explicit SCP denials return `explicitDeny`.

## Working method

1. Read the project manifest for its exact SDK packages and runtime; consult
   lockfiles only when the manifest does not pin them.
2. Check lifecycle, packaging, endpoint, retry, authentication, and transport
   changes before editing dependencies or generated clients.
3. Open the task-specific reference before emitting operation names, request
   fields, enums, limits, or exception handling.
4. Preserve explicit compatibility settings during migrations unless the task
   explicitly removes them.
5. Trust project manifests, code, tests, and observed current behavior when they
   conflict with generalized guidance.
