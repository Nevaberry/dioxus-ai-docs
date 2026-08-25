# Serverless, AI runtimes, storage, and CDK

## CDK Mixins (`service-client-launches`)

- **CDK Mixins.** `aws-cdk-lib` supplies composable Mixins that add reusable
  behavior to L1, L2, or custom constructs through `.with()` without
  rebuilding the hierarchy. `Mixins.of()` applies policies across a scope with
  resource-type or path-pattern filters.

## Lambda

### Function code, capacity, and status

- **Lambda code in self-managed S3 buckets (`2026-06`).** Function code can
  reside in a self-managed S3 bucket, allowing one retained copy and
  user-managed code-storage limits.
- **Lambda managed-capacity telemetry and runtimes (`2026-07-2`).** Managed
  Instances Capacity Providers accept `TelemetryConfig` for system-log level
  and a custom log group. Runtime enums include `java8.al2023`,
  `java11.al2023`, `java17.al2023`, `python3.15`, and `nodejs26.x`.
- **Lambda dependency failure reasons (`2026-07-2`).** `StateReasonCode` and
  `LastUpdateStatusReasonCode` can return `DependencyError` when an upstream
  service prevents a function from becoming healthy.

### Durable execution creation (`service-client-launches`)

- **Lambda durable-function creation and compatibility.** Select durable
  execution when creating the function; it cannot be enabled later. Launch
  runtimes are Node.js 22 or 24 for JavaScript/TypeScript and Python 3.13 or
  3.14. Bundle the durable SDK and publish production functions as versions so
  suspended executions replay against the version that started them.
- **Lambda durable execution primitives.** Completed steps are checkpointed;
  replay skips them. Waits can suspend without compute charges for up to one
  year. `context.step()` checkpoints and retries, while `context.wait()`,
  `wait_for_condition()`, `create_callback()`, `parallel()`, and `map()` cover
  suspension, polling, external completion, and concurrency.

  ```python
  from aws_durable_execution_sdk_python import durable_execution, durable_step

  @durable_step
  def work(step_context, value):
      return {"value": value}

  @durable_execution
  def lambda_handler(event, context):
      return context.step(work(event["value"]))
  ```

- **Lambda durable retries, callbacks, and invocation.** Step exceptions use
  the step retry strategy; an unhandled exception outside a step terminates
  the execution. `context.logger` suppresses replay duplicates. Complete a
  `callback_id` with `SendDurableExecutionCallbackSuccess` or
  `SendDurableExecutionCallbackFailure`. Reusing a durable execution name
  returns its existing result instead of starting a duplicate.
- **Lambda durable events and local tests.** Status changes go to the default
  EventBridge bus with source `aws.lambda` and detail type
  `Durable Execution Status Change`. The testing SDK supports credential-free
  pytest tests; SAM supports broader integration tests.

### Durable encryption (`2026-07`)

- **Lambda Durable Functions KMS keys.** Durable Config accepts a
  customer-managed KMS key to encrypt all durable-execution data.

## S3 Vectors and vector search (`service-client-launches`)

### Resources and indexes

- **S3 Vectors resources and indexes.** Create vector buckets and indexes as
  separate resources. Indexes use `float32`; their dimensions must match the
  embedding source, and distance is cosine or Euclidean.

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

### Metadata, queries, and deployment

- **S3 Vectors metadata, queries, and deployment.** Each vector accepts up to
  50 metadata keys; up to 10 can be non-filterable. Filters use only
  filterable metadata, while responses can return metadata and distance and
  contain up to 100 results. Indexes inherit bucket encryption unless assigned
  an index KMS key. Buckets and indexes support tags, CloudFormation, and
  PrivateLink; Bedrock Knowledge Bases and OpenSearch can use them as stores.

  ```sh
  aws s3vectors query-vectors \
    --index-arn "$INDEX_ARN" \
    --query-vector "{\"float32\": $VECTOR}" \
    --top-k 100 \
    --return-metadata \
    --return-distance
  ```

## Other storage behavior

- **S3 lifecycle transition timing (`2026-07-2`).** The former 30-day minimum
  before transitioning to Standard-IA or OneZone-IA is removed; lifecycle
  configurations need not preserve it.
- **DynamoDB vector indexes (`2026-07-2`).** Vector indexes perform
  approximate-nearest-neighbor similarity search over embeddings stored in
  table items.
- **ECR replication-rule limit (`2026-08`).** `PutReplicationConfiguration`
  accepts up to 25 replication rules rather than 10.
- **Read-only S3 backup access points (`2026-08`).** AWS Backup and S3 support
  read-only access points for S3 recovery points, allowing S3 API access to
  backup data without restoration.

## AgentCore fundamentals (`service-client-launches`)

### Runtime SDK and deployment

- **AgentCore Runtime SDK and deployment CLI.** Expose any agent framework
  through `BedrockAgentCoreApp`. The decorated entry point defines the payload
  contract shared by local and cloud invocation. The starter toolkit creates
  an execution role and ECR repository, builds locally or remotely, and
  reports endpoint status.

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

### Memory

- **AgentCore short- and long-term memory.** `MemoryClient.create_event()`
  stores `USER`, `ASSISTANT`, and `TOOL` messages by memory, actor, and session;
  `list_events()` gets recent short-term context. Long-term preference,
  summary, or semantic-fact strategies use namespaces such as
  `/facts/{actorId}` and `retrieve_memories()` for semantic retrieval.
  Strategies added later affect only subsequently created events.

