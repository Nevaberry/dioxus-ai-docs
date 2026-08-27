# Compute, deployment, and networking

Use this reference when generating infrastructure requests or consuming models
for CloudFormation, EC2, containers, clusters, VPC networking, hybrid
infrastructure, managed databases, or streaming infrastructure.

## Deployment and build systems

### CloudFormation validation and Express mode (2026-06)

`CreateStack` and `UpdateStack` run pre-deployment validation automatically.
`DisableValidation` skips it. `DeploymentConfig` enables Express mode, whose
operation completes after resource configuration has been applied.

### CodeBuild host-kernel selection (2026-06)

On-demand CodeBuild requests can select the host kernel. Expose the field when
kernel compatibility matters instead of assuming the service default.

### Image Builder AMI watermarks (2026-06)

Image Builder models support AMI watermarks. Preserve this metadata in generated
models and image-governance workflows.

### CloudFormation sensitive-property drift reasons (2026-07-2)

`DriftIgnoredReason` includes a sensitive-property enum value. Drift consumers
can distinguish properties omitted because they are sensitive from other
ignored drift.

### CodeCommit server-side blob diffs (2026-08)

`GetBlobDifferences` returns paginated line-level hunks with context, additions,
and deletions between blob versions. Use it when a structured diff is needed
without cloning the repository.

## EC2 and Auto Scaling

### VPC endpoint payer responsibility (2026-06)

`ModifyVpcEndpointPayerResponsibility` lets an endpoint-service owner change the
billing account for an individual VPC endpoint.

### Auto Scaling reservations-first distribution (2026-06)

The `reservations-then-balanced` capacity distribution strategy consumes
Capacity Reservations first, then balances remaining capacity across healthy
Availability Zones.

### EC2 precision-time placement groups (2026-06)

EC2 supports the precision-time placement strategy. `CreatePlacementGroup` and
`DescribePlacementGroups` include `parentGroupId` for placement on
precision-time-capable hardware.

### EC2 CreateFleet overrides and placement details (2026-07)

`CreateFleet` launch-template overrides accept
`LaunchTemplateSpecificationUserData`, `KeyName`, `IamInstanceProfile`, and
`MetadataOptions`. Launched-instance responses add `SubnetId`,
`AvailabilityZone`, and `AvailabilityZoneId`.

### EC2 root-volume replacement from an existing volume (2026-07)

Replace Root Volume workflows accept `VolumeId`, allowing a prepared EBS volume
to become the replacement root volume.

### EC2 public-AMI SSM metadata (2026-07)

Public AMI metadata exposes its associated public Systems Manager parameter.
Use the returned parameter instead of maintaining a parallel AMI mapping.

### EC2 VPC Encryption Controls policies (2026-07)

EC2 provides declarative policies for enabling VPC Encryption Controls across
an organization or selected accounts.

### EC2 SEV-SNP dedicated hosts (2026-07)

EC2 Dedicated Hosts support AMD SEV-SNP. Include the capability in placement and
host-selection logic for confidential workloads.

### EC2 managed-resource visibility (2026-07)

Managed-resource visibility settings control whether AWS-provisioned resources
appear in console views and API list operations. A missing list item may be
hidden rather than absent.

### EC2 instance-type model additions (2026-07-2)

The EC2 model includes M9g, M9gd, C9g, C9gd, C8in, M8in, R8in, C8ib, M8ib,
R8ib, C8ine, M8ine, M8idn, R8idn, M8idb, R8idb, Mac-m3ultra, and G7 instance
types. Avoid stale closed enums in validation and UI code.

### EC2 application status checks (2026-07-2)

Application status checks monitor configurable HTTP or HTTPS paths and ports,
allowing automated response to application-level impairment rather than only
host or instance failure.

### EC2 IPAM BGP route protection (2026-08)

EC2 IPAM supports BGP route discovery, RPKI protection findings, and delegated
RPKI resources for Internet Registry associations, routing-policy registrations,
and ROA management on BYOIP prefixes.

### Spot Placement Scores for Local Zones (2026-08)

Spot Placement Score requests accept `IncludeLocalZones`. It defaults to
`false`; set it to `true` to include relevant Local Zones.

### Auto Scaling operator ownership (2026-08)

Auto Scaling group models include an operator field when another AWS service
manages the group. Use it to avoid treating a service-managed group as directly
owned.

## EKS, ECS, PCS, and hybrid compute

### EKS version rollback controls (2026-06)

EKS adds `CancelUpdate` for an in-progress `VersionRollback`,
`RollbackConfig.timeoutMinutes`, and cancellation details in
`Update.cancellation`.

### Network Firewall container associations (2026-06)

Network Firewall container associations dynamically track IP addresses for
running ECS and EKS workloads.

### EVS self-deployed VCF (2026-06)

EVS supports self-deployed VMware Cloud Foundation and connectors to Operations
and SDDC managers for coverage and usage monitoring.

### In-place PCS Slurm upgrades (2026-06)

`UpdateCluster` accepts `scheduler.version` to upgrade an existing PCS cluster's
Slurm version in place.

### ECS circuit-breaker controls (2026-06)

ECS deployment circuit breakers accept a custom failure threshold and a
selectable failure-counting mechanism.

### ECS Express Mode architecture selection (2026-07)

ECS automatically detects the correct CPU architecture for Express Mode
services; do not hard-code an architecture workaround.

### EMR on EKS security and Spark controls (2026-07-2)

