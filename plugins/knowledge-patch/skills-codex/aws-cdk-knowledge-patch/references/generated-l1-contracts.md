# Generated L1 and CloudFormation contracts

Use this reference for generated l1 and cloudformation contracts compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## Generated L1 and CloudFormation contracts

### Experimental L1 removals

**Batch:** `2025-03`

The experimental bindings removed `CfnWorkgroup.attrWorkgroupMaxCapacity`, `CfnAnalysis.SheetTextBoxProperty.interactions`, `CfnDashboard.SheetTextBoxProperty.interactions`, `CfnTemplate.SheetTextBoxProperty.interactions`, and `CfnDistributionConfiguration.DistributionProperty.ssmParameterConfigurations`.

### Experimental L1 schema changes

**Batch:** `2025-04`

Removed properties include Backup `RestoreTestingPlan.ScheduleStatus`; EKS `PodIdentityAssociation.DisableSessionTags`, `TargetRoleArn`, and `ExternalId`; Neptune `DBSubnetGroup.Id`, `DBClusterParameterGroup.Id`, and `DBParameterGroup.Id`; RDS `DBInstance.CertificateDetails` and `Endpoint`; and Redshift Serverless `Workgroup.BaseCapacity`. Launch Wizard `CfnDeployment.specifications` and SES `RuleBooleanToEvaluateProperty.attribute` changed from required to optional.

### L1 contract changes

**Batch:** `2025-08`

`AWS::RDS::DBInstance.StatusInfos` and `AWS::SageMaker::Domain.SingleSignOnApplicationArn` were removed, while `AWS::CloudFront::Function.Name` became immutable. `CfnServer` for `AWS::OpsWorksCM::Server` is no longer provisionable; on `CfnCampaign`, `DataDestinationConfigs`, `SignalsToCollect`, and `SignalsToFetch` are immutable and updates replace the resource.

### L1 contract changes

**Batch:** `2025-10`

Generated L1 bindings now require `PortfolioId` and `PrincipalARN` on `AWS::ServiceCatalog::PortfolioPrincipalAssociation`, `SnsTopicArn` on `AWS::Neptune::EventSubscription`, and `IamRoleArn` and `LocationScope` on `AWS::S3::AccessGrantsLocation`; `AWS::Lex::ResourcePolicy.ResourceArn` is now immutable. The `Id` attribute was removed from Service Catalog portfolio-product associations, portfolio shares, and tag-option associations and from Neptune event subscriptions; `AWS::DataZone::ProjectProfile.Id` and `AWS::Logs::DeliveryDestination.DeliveryDestinationType` were also removed.

### L1 contract changes

**Batch:** `2025-11`

`AWS::DynamoDB::GlobalTable.ResourcePolicy` is now required, while DynamoDB global-table replication-mode and source-ARN properties were removed. `AWS::OpenSearchServerless::Collection.StandbyReplicas` is immutable; ID attributes were removed from EventBridge event-bus policies and Service Catalog portfolio-principal associations; and the logically air-gapped backup-vault encryption-key ARN attribute was removed.

### L1 contract changes

**Batch:** `2026-02`

`AWS::LicenseManager::License` now requires both `Beneficiary` and `ProductSKU`. `AWS::SageMaker::Cluster.Orchestrator.Eks` is now immutable, so it cannot be changed in place.

### L1 contract changes

**Batch:** `2026-04`

Removed generated surface includes `SourceSecurityGroup` and the `PolicyItem` and `SourceSecurityGroup` types from `AWS::ElasticLoadBalancing::LoadBalancer`; `MonitoringConfiguration` and its associated configuration types from `AWS::EMR::Cluster`; the `Id` attribute from `AWS::AppStream::Stack`; the `ExecutionStatus` attribute from `AWS::BedrockAgentCore::OnlineEvaluationConfig`; and the `EKS_CAPABILITY_ACK_S3_LOGS` vended-log type from `AWS::EKS::Capability`. AppSync GraphQL API log configuration now requires `CloudWatchLogsRoleArn` and `FieldLogLevel`, Kafka Connect provisioned capacity requires `McuCount`, and `AWS::AppStream::ImageBuilder.Name` is immutable.

