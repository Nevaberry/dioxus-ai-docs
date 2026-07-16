# Serverless, AI runtimes, storage, and CDK

## Contents

- [Lambda code storage and encryption](#lambda-code-storage-and-encryption)
- [Lambda Durable Functions](#lambda-durable-functions)
- [AgentCore](#agentcore)
- [S3 Vectors](#s3-vectors)
- [CDK Mixins](#cdk-mixins)

## Lambda code storage and encryption

- Lambda can reference function source code in a customer-managed S3 bucket (since `2026-06`). This permits one managed copy of the code and gives the customer control over code-storage limits; grant Lambda access to the object and any encryption key.
- Durable Config can specify a customer-managed KMS key for Lambda Durable Functions execution data (since `2026-07`). Include KMS permissions for every execution path that reads or writes durable state.

## Lambda Durable Functions

### Creation and compatibility

Select durable execution when creating the Lambda function; it cannot be added to an existing function. An execution can suspend at defined points for up to one year without holding idle compute.

Launch SDK support covers:

- JavaScript and TypeScript on Node.js 22 or 24.
- Python on Python 3.13 or 3.14.

Bundle the durable-execution SDK with the function. Publish production code as Lambda versions so a suspended execution always replays against the version on which it began.

### Steps, waits, and concurrency

In Python, decorate the handler with `@durable_execution` and replay-safe units of work with `@durable_step`. `context.step()` checkpoints a result, retries failures, and skips completed work when the handler replays.

```python
from aws_durable_execution_sdk_python import (
    DurableContext, StepContext, durable_execution, durable_step,
)

@durable_step
def work(step_context: StepContext, value: str) -> dict:
    return {"value": value}

@durable_execution
def lambda_handler(event: dict, context: DurableContext) -> dict:
    return context.step(work(event["value"]))
```

Use `context.wait()` to suspend without consuming compute. Use `wait_for_condition()` for polling and `parallel()` or `map()` for concurrent patterns.

### Callbacks and retry boundaries

`context.create_callback()` returns a callback ID to send to an external system. `callback.result()` suspends until the external system calls `SendDurableExecutionCallbackSuccess` or `SendDurableExecutionCallbackFailure`.

```python
callback = context.create_callback(
    name="awaiting-approval",
    config=CallbackConfig(timeout=Duration.from_minutes(3)),
)
context.step(send_for_approval(callback.callback_id, order_id))
approval_result = callback.result()
```

Exceptions inside a step use that step's default retry policy or `StepConfig`. An unhandled exception outside a step terminates the entire execution. Log through `context.logger` and `step_context.logger` so replay does not duplicate log entries.

### Invocation, events, and tests

- Start a durable workflow with an asynchronous invocation.
- Reusing the same durable execution name is idempotent: Lambda returns the existing result instead of creating a duplicate execution.
- Status changes are delivered to the default EventBridge bus.

```json
{
  "source": ["aws.lambda"],
  "detail-type": ["Durable Execution Status Change"]
}
```

Use the separate testing SDK with pytest or AWS SAM for local tests; those tests do not require AWS credentials.

## AgentCore

### Runtime SDK and deployment CLI

The `bedrock-agentcore` package wraps an arbitrary agent framework in `BedrockAgentCoreApp`. The `bedrock-agentcore-starter-toolkit` package provides the `agentcore` CLI.

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    return agent(payload.get("prompt", "No prompt supplied"))

if __name__ == "__main__":
    app.run()
```

The `configure` command can create the execution role and ECR repository and detect dependencies. Local and cloud launch modes use the same entry-point payload contract.

```sh
agentcore configure --entrypoint my_agent.py
agentcore launch --local
agentcore invoke --local '{"prompt":"hello"}'
agentcore launch
agentcore status
agentcore invoke '{"prompt":"hello"}'
```

At general availability, every AgentCore service supports VPC connectivity, PrivateLink, CloudFormation, and resource tags.

### Short- and long-term memory

`MemoryClient.create_memory_and_wait(..., strategies=[])` creates short-term storage. `create_event()` stores role-tagged messages under a memory, actor, and session; `list_events()` reloads recent turns.

Long-term strategies extract preferences, summaries, or semantic facts into namespace-partitioned storage. Adding a strategy to an existing store affects new events. `retrieve_memories()` performs semantic lookup within one namespace.

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")
memory = client.create_memory_and_wait(
    name="CustomerSupport",
    description="Customer support conversations",
    strategies=[{
        "semanticMemoryStrategy": {
            "name": "semanticFacts",
            "namespaces": ["/facts/{actorId}"],
        }
    }],
)
client.create_event(
    memory_id=memory["id"], actor_id="user-123", session_id="session-456",
    messages=[("Hi", "USER"), ("Hello", "ASSISTANT")],
)
facts = client.retrieve_memories(
    memory_id=memory["id"], namespace="/facts/user-123", query="preferences",
)
```

### Workload identity and credentials

`IdentityClient.create_workload_identity()` gives an agent its own identity. Credential providers can vault OAuth client credentials, user tokens, or API keys. Functions decorated with `@requires_access_token` request a named provider and scopes. Vaulted OAuth user tokens are reused until expiry; then a new authorization prompt is required.

```python
from bedrock_agentcore.services.identity import IdentityClient

identity = IdentityClient("us-east-1")
workload = identity.create_workload_identity(name="my-agent")
provider = identity.create_api_key_credential_provider({
    "name": "external-api",
    "apiKey": "api-key",
})
```

### Gateway and authorizers

AgentCore Gateway exposes one MCP interface over AWS services described by Smithy, Lambda functions, and internal or third-party APIs described by OpenAPI. It applies separate authentication to inbound agent requests and outbound target connections. It can publish an OAuth interface for tools, including AWS services, that do not expose one themselves.

Inbound authorizers can map allowed scopes to different advertised scopes (since `2026-07`). Keep the enforcement and discovery mappings distinct.

### Observability

Starter configuration enables observability by default. CloudWatch trace delivery additionally requires Transaction Search and suitable permissions on the execution role. The X-Ray settings below affect trace ingestion for the whole account, not only one agent. AgentCore telemetry is OpenTelemetry-compatible.

```sh
aws xray update-trace-segment-destination --destination CloudWatchLogs
aws xray update-indexing-rule \
  --name Default \
  --rule '{"Probabilistic":{"DesiredSamplingPercentage":1}}'
```

## S3 Vectors

### Buckets and indexes

The `s3vectors` client creates vector buckets and indexes separately. An index uses `float32` data, an embedding dimension that must match the embedding source, either `cosine` or Euclidean distance, and optional non-filterable metadata keys.

```sh
aws s3vectors create-vector-bucket --vector-bucket-name "$BUCKET_NAME"
aws s3vectors create-index \
  --vector-bucket-name "$BUCKET_NAME" \
  --index-name "$INDEX_NAME" \
  --data-type float32 \
  --dimension "$DIMENSIONS" \
  --distance-metric "$DISTANCE_METRIC" \
  --metadata-configuration \
    'nonFilterableMetadataKeys=AMAZON_BEDROCK_TEXT,AMAZON_BEDROCK_METADATA'
```

### Metadata and queries

Each vector can have up to 50 metadata keys, of which at most 10 can be non-filterable. Filterable keys can constrain similarity searches; non-filterable keys store context without enlarging the searchable index. `query-vectors` accepts a `float32` query vector and can return metadata and distances.

```sh
aws s3vectors query-vectors \
  --index-arn "$S3_VECTOR_INDEX_ARN" \
  --query-vector "{\"float32\": $VECTOR_ARRAY}" \
  --top-k 3 \
  --return-metadata \
  --return-distance
```

### Encryption and integrations

Indexes inherit vector-bucket encryption unless they override it with a customer-managed KMS key. Vector buckets and indexes support tags; index tags can drive access control and cost allocation.

Manage vector resources with CloudFormation and access them through PrivateLink. S3 Vectors can serve as the vector store for Bedrock Knowledge Bases or as the storage layer behind OpenSearch.

## CDK Mixins

`aws-cdk-lib` supports composable Mixins on L1, L2, and custom constructs through `.with()` calls. Mixins can add encryption, versioning, auto-delete, public-access blocking, and similar policies without replacing the construct.

`Mixins.of()` applies policies across a scope and can filter by resource type or path pattern. Combine multiple Mixins into a custom L2 construct when a reusable higher-level policy bundle is needed.
