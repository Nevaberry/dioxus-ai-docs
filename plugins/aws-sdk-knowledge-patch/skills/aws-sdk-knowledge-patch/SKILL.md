---
name: aws-sdk-knowledge-patch
description: "AWS SDK changes since training cutoff — S3 default checksums, S3 Vectors, Lambda Durable Functions, Bedrock AgentCore, CDK Mixins, SigV4a, SDK lifecycle. Load before working with AWS SDKs."
version: "0.1.0"
license: MIT
metadata:
  author: Nevaberry
---

# AWS SDK Knowledge Patch

Covers AWS SDK changes from 2024-12 through 2026-03. Applies to JS v3 ~3.600+, boto3 ~1.34+, aws-sdk-go-v2 ~1.26+, CDK v2 ~2.140+.

## Index

| Topic | Reference | Key features |
|---|---|---|
| S3 checksums & vectors | [references/s3-checksums-and-vectors.md](references/s3-checksums-and-vectors.md) | Default CRC checksums, CRC64NVME, full-object multipart checksums, S3 Vectors service |
| Lambda Durable Functions | [references/lambda-durable-functions.md](references/lambda-durable-functions.md) | Checkpoint-and-replay, `@durable_step`, wait/callback, idempotency |
| Bedrock AgentCore | [references/bedrock-agentcore.md](references/bedrock-agentcore.md) | Runtime deployment, memory client, identity/OAuth2, CLI |
| CDK & SDK config | [references/cdk-and-sdk-config.md](references/cdk-and-sdk-config.md) | CDK Mixins `.with()`, SigV4a auth scheme preference, STS regional default, SDK lifecycle |

---

## S3 Default Checksums (Dec 2024) — Breaking Change

SDKs now compute CRC checksums on **every upload** by default. S3 also computes server-side checksums on all uploads.

New algorithm: **CRC64NVME**. Default algorithms vary by SDK:

| SDK | Default algorithm |
|---|---|
| CLI, C++, Rust | CRC64NVME |
| Go, Java, JS, Kotlin, .NET, PHP, Python, Ruby | CRC32 |

Config settings:

| Setting | Env var | Default |
|---|---|---|
| `request_checksum_calculation` | `AWS_REQUEST_CHECKSUM_CALCULATION` | `WHEN_SUPPORTED` |
| `response_checksum_validation` | `AWS_RESPONSE_CHECKSUM_VALIDATION` | `WHEN_SUPPORTED` |

Multipart uploads now support `ChecksumType='FULL_OBJECT'` for a single whole-object checksum instead of per-part composites.

See [references/s3-checksums-and-vectors.md](references/s3-checksums-and-vectors.md) for full examples.

## S3 Vectors (GA Dec 2025)

New S3 service for storing/querying vector embeddings. Separate from regular S3 buckets.

```bash
aws s3vectors create-vector-bucket --vector-bucket-name my-vectors
aws s3vectors create-index \
    --vector-bucket-name my-vectors \
    --index-name my-index \
    --data-type float32 --dimension 1024 \
    --distance-metric cosine \
    --metadata-configuration "nonFilterableMetadataKeys=text_chunk"
```

Supports cosine and euclidean distance. Up to 2B vectors/index, 50 metadata keys/vector (10 non-filterable). Integrates with Bedrock Knowledge Bases and OpenSearch.

See [references/s3-checksums-and-vectors.md](references/s3-checksums-and-vectors.md) for query examples.

## Lambda Durable Functions (Dec 2025)

Checkpoint-and-replay execution for Lambda. **Must be enabled at function creation time** (cannot be added later). Open-source SDK.

```python
from aws_durable_execution_sdk_python import (
    DurableContext, StepContext, durable_execution, durable_step,
)
from aws_durable_execution_sdk_python.config import Duration, StepConfig, CallbackConfig

@durable_step
def my_step(step_context: StepContext, data: str) -> dict:
    return {"result": data}

@durable_execution
def lambda_handler(event: dict, context: DurableContext) -> dict:
    result = context.step(my_step(event["data"]))
    context.wait(Duration.from_minutes(5))  # suspends without compute charges
    return result
```

Supports JS/TS (Node.js 22/24) and Python (3.13/3.14). See [references/lambda-durable-functions.md](references/lambda-durable-functions.md) for callbacks and retry strategies.

## Bedrock AgentCore (GA Oct 2025)

Enterprise services for deploying AI agents at scale. Framework-agnostic (Strands, LangGraph, etc.).

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    return agent(payload.get("prompt"))
```

Install: `pip install bedrock-agentcore bedrock-agentcore-starter-toolkit`
CLI: `agentcore configure`, `agentcore launch [--local]`, `agentcore invoke`.

See [references/bedrock-agentcore.md](references/bedrock-agentcore.md) for memory client, identity, and full API.

## CDK Mixins (GA Mar 2026)

Composable, reusable abstractions for any CDK construct via `.with()` syntax:

```typescript
const bucket = new s3.CfnBucket(this, 'Bucket').with(
  AutoDelete(),
  Encryption(),
  Versioning(),
  BlockPublicAccess(),
);
// Apply compliance policies across a scope:
Mixins.of(this).add(/* resource type or path pattern filtering */);
```

See [references/cdk-and-sdk-config.md](references/cdk-and-sdk-config.md) for details.

## Auth Scheme Preference (SigV4a)

New config for cross-region signing (e.g., multi-region access points):

```ini
# ~/.aws/config
[default]
auth_scheme_preference = sigv4a, sigv4
sigv4a_signing_region_set = us-east-1, eu-west-1
```

Env vars: `AWS_AUTH_SCHEME_PREFERENCE`, `AWS_SIGV4A_SIGNING_REGION_SET`.

## SDK Version Lifecycle

| SDK | Maintenance | End of Support | Migrate To |
|---|---|---|---|
| JS v2 | Sep 2024 | Sep 2025 | JS v3 |
| Go v1 | Jul 2024 | Jul 2025 | Go v2 |
| .NET v3 | Mar 2026 | Jun 2026 | .NET v4 (GA Apr 2025) |

**JS v3 Node.js**: Follows Node.js release + 8 months. Node.js 18 dropped Jan 2026 (requires 20+). Node.js 20 drops Jan 2027.

**Python (boto3)**: 6-month grace after PSF EOL. Python 3.9 drops Apr 2026, 3.10 drops Apr 2027.

## SDK Default Changes (July 2025)

- **STS endpoint**: Python, PHP, C++, .NET, PowerShell switch to `regional` default (was global)
- **Retry strategy**: Switch to `standard` (token-bucket throttling) delayed — AWS found concerns, will reschedule

## Reference Files

| File | Contents |
|---|---|
| [s3-checksums-and-vectors.md](references/s3-checksums-and-vectors.md) | Default checksums, CRC64NVME, multipart full-object checksums, S3 Vectors API |
| [lambda-durable-functions.md](references/lambda-durable-functions.md) | Durable execution SDK, steps, wait/callback, retry strategies |
| [bedrock-agentcore.md](references/bedrock-agentcore.md) | Runtime deployment, memory client, identity, CLI commands |
| [cdk-and-sdk-config.md](references/cdk-and-sdk-config.md) | CDK Mixins, SigV4a, STS regional default, SDK lifecycle dates |
