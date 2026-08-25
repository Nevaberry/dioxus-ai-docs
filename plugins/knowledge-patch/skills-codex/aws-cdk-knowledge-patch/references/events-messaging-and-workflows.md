# Events, messaging, and workflows

Use this reference for events, messaging, and workflows compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## AWS Step Functions

### Capacity-provider strategies for EcsRunTask

**Batch:** `2026-01`

Step Functions `EcsRunTask` integrations for both Fargate and EC2 support capacity-provider strategies.

### Custom CSV delimiters

**Batch:** `2025-02`

Step Functions `S3CsvItemReader` supports custom CSV delimiters.

### Distributed Map permissions

**Batch:** `2025-09`

State machines synthesize the permissions needed to run and redrive Distributed Map, including maps defined only in nested `StateGraph` objects.

### Distributed Map result-writer configuration

**Batch:** `2025-04`

Step Functions Distributed Map supports custom `WriterConfig` fields for its `ResultWriter`.

### Dynamic Distributed Map result buckets

**Batch:** `2025-05`

Step Functions `ResultWriter` accepts JSONPath or JSONata expressions for its bucket.

### Dynamic Step Functions queue ARNs

**Batch:** `2025-03`

Step Functions task integrations allow `jobQueueArn` to be supplied with either JsonPath or JSONata.

### EvaluateExpression architecture

**Batch:** `2025-11`

The Step Functions `EvaluateExpression` task supports selecting an architecture.

### Intrinsic Step Functions API endpoints

**Batch:** `2025-10`

Under its feature flag, Step Functions tasks accept an intrinsic function as `apiEndpoint`.

### JSONata Map concurrency

**Batch:** `2026-01`

Step Functions Map states accept JSONata expressions for `maxConcurrency`.

### JSONata Map item selectors

**Batch:** `2025-06`

Step Functions Map states accept JSONata expressions in `ItemSelector`.

### Node.js 22 expression evaluation

**Batch:** `2025-09`

Step Functions `EvaluateExpression` supports Node.js 22.

### Parallel-state parameters

**Batch:** `2025-05`

Step Functions `Parallel` states support parameters.

### Step Functions JSONata and variables

**Batch:** `2025-02`

Step Functions constructs support JSONata and workflow variables.

## Amazon Kinesis and Data Firehose

### Firehose destination time zones

**Batch:** `2025-07`

Kinesis Data Firehose S3 destinations support custom time-zone settings.

### Firehose destinations for EC2 flow logs

**Batch:** `2026-02`

EC2 flow-log destinations accept Firehose `IDeliveryStreamRef` values.

### Firehose dynamic partitioning

**Batch:** `2026-02`

Kinesis Data Firehose constructs support dynamic partitioning.

### Firehose HTTP destinations

**Batch:** `2026-08`

Kinesis Data Firehose constructs support HTTP endpoint and Datadog destinations.

### Firehose output integrations

**Batch:** `2025-04`

Kinesis Data Firehose supports S3 file-extension formats, and CloudWatch Logs destination constructs can target Amazon Data Firehose.

### Firehose record-format conversion

**Batch:** `2025-10`

Kinesis Data Firehose `DeliveryStream` constructs support record-format conversion for S3 bucket destinations.

### Firehose SNS subscriptions

**Batch:** `2025-06`

SNS subscription constructs support Amazon Data Firehose destinations.

### Kinesis Analytics v2 package

**Batch:** `2025-09`

Using Kinesis Analytics v2 through `aws-kinesisanalytics` is deprecated; use `aws-kinesisanalyticsv2`.

### Kinesis shard-level metrics

**Batch:** `2025-10`

Kinesis stream constructs expose shard-level metrics.

### Kinesis stream consumers

**Batch:** `2025-02`

Kinesis constructs support stream consumers.

### Lambda stream failures to S3

**Batch:** `2025-03`

Lambda event sources for Kinesis and DynamoDB streams support S3 as an on-failure destination.

### Stable Firehose constructs

**Batch:** `2025-02`

