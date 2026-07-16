# Security, Operations, and Developer Tools

Use this reference for IAM, organization policy, encryption, data governance, billing and audit behavior, developer tooling, and API controls.

## Contents

- [Access control, identity, and organization policy](#access-control-identity-and-organization-policy)
- [Encryption, governance, and jurisdiction](#encryption-governance-and-jurisdiction)
- [Operations, billing, audit, and quotas](#operations-billing-audit-and-quotas)
- [Developer tools and API surfaces](#developer-tools-and-api-surfaces)

## Access control, identity, and organization policy

### Agent Engine Access Transparency (2025-10)

Access Transparency is available for Vertex AI Agent Engine.

### Agent Engine identity and enterprise controls (2025-08)

Agent Engine can use a custom service account as the agent identity. It also supports private-VPC deployment through a Private Service Connect interface, CMEK, configurable instance bounds, per-container resource limits and concurrency, and HIPAA workloads.

### BigQuery custom constraints on additional resources (2026-04)

Preview custom organization policies can allow or deny specific operations on BigQuery tables, data policies, and row access policies.

### BigQuery custom organization constraints (2025-05)

Preview custom Organization Policy constraints can restrict supported fields on BigQuery resources.

### BigQuery data preparation lifecycle and IAM (2025-04)

BigQuery data preparation is GA, including visual pipelines and Dataform scheduling. Its required permissions can be granted through `roles/bigquery.studioUser` and `roles/cloudaicompanion.user`, plus access to the prepared data; `roles/bigquery.dataEditor` and `roles/serviceusage.serviceUsageConsumer` are no longer required.

### BigQuery Data Transfer defaults and IAM (2025-10)

`bigquerydatatransfer.googleapis.com` is enabled by default for new projects. Starting March 17, 2026, creating or updating a transfer configuration requires `bigquery.datasets.getIamPolicy` and `bigquery.datasets.setIamPolicy` on its target dataset.

### BigQuery IAM tags in SQL (2025-06)

At GA, SQL can manage IAM tags on BigQuery datasets and tables.

### BigQuery policy controls reach GA (2026-06)

Custom Organization Policy constraints on supported BigQuery sharing data-exchange and listing fields, and IAM deny policies for BigQuery resources, are GA.

### Cloud Run deployment IAM (2025-01)

Creating or updating a Cloud Run resource now requires the acting user or service account to have explicit access to every referenced container image; for Artifact Registry, grant the deploying principal `roles/artifactregistry.reader` on the image project or repository. For source deployments, grant the Preview `roles/run.builder` role to the Compute Engine default service account that builds the service or function.

### Conditional Cloud Run invocation (2025-06)

Cloud Run invocation IAM Conditions can use the request host and request path when defining access to a service.

### Conditional dataset IAM (2025-01)

BigQuery dataset ACLs support conditional IAM access at GA, and Java client 2.46.0 can configure IAM conditions on datasets.

### Custom constraints for BigQuery sharing (2025-10)

Preview custom Organization Policy constraints can restrict supported fields on BigQuery sharing data exchanges and listings.

### Dataset custom constraints GA (2025-11)

Custom Organization Policy constraints on specific fields of BigQuery dataset resources are GA.

### Dataset IAM permission enforcement (2025-05)

Starting March 17, 2026, viewing dataset access controls or querying `INFORMATION_SCHEMA.OBJECT_PRIVILEGES` requires `bigquery.datasets.getIamPolicy`. Updating dataset access controls, or creating a dataset with access controls through the API, requires `bigquery.datasets.setIamPolicy`; early enforcement can be enabled before that date.

### Direct Identity-Aware Proxy for Cloud Run (2026-03)

Configuring IAP directly on a Cloud Run service, without a load balancer, is GA.

### Extended user-credential access for BigQuery workflows (2026-06)

In Preview, a data preparation running or scheduled with Google Account credentials can receive Google Drive access, while a pipeline can receive Google Drive, Bigtable, and Knowledge Catalog access.

### Gemini in BigQuery IAM roles (2025-05)

The BigQuery Studio User and BigQuery Studio Admin roles now include permissions to use Gemini in BigQuery features.

### Identity-Aware Proxy for Cloud Run (2025-04)

In Preview, IAP can secure a Cloud Run service across all ingress paths.

### Identity-based BigQuery reservation routing (2026-06)

An optional `principal` property on a reservation assignment can route queries by the executing user, service account, or third-party identity.

### Legacy SQL access restriction (2026-02)

Effective June 1, 2026, an organization or project with no Legacy SQL use from November 1, 2025 through June 1, 2026 loses Legacy SQL access. Prior users keep existing workloads, but new Legacy SQL workloads might not be allowed.

### Migration-service organization policies (2025-11)

Preview custom organization policies can allow or deny specific BigQuery migration operations, including disabling AI suggestions during a migration.

### Organization policies for BigQuery routines (2026-03)

Preview custom organization-policy constraints can allow or deny specific operations on BigQuery routines.

### Routine-level IAM (2025-05)

In Preview, IAM access controls can be applied directly to BigQuery routines.

### Row-level policy subqueries (2025-03)

GA BigQuery row-level access policies can contain subqueries and work with BigLake managed tables and the BigQuery Storage Read API.

### Salted random-hash masking (2026-01)

The `RANDOM_HASH` predefined BigQuery masking rule returns a salted hash of a column value and provides stronger protection than the standard SHA-256 masking rule.

### Shared and role-authorized stored procedures (2025-11)

In Preview, BigQuery sharing listings can include SQL stored procedures, and stored procedures can use role-based authorization.

### Strict act-as enforcement for BigQuery workflows (2026-01)

Dataform workflows, BigQuery notebooks, pipelines, and data preparations now enforce strict act-as mode project-wide, so every repository must use a custom service account instead of the default Dataform service agent. Grant `roles/iam.serviceAccountUser` to that default agent and the relevant principals or automatic releases can fail.


## Encryption, governance, and jurisdiction

### BigQuery CMEK key rotation (2025-07)

At GA, updating a table with its existing Cloud KMS key updates the table's encryption key, so key rotation does not require changing the key resource.

### Cloud KMS Autokey for Cloud Run (2025-04)

Cloud KMS with Autokey is GA for Cloud Run.

### Data policies directly on BigQuery columns (2025-07)

In Preview, data policies can be associated directly with columns for database-level access control, masking, and transformation rules.

### Dataform CMEK organization policy (2025-03)

Dataform supports the CMEK organization policy.

### Direct BigQuery column data policies reach GA (2026-02)

Associating data policies directly with BigQuery columns for access control, masking, and transformation is now GA.

### Gemini in BigQuery data jurisdiction (2026-02)

Gemini in BigQuery processes data in the same `US` or `EU` jurisdiction as the associated datasets, or in a user-selected processing location.


## Operations, billing, audit, and quotas

### Automatic BigQuery ML quota synchronization (2025-07)

BigQuery ML automatically detects Vertex AI model-quota increases and adjusts quotas for BigQuery ML functions that use those models, removing the previous email-based increase process.

### BigQuery daily token quotas temporarily unavailable (2026-06)

Daily token quotas for controlling generative AI function costs were announced at GA on June 8, but support for configuring them was temporarily disabled on June 15.

### BigQuery Data Transfer billing label migration (2026-05)

On August 11, 2026, the billing label changes from `goog-bq-feature-type: DATA_TRANSFER_SERVICE` to `goog-bq-feature-type: data_transfer_service` and expands to orchestration, load, and merge costs. Billing exports, dashboards, and reporting queries should accept both labels during the transition.

### BigQuery Migration Service billing-account requirement (2026-06)

New users have required a Cloud Billing account for BigQuery Migration Service since March 9, 2026, and all users have required one since May 18, even though the service remains without charge.

### BigQuery regression re-execution audit identity (2026-05)

BigQuery can re-execute side-effect-free instructions at no cost or resource consumption to detect regressions. Data Access logs can identify these executions as `bigquery-adminbot@system.gserviceaccount.com`.


## Developer tools and API surfaces

### Automatic MCP enablement and policy migration (2026-02)

After March 17, 2026, enabling BigQuery or GKE automatically enables that product’s MCP server. The `gcp.managed.allowedMCPServices` organization-policy constraint no longer controls MCP use after that date; use IAM deny policies instead.

### Cloud API Registry (2025-12)

Preview Cloud API Registry in the Google Cloud console can view and manage the MCP servers and tools that an agent is allowed to access.

### Default Gemini API enablement for BigQuery (2025-07)

The `cloudaicompanion.googleapis.com` API is enabled by default for most BigQuery projects, except opted-out projects and projects linked to accounts based in EMEA regions.

### Gemini API enablement for European BigQuery projects (2026-03)

The Gemini for Google Cloud API, `cloudaicompanion.googleapis.com`, is now enabled for existing BigQuery projects in the European jurisdiction.

### Pub/Sub Go resource tags and ingestion diagnostics (2025-10)

Go Pub/Sub v2.3.0 adds tags to `Subscription`, `Topic`, and `CreateSnapshotRequest` for their corresponding create requests. It also adds `AwsKinesisFailureReason.ApiViolationReason` for Kinesis ingestion failures.
