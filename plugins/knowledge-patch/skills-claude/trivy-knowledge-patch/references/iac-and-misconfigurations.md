# IaC and Misconfigurations

Use this reference for check metadata, ignores, Terraform and OpenTofu, Rego, CloudFormation, Kubernetes, Helm, Dockerfile/image instructions, and cloud resource schemas.

## Check metadata, results, and ignores

### Examples in check metadata (0.59.0)

Check metadata accepts an `examples` field alongside its other metadata.

### Inline misconfiguration ignores (0.59.0)

Inline-comment ignores work when scanning Dockerfiles and Helm content.

### Terraform misconfiguration causes (0.60.0)

Terraform findings render their causes in report output.

### Image-history check selection (0.60.0)

Image-history scans do not run check `AVD-DS-0007`.

### Minimum Trivy version metadata (0.63.0)

Misconfiguration content can declare `Minimum Trivy Version`.

### Misconfiguration audit attribute (0.66.0)

Misconfiguration configuration accepts an `audit` attribute.

### Chart subdirectory ignore paths (0.66.0)

Ignore rules account for a chart's path when the chart is in a subdirectory.

### Misconfiguration metadata and ignore markers (0.68.0)

Boolean check-metadata values remain booleans. A candidate ignore marker is accepted only if its value is known and non-null.

### Provider mapping identifier (0.69.0)

Provider mappings use `ID` instead of `AVDID`. Update custom mappings and consumers; this is a breaking field rename.

### Check aliases in `.trivyignore` (0.70.0)

Filtering resolves check aliases in `.trivyignore`, so ignoring an alias suppresses its corresponding check.

### Case-insensitive misconfiguration ignores (0.71.0)

Misconfiguration ignore identifiers are matched case-insensitively.

## Terraform and OpenTofu parsing

### Terraform submodule parser options (0.60.0)

Terraform parser options apply to submodules and the root module.

### Ephemeral configuration blocks (0.61.0)

The misconfiguration schema recognizes `ephemeral` block types.

### Nested document loading (0.61.0)

Misconfiguration scanning loads documents from subdirectories.

### Unknown variables in misconfiguration analysis (0.62.0)

Missing variables are represented as unknown values during evaluation.

### JSON manifest null nodes (0.62.0)

JSON manifest parsing filters null nodes.

### Terraform evaluation context and references (0.62.0)

Evaluation assigns the correct context to module instances and multiple block instances. HCL object expressions return their references.

### JSONC inputs (0.63.0)

JSON parsing accepts comments and trailing commas:

```jsonc
{
  // comment
  "enabled": true,
}
```

### Raw Terraform data in Rego (0.63.0)

Misconfiguration analysis exports raw Terraform data to Rego policies.

### Terraform parser working directory (0.63.0)

The Terraform parser accepts an explicit current working directory.

### Unknown Terraform dynamic iteration (0.63.0)

Before expanding a dynamic block, evaluation checks whether its `for_each` value is known.

### OpenTofu file extensions (0.64.0)

Input discovery recognizes OpenTofu-specific file extensions.

### Terraform policy templates (0.64.0)

Terraform misconfiguration analysis partially evaluates policy templates.

### Terraform map expansion (0.65.0)

A Terraform `for_each` map expands to one resource for every key.

### Cached remote modules in Terraform plan scans (0.66.0)

Plan scans use remote modules cached in `.terraform`. Cached remote submodules retain their original paths.

### OpenTofu module detection (0.67.0)

Module detection includes OpenTofu files.

### Expanded IaC schema coverage (0.69.0)

Analysis recognizes Terraform `action` blocks, Azure ARM resources expressed as objects, `azurerm_*_web_app` resources, and expanded Azure Database schemas. Plan analysis uses plan configuration to partially restore schema information.

### Terraform plan handling (0.71.0)

Nested values in plan lists render correctly. Resources with no `after` changes are skipped.

### Terraform filesystem-function boundaries (0.71.0)

Terraform filesystem functions prevent path traversal during evaluation.

### Docker configuration v2 migration (0.72.0)

Docker configuration moves to `dockers_v2`. Consumers of the previous representation must migrate.

