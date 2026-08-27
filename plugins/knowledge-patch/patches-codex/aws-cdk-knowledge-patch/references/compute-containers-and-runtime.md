# Compute, containers, and runtimes

Use this reference for compute, containers, and runtimes compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## Amazon ECS

### Built-in ECS linear and canary deployments

**Batch:** `2026-01`

ECS constructs now provide built-in linear and canary deployment configurations.

### Deprecated ECS instance-role isolation property

**Batch:** `2025-01`

ECS deprecates `canContainersAccessInstanceRole`.

### ECS AL2023 Neuron AMIs

**Batch:** `2026-07`

ECS constructs support ECS-optimized Amazon Linux 2023 Neuron AMIs.

### ECS availability-zone rebalancing

**Batch:** `2025-02`

ECS constructs support service availability-zone rebalancing.

### ECS availability-zone rebalancing default

**Batch:** `2025-09`

For `AWS::ECS::Service`, the `AvailabilityZoneRebalancing` default changed from `ENABLED` to `DISABLED`.

### ECS container version consistency

**Batch:** `2025-02`

ECS constructs support container version consistency.

### ECS Exec for Batch

**Batch:** `2025-09`

Batch constructs support ECS Exec.

### ECS fault injection

**Batch:** `2025-01`

ECS constructs expose the service fault-injection flag.

### ECS managed-instances capacity providers

**Batch:** `2025-10`

ECS provides an L2 `ManagedInstancesCapacityProvider`, and the construct implements `IConnectable` so it can participate in connection rules.

### ECS managed-storage encryption

**Batch:** `2025-03`

ECS constructs support encryption for ECS-managed storage.

### ECS Service Connect access logs

**Batch:** `2026-04`

ECS constructs support access-log configuration for Service Connect.

### ECS Service Connect TLS

**Batch:** `2025-02`

`ServiceConnectService` accepts TLS configuration.

### ECS volume initialization rate

**Batch:** `2025-09`

ECS constructs expose volume initialization rate.

### External ECS daemon services

**Batch:** `2025-02`

ECS `ExternalService` supports the daemon scheduling strategy.

### Forced ECS deployments

**Batch:** `2026-03`

ECS services accept `forceNewDeployment` to request a new deployment.

### Native ECS blue/green deployments

**Batch:** `2025-07`

ECS L1 bindings support native blue/green deployment configuration for services.

### Native ECS blue/green L2 support

**Batch:** `2025-08`

Native ECS blue/green deployments are configurable through L2 constructs. The feature landed in 2.209.0, was reverted in 2.210.0, and returned in 2.211.0.

## Amazon EC2 and Auto Scaling

### Auto Scaling availability-zone distribution

**Batch:** `2025-01`

`AutoScalingGroup` accepts `availabilityZoneDistribution` to control capacity distribution across Availability Zones.

### Auto Scaling instance-refresh policies

**Batch:** `2026-08`

Auto Scaling supports the `AutoScalingInstanceRefresh` CloudFormation update policy.

### Auto Scaling lifecycle controls

**Batch:** `2026-03`

`AutoScalingGroup` accepts `deletionProtection` and `instanceLifecyclePolicy`.

### EC2 C8A instances

**Batch:** `2026-05`

The EC2 instance-type catalog includes C8A.

### EC2 C8GN instances

**Batch:** `2025-07`

The EC2 instance-class catalog includes C8GN.

### EC2 Fleet replacement constraints

**Batch:** `2025-12`

`AWS::EC2::EC2Fleet` now treats `DefaultTargetCapacityType` and `TargetCapacityUnitType` as immutable, so changing either property replaces the fleet rather than updating it in place.

### EC2 instance metadata options

**Batch:** `2025-12`

EC2 instance constructs expose their `MetadataOptions` configuration for callers that need to inspect the instance metadata settings.

### Launch-template EBS controls

**Batch:** `2026-08`

Launch-template EBS properties support volume initialization rate, and CDK accepts gp3 and io2 volume sizes up to 64 TiB.

### Managed Instances capacity-provider changes

**Batch:** `2026-01`

`ManagedInstancesCapacityProvider` now creates its EC2 instance profile automatically, requires at least one `securityGroups` entry, and accepts `capacityOptionType` for Spot capacity.

### Multiple Auto Scaling health checks

**Batch:** `2025-03`

The new `HealthChecks` API supports multiple health-check types, including EBS and `VPC_LATTICE`.

## AWS Lambda

### ADOT Lambda layers

**Batch:** `2025-02`

The Lambda ADOT layer catalog includes version 0.115.0.

### Deprecated Lambda policy feature flag

**Batch:** `2025-04`

The default `@aws-cdk/aws-lambda:createNewPoliciesWithAddToRolePolicy` feature flag is deprecated.

### Deprecated Lambda runtime

**Batch:** `2025-01`

The Lambda Python 3.8 runtime is marked deprecated.

### Infinite Lambda event-source retries

**Batch:** `2025-04`

Lambda `EventSourceMapping` accepts `retryAttempts: -1` to request infinite retries.

### Lambda capacity providers

**Batch:** `2025-12`

Lambda constructs support capacity providers.

### Lambda capacity-provider settings

**Batch:** `2026-08`

Lambda `CapacityProvider` supports `logGroup`, `systemLogLevel`, and tag propagation.

