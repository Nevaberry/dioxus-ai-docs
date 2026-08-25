# Compute Delivery and Workflows

Topic-organized compatibility guidance for AWS CDK.

## Auto Scaling, Batch, and EC2

### Auto Scaling availability-zone distribution (`2025-01`)

`AutoScalingGroup` accepts `availabilityZoneDistribution` to control capacity distribution across Availability Zones.

### Auto Scaling instance-refresh policies (`2026-08`)

Auto Scaling supports the `AutoScalingInstanceRefresh` CloudFormation update policy.

### Auto Scaling lifecycle controls (`2026-03`)

`AutoScalingGroup` accepts `deletionProtection` and `instanceLifecyclePolicy`.

### Batch AL2023 images and default (`2026-04`)

Batch adds Amazon Linux 2023 image types and, under its feature flag, defaults to AL2023.

### Batch instance-class selection (`2025-10, 2026-01`)

EC2 managed compute environments support default instance classes. `useOptimalInstanceClasses` remains supported; its 2025-10 deprecation was reversed in 2026-01.

### Batch job-definition updates (`2026-04`)

Batch skips unregistering a job definition during an update.

### EC2 C8A instances (`2026-05`)

The EC2 instance-type catalog includes C8A.

### EC2 C8GN instances (`2025-07`)

The EC2 instance-class catalog includes C8GN.

### EC2 Fleet replacement constraints (`2025-12`)

`AWS::EC2::EC2Fleet` now treats `DefaultTargetCapacityType` and `TargetCapacityUnitType` as immutable, so changing either property replaces the fleet rather than updating it in place.

### EC2 instance metadata options (`2025-12`)

EC2 instance constructs expose their `MetadataOptions` configuration for callers that need to inspect the instance metadata settings.

### Launch-template EBS controls (`2026-08`)

Launch-template EBS properties support volume initialization rate, and CDK accepts gp3 and io2 volume sizes up to 64 TiB.

### Managed Instances capacity-provider changes (`2026-01`)

`ManagedInstancesCapacityProvider` now creates its EC2 instance profile automatically, requires at least one `securityGroups` entry, and accepts `capacityOptionType` for Spot capacity.

### Multiple Auto Scaling health checks (`2025-03`)

The new `HealthChecks` API supports multiple health-check types, including EBS and `VPC_LATTICE`.

## CodeBuild, Assets, and Packaging

### Asset-bundling platform selection (`2025-05`)

Core asset bundling now honors the configured `platform` instead of ignoring it.

### Attribute-based CodeBuild fleets (`2025-02`)

CodeBuild Fleet constructs support attribute-based compute types.

### Bundling aws-cdk-lib (`2026-04`)

Packages can use `aws-cdk-lib` as a `bundledDependency`; the previous packaging failure was fixed.

### CodeBuild fleet configuration (`2025-10`)

CodeBuild Fleets support custom instance types, VPC configuration, and overflow behavior.

### CodeBuild macOS 15 runners (`2025-12`)

CodeBuild constructs support macOS 15 runners.

### CodeBuild macOS 26 runners (`2026-03`)

CodeBuild constructs support macOS 26 runners.

### Custom bootstrap qualifiers in staging roles (`2025-08`)

The app-staging synthesizer propagates a custom bootstrap qualifier into the deployment-role name.

### Docker 27.4 tarball assets (`2025-04`)

`TarballImageAsset` supports the output format produced by Docker 27.4 and later.

### Docker build controls (`2025-09`)

`DockerBuildOptions` accepts a network parameter, and `TarballImageAsset` honors `CDK_DOCKER`.

### Go app-staging synthesizer (`2025-05`)

The experimental `app-staging-synthesizer-alpha` package is now published for Go.

### New Bun lockfile support (`2025-09`)

CDK recognizes the newer Bun lockfile format.

### Shared CodeBuild caches (`2025-07`)

CodeBuild project constructs support cache sharing.

### Windows Server Core 2022 build images (`2025-08`)

CodeBuild supports Windows Server Core 2022 images with on-demand capacity.

## CodePipeline and CDK Pipelines

### CodePipeline commands action (`2025-02`)

CodePipeline actions can run commands directly through a commands action.

### CodePipeline Git-push filters (`2025-03`)

CodePipeline L2 Git-push filters support branch and file criteria.

### CodePipeline stage conditions (`2025-03`)

CodePipeline L2 constructs support stage-level conditions.

### CodePipeline V2 in pipelines (`2025-04`)

The pipelines L3 construct supports the `V2` pipeline type.

### Combined CodePipeline trigger filters (`2025-05`)

CodePipeline configurations can use both `pullRequestFilter` and `pushFilter`.

### Configurable cdk-assets version (`2025-07`)

CDK Pipelines can configure the `cdk-assets` version.

### EC2 deployment actions (`2025-06`)

CodePipeline action constructs support native Amazon EC2 deployments.

### Narrower pipeline-role trust (`2025-03`)

Under `@aws-cdk/pipelines:reduceStageRoleTrustScope`, the trust policy uses the current pipeline role instead of the account root principal.

### Pipeline CodeBuild configuration propagation (`2025-12`)

CDK Pipelines now propagates CodeBuild `fleet` and `certificate` settings instead of dropping them from the generated projects.

### Pipeline invoke actions (`2025-04`)

CodePipeline action constructs support invoking a pipeline.

### Pipeline manual-approval metadata (`2025-06`)

CDK Pipelines manual approvals can include a review URL and an SNS notification topic.

### Pipeline service roles for actions (`2025-04`)

CodePipeline L2 adds `usePipelineRoleForActions`, and pipelines actions can default to the pipeline service role instead of creating a separate role.

### Remote Docker servers (`2025-09`)

