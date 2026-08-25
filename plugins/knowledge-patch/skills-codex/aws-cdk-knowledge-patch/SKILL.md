---
name: aws-cdk-knowledge-patch
description: AWS CDK
version: 2.262.1
license: MIT
metadata:
  author: Nevaberry
---


# AWS CDK Knowledge Patch

Use this skill when writing, reviewing, upgrading, or debugging AWS CDK applications and construct libraries. Consult the topic references before assuming a generated L1 shape, default runtime, validation behavior, feature-flag effect, or recently added L2 capability.

## How to use this patch

1. Identify the affected construct, service, and language binding.
2. Check the breaking changes and deprecations below first.
3. Open the matching topic reference for complete compatibility details.
4. Prefer the project manifest, lockfile, synthesized template, and tests when they conflict with generic guidance.
5. For generated L1 properties, compare the installed library's type declarations with the current CloudFormation contract before editing code.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compute, containers, and runtimes](references/compute-containers-and-runtime.md) | EC2, Auto Scaling, Batch, ECS, EKS, Lambda, runtimes, and capacity providers |
| [Core, CLI, synthesis, and validation](references/core-cli-and-synthesis.md) | CLI, bootstrap, context, custom resources, synthesis, validation, errors, Mixins, and references |
| [Delivery, assets, and pipelines](references/delivery-assets-and-pipelines.md) | CodeBuild, CodePipeline, CDK Pipelines, Docker, bundling, staging, and deployments |
| [Events, messaging, and workflows](references/events-messaging-and-workflows.md) | EventBridge, Firehose, Kinesis, SNS, SQS, SES, Step Functions, AppSync, Kafka, and data integrations |
| [Generated L1 and CloudFormation contracts](references/generated-l1-contracts.md) | Required and removed properties, immutable fields, attributes, reference interfaces, import factories, and type guards |
| [Identity, security, and AI services](references/identity-security-and-ai.md) | IAM, KMS, Cognito, Secrets Manager, Bedrock, AgentCore, certificates, and inference |
| [Networking, edge, APIs, and DNS](references/networking-edge-and-dns.md) | API Gateway, CloudFront, Elastic Load Balancing, Route 53, VPCs, endpoints, and Cloud Map |
| [Observability, operations, and configuration](references/observability-operations-and-config.md) | CloudWatch, CloudWatch Logs, Synthetics, AppConfig, Backup, and operational defaults |
| [Storage, databases, and search](references/storage-and-databases.md) | S3, EFS, DynamoDB, RDS, Aurora, DocumentDB, OpenSearch, and other data stores |

## Breaking changes and migration traps

### Treat validation failures as typed errors

Many construct families and the CLI now throw `ValidationError` rather than untyped errors. CDK errors and annotations can also carry error codes. Catch or classify by type and code; do not parse message text.

Built-in template validation uses a comprehensive default rule set. Disable it for one invocation only when necessary:

```sh
CDK_VALIDATION=false cdk synth
```

Validation reports are always written to the cloud assembly, include construct annotations, and use the newer self-contained schema. Report consumers must handle suppressed violations. The `failSynthOnValidationErrors` context key can suppress validation console output and the failing exit code.

### Recheck generated L1 contracts after upgrades

Generated bindings have accumulated required-property additions, removed attributes and types, immutable fields, and replacement-only updates. Do not rely on an older L1 signature. Inspect [Generated L1 and CloudFormation contracts](references/generated-l1-contracts.md) whenever a compilation error, unexpected replacement, or missing attribute appears after upgrading.

Every generated L1 supplies `from<Resource>Arn`, `from<Resource><Prop>`, and `isCfn<ResourceName>` helpers. Prefer these supported factories and guards over hand-built casts.

Some exposed values now use narrow reference interfaces such as `IComputeEnvironmentRef`, `IBackupVaultRef`, `IEventBusRef`, and `ILogGroupRef`. Type-test or cast only when richer L2 members are actually required.

