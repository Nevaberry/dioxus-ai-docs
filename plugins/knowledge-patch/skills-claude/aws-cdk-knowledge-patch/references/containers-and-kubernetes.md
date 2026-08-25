# Containers and Kubernetes

Topic-organized compatibility guidance for AWS CDK.

## Amazon ECR

### Auto-delete mixins (`2026-03`)

ECR adds `RepositoryAutoDeleteImages`, and S3's `BucketAutoDeleteObjects` mixin graduates into `aws-cdk-lib`.

### Docker build contexts for ECR assets (`2026-03`)

ECR asset constructs support Docker build contexts.

### ECR and Inspector CodePipeline actions (`2025-04`)

CodePipeline action constructs add ECR build-and-publish, Inspector ECR image scanning, and Inspector source-code scanning.

### ECR tag-mutability exclusions (`2025-10`)

ECR repositories support exclusion filters for image-tag mutability.

### Existing ECR repository lookup (`2025-03`)

ECR constructs can look up an existing repository rather than requiring its attributes to be supplied manually.

## Amazon ECS

### Built-in ECS linear and canary deployments (`2026-01`)

ECS constructs now provide built-in linear and canary deployment configurations.

### Complete ECS task overrides (`2025-02`)

Event target constructs expose all ECS task overrides.

### Deprecated ECS instance-role isolation property (`2025-01`)

ECS deprecates `canContainersAccessInstanceRole`.

### ECS AL2023 Neuron AMIs (`2026-07`)

ECS constructs support ECS-optimized Amazon Linux 2023 Neuron AMIs.

### ECS availability-zone rebalancing (`2025-02`)

ECS constructs support service availability-zone rebalancing.

### ECS availability-zone rebalancing default (`2025-09`)

For `AWS::ECS::Service`, the `AvailabilityZoneRebalancing` default changed from `ENABLED` to `DISABLED`.

### ECS container version consistency (`2025-02`)

ECS constructs support container version consistency.

### ECS Exec for Batch (`2025-09`)

Batch constructs support ECS Exec.

### ECS fault injection (`2025-01`)

ECS constructs expose the service fault-injection flag.

### ECS managed-instances capacity providers (`2025-10`)

ECS provides an L2 `ManagedInstancesCapacityProvider`, and the construct implements `IConnectable` so it can participate in connection rules.

### ECS managed-storage encryption (`2025-03`)

ECS constructs support encryption for ECS-managed storage.

### ECS Service Connect access logs (`2026-04`)

ECS constructs support access-log configuration for Service Connect.

### ECS Service Connect TLS (`2025-02`)

`ServiceConnectService` accepts TLS configuration.

### ECS volume initialization rate (`2025-09`)

ECS constructs expose volume initialization rate.

### Enhanced Container Insights (`2025-01`)

ECS constructs can enable enhanced observability for Container Insights.

### Existing Cloud Map namespaces (`2026-08`)

ECS cluster constructs can use existing Cloud Map namespaces.

### External ECS daemon services (`2025-02`)

ECS `ExternalService` supports the daemon scheduling strategy.

### Forced ECS deployments (`2026-03`)

ECS services accept `forceNewDeployment` to request a new deployment.

### Native ECS blue/green L2 support (`2025-08`)

Native ECS blue/green deployments are configurable through L2 constructs. The feature landed in 2.209.0, was reverted in 2.210.0, and returned in 2.211.0.

## Amazon EKS

### Additional EKS access-entry types (`2026-02`)

EKS access entries support the `EC2`, `HYBRID_LINUX`, and `HYPERPOD_LINUX` types.

### EKS AL2023 default (`2026-06`)

Under its feature flag, EKS uses the recommended Amazon Linux 2023 AMI type instead of Amazon Linux 2.

### EKS cluster deletion protection (`2026-06`)

The EKS `Cluster` construct accepts `deletionProtection`.

### EKS cluster removal policies (`2025-10`)

EKS cluster constructs support removal policies.

### EKS Hybrid Nodes (`2025-02`)

EKS provides L2 constructs for Hybrid Nodes.

### EKS isolated kubectl subnets (`2026-03, 2026-04`)

EKS reports isolated kubectl subnets as a warning. The validation first landed as an error in 2026-03 and was relaxed to a warning in 2026-04.

### EKS Kubernetes 1.32 (`2025-02`)

The EKS Kubernetes-version catalog includes version 1.32.

### EKS Kubernetes 1.33 (`2025-06`)

The EKS Kubernetes-version catalog includes version 1.33.

### EKS Kubernetes 1.35 (`2026-03`)

The EKS Kubernetes-version catalog includes version 1.35.

### EKS load-balancer controller versions (`2026-06`)

`AlbControllerVersion` supports versions 2.8.3 through 3.2.2.

### EKS load-balancer-controller values (`2025-04`)

EKS constructs can pass additional Helm chart values to the AWS Load Balancer Controller.

### EKS managed node repair (`2025-03`)

`Nodegroup` supports `nodeRepairConfig`, exposing managed node-group repair configuration.

### EKS provisioned control planes and Kubernetes 1.36 (`2026-08`)

EKS supports provisioned control planes through `controlPlaneScalingTier` and adds Kubernetes version 1.36.

### EKS removal policies (`2026-02`)

Removal policies can be applied across all EKS constructs.

### EKS self-managed add-on bootstrapping (`2025-06`)

EKS cluster constructs expose `bootstrapSelfManagedAddons` to control whether the cluster bootstraps its default self-managed add-ons.

### Native EKS OIDC providers (`2026-02`)

EKS provides `OidcProviderNative`, backed by the native L1 resource, and deprecates the custom-resource-based `OpenIdConnectProvider`.

### New platform versions (`2025-11`)

The EKS catalog includes Kubernetes 1.34, and the Lambda runtime catalog includes Node.js 24.x, Java 25, and Python 3.14.

### Required EKS kubectl layer (`2025-02`)

The experimental EKS `Cluster` and `FargateCluster` constructs now require `kubectlLayer`; the outdated default was removed, so the supplied layer should match the Kubernetes version.

### Service-account overwrite control (`2026-02`)

The EKS service-account construct accepts `overwriteServiceAccount`.

### Stable EKS v2 constructs (`2026-02`)

The EKS v2 constructs have graduated to stable.

### Synthesized security behavior (`2025-09`)

`BucketNotificationsHandler` scopes IAM permissions to specific bucket ARNs, and ECS patterns keep `openListener` false when given a custom security group. The EKS kubectl provider uses the `AmazonEC2ContainerRegistryPullOnly` managed policy.

## Amazon MSK

### MSK Express brokers (`2025-11`)

MSK constructs support Express brokers.
