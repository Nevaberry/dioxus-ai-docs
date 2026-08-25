---
name: aws-cdk-knowledge-patch
description: AWS CDK
version: 2.262.1
license: MIT
metadata:
  author: Nevaberry
---


# AWS CDK Knowledge Patch

Load this skill when changing, reviewing, debugging, or upgrading AWS CDK applications, construct libraries, CLI integrations, or synthesized CloudFormation templates.

Prefer the project's manifests, lockfiles, source, synthesized output, and tests when they disagree with this guidance. Apply feature-flagged behavior only when the relevant flag is enabled.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compute delivery and workflows](references/compute-delivery-and-workflows.md) | Lambda, custom resources, Step Functions, CodeBuild, CodePipeline, assets, Auto Scaling, Batch, and EC2 |
| [Containers and Kubernetes](references/containers-and-kubernetes.md) | ECS, EKS, ECR, MSK, deployment strategies, add-ons, and platform versions |
| [Core toolkit and validation](references/core-toolkit-and-validation.md) | CLI, bootstrap, import, synthesis, context, feature flags, validation, errors, and Mixins |
| [Events, messaging, and streaming](references/events-messaging-and-streaming.md) | EventBridge, Scheduler, Kinesis, Data Firehose, SNS, SQS, and Kafka event sources |
| [Generated contracts and types](references/generated-contracts-and-types.md) | L1 schema changes, generated imports and guards, reference interfaces, and grants |
| [Identity, security, and AI](references/identity-security-and-ai.md) | Cognito, IAM, KMS, Secrets Manager, certificates, Bedrock, and AgentCore |
| [Networking, APIs, and edge](references/networking-apis-and-edge.md) | API Gateway, AppSync, CloudFront, Elastic Load Balancing, Route 53, VPC, and Cloud WAN |
| [Observability and service integrations](references/observability-and-service-integrations.md) | CloudWatch, Logs, Synthetics, AppConfig, SES, EMR, Glue, and media services |
| [Storage and databases](references/storage-and-databases.md) | S3, S3 Tables, RDS, Aurora, DynamoDB, OpenSearch, DocumentDB, EFS, and ElastiCache |

## First-pass compatibility audit

Before editing an established application:

1. Read the package-manager manifest and lockfile to identify the exact `aws-cdk-lib`, constructs, CLI, and alpha-module versions.
2. Inspect `cdk.json`, context files, environment variables, and feature flags; many defaults are intentionally flag-gated.
3. Search for generated L1 properties or attributes that became required, immutable, optional, renamed, or removed.
4. Check custom implementations of public interfaces for newly required reference getters or narrower return types.
5. Review Lambda, custom-resource, EKS, Batch, and CloudFront runtime defaults before accepting a synthesized diff.
6. Synthesize and inspect replacement-sensitive resources, IAM policies, runtime choices, validation reports, and asset commands.
7. Run the application's tests and any snapshot assertions against the actual synthesized assembly.

## Breaking contracts and reversals

### Treat validation failures as typed errors

Many construct libraries and the CLI now throw `ValidationError` rather than untyped errors. Catch typed errors and use error codes where available; do not classify failures by message text.

### Audit generated L1 surfaces during upgrades

CloudFormation schema refreshes can remove attributes and nested types, make properties required or immutable, or change replacement behavior. Compile all languages and inspect the synthesized template rather than assuming a former generated member still exists.

Generated L1s also expose import factories, resource interfaces, construct-valued relationship parameters, and static `isCfn<ResourceName>` guards. Prefer these public contracts to hand-built casts.

### Account for narrower reference interfaces

Several APIs now return `I<Resource>Ref` values instead of richer L2 interfaces. Type-test or cast only when code genuinely needs L2-only members.

`IEncryptedResource` is environment-aware but is not necessarily an `IResource`. Use an intersection type or `Resource.isResource()` when both contracts are required.

### Use current reversal outcomes

- CloudWatch Logs metric-filter metrics do not retain the filter dimension map.
- Batch `useOptimalInstanceClasses` remains supported despite its earlier deprecation.
- Isolated kubectl subnets produce an EKS warning, not an error.
- Native ECS blue/green L2 support is present; do not infer absence from the short-lived revert.

### Recheck replacement-sensitive L1 properties

Immutable properties on resources such as EC2 Fleets, CloudFront Functions, OpenSearch Serverless collections, SageMaker clusters, Lex policies, and AppStream image builders can force replacement. Treat synthesized replacement changes as deployment decisions, not formatting noise.

## Runtime and platform defaults

### Lambda and custom resources

Framework functions, custom resources, and `Runtime.NODEJS_LATEST` now select Node.js 24.x. Callback-style asynchronous handlers are unsupported there; convert them to `async`, pin Node.js 22.x, or disable latest-runtime selection for `NodejsFunction`.

The runtime catalogs also contain newer Ruby, Java, Python, and Node.js entries. Confirm regional availability and test native dependencies before changing a runtime.

### EKS and container platforms

Experimental EKS clusters require an explicit `kubectlLayer` matching the Kubernetes version. Stable EKS v2 constructs, newer Kubernetes versions, Hybrid Nodes, managed node repair, native OIDC providers, access-entry types, and provisioned control planes are available.

Feature flags can switch EKS and Batch defaults to Amazon Linux 2023. Review AMI changes and bootstrap assumptions before rollout.

### CloudFront Functions and Synthetics