### Update Lambda and custom-resource runtimes deliberately

Framework functions, custom resources, and `Runtime.NODEJS_LATEST` now resolve to Node.js 24 in every region. Node.js 24 rejects callback-style asynchronous handlers; convert them to `async`, pin `Runtime.NODEJS_22_X`, or set `useLatestRuntimeVersion: false` on `NodejsFunction`.

Python 3.8 is deprecated. Current catalogs also include Ruby 4.0, Node.js 24.x, Java 25, Python 3.14, and Java 8/11/17 variants on Amazon Linux 2023. Verify runtime availability and bundling behavior in the target region.

### Do not assume old ECS defaults

`AWS::ECS::Service.AvailabilityZoneRebalancing` defaults to `DISABLED`. Set it explicitly when the intended behavior is enabled rebalancing.

`ManagedInstancesCapacityProvider` creates its instance profile, requires at least one security group, and accepts `capacityOptionType` for Spot. The deprecated `canContainersAccessInstanceRole` property should not be used.

Native ECS blue/green deployment support exists at L1 and L2, and built-in linear and canary configurations are available. Prefer those constructs over reconstructing the deployment contract manually.

### Supply EKS dependencies and choose defaults explicitly

The older experimental `Cluster` and `FargateCluster` APIs require a `kubectlLayer` matching the Kubernetes version. EKS v2 constructs are stable, support native OIDC providers, removal policies, service-account overwrite control, deletion protection, provisioned control planes, and newer access-entry types.

Feature-flagged defaults can select Amazon Linux 2023 for EKS nodes. Isolated kubectl subnets produce a warning. Keep cluster, AMI, kubectl layer, and load-balancer-controller versions compatible.

### Preserve explicit S3 deployment behavior

`Source.jsonData()` no longer escapes JSON automatically. Request the earlier behavior when needed:

```ts
Source.jsonData("config.json", data, { escape: true })
```

List-contained tokens are resolved, and `Source.data()` accepts an empty string. Asset bundling honors its configured platform, Docker builds accept network and context controls, and `TarballImageAsset` supports newer Docker tarball output.

### Account for reversals, not just introductions

CloudWatch Logs metric-filter metrics do not retain the filter dimension map; the short-lived retention behavior was reverted. Batch `useOptimalInstanceClasses` remains supported after its earlier deprecation was reversed. EKS isolated-subnet validation is a warning rather than the earlier error.

## High-value core and CLI capabilities

### Bootstrap, plugins, and imports

- Use `cdk bootstrap --untrust` to retract bootstrap trust.
- Build CLI plugins against the public contract; imports from internal CLI libraries are unsupported.
- Credential plugins may return `null` expiration values and initially empty credentials.
- Use simplified resource import to bring existing resources under stack management with less setup.
- Treat `CDK_TOOLKIT_VERSION` as a supported cloud-assembly environment variable.

### Synthesis and construct composition

- Use `RemovalPolicies.of(scope)` to apply removal policies from a scope-oriented entry point.
- Use additional context cache keys when otherwise identical lookups need distinct cached results.
- Use `IEnvironmentAware` to retrieve a construct's environment.
- Prefer weak cross-stack references when reference strength is unspecified; they support cross-environment use and list-valued attributes.
- Use `Fn::GetStackOutput` for cross-region stack outputs.
- Use `Box` for deferred values when accurate source traces matter.
- Use property injectors across L2 constructors and `PropertyMergeStrategy` for object or array merge behavior.

### Mixins and validation plugins

Mixins are the stable extension mechanism exposed by `@aws-cdk/cfn-property-mixins`, with Aspect conversion helpers and S3/ECS service mixins in `aws-cdk-lib`. ECR and S3 provide auto-delete mixins.

Add app validation plugins through `Validations`; use `addWarning`, `addError`, and `acknowledge`. Policy-validation APIs use `policyValidation`, and validation plugins receive scope context and may write files into the cloud assembly.

