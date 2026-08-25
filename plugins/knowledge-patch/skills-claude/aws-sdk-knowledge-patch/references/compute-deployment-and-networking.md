# Compute, deployment, and networking

## Infrastructure deployment

### CloudFormation

- **CloudFormation validation and Express mode (`2026-06`).** `CreateStack`
  and `UpdateStack` run pre-deployment validation automatically.
  `DisableValidation` skips it; `DeploymentConfig` enables Express mode, which
  completes after resource configuration is applied.
- **CloudFormation sensitive-property drift reasons (`2026-07-2`).** The
  `DriftIgnoredReason` enum can indicate that drift was ignored because a
  property is sensitive.

### CodeBuild and CodeCommit

- **CodeBuild host-kernel selection (`2026-06`).** On-demand builds can select
  the host kernel.
- **CodeCommit server-side blob diffs (`2026-08`).** `GetBlobDifferences`
  returns paginated line-level hunks, including context, additions, and
  deletions between blob versions, without a local clone.

### Image Builder and Device Farm

- **Image Builder AMI watermarks (`2026-06`).** Image Builder models support
  AMI watermarks.
- **Cloud9 Amazon Linux 2 API removal (`2026-07`).** The public
  EC2-environment creation API no longer accepts Amazon Linux 2 as an AMI
  option.
- **Device Farm generated insights (`2026-08`).** Run, job, and test models
  expose service-generated insights.

## EKS, ECS, and container networking

### EKS

- **EKS version rollback controls (`2026-06`).** `CancelUpdate` can cancel an
  in-progress `VersionRollback`; `RollbackConfig.timeoutMinutes` sets the
  timeout, and `Update.cancellation` reports cancellation details.
- **EKS Pod Identity request context (`2026-07-2`).** `AssumeRoleForPodIdentity`
  accepts optional `eksNodeName`, `instanceId`, and `zone`.
- **EKS control-plane configuration tuning (`2026-08`).** Cluster models can
  selectively tune Kubernetes control-plane component configurations.

### ECS

- **ECS circuit-breaker controls (`2026-06`).** Deployment circuit breakers
  accept a custom failure threshold and a selectable failure-counting method.
- **ECS Express Mode architecture selection (`2026-07`).** Express Mode
  services automatically detect the correct CPU architecture.

### Network Firewall

- **Network Firewall container associations (`2026-06`).** Container
  associations dynamically track IP addresses for running ECS and EKS
  workloads.
- **Network Firewall association status (`2026-07-2`).** Pollers for container
  associations must handle the new `UPDATING` state.

## EC2 and Auto Scaling

### Fleet, placement, and instance models

- **EC2 precision-time placement groups (`2026-06`).** `CreatePlacementGroup`
  and `DescribePlacementGroups` support the `precision-time` strategy and
  `parentGroupId` for precision-time-capable hardware.
- **EC2 CreateFleet overrides and placement details (`2026-07`).** Launch
  template overrides accept `LaunchTemplateSpecificationUserData`, `KeyName`,
  `IamInstanceProfile`, and `MetadataOptions`. Launched-instance responses add
  `SubnetId`, `AvailabilityZone`, and `AvailabilityZoneId`.
- **EC2 instance-type model additions (`2026-07-2`).** Models include M9g,
  M9gd, C9g, C9gd, C8in, M8in, R8in, C8ib, M8ib, R8ib, C8ine, M8ine, M8idn,
  R8idn, M8idb, R8idb, Mac-m3ultra, and G7 types.
- **GameLift fleet instance families (`2026-08`).** GameLift managed EC2 and
  container fleets accept C8a, C8i, C9g, M8a, M8i, and M9g families.
- **Spot Placement Scores for Local Zones (`2026-08`).** Requests accept
  `IncludeLocalZones`; it defaults to `false` and includes relevant Local
  Zones when `true`.

### Host, volume, and health controls

- **EC2 root-volume replacement from an existing volume (`2026-07`).** Replace
  Root Volume workflows accept `VolumeId` for a prepared replacement volume.
- **EC2 public-AMI SSM metadata (`2026-07`).** Public AMI metadata exposes the
  associated public SSM parameter.
- **EC2 SEV-SNP dedicated hosts (`2026-07`).** Dedicated Hosts support AMD
  SEV-SNP.
- **EC2 managed-resource visibility (`2026-07`).** Visibility settings control
  whether AWS-provisioned resources appear in consoles and list APIs.
- **EC2 application status checks (`2026-07-2`).** Application checks monitor
  configurable HTTP or HTTPS paths and ports, enabling responses to
  application impairment rather than only host or instance failures.

### Auto Scaling

- **Auto Scaling reservations-first distribution (`2026-06`).** The
  `reservations-then-balanced` strategy uses Capacity Reservations first and
  balances remaining capacity across healthy Availability Zones.
- **Auto Scaling multi-instance termination (`2026-08`).**
  `TerminateInstanceInAutoScalingGroup` accepts `InstanceIds` and returns an
  `Activities` list. Duplicate `LaunchInstances` client tokens can return
  `IdempotentCallInProgressFault`.
- **Auto Scaling operator ownership (`2026-08`).** Group models expose an
  operator when another AWS service manages the group.

