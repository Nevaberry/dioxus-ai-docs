# Serverless, AI runtimes, storage, and CDK

Use this reference for Lambda, AgentCore, Bedrock, SageMaker, vector indexes,
backup access points, S3 lifecycle changes, and CDK Mixins.

## Lambda deployment and durable execution

### Lambda code in self-managed S3 buckets (2026-06)

Lambda can reference function code in a self-managed S3 bucket. This permits a
single retained code copy and makes code-storage limits user-managed.

### Lambda Durable Functions KMS keys (2026-07)

Lambda Durable Config accepts a customer-managed KMS key that encrypts all
durable-execution data.

### Lambda durable-function creation and compatibility

Durable execution must be selected when the function is created and cannot be
enabled later. Launch runtimes are Node.js 22 or 24 for JavaScript/TypeScript
and Python 3.13 or 3.14. Bundle the fast-moving durable execution SDK with the
function and publish production code as Lambda versions so suspended execution
replay uses the version that started it. (`service-client-launches`)

### Lambda durable execution primitives

Durable functions checkpoint completed steps and replay the handler after an
interruption while skipping those steps. Waits suspend without compute charges
for up to one year. Use `context.step()` for checkpoints and retries,
`context.wait()` for suspension, `wait_for_condition()` for polling,
`create_callback()` for external completion, and `parallel()` or `map()` for
concurrency. (`service-client-launches`)

```python
from aws_durable_execution_sdk_python import durable_execution, durable_step

@durable_step
def work(step_context, value):
    return {"value": value}

@durable_execution
def lambda_handler(event, context):
    return context.step(work(event["value"]))
```

### Lambda durable retries, callbacks, and invocation

Exceptions inside a step trigger its retry strategy; an unhandled exception
outside a step terminates the execution. `context.logger` suppresses replay
duplicates. A callback exposes `callback_id` for
`SendDurableExecutionCallbackSuccess` or
`SendDurableExecutionCallbackFailure`. Invoking twice with the same durable
execution name returns the existing result instead of starting a duplicate.
(`service-client-launches`)

### Lambda durable events and local tests

Lambda publishes status changes to the default EventBridge bus with source
`aws.lambda` and detail type `Durable Execution Status Change`. The separate
testing SDK supports credential-free pytest tests; SAM provides broader
integration testing. (`service-client-launches`)

### Lambda managed-capacity telemetry and runtimes (2026-07-2)

Managed Instances Capacity Providers accept `TelemetryConfig` for system-log
level and a custom log group. Lambda also recognizes `java8.al2023`,
`java11.al2023`, `java17.al2023`, `python3.15`, and `nodejs26.x` runtimes.

### Lambda dependency failure reasons (2026-07-2)

`StateReasonCode` and `LastUpdateStatusReasonCode` can return `DependencyError`
when an upstream dependency or service prevents a function from becoming
healthy.

## S3 Vectors, DynamoDB vectors, and backup access

### S3 Vectors resources and indexes

Vector buckets and indexes are separate resources. An index uses `float32`, its
dimension must match the embedding source, and its distance metric is cosine or
Euclidean. (`service-client-launches`)

```sh
aws s3vectors create-vector-bucket \
  --vector-bucket-name "$BUCKET_NAME"
aws s3vectors create-index \
  --vector-bucket-name "$BUCKET_NAME" \
  --index-name "$INDEX_NAME" \
  --data-type float32 \
  --dimension "$DIMENSIONS" \
  --distance-metric "$DISTANCE_METRIC"
```

### S3 Vectors metadata, queries, and deployment

Each vector supports up to 50 metadata keys; at most 10 can be non-filterable.
Only filterable metadata participates in query filters. Queries can return
metadata and distance for up to 100 results. Indexes inherit bucket encryption
unless assigned an index-level KMS key. Buckets and indexes support tags,
CloudFormation, and PrivateLink; Bedrock Knowledge Bases and OpenSearch can use
S3 Vectors as a vector store. (`service-client-launches`)

```sh
aws s3vectors query-vectors \
  --index-arn "$INDEX_ARN" \
  --query-vector "{\"float32\": $VECTOR}" \
  --top-k 100 \
  --return-metadata \
  --return-distance
```

### S3 lifecycle transition timing (2026-07-2)

The former 30-day minimum before transition to Standard-IA or OneZone-IA has
been removed. Lifecycle configuration generators no longer need to preserve
that delay.

### DynamoDB vector indexes (2026-07-2)

DynamoDB vector indexes perform approximate-nearest-neighbor similarity search
over embeddings stored in table items.

### Read-only S3 backup access points (2026-08)

AWS Backup and S3 support read-only access points for S3 recovery points. They
allow S3 API access to backup data without restoring it first.

## AgentCore runtime, deployment, and identity

### AgentCore Runtime SDK and deployment CLI

Expose any agent framework through `BedrockAgentCoreApp`. The decorated entry
point defines the invocation payload, and local and cloud invocations use the
same contract. The starter toolkit creates an execution role and ECR
repository, builds and launches locally or remotely, and reports endpoint
status. (`service-client-launches`)

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    return payload["prompt"]