## High-value service capabilities

### Workflows and event delivery

- Step Functions supports JSONata, workflow variables, JSONata `ItemSelector` and `maxConcurrency`, dynamic queue ARNs and result buckets, Parallel parameters, and custom Distributed Map writer configuration.
- State machines synthesize permissions for running and redriving Distributed Map, including maps nested in a `StateGraph`.
- EventBridge supports explicit rule roles, event-bus logging, archive encryption, HTTP API integrations, and targets for HTTP APIs, SNS, SQS, and Data Firehose.
- Data Firehose is stable and supports dynamic partitioning, record-format conversion, HTTP and Datadog destinations, processors, time zones, and EC2 flow-log destinations.
- Lambda Kafka event sources support timestamps, schema registries, failure destinations, and observability configuration.

### Networking and edge

- CloudFront supports gRPC, VPC origins, origin-group selection criteria, versioned reads, IP-address controls, response-completion timeouts, and the `Managed-HostHeaderOnly` origin request policy.
- API Gateway supports dual-stack REST, HTTP, WebSocket, and domain configurations; TLS 1.3 domain policies; response streaming; WebSocket usage plans and API keys; and explicit Lambda-authorizer roles.
- Elastic Load Balancing supports minimum capacity reservations, NLB subnet mappings, mTLS CA-name advertisement, target-group health attributes, multi-value Lambda headers, and ALB JWT verification.
- Route 53 supports SVCB, HTTPS, failover records, accelerated recovery, and restricted delegation grants. Supplying TTL with an alias target produces a warning.
- Gateway VPC endpoints accept `ipAddressType` and `dnsRecordIpType`; ECS clusters can attach existing Cloud Map namespaces.

### Data services

- DynamoDB `TableV2` supports MRSC and cross-account global-table replication. Resource policies cover streams, and grants include index ARNs added after the original grant.
- RDS supports deferred modifications, Database Insights, engine lifecycle settings, snapshot restores, standalone parameter groups, proxy authentication schemes, and service-native Secrets Manager credentials.
- Aurora supports instance Availability Zones, Serverless v2 auto-pause, Limitless PostgreSQL, and current engine catalogs.
- S3 supports replication filters and custom roles, attribute-based access control, blocked encryption types, bucket-name prefixes and namespaces, and S3 Tables L2 constructs with KMS encryption.
- OpenSearch supports node options, S3 Vectors, gp3 throughput up to 2000 MiB/s, and local-storage node families that do not require EBS.

### Observability and operations

- CloudWatch Logs supports field indexes, transformers, multiple `stats` commands, transformed-log metric filters, Infrequent Access in ADC regions, and deletion protection.
- Dashboard widgets support search expressions, query languages, pie-chart labels, cross-account visibility, metric IDs, and visibility controls.
- CloudWatch supports anomaly-detection alarms, PromQL alarms, composite `AT_LEAST` expressions, and mute rules.
- Synthetics supports safe updates, retries, tags, canary groups, browser selection, root-level scripts for newer Puppeteer runtimes, and current Node.js, Python, and Playwright runtimes.
- AppConfig supports environment and configuration-profile deletion protection, deployment-tick extensions, and KMS-encrypted hosted configurations.

## Review checklist

- Confirm the installed `aws-cdk-lib` and construct package versions before applying compatibility advice.
- Inspect generated types for required, removed, and immutable L1 fields.
- Synthesize and diff changes that touch defaults, update policies, replacement-only properties, IAM, or encryption.
- Check feature flags explicitly; several behaviors are flag-controlled or changed defaults.
- Verify runtime, region, architecture, and image availability for deployment targets.
- Treat tokens as unresolved during validation unless the referenced guidance says token values are accepted.
- Prefer typed errors, error codes, and validation reports over message parsing.
- Open the full topic reference when an item involves more than one service.