CloudFront Functions can default to JavaScript 2.0 under its feature flag. Synthetics supports newer Node.js, Playwright, Puppeteer, Python Selenium, browser-selection, retry, group, and safe-update capabilities; choose an explicit runtime when reproducibility matters.

## Validation and synthesis

### Built-in template validation

CDK validates templates with a comprehensive default rule set. For a single invocation, set `CDK_VALIDATION=false` only when bypassing built-in validation is deliberate:

```sh
CDK_VALIDATION=false cdk synth
```

Do not treat this switch as a substitute for fixing application or policy-validation findings.

### Validation plugins and reports

Use `Validations` to add plugins and emit warnings or errors. The stable policy-validation interfaces omit the older beta suffix.

Validation reports are always written to the cloud assembly, include construct annotations and suppressed violations, use the newer schema, and may include plugin-created files. Consumers must not assume every reported violation failed synthesis.

`failSynthOnValidationErrors` can suppress validation-error console output and the failing exit code. Keep CI behavior explicit when adopting it.

### Diagnostics and source traces

Deferred `Box` values preserve source traces. L1 property mutations and external `ConstructError` traces can flow into cloud-assembly metadata, making post-construction changes easier to locate.

### Weak references and cross-region outputs

Choose reference strength deliberately. Weak cross-stack references work within and across environments, including list-valued attributes, while `Fn::GetStackOutput` supports cross-region output references.

## CLI, bootstrap, and plugin boundaries

Use `cdk bootstrap --untrust` to retract bootstrap trust.

CLI plugins must target the public plugin contract and must not import internal CLI libraries. Credential plugins may return a null expiration and may initially return empty credentials.

Simplified CloudFormation resource import reduces manual import setup. Keep logical-ID and ownership changes under review when bringing existing resources into a stack.

`CDK_TOOLKIT_VERSION` is a supported cloud-assembly environment contract. Pipelines can also pin the `cdk-assets` version.

## Workflow quick reference

### Step Functions

JSONata and workflow variables are supported across additional task and state properties, including Map selectors and concurrency, dynamic queue ARNs and result buckets, intrinsic API endpoints, and REST API paths.

Distributed Map supports custom writer configuration and synthesizes run and redrive permissions, including for maps nested only in a `StateGraph`.

### CodePipeline and CodeBuild

Pipelines support command, invoke-pipeline, EC2 deployment, ECR publish, Inspector scan, trigger-filter, stage-condition, and manual-approval capabilities. Pipeline projects propagate fleet and certificate settings.

CodeBuild supports attribute-based fleets, custom fleet instances and VPCs, shared caches, remote Docker servers, newer Windows and macOS images, and configurable build compute types.

### Assets and packaging

Asset bundling honors `platform`; Docker build options accept network and context controls; tarball assets handle newer Docker output and honor `CDK_DOCKER`; and current Bun lockfiles are recognized without forcing frozen-lockfile behavior.

## Service quick reference

### Containers

ECS includes enhanced Container Insights, fault injection, availability-zone rebalancing controls, Service Connect TLS and access logs, managed-storage encryption, managed-instances capacity providers, deployment strategies, and existing Cloud Map namespaces.

Check the current availability-zone rebalancing default for raw `AWS::ECS::Service` resources, and review security-group behavior when using ECS patterns.

### Networking and APIs

API Gateway supports dual-stack APIs and domains, private-API policies, response streaming, WebSocket usage plans, stage variables, access logs, TLS 1.3, Lambda-authorizer roles, and additional integrations.

CloudFront supports gRPC, VPC origins, versioned reads, origin-group criteria, HTTP-origin controls, Lambda Function URL addressing, host-header-only origin policy, and stronger certificate diagnostics.

Elastic Load Balancing supports minimum capacity, NLB subnet mappings, mTLS CA-name advertisement, Lambda multi-value headers, health attributes, ALB JWT verification, and feature-flagged NLB security groups.

### Storage and databases

RDS and Aurora include lookup, proxy endpoints, maintenance-window modification, backup retention, replication sources, lifecycle controls, Database Insights, Serverless v2 auto-pause, native Secrets Manager credentials, and expanded engine catalogs.

S3 includes replication filters and custom roles, public-access defaults, deployment token fixes, blocked encryption types, attribute-based access control, naming prefixes and namespaces, and auto-delete Mixins. S3 Tables includes table, namespace, and KMS-encryption support.

DynamoDB includes the point-in-time recovery specification, MRSC and cross-account global-table replication, compound GSI keys, stream resource policies, index-aware grant policies, and stricter grantee validation.

### Events and observability

EventBridge, Scheduler, Kinesis, Data Firehose, SNS, SQS, and Lambda event sources expose additional destinations, processors, failure handling, dynamic partitioning, format conversion, HTTP delivery, stream consumers, and observability controls.

CloudWatch adds newer alarm, dashboard, metric, query, transformer, field-index, deletion-protection, PromQL, cross-account, and composite-rule capabilities. Verify AgentCore metric dimensions before reusing existing alarms or dashboards.

### Identity and AI services

Cognito supports managed login, analytics, choice-based authentication, passkeys, refresh-token rotation, identity pools, and newer pre-token trigger events.

Bedrock and AgentCore include newer foundation-model identifiers, inference profiles, customization workflows, runtimes, tools, memory, gateways, interface endpoints, authorizers, IAM credential targets, and stream delivery resources.

Use the detailed references for exact property names, defaults, version catalogs, feature-flag conditions, and generated schema changes.
