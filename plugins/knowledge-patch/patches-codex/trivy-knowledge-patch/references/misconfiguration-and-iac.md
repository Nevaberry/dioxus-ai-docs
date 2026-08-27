# Misconfiguration and Infrastructure as Code

## Check metadata and policy integration

### Metadata fields

Check metadata accepts an `examples` field (since 0.59.0) and a `Minimum Trivy
Version` field (since 0.63.0). Boolean-valued metadata is interpreted as a
boolean rather than a string (since 0.68.0).

### Provider mapping identifiers

Provider mappings use `ID` instead of `AVDID` (since 0.69.0). This is a
breaking change: update custom mappings, decoders, and tests that access the old
identifier.

```yaml
# Old
AVDID: <check-id>

# Current
ID: <check-id>
```

### Rego integration

The IaC scanner can receive a Rego scanner through an option (since 0.62.0).
Misconfiguration analysis exports raw Terraform data to Rego policies (since
0.63.0). Rego can ignore findings by type, and callers can configure a Rego
error limit (since 0.68.0). Diagnostic snippets for manifests include map keys.

## Ignore behavior

### Inline and chart-aware ignores

Inline-comment ignores are supported in Dockerfile and Helm scans (since
0.59.0). When a Helm chart is in a subdirectory, ignore rules respect its chart
path (since 0.66.0).

### IDs, aliases, and expressions

Ignore-rule identifiers are matched case-insensitively (since 0.71.0).
`.trivyignore` filtering resolves check aliases, so ignoring an alias suppresses
the associated check (since 0.70.0). An expression used as an ignore marker
must evaluate to a value that is both known and non-null (since 0.68.0).

## Terraform and OpenTofu

### File and module discovery

OpenTofu-specific file extensions are discovered as scan inputs (since
0.64.0), and OpenTofu files participate in module detection (since 0.67.0).
OpenTofu `language` blocks are supported (since 0.74.0).

The Terraform parser accepts a current-working-directory option (since
0.63.0). Nested documents are loaded from subdirectories rather than skipped
(since 0.61.0), and parser options apply to submodules as well as the root
module (since 0.60.0).

### Evaluation context and references

Evaluation assigns the correct context to module instances and multiple block
instances. HCL object expressions return their references (since 0.62.0).
Missing variables become unknown values rather than concrete placeholders, and
null nodes are removed while parsing JSON manifests.

Before a dynamic block expands, analysis tests whether its `for_each` value is
known (since 0.63.0). A known `for_each` map expands to one resource per key
(since 0.65.0).

### Cached remote modules

Terraform plan scans use remote modules cached under `.terraform`. When a
remote submodule is loaded from the cache, its original path is preserved
(since 0.66.0).

### Plans and schema recovery

Terraform plan configuration can partially restore resource schema information
(since 0.69.0). Nested list values in plans render correctly, and resources
without `after` changes are skipped (since 0.71.0).

### Policy templates and filesystem functions

Terraform policy templates support partial evaluation (since 0.64.0).
Terraform filesystem functions prevent path traversal during evaluation (since
0.71.0).

### Language constructs

The schema recognizes `ephemeral` block types (since 0.61.0) and Terraform
`action` blocks (since 0.69.0).

## AWS and CloudFormation

### Terraform AWS resources

Resource adaptation covers `aws_default_security_group` and
`aws_opensearch_domain`, and analysis supports `aws_ami` (since 0.61.0).

### Managed policy documents

AWS managed policies are converted into documents so policy checks can
evaluate them (since 0.62.0).

### CloudFormation resources and intrinsics

Adapters cover `AWS::DynamoDB::Table` and `AWS::EC2::VPC`, while
`AWS::EKS::Cluster.ResourcesVpcConfig` receives its defaults (since 0.61.0).

`Fn::FindInMap` supports default values and list-valued results (since 0.67.0).
`Fn::ForEach` is supported (since 0.69.0). `AWS::EC2::Instance`
`MetadataOptions` are propagated to checks (since 0.71.0).

### ECS and CloudFront

ECS definitions recognize the enhanced Container Insights setting (since
0.60.0). Check `AVD-AWS-0010` supports CloudFront standard logging v2 (since
0.72.0).

## Azure

### Document and schema handling

Azure `CreateUiDefinition` documents are excluded from misconfiguration scans
(since 0.61.0). Azure schemas cover agent pools, role assignments, and storage
account `https_traffic_only_enabled`, with broader App Service, Compute,
Container, Network, Storage, and Security Center coverage (since 0.68.0).

Analysis recognizes ARM resources expressed as objects,
`azurerm_*_web_app` resources, and expanded Azure Database schemas (since
0.69.0).

### Resource relationships

Analysis adapts Azure Resource Manager Kubernetes clusters, resolves resources
through `resource_id`, and supports
`azurerm_network_interface_security_group_association` (since 0.70.0).

### Flexible-server parameters

Azure flexible-server parameters are parsed under their individual names so
values remain available at the expected schema fields (since 0.74.0).

## Google Cloud

### GKE defaults

Terraform `google_container_cluster` supports `auto_provisioning_defaults`
(since 0.62.0).

### Networking and storage attributes

Analysis exposes private IP Google access on subnetworks and logging and
versioning on storage buckets (since 0.65.0). The bucket logging field is
`log_bucket`, not `target_bucket` (since 0.66.0).

## Kubernetes and Helm

### Kubernetes resources

Kubernetes scans collect components from namespaced resources (since 0.63.0).
JSON manifest parsing filters null nodes (since 0.62.0).

### Helm chart discovery and deployment

Chart detection uses the chart file's exact filename rather than a loose name
match (since 0.61.0). `.yml` files are included when a Helm chart is detected
(since 0.69.0). The Helm deployment accepts `sslCertDir` for an SSL certificate
directory (since 0.69.0).

## Dockerfile and image configuration

Dockerfile parsing tolerates unsupported experimental flags and maps the
health-check start-period option to `--start-period` (since 0.68.0).

Image-history parsing normalizes Buildah and legacy Docker `CreatedBy` values
(since 0.64.0), removes build-metadata suffixes, and quotes legacy `ENV` values
to preserve spaces (since 0.67.0). When determining the effective image user,
`.Config.User` always overrides `USER` entries from `.History` (since 0.64.0).

## Other IaC inputs

### JSON with comments

JSON input accepts comments and trailing commas (JSONC, since 0.63.0):

```jsonc
{
  // accepted
  "enabled": true,
}
```

### Ansible

Trivy has initial support for scanning Ansible content for
misconfigurations (since 0.69.0).

### GitHub repository settings

Misconfiguration analysis supports the
`github_repository_vulnerability_alerts` resource (since 0.72.0).

## Finding explanations and audit data

Terraform findings render their causes in reports (since 0.60.0).
Misconfiguration analysis supports an `audit` configuration attribute (since
0.66.0).