EMR on EKS adds `DeleteSecurityConfiguration` and
`authenticationConfiguration`. Spark Connect adds
`sessionIdleTimeoutInMinutes`, `sessionEnabled`, `endpointToken`, `authProxyUrl`,
and `encryptionKeyArn`. Virtual clusters can cap concurrently running and
queued jobs.

### PCS node lifecycle actions (2026-07-2)

PCS compute node groups can execute custom scripts through structured node
lifecycle actions at defined points in a node's lifecycle.

### Outposts EKS service support (2026-07-2)

Outposts adds `EKS` to `AWSServiceName`. The `Address` field is marked sensitive,
so logging and serialization must respect sensitive-data handling.

### EKS Pod Identity request context (2026-07-2)

`AssumeRoleForPodIdentity` accepts optional `eksNodeName`, `instanceId`, and
`zone` context fields.

### Outposts VPC endpoint configuration (2026-08)

`CreatePrivateConnectivityConfig` accepts VPC endpoint configuration for scoped
private connectivity and provisioning-role creation on Outposts installations.

### EKS control-plane configuration tuning (2026-08)

EKS cluster models can selectively tune configurations of Kubernetes
control-plane components. Preserve unknown component settings during updates.

## Networking and routing

### Mutable VPC Lattice idle timeouts (2026-06)

VPC Lattice service models allow the idle-timeout configuration to be changed.

### MSK Replicator mTLS for external Kafka (2026-06)

MSK Replicator supports mutual TLS with external Kafka clusters when replicating
to Amazon MSK Express brokers.

### Route 53 Global Resolver shared views (2026-07)

`ListSharedDNSViews` lists DNS Views shared through Resource Access Manager.
`ListHostedZoneAssociations` permits an omitted resource ARN to list every
association in the account.

### Cloud Map dual-stack endpoint resolution (2026-07-2)

When dual stack is enabled, Cloud Map endpoint resolution now routes to the
dual-stack endpoint. Remove workarounds for the prior incorrect routing.

### NLB source-IP family matching (2026-07-2)

Elastic Load Balancing v2 adds `IpAddressType` to `SourceIpConfig`, allowing NLB
listener rules to distinguish IPv4 and IPv6 source traffic.

### Transit Gateway policy-based routing (2026-07-2)

EC2 Transit Gateway policy tables can match source and destination IPs, source
and destination ports, and protocol, then direct traffic to a target route
table.

### Network Firewall association status (2026-07-2)

Container-association polling must handle the `UPDATING` status as a
nonterminal state.

### Direct Connect route visibility (2026-07-2)

`ListVirtualInterfaceRoutes` returns BGP routes advertised over a virtual
interface, including AS paths and BGP communities.

### MSK authorizer logs (2026-08)

MSK clusters can deliver authorizer logs alongside broker logs to configured
log destinations.

## WorkSpaces, game streaming, and recovery

### GameLift Streams admin shell (2026-07)

`CreateStreamSessionAdminShell` opens a secure terminal connection to a live
stream-session runtime for troubleshooting. Restrict its use as privileged
administrative access.

### GameLift Streams session controls (2026-07-2)

Stream sessions can assume an IAM role for account resources and select
landscape, portrait, or square aspect ratios. `CreateStreamUrl`, `GetStreamUrl`,
`ListStreamUrls`, and `RevokeStreamUrl` manage temporary unauthenticated browser
access.

### WorkSpaces client-experience policy (2026-07-2)

`ModifyClientProperties` and `DescribeClientProperties` support
`ClientExperiencePolicy` in `ClientProperties`.

### WorkSpaces nested virtualization (2026-08)

WorkSpaces create and property-update models can enable or disable nested
virtualization for hypervisors and virtualization-based workloads.

### DRS recovery plans (2026-08)

Elastic Disaster Recovery supports reusable Recovery Plans that order
multi-server recovery with explicit steps and wait times. Plans also support
non-disruptive drills and run monitoring.

### GameLift fleet instance families (2026-08)

GameLift managed EC2 and container fleets support C8a, C8i, C9g, M8a, M8i, and
M9g instance families.

## Managed database and stream infrastructure

### Configurable RabbitMQ storage (2026-07-2)

Amazon MQ RabbitMQ 4.2 cluster deployments can set storage size within the
range supported by the selected broker instance size.

### RDS lifecycle, role, and storage controls (2026-07-2)

`ModifyDBInstance` and `ModifyDBCluster` can change `EngineLifecycleSupport`.
Cluster create and restore operations accept `AssociatedRoles`, avoiding a
later `AddRoleToDBCluster`. `DescribeDBInstances` returns
`StorageOperationStatus` and `StorageOperationPercentProgress` during storage
initialization and optimization.

### Managed Service for Apache Flink 2.3 (2026-07-2)

Managed Service for Apache Flink supports Flink 2.3. Accept that engine value in
deployment and validation logic.

### Timestream for InfluxDB plugins and data protection (2026-07-2)

InfluxDB 3 Core and Enterprise DB parameter groups accept a plugin repository
URL and optional Secrets Manager secret ARN for public or private Python
plugins. New instances and clusters can use customer-managed KMS keys, and
customer-managed backups can be restored.

### Oracle Exadata Exascale resources (2026-08)

The ODB client supports Oracle Exadata on Exascale Infrastructure (`ExaDB-XS`),
including storage vaults and VM clusters.

### ECR replication-rule limit (2026-08)

`PutReplicationConfiguration` permits up to 25 ECR replication rules instead of
10. Update client validation and partitioning logic.
