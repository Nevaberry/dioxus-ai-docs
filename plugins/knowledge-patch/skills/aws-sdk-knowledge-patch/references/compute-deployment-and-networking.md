# Compute, deployment, and networking

## Build and infrastructure deployment

### CodeBuild

On-demand CodeBuild builds can select the host kernel (since `2026-06`). Include the selected kernel in reproducibility and compatibility checks rather than assuming the platform default.

### CloudFormation

`CreateStack` and `UpdateStack` now run pre-deployment validation automatically (since `2026-06`). Set `DisableValidation` to skip it. Use `DeploymentConfig` to enable Express mode, in which the operation completes once resource configuration has been applied rather than waiting for the ordinary completion boundary.

### Image Builder

Image Builder can apply watermarks to AMIs (since `2026-06`). Account for the watermark configuration when comparing or distributing generated images.

### EVS and PCS

- EVS supports a self-deployed VMware Cloud Foundation mode and connectors to Operations Manager and SDDC Manager for coverage and usage monitoring (since `2026-06`).
- PCS `UpdateCluster` accepts a target Slurm version in `scheduler.version` and can perform an in-place upgrade (since `2026-06`).

## Kubernetes, containers, and scaling

### EKS rollback

EKS supports `VersionRollback` updates (since `2026-06`). `RollbackConfig.timeoutMinutes` bounds a rollback, `CancelUpdate` cancels one in progress, and `Update.cancellation` reports cancellation details.

### ECS

- Deployment circuit breakers accept a custom failure threshold and a choice of failure-counting mechanism (since `2026-06`). Do not assume the former fixed threshold behavior when interpreting deployment failures.
- ECS automatically detects the correct CPU architecture for Express Mode services (since `2026-07`); avoid hard-coding an architecture solely to compensate for the earlier behavior.

### Auto Scaling

The `reservations-then-balanced` capacity distribution strategy launches into Capacity Reservations first, then balances remaining capacity across healthy Availability Zones (since `2026-06`).

### Network Firewall container associations

Network Firewall container associations can dynamically track IP addresses of running ECS and EKS containers for workload monitoring (since `2026-06`). Use associations where ephemeral container addressing previously required manual rule updates.

## EC2

### Precision-time placement groups

`CreatePlacementGroup` and `DescribePlacementGroups` support the `precision-time` strategy and `parentGroupId` (since `2026-06`). Precision-time groups, and cluster placement groups parented to them, place instances on precision-time-capable hardware.

### CreateFleet overrides and placement results

`CreateFleet` launch-template overrides add `LaunchTemplateSpecificationUserData`, `KeyName`, `IamInstanceProfile`, and `MetadataOptions` (since `2026-07`). The response identifies each launched instance's subnet, Availability Zone, and Availability Zone ID.

### Root-volume replacement

Replace Root Volume accepts `VolumeId` (since `2026-07`), allowing a prepared EBS volume to become the replacement root instead of requiring the service to derive one through the older paths.

### AMI and managed-resource metadata

- Public AMI metadata surfaces the public SSM parameter associated with the AMI (since `2026-07`).
- Managed-resource visibility settings control whether AWS-provisioned resources appear in console views and API list operations (since `2026-07`). Treat hidden resources as a visibility choice, not proof that the resources do not exist.

### Organization security and hosts

- EC2 declarative policies can enable VPC Encryption Controls across an organization or selected accounts (since `2026-07`).
- EC2 Dedicated Hosts support AMD SEV-SNP (since `2026-07`). Validate instance family, host, and guest prerequisites before requesting confidential-computing features.

## Networking and certificates

### VPC Lattice

The idle-timeout configuration of a VPC Lattice service is mutable (since `2026-06`). Update it directly instead of replacing the service solely to change the timeout.

### Route 53 Global Resolver

`ListSharedDNSViews` lists DNS Views shared through Resource Access Manager (since `2026-07`). `ListHostedZoneAssociations` makes its resource ARN optional, allowing an account-wide association listing.

### MSK Replicator

MSK Replicator can use mutual TLS with external Kafka clusters when the replication target is an MSK Express broker (since `2026-06`). Supply the external-cluster client authentication material and ensure the target broker type satisfies the constraint.

### ACM ACME issuance

Certificate Manager can issue public certificates through ACME for automated lifecycle management on customer-managed infrastructure, including on-premises hosts and Kubernetes clusters (since `2026-06`).