### L1 contract changes

**Batch:** `2026-05`

`AWS::NeptuneGraph::GraphSnapshot.GraphIdentifier` is now required. The `Id` attributes were removed from `AWS::ElastiCache::CacheCluster` and `AWS::SageMaker::Model`, and the `AWS::VpcLattice::AuthPolicy.State` enum values changed from `ACTIVE` and `INACTIVE` to `Active` and `Inactive`.

### L1 contract changes

**Batch:** `2026-07`

`AWS::CloudWatch::LogAlarm.ScheduledQueryConfiguration` no longer has `QueryLanguage`. `AWS::ElasticLoadBalancing::LoadBalancer` no longer exposes `Id`, and its primary identifier is now `LoadBalancerName`.

### L1 property-mutation tracing

**Batch:** `2026-04`

Core records source traces for property mutations on L1 constructs, improving diagnostics for changes made after construction.

### L2 event patterns on L1 rules

**Batch:** `2025-11`

EventBridge L2 `EventPattern` interfaces can be used with `CfnRule`.

### PCA Connector AD L1 requirements

**Batch:** `2026-06`

`AWS::PCAConnectorAD::ServicePrincipalName` now requires `ConnectorArn` and `DirectoryRegistrationArn`. `AWS::PCAConnectorAD::TemplateGroupAccessControlEntry` now requires `GroupSecurityIdentifier` and `TemplateArn`.

### Removed L1 Id attributes

**Batch:** `2025-07`

The `Id` attribute was removed from `aws_ec2.CfnTrafficMirrorFilterRule`, `aws_kinesis.StreamConsumer`, and `aws_neptune.DBInstance`.

### Removed L1 Id attributes

**Batch:** `2026-03`

The generated L1 bindings removed the `Id` attributes from `AWS::CodeDeploy::DeploymentGroup` and `AWS::SSM::MaintenanceWindow`.

### Required VPC Lattice L1 properties

**Batch:** `2025-05`

Experimental VPC Lattice L1 bindings now require `name` and `resourceConfigurationType` in `CfnResourceConfigurationProps`, plus `name`, `subnetIds`, and `vpcIdentifier` in `CfnResourceGatewayProps`.

### Security Hub and SSM L1 removals

**Batch:** `2026-01`

The Security Hub `ConnectorV2` L1 removed several Jira Cloud and ServiceNow provider attributes and replaced the `JiraCloud` and `ServiceNow` types with `JiraCloudProviderConfiguration` and `ServiceNowProviderConfiguration`; `AWS::SSM::MaintenanceWindowTarget` also lost its `Id` attribute.

## Generated resource interfaces and helpers

### Construct-valued L1 relationships

**Batch:** `2025-11`

Generated L1 constructs can accept construct objects as parameters for known resource relationships.

### Generated L1 type guards

**Batch:** `2025-12`

Every generated L1 construct now has a static `isCfn<ResourceName>` helper for testing whether a value is that resource type.

```ts
if (s3.CfnBucket.isCfnBucket(value)) {
  // value is a CfnBucket
}
```

### Generated resource interoperability

**Batch:** `2025-09`

Every generated L1 now provides `from<Resource>Arn` and `from<Resource><Prop>` import factories. New resource interfaces are shared by L1 and L2 constructs.

### Narrower resource-reference types

**Batch:** `2026-01`

Several exposed values now use reference interfaces: `JobQueue.computeEnvironments[].computeEnvironment` uses `IComputeEnvironmentRef`, `BackupPlanRule.props.backupVault` uses `IBackupVaultRef`, `EventDestination.bus` uses `IEventBusRef`, and log-group results use `ILogGroupRef`; `ApiDestination.fromApiDestinationAttributes()` now returns `IApiDestination`. Code that needs members from the richer L2 interfaces must type-test or cast these values.