### OpenTofu language blocks (0.74.0)

Misconfiguration scanning supports OpenTofu `language` blocks.

## Rego integration and diagnostics

### Rego scanner injection (0.62.0)

The IaC scanner accepts an option that supplies a Rego scanner.

### Rego finding and error controls (0.68.0)

Rego can ignore findings by type, and callers can configure the Rego error limit. Manifest diagnostic snippets include map keys.

## Kubernetes and Helm

### Kubernetes controllers and complete reports (0.61.0)

Kubernetes scanning supports controllers. A scan using `--report all` emits the complete requested report.

### Exact Helm chart identification (0.61.0)

Helm detection identifies a chart file by exact filename rather than a loose name match.

### Kubernetes artifact inputs (0.62.0)

Kubernetes scans compare artifact versions correctly and do not use the `last-applied-configuration` annotation.

### Kubernetes summary reports (0.62.0)

Kubernetes summary reports omit passed misconfigurations.

### Kubernetes namespaced components (0.63.0)

Kubernetes scans collect components from namespaced resources.

### Helm SSL certificate directory (0.69.0)

The Helm deployment accepts `sslCertDir` for an SSL certificate directory.

### Helm `.yml` files (0.69.0)

Helm chart detection includes `.yml` files as misconfiguration inputs.

## AWS and CloudFormation

### ECS enhanced Container Insights (0.60.0)

The enhanced Container Insights setting is recognized in ECS definitions.

### AWS misconfiguration resource coverage (0.61.0)

Resource adapters cover Terraform `aws_default_security_group`, `aws_opensearch_domain`, and `aws_ami`, plus CloudFormation `AWS::DynamoDB::Table`, `AWS::EC2::VPC`, and `AWS::EKS::Cluster.ResourcesVpcConfig`. The EKS VPC configuration receives default values during evaluation.

### AWS managed policy documents (0.62.0)

AWS managed policies are converted to documents and evaluated as policy documents.

### CloudFormation map lookups (0.67.0)

`Fn::FindInMap` supports default values and list-valued results.

### CloudFormation `Fn::ForEach` (0.69.0)

CloudFormation evaluation supports the `Fn::ForEach` intrinsic.

### CloudFormation instance metadata options (0.71.0)

CloudFormation analysis propagates `AWS::EC2::Instance` `MetadataOptions` to checks.

### CloudFront standard logging v2 (0.72.0)

Check `AVD-AWS-0010` supports CloudFront standard logging v2 configurations.

## Azure, GCP, and GitHub schemas

### Azure UI definition exclusion (0.61.0)

Azure `CreateUiDefinition` documents are skipped during misconfiguration scanning.

### GKE auto-provisioning defaults (0.62.0)

Terraform `google_container_cluster` analysis supports `auto_provisioning_defaults`.

### GCP misconfiguration attributes (0.65.0)

Analysis exposes private IP Google access on subnetworks and logging and versioning attributes on GCP storage buckets.

### GCP bucket logging field (0.66.0)

GCP bucket analysis uses the `log_bucket` field rather than `target_bucket`.

### Azure misconfiguration schema coverage (0.68.0)

Azure schemas include agent pools, role assignments, and storage-account `https_traffic_only_enabled`. App Service, Compute, Container, Network, Storage, and Security Center schemas are expanded for additional checks.

### Azure resource relationships (0.70.0)

Analysis adapts Azure Resource Manager Kubernetes clusters, resolves Azure resources through `resource_id`, and supports Terraform `azurerm_network_interface_security_group_association`.

### GitHub repository vulnerability alerts (0.72.0)

Misconfiguration analysis supports the `github_repository_vulnerability_alerts` resource.

### Azure flexible-server parameters (0.74.0)

Flexible-server parameters are parsed under their own names, preserving them under the expected schema fields.

## Other input formats

### Dockerfile misconfiguration parsing (0.68.0)

Dockerfile parsing tolerates unsupported experimental flags and maps the health-check start-period option to `--start-period`.

### Ansible misconfiguration scanning (0.69.0)

Trivy has initial support for scanning Ansible content for misconfigurations.
