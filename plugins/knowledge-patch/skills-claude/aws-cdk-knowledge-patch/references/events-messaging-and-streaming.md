# Events, Messaging, and Streaming

Topic-organized compatibility guidance for AWS CDK.

## Event Sources and Streaming

### Kafka event-source failure destinations (`2025-11`)

Lambda Kafka event-source mappings support an on-failure destination.

### Kafka event-source observability (`2026-02`)

Lambda Kafka event-source mappings support observability configuration.

### Kafka schema registries for Lambda (`2025-06`)

Lambda Kafka event-source constructs support schema-registry configuration.

### Timestamp starts for Kafka event sources (`2025-03`)

Lambda Kafka event sources support a starting-position timestamp.

## EventBridge and Scheduler

### API destination policy ARN (`2025-07`)

EventBridge API destinations expose an `arnForPolicy` attribute.

### EventBridge HTTP integration defaults (`2026-05`)

`HttpEventBridgeIntegration` automatically includes `EventBusName` in its default parameter mapping.

### EventBridge logging and archive encryption (`2025-09`)

Event buses support logging configuration, and `Archive` can use customer-managed keys.

### EventBridge PutEvents HTTP API integration (`2026-01`)

API Gateway v2 integrations can invoke EventBridge `PutEvents`.

### EventBridge rule roles (`2025-04`)

EventBridge `Rule` constructs support an explicitly configured role.

### Firehose integrations and processors (`2025-11`)

EventBridge Data Firehose targets accept Firehose's `IDeliveryStream`. Delivery streams also provide built-in processors for decompressing CloudWatch Logs data and extracting messages.

### HTTP APIs as EventBridge targets (`2025-04`)

EventBridge target constructs support API Gateway v2 `HttpApi`.

### Message groups on standard SQS targets (`2025-12`)

EventBridge SQS targets support `messageGroupId` for standard queues as well as FIFO queues.

### SNS EventBridge targets with IAM roles (`2025-05`)

The EventBridge `SnsTopic` target can opt into using an IAM role.

### Stable EventBridge Scheduler (`2025-03`)

EventBridge Scheduler and its target constructs graduated from experimental to stable. Scheduler targets also include `EcsRunTask`.

## General Guidance

### Batched IoT HTTP actions (`2026-01`)

IoT `HttpAction` supports batching messages. `enableBatchConfig` is explicitly disabled by default, so batching remains opt-in.

## Kinesis and Data Firehose

### Firehose destinations for EC2 flow logs (`2026-02`)

EC2 flow-log destinations accept Firehose `IDeliveryStreamRef` values.

### Firehose dynamic partitioning (`2026-02`)

Kinesis Data Firehose constructs support dynamic partitioning.

### Firehose HTTP destinations (`2026-08`)

Kinesis Data Firehose constructs support HTTP endpoint and Datadog destinations.

### Firehose SNS subscriptions (`2025-06`)

SNS subscription constructs support Amazon Data Firehose destinations.

### Kinesis Analytics v2 package (`2025-09`)

Using Kinesis Analytics v2 through `aws-kinesisanalytics` is deprecated; use `aws-kinesisanalyticsv2`.

### Kinesis shard-level metrics (`2025-10`)

Kinesis stream constructs expose shard-level metrics.

### Kinesis stream consumers (`2025-02`)

Kinesis constructs support stream consumers.

### SES event destinations (`2025-02`)

SES configuration sets support the default event bus and Firehose as event destinations.

### Stable Firehose constructs (`2025-02`)

Kinesis Data Firehose constructs graduated from experimental to stable.

## SNS and SQS

### API Gateway v2 SQS integrations (`2025-02`)

API Gateway v2 integration constructs support SQS.

### High-throughput FIFO topics (`2025-02`)

SNS constructs support high-throughput mode for FIFO topics.

### SQS provisioned pollers (`2026-05`)

Lambda SQS event-source mappings support `provisionedPollerConfig`, including validation and corrected typing.