## VPC, DNS, and load balancing

### VPC and Transit Gateway

- **VPC endpoint payer responsibility (`2026-06`).**
  `ModifyVpcEndpointPayerResponsibility` lets an endpoint-service owner change
  the billing account for an individual endpoint.
- **Mutable VPC Lattice idle timeouts (`2026-06`).** VPC Lattice service
  models support changing idle-timeout configuration.
- **EC2 VPC Encryption Controls policies (`2026-07`).** Declarative policies
  can enable VPC Encryption Controls across an organization or selected
  accounts.
- **Transit Gateway policy-based routing (`2026-07-2`).** Policy tables can
  match source/destination IPs, source/destination ports, and protocol, then
  direct traffic to a target route table.
- **EC2 IPAM BGP route protection (`2026-08`).** IPAM adds BGP route discovery,
  RPKI protection findings, and delegated RPKI resources for Internet Registry
  associations, routing-policy registrations, and ROA management on BYOIP
  prefixes.

### DNS and endpoint resolution

- **Route 53 Global Resolver shared views (`2026-07`).** `ListSharedDNSViews`
  lists DNS Views shared through Resource Access Manager.
  `ListHostedZoneAssociations` permits an omitted resource ARN to list all
  account associations.
- **Cloud Map dual-stack endpoint resolution (`2026-07-2`).** With dual stack
  enabled, endpoint resolution correctly uses the dual-stack endpoint; remove
  workarounds for the prior routing behavior.

### Load balancing and direct connectivity

- **NLB source-IP family matching (`2026-07-2`).** `SourceIpConfig` accepts
  `IpAddressType`, allowing listener rules to distinguish IPv4 and IPv6 source
  traffic.
- **Direct Connect route visibility (`2026-07-2`).**
  `ListVirtualInterfaceRoutes` returns advertised BGP routes, including AS
  paths and communities.

## Outposts and hybrid infrastructure

- **Outposts phone-number validation (`2026-07`).** Site requests enforce a
  stricter `ContactPhoneNumber` regular expression; formerly accepted formats
  can fail validation.
- **Outposts EKS service support (`2026-07-2`).** `AWSServiceName` accepts
  `EKS`, and `Address` is marked sensitive.
- **Outposts VPC endpoint configuration (`2026-08`).**
  `CreatePrivateConnectivityConfig` accepts VPC endpoint configuration for
  scoped private connectivity and provisioning-role creation.
- **EVS self-deployed VCF (`2026-06`).** EVS adds self-deployed VMware Cloud
  Foundation plus Operations Manager and SDDC Manager connectors for coverage
  and usage monitoring.
- **WorkSpaces nested virtualization (`2026-08`).** Creation and property
  update models can enable or disable nested virtualization for hypervisors
  and virtualization-based workloads inside a WorkSpace.
- **WorkSpaces client-experience policy (`2026-07-2`).**
  `ModifyClientProperties` and `DescribeClientProperties` support
  `ClientExperiencePolicy` in `ClientProperties`.

## Clusters, schedulers, and streaming infrastructure

### PCS and EMR on EKS

- **In-place PCS Slurm upgrades (`2026-06`).** `UpdateCluster` accepts
  `scheduler.version` to upgrade an existing PCS cluster's Slurm version.
- **PCS node lifecycle actions (`2026-07-2`).** Compute node groups can run
  structured custom scripts at defined node lifecycle points.
- **EMR on EKS security and Spark controls (`2026-07-2`).** The client adds
  `DeleteSecurityConfiguration`, `authenticationConfiguration`, and Spark
  Connect fields `sessionIdleTimeoutInMinutes`, `sessionEnabled`,
  `endpointToken`, `authProxyUrl`, and `encryptionKeyArn`. Virtual clusters
  can cap concurrently running and queued jobs.

### Kafka, RabbitMQ, and Flink

- **MSK Replicator mTLS for external Kafka (`2026-06`).** Replicator can use
  mutual TLS with external Kafka when replicating to MSK Express brokers.
- **MSK authorizer logs (`2026-08`).** Clusters can deliver authorizer logs
  alongside broker logs to configured destinations.
- **Configurable RabbitMQ storage (`2026-07-2`).** RabbitMQ 4.2 cluster
  deployments can set storage size within the range supported by the broker
  instance size.
- **Managed Service for Apache Flink 2.3 (`2026-07-2`).** Managed Service for
  Apache Flink supports Flink 2.3.

## Migration, recovery, and data movement

- **DataSync Enhanced mode expansion (`2026-07-2`).** Enhanced mode works
  agentlessly with EFS and FSx for Lustre, and through an agent with HDFS plus
  TDE, Azure Blob, and object-storage locations. HDFS supports multiple
  NameNodes for high availability, and Enhanced-mode agents can run on
  Hyper-V.
- **Idempotent ARC plan execution (`2026-07-2`).** `StartPlanExecution`
  accepts a client token for retrying ARC Region Switch executions without
  starting duplicates.
- **DRS recovery plans (`2026-08`).** Elastic Disaster Recovery supports
  reusable Recovery Plans with ordered multi-server steps and wait times,
  non-disruptive drills, and run monitoring.