### Identity and Gateway

- **AgentCore identity and gateway compatibility.** `IdentityClient` creates
  workload identities and OAuth 2.0 or API-key credential providers.
  `@requires_access_token` provides provider-scoped vaulted tokens. Gateway
  exposes Smithy AWS services, Lambda functions, and OpenAPI APIs through MCP,
  with separate inbound and outbound authentication.

### Deployment and observability

- **AgentCore deployment and observability.** Every AgentCore service supports
  VPC connectivity, PrivateLink, CloudFormation, and tags. Starter-toolkit
  configuration enables observability, but trace delivery also requires
  CloudWatch Transaction Search and execution-role permissions. Telemetry is
  OpenTelemetry-compatible.

## AgentCore API evolution

### Gateway and authentication

- **AgentCore authorizer scope mapping (`2026-07`).** Gateway inbound
  authorizers can map allowed scopes to a separate advertised-scope set.
- **AgentCore endpoint validation and model parameters (`2026-07-2`).** Control
  validates service-emitted harness ARNs containing `harness-endpoint` instead
  of `endpoint`; provider model configuration accepts `additionalParams` for
  passthrough values.
- **AgentCore Gateway schema pinning and streamed metadata (`2026-07-2`).**
  Targets can pin a connector version to stabilize tool schemas. Web-search
  connector 1.2.0 adds agent-side domain and publication-date filters plus
  administrator allowlists. InvokeHarness deltas expose `toolResultMetadata`
  so metadata need not be embedded in large SSE frames.
- **AgentCore private-key JWT authentication (`2026-07-2`).** Identity OAuth
  2.0 providers support private-key JWT client authentication, signing client
  assertions with a customer-managed KMS asymmetric key.
- **AgentCore gateway limits and EC2 runtimes (`2026-08`).** Gateways can limit
  requests, tokens, and active connections. Capacity providers can run
  runtimes on customer EC2 instances and allow deletion of an active provider
  session.
- **AgentCore Memory connector access controls (`2026-08`).** Memory supports
  fine-grained access control through managed Gateway HTTP connectors.

### Storage and memory integration

- **AgentCore bring-your-own storage (`2026-07-2`).** Browser and Code
  Interpreter can mount S3 files and EFS file systems through access points.
- **Agentic retrieval memory (`2026-08`).** Bedrock `AgenticRetrieveStream`
  accepts `memoryConfiguration` to resume from AgentCore short-term memory and
  retrieve relevant long-term memory.

### Evaluators and payments

- **AgentCore OpenResponses evaluators (`2026-07-2`).** `CreateEvaluator` and
  `UpdateEvaluator` accept OpenResponses model configuration for custom
  LLM-as-a-Judge evaluators.
- **AgentCore third-party evaluators (`2026-08`).** Control supports
  third-party evaluators as managed services and as custom-evaluator
  templates.
- **AgentCore recommendation evaluator input (`2026-08`).** Recommendation
  requests can include an online-evaluation ARN.
- **AgentCore payment options (`2026-08`).** Payments supports
  customer-managed keys, Marketplace subscriptions, QuickCreate, Machine
  Payments Protocol resources, and the `upto` scheme for x402 payments.

## Bedrock

- **Bedrock mid-conversation tool changes (`2026-07-2`).** `Converse` and
  `ConverseStream` can change the available tools during a conversation.
- **Bedrock ingested-document ACL inspection (`2026-08`).** Knowledge Bases
  adds `CheckIngestedDocumentAcl` and `GetIngestedDocumentAcl` to test a user's
  document access and retrieve allow and deny entries.

## SageMaker and feature data

- **Feature Store batch and list operations (`2026-06`).** SageMaker Feature
  Store runtime adds `ListRecords` and `BatchWriteRecord`.
- **SageMaker instance-type support (`2026-07-2`).** HyperPod supports g4d,
  c6g, c7g, c8g, c6a, m6a, m6g, m7g, and m8g; inference endpoints support g7.
  Studio JupyterLab and CodeEditor accept g7 in `us-east-1`, `us-west-2`, and
  `us-east-2`.
- **SageMaker inference-optimization adapters (`2026-07-2`).** Inference
  optimization supports LoRA adapters and training plans:
  `CreateAIRecommendationJob` accepts `AdapterSource`, while
  `CreateOptimizationJob` accepts `TrainingPlanArns`, `ml.g7e`, and
  `ml.p6-b200`.
- **SageMaker g7 and training controls (`2026-08`).** Model customization adds
  `SequenceLength`; training and processing support g7. HyperPod accepts
  `g7.2xlarge`, `g7.4xlarge`, `g7.8xlarge`, `g7.12xlarge`, `g7.24xlarge`, and
  `g7.48xlarge`.
- **SageMaker prefix-aware routing (`2026-08`).** Endpoint configurations
  accept `PREFIX_AWARE` and `PrefixAwareRoutingConfig` with `PrefixLength` and
  `ConcurrencyThreshold`. Runtime requests pass `PrefixAwareId` to
  `InvokeEndpoint` or `InvokeEndpointWithResponseStream`.
- **SageMaker notebook maintenance states (`2026-08`).** Notebook Instances
  expose maintenance lifecycle statuses.

## Amplify

- **Longer Amplify OAuth tokens (`2026-08`).** `CreateApp` and `UpdateApp`
  accept longer `oauthToken` strings for third-party Git providers.
