# Delivery, assets, and pipelines

Use this reference for delivery, assets, and pipelines compatibility details. Entries are grouped by task and service, with their source batch shown inline.

## CodeBuild

### Attribute-based CodeBuild fleets

**Batch:** `2025-02`

CodeBuild Fleet constructs support attribute-based compute types.

### CodeBuild fleet configuration

**Batch:** `2025-10`

CodeBuild Fleets support custom instance types, VPC configuration, and overflow behavior.

### CodeBuild macOS 15 runners

**Batch:** `2025-12`

CodeBuild constructs support macOS 15 runners.

### CodeBuild macOS 26 runners

**Batch:** `2026-03`

CodeBuild constructs support macOS 26 runners.

### Pipeline CodeBuild configuration propagation

**Batch:** `2025-12`

CDK Pipelines now propagates CodeBuild `fleet` and `certificate` settings instead of dropping them from the generated projects.

### Remote Docker servers

**Batch:** `2025-09`

CodeBuild supports remote Docker servers, and pipelines' `CodeBuildFactory` can use Docker-server support.

### Shared CodeBuild caches

**Batch:** `2025-07`

CodeBuild project constructs support cache sharing.

### Windows Server Core 2022 build images

**Batch:** `2025-08`

CodeBuild supports Windows Server Core 2022 images with on-demand capacity.

## CodePipeline and CDK Pipelines

### CodePipeline commands action

**Batch:** `2025-02`

CodePipeline actions can run commands directly through a commands action.

### CodePipeline Git-push filters

**Batch:** `2025-03`

CodePipeline L2 Git-push filters support branch and file criteria.

### CodePipeline stage conditions

**Batch:** `2025-03`

CodePipeline L2 constructs support stage-level conditions.

### CodePipeline V2 in pipelines

**Batch:** `2025-04`

The pipelines L3 construct supports the `V2` pipeline type.

### Combined CodePipeline trigger filters

**Batch:** `2025-05`

CodePipeline configurations can use both `pullRequestFilter` and `pushFilter`.

### Configurable cdk-assets version

**Batch:** `2025-07`

CDK Pipelines can configure the `cdk-assets` version.

### EC2 deployment actions

**Batch:** `2025-06`

CodePipeline action constructs support native Amazon EC2 deployments.

### ECR and Inspector CodePipeline actions

**Batch:** `2025-04`

CodePipeline action constructs add ECR build-and-publish, Inspector ECR image scanning, and Inspector source-code scanning.

### Narrower pipeline-role trust

**Batch:** `2025-03`

Under `@aws-cdk/pipelines:reduceStageRoleTrustScope`, the trust policy uses the current pipeline role instead of the account root principal.

### Pipeline invoke actions

**Batch:** `2025-04`

CodePipeline action constructs support invoking a pipeline.

### Pipeline manual-approval metadata

**Batch:** `2025-06`

CDK Pipelines manual approvals can include a review URL and an SNS notification topic.

### Pipeline service roles for actions

**Batch:** `2025-04`

CodePipeline L2 adds `usePipelineRoleForActions`, and pipelines actions can default to the pipeline service role instead of creating a separate role.

## Assets, bundling, Docker, and deployment

### Amplify build compute types

**Batch:** `2025-10`

Amplify constructs support configuring the build compute type.

### Asset-bundling platform selection

**Batch:** `2025-05`

Core asset bundling now honors the configured `platform` instead of ignoring it.

### Bun lockfile behavior

**Batch:** `2025-03`

Lambda Node.js bundling no longer requires a frozen lockfile when Bun is used.

### Bundling aws-cdk-lib

**Batch:** `2026-04`

Packages can use `aws-cdk-lib` as a `bundledDependency`; the previous packaging failure was fixed.

### Custom bootstrap qualifiers in staging roles

**Batch:** `2025-08`

The app-staging synthesizer propagates a custom bootstrap qualifier into the deployment-role name.

### Docker 27.4 tarball assets

**Batch:** `2025-04`

`TarballImageAsset` supports the output format produced by Docker 27.4 and later.

### Docker build contexts for ECR assets

**Batch:** `2026-03`

ECR asset constructs support Docker build contexts.

### Docker build controls

**Batch:** `2025-09`

`DockerBuildOptions` accepts a network parameter, and `TarballImageAsset` honors `CDK_DOCKER`.

### ECR tag-mutability exclusions

**Batch:** `2025-10`

ECR repositories support exclusion filters for image-tag mutability.

### Empty S3 deployment data

**Batch:** `2025-10`

S3 Deployment's `Source.data()` accepts an empty string.

### Existing ECR repository lookup

**Batch:** `2025-03`

ECR constructs can look up an existing repository rather than requiring its attributes to be supplied manually.

### Gitignore negation in subdirectories

**Batch:** `2025-09`

Negated gitignore patterns inside subdirectories now re-include matching files.

### Go app-staging synthesizer

**Batch:** `2025-05`

The experimental `app-staging-synthesizer-alpha` package is now published for Go.

### New Bun lockfile support

**Batch:** `2025-09`

CDK recognizes the newer Bun lockfile format.

### Opt-in JSON escaping

**Batch:** `2025-04`

`Source.jsonData()` no longer escapes JSON automatically. Pass `{ escape: true }` as its third argument when special characters require the former behavior: `Source.jsonData("config.json", data, { escape: true })`.

### Refactoring exclusions

**Batch:** `2025-06`

CDK refactoring excludes `lambda.Version` and `apigateway.Deployment` resources.

### Source.jsonData list-token resolution

**Batch:** `2025-08`

S3 Deployment's `Source.jsonData()` now resolves tokens contained in lists.

### VPC-enabled bucket deployments

**Batch:** `2025-11`

S3 `BucketDeploymentProps` accepts security groups.