CodeBuild supports remote Docker servers, and pipelines' `CodeBuildFactory` can use Docker-server support.

## Lambda and Custom Resources

### ADOT Lambda layers (`2025-02`)

The Lambda ADOT layer catalog includes version 0.115.0.

### Async custom-resource logging default (`2025-07`)

Logging in the asynchronous custom-resource provider framework defaults to off.

### AwsCustomResource external IDs (`2025-11`)

`AwsCustomResource` supports an external ID.

### Bun lockfile behavior (`2025-03`)

Lambda Node.js bundling no longer requires a frozen lockfile when Bun is used.

### Consolidated Lambda integration permissions (`2025-11`)

REST and HTTP API Lambda integrations can opt to consolidate their Lambda permissions.

### Custom-resource service timeout (`2025-01`)

Custom resources accept a `serviceTimeout` property, allowing the service-side operation timeout to be configured independently.

### Deprecated Lambda policy feature flag (`2025-04`)

The default `@aws-cdk/aws-lambda:createNewPoliciesWithAddToRolePolicy` feature flag is deprecated.

### Deprecated Lambda runtime (`2025-01`)

The Lambda Python 3.8 runtime is marked deprecated.

### EvaluateExpression architecture (`2025-11`)

The Step Functions `EvaluateExpression` task supports selecting an architecture.

### Infinite Lambda event-source retries (`2025-04`)

Lambda `EventSourceMapping` accepts `retryAttempts: -1` to request infinite retries.

### Lambda capacity providers (`2025-12`)

Lambda constructs support capacity providers.

### Lambda capacity-provider settings (`2026-08`)

Lambda `CapacityProvider` supports `logGroup`, `systemLogLevel`, and tag propagation.

### Lambda durable functions (`2025-12`)

Lambda constructs support durable functions.

### Lambda Java AL2023 runtimes (`2026-08`)

Lambda adds Java 8, Java 11, and Java 17 runtimes on Amazon Linux 2023.

### Lambda log removal policies (`2025-07`)

Lambda function constructs support setting a removal policy for their logs.

### Lambda multi-tenancy (`2025-11`)

Lambda constructs support multi-tenancy through `TenancyConfig`.

### Lambda Node.js 24 defaults (`2026-06`)

Lambda framework functions and custom resources now default to `nodejs24.x`, and `Runtime.NODEJS_LATEST` resolves to it in every region. Node.js 24 does not support callback-style asynchronous handlers; migrate them to `async` handlers or pin `Runtime.NODEJS_22_X` (or set `useLatestRuntimeVersion: false` on `NodejsFunction`).

### Lambda Node.js parent-path entries (`2026-06`)

Lambda Node.js bundling accepts entry paths containing `..`.

### Lambda Ruby 3.4 (`2025-03`)

The Lambda runtime catalog includes Ruby 3.4.

### Lambda Ruby 4.0 (`2026-04`)

The Lambda runtime catalog includes Ruby 4.0.

### Lambda tag propagation (`2025-06`)

Lambda functions can propagate their tags to their log groups.

### Latest Lambda Node.js fallback (`2025-10`)

The fallback used for the latest Lambda Node.js runtime is now Node.js 22.x.

### Managed Lambda log-group flag default (`2025-06`)

When `aws-lambda:useCdkManagedLogGroup` is absent, CDK treats the feature flag as disabled.

### Node.js 22 custom-resource default (`2025-05`)

Custom resources now default to the Node.js 22 runtime in commercial, China, and government regions.

### Node.js 22 expression evaluation (`2025-09`)

Step Functions `EvaluateExpression` supports Node.js 22.

### Python custom-resource runtimes (`2025-09`)

Python custom resources use Python 3.13. Secrets Manager's `SecretRotationApplication` no longer creates an EOL Python 3.9 function.

### Refactoring exclusions (`2025-06`)

CDK refactoring excludes `lambda.Version` and `apigateway.Deployment` resources.

### Regional custom-resource runtime default (`2025-02`)

The default custom-resource Node.js runtime in China and government regions is Node.js 20.

## Step Functions

### Capacity-provider strategies for EcsRunTask (`2026-01`)

Step Functions `EcsRunTask` integrations for both Fargate and EC2 support capacity-provider strategies.

### Custom CSV delimiters (`2025-02`)

Step Functions `S3CsvItemReader` supports custom CSV delimiters.

### Distributed Map permissions (`2025-09`)

State machines synthesize the permissions needed to run and redrive Distributed Map, including maps defined only in nested `StateGraph` objects.

### Distributed Map result-writer configuration (`2025-04`)

Step Functions Distributed Map supports custom `WriterConfig` fields for its `ResultWriter`.

### Dynamic Distributed Map result buckets (`2025-05`)

Step Functions `ResultWriter` accepts JSONPath or JSONata expressions for its bucket.

### Dynamic Step Functions queue ARNs (`2025-03`)

Step Functions task integrations allow `jobQueueArn` to be supplied with either JsonPath or JSONata.

### Intrinsic Step Functions API endpoints (`2025-10`)

Under its feature flag, Step Functions tasks accept an intrinsic function as `apiEndpoint`.

### JSONata Map concurrency (`2026-01`)

Step Functions Map states accept JSONata expressions for `maxConcurrency`.

### JSONata Map item selectors (`2025-06`)

Step Functions Map states accept JSONata expressions in `ItemSelector`.

### Parallel-state parameters (`2025-05`)

Step Functions `Parallel` states support parameters.

### Step Functions JSONata and variables (`2025-02`)

Step Functions constructs support JSONata and workflow variables.

### Step Functions REST API JSONata paths (`2026-08`)

`CallApiGatewayRestApiEndpoint` supports JSONata expressions for `api_path`.