### Lambda durable functions

**Batch:** `2025-12`

Lambda constructs support durable functions.

### Lambda Java AL2023 runtimes

**Batch:** `2026-08`

Lambda adds Java 8, Java 11, and Java 17 runtimes on Amazon Linux 2023.

### Lambda log removal policies

**Batch:** `2025-07`

Lambda function constructs support setting a removal policy for their logs.

### Lambda multi-tenancy

**Batch:** `2025-11`

Lambda constructs support multi-tenancy through `TenancyConfig`.

### Lambda Node.js 24 defaults

**Batch:** `2026-06`

Lambda framework functions and custom resources now default to `nodejs24.x`, and `Runtime.NODEJS_LATEST` resolves to it in every region. Node.js 24 does not support callback-style asynchronous handlers; migrate them to `async` handlers or pin `Runtime.NODEJS_22_X` (or set `useLatestRuntimeVersion: false` on `NodejsFunction`).

### Lambda Node.js parent-path entries

**Batch:** `2026-06`

Lambda Node.js bundling accepts entry paths containing `..`.

### Lambda Ruby 3.4

**Batch:** `2025-03`

The Lambda runtime catalog includes Ruby 3.4.

### Lambda Ruby 4.0

**Batch:** `2026-04`

The Lambda runtime catalog includes Ruby 4.0.

### Latest Lambda Node.js fallback

**Batch:** `2025-10`

The fallback used for the latest Lambda Node.js runtime is now Node.js 22.x.

### Node.js 22 custom-resource default

**Batch:** `2025-05`

Custom resources now default to the Node.js 22 runtime in commercial, China, and government regions.

### Regional custom-resource runtime default

**Batch:** `2025-02`

The default custom-resource Node.js runtime in China and government regions is Node.js 20.

## Amazon EKS

### Additional EKS access-entry types

**Batch:** `2026-02`

EKS access entries support the `EC2`, `HYBRID_LINUX`, and `HYPERPOD_LINUX` types.

### EKS AL2023 default

**Batch:** `2026-06`

Under its feature flag, EKS uses the recommended Amazon Linux 2023 AMI type instead of Amazon Linux 2.

### EKS cluster deletion protection

**Batch:** `2026-06`

The EKS `Cluster` construct accepts `deletionProtection`.

### EKS cluster removal policies

**Batch:** `2025-10`

EKS cluster constructs support removal policies.

### EKS Hybrid Nodes

**Batch:** `2025-02`

EKS provides L2 constructs for Hybrid Nodes.

### EKS isolated-subnet validation

**Batch:** `2026-04`

The kubectl isolated-subnet validation introduced as an error in the previous batch is now a warning.

### EKS kubectl subnet validation

**Batch:** `2026-03`

EKS now throws an error when kubectl subnets are isolated.

### EKS Kubernetes 1.32

**Batch:** `2025-02`

The EKS Kubernetes-version catalog includes version 1.32.

### EKS Kubernetes 1.33

**Batch:** `2025-06`

The EKS Kubernetes-version catalog includes version 1.33.

### EKS Kubernetes 1.35

**Batch:** `2026-03`

The EKS Kubernetes-version catalog includes version 1.35.

### EKS load-balancer-controller values

**Batch:** `2025-04`

EKS constructs can pass additional Helm chart values to the AWS Load Balancer Controller.

### EKS managed node repair

**Batch:** `2025-03`

`Nodegroup` supports `nodeRepairConfig`, exposing managed node-group repair configuration.

### EKS provisioned control planes and Kubernetes 1.36

**Batch:** `2026-08`

EKS supports provisioned control planes through `controlPlaneScalingTier` and adds Kubernetes version 1.36.

### EKS removal policies

**Batch:** `2026-02`

Removal policies can be applied across all EKS constructs.

### EKS self-managed add-on bootstrapping

**Batch:** `2025-06`

EKS cluster constructs expose `bootstrapSelfManagedAddons` to control whether the cluster bootstraps its default self-managed add-ons.

### New platform versions

**Batch:** `2025-11`

The EKS catalog includes Kubernetes 1.34, and the Lambda runtime catalog includes Node.js 24.x, Java 25, and Python 3.14.

### Required EKS kubectl layer

**Batch:** `2025-02`

The experimental EKS `Cluster` and `FargateCluster` constructs now require `kubectlLayer`; the outdated default was removed, so the supplied layer should match the Kubernetes version.

### Service-account overwrite control

**Batch:** `2026-02`

The EKS service-account construct accepts `overwriteServiceAccount`.

### Stable EKS v2 constructs

**Batch:** `2026-02`

The EKS v2 constructs have graduated to stable.

## AWS Batch

### Batch AL2023 images and default

**Batch:** `2026-04`

Batch adds Amazon Linux 2023 image types and, under its feature flag, defaults to AL2023.

### Batch default instance classes

**Batch:** `2025-10`

EC2 managed compute environments support default instance classes, and `useOptimalInstanceClasses` is deprecated.

### Batch job-definition updates

**Batch:** `2026-04`

Batch skips unregistering a job definition during an update.

### Batch optimal instance classes remain supported

**Batch:** `2026-01`

`useOptimalInstanceClasses` was undeprecated, reversing its earlier deprecation; it remains supported for Batch compute environments.