Kinesis Data Firehose constructs graduated from experimental to stable.

## Amazon EventBridge and Scheduler

### API destination policy ARN

**Batch:** `2025-07`

EventBridge API destinations expose an `arnForPolicy` attribute.

### EventBridge HTTP integration defaults

**Batch:** `2026-05`

`HttpEventBridgeIntegration` automatically includes `EventBusName` in its default parameter mapping.

### EventBridge logging and archive encryption

**Batch:** `2025-09`

Event buses support logging configuration, and `Archive` can use customer-managed keys.

### EventBridge rule roles

**Batch:** `2025-04`

EventBridge `Rule` constructs support an explicitly configured role.

### Firehose integrations and processors

**Batch:** `2025-11`

EventBridge Data Firehose targets accept Firehose's `IDeliveryStream`. Delivery streams also provide built-in processors for decompressing CloudWatch Logs data and extracting messages.

### Message groups on standard SQS targets

**Batch:** `2025-12`

EventBridge SQS targets support `messageGroupId` for standard queues as well as FIFO queues.

### SES event destinations

**Batch:** `2025-02`

SES configuration sets support the default event bus and Firehose as event destinations.

### SNS EventBridge targets with IAM roles

**Batch:** `2025-05`

The EventBridge `SnsTopic` target can opt into using an IAM role.

### Stable EventBridge Scheduler

**Batch:** `2025-03`

EventBridge Scheduler and its target constructs graduated from experimental to stable. Scheduler targets also include `EcsRunTask`.

## Cross-service event integrations

### Complete ECS task overrides

**Batch:** `2025-02`

Event target constructs expose all ECS task overrides.

## AWS AppSync

### AppSync data-source integrations

**Batch:** `2025-04`

AppSync constructs support data-source integrations.

### AppSync enhanced metrics

**Batch:** `2026-03`

AppSync GraphQL APIs support `EnhancedMetricsConfigProperty`.

### AppSync Events

**Batch:** `2025-02`

AppSync Events has L2 constructs.

## Amazon SNS, SQS, and SES

### Fluentd asynchronous connections

**Batch:** `2025-04`

`FluentdLogDriver` uses `async`, replacing the deprecated `asyncConnect` property.

### High-throughput FIFO topics

**Batch:** `2025-02`

SNS constructs support high-throughput mode for FIFO topics.

### SES configuration-set email validation

**Batch:** `2026-05`

SES configuration sets support automatic email validation.

### SES custom-tracking HTTPS policy

**Batch:** `2025-05`

SES constructs support an HTTPS policy for custom tracking domains.

### SQS provisioned pollers

**Batch:** `2026-05`

Lambda SQS event-source mappings support `provisionedPollerConfig`, including validation and corrected typing.

## Streaming and data integrations

### Batched IoT HTTP actions

**Batch:** `2026-01`

IoT `HttpAction` supports batching messages. `enableBatchConfig` is explicitly disabled by default, so batching remains opt-in.

### EMR instance-fleet priority allocation

**Batch:** `2026-05`

EMR instance fleets support priority allocation.

### Expanded EMR create-cluster options

**Batch:** `2025-09`

`EmrCreateClusterOptions` accepts `ebsRootVolumeIops`, `ebsRootVolumeThroughput`, and `managedScalingPolicy`.

### Kafka event-source failure destinations

**Batch:** `2025-11`

Lambda Kafka event-source mappings support an on-failure destination.

### Kafka event-source observability

**Batch:** `2026-02`

Lambda Kafka event-source mappings support observability configuration.

### Kafka schema registries for Lambda

**Batch:** `2025-06`

Lambda Kafka event-source constructs support schema-registry configuration.

### MSK Express brokers

**Batch:** `2025-11`

MSK constructs support Express brokers.

### Timestamp starts for Kafka event sources

**Batch:** `2025-03`

Lambda Kafka event sources support a starting-position timestamp.

### Typed Glue partition projection

**Batch:** `2026-02`

Glue constructs support typed partition-projection configuration.