app.run()
```

```sh
agentcore configure --entrypoint my_agent.py
agentcore launch --local
agentcore invoke --local '{"prompt":"hello"}'
agentcore launch
agentcore status
```

### AgentCore short- and long-term memory

`MemoryClient.create_event()` stores `USER`, `ASSISTANT`, and `TOOL` messages
under a memory, actor, and session; `list_events()` retrieves recent short-term
context. Long-term strategies for preferences, summaries, or semantic facts use
namespaces such as `/facts/{actorId}` and `retrieve_memories()` for semantic
retrieval. A strategy added to an existing store affects only subsequently
created events. (`service-client-launches`)

### AgentCore identity and gateway compatibility

`IdentityClient` creates workload identities and OAuth 2.0 or API-key credential
providers. `@requires_access_token` supplies provider-scoped tokens from the
managed vault. Gateway exposes Smithy-modeled AWS services, Lambda functions,
and OpenAPI APIs through MCP, with separate inbound and outbound
authentication. (`service-client-launches`)

### AgentCore deployment and observability

All AgentCore services support VPC connectivity, PrivateLink, CloudFormation,
and tags. Starter-toolkit configuration enables observability by default, but
CloudWatch trace delivery also needs Transaction Search and permissions on the
execution role. Telemetry is OpenTelemetry-compatible.
(`service-client-launches`)

### AgentCore authorizer scope mapping (2026-07)

Gateway inbound authorizers can map allowed scopes to a separate set of scopes
advertised to clients.

### AgentCore endpoint validation and model parameters (2026-07-2)

AgentCore Control accepts service-emitted harness ARNs containing
`harness-endpoint` rather than `endpoint`. Provider model configuration also
accepts `additionalParams` for provider-specific passthrough values.

### AgentCore Gateway schema pinning and streamed metadata (2026-07-2)

Gateway targets can pin a connector version to stabilize tool schemas. Web
search connector 1.2.0 adds agent-side domain and publication-date filters and
administrator domain allowlists. InvokeHarness streaming deltas expose
`toolResultMetadata`, avoiding oversized SSE frames that embed MCP metadata.

### AgentCore bring-your-own storage (2026-07-2)

AgentCore Browser and Code Interpreter can mount S3 files and EFS file systems
through access points.

### AgentCore OpenResponses evaluators (2026-07-2)

`CreateEvaluator` and `UpdateEvaluator` accept an OpenResponses model
configuration for custom LLM-as-a-Judge evaluators.

### AgentCore third-party evaluators (2026-08)

AgentCore Control supports third-party evaluators as managed services and as
templates within custom evaluators.

### AgentCore payment options (2026-08)

AgentCore Payments supports customer-managed keys, Marketplace subscriptions,
QuickCreate, Machine Payments Protocol resources, and the `upto` scheme for
x402 payments.

### AgentCore recommendation evaluator input (2026-08)

AgentCore recommendation requests can include an online-evaluation ARN.

### AgentCore gateway limits and EC2 runtimes (2026-08)

AgentCore gateways can rate-limit requests, tokens, and active connections.
Capacity providers can run runtimes on customer EC2 instances and allow an
active capacity-provider session to be deleted.

### AgentCore Memory connector access controls (2026-08)

AgentCore Memory supports fine-grained access control through managed AgentCore
Gateway HTTP connectors.

## Bedrock retrieval and conversation APIs

### Bedrock mid-conversation tool changes (2026-07-2)

Bedrock `Converse` and `ConverseStream` can change the available tools during a
conversation. Do not assume the initial tool set remains fixed.

### Agentic retrieval memory (2026-08)

Bedrock `AgenticRetrieveStream` accepts `memoryConfiguration` to continue a
session from AgentCore short-term memory and retrieve relevant long-term memory.

### Bedrock ingested-document ACL inspection (2026-08)

Knowledge Bases provides `CheckIngestedDocumentAcl` and
`GetIngestedDocumentAcl` to test a user's access to an ingested document and
retrieve its allow and deny entries.

## SageMaker training, inference, and notebooks

### SageMaker instance-type support (2026-07-2)

HyperPod supports g4d, c6g, c7g, c8g, c6a, m6a, m6g, m7g, and m8g. Inference
endpoints support g7. Studio JupyterLab and CodeEditor apps support g7 in
`us-east-1`, `us-west-2`, and `us-east-2`.

### SageMaker inference-optimization adapters (2026-07-2)

Inference optimization supports LoRA adapters and training plans:
`CreateAIRecommendationJob` accepts `AdapterSource`, while
`CreateOptimizationJob` accepts `TrainingPlanArns` and `ml.g7e` and
`ml.p6-b200` instance families.

### SageMaker g7 and training controls (2026-08)

SageMaker model-customization training accepts `SequenceLength`; training and
processing support g7. HyperPod accepts `g7.2xlarge`, `g7.4xlarge`,
`g7.8xlarge`, `g7.12xlarge`, `g7.24xlarge`, and `g7.48xlarge`.

### SageMaker prefix-aware routing (2026-08)

Endpoint configurations accept `PREFIX_AWARE` and `PrefixAwareRoutingConfig`
with `PrefixLength` and `ConcurrencyThreshold`. `InvokeEndpoint` and
`InvokeEndpointWithResponseStream` accept `PrefixAwareId` as the routing hint.

### SageMaker notebook maintenance states (2026-08)

SageMaker Notebook Instances expose maintenance lifecycle statuses. Treat these
as valid states in pollers and user interfaces.

## CDK composition

### CDK Mixins

`aws-cdk-lib` provides composable Mixins that add reusable behavior to L1, L2,
or custom constructs through `.with()` without rebuilding the construct
hierarchy. `Mixins.of()` applies policies across a scope with resource-type or
path-pattern filtering. (`service-client-launches`)
