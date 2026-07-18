---
name: gcp-knowledge-patch
description: Google Cloud Platform
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Google Cloud Platform Knowledge Patch

Use this skill to account for recent Google Cloud behavior, APIs, lifecycle changes, defaults, and service availability. Read the quick reference first, then load only the topic reference needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [AI, ML, and agents](references/ai-ml-and-agents.md) | Gemini and partner models, Model Garden, Agent Engine, ADK, RAG, generative media, BigQuery AI/ML, evaluation, endpoint lifecycle |
| [Analytics, messaging, and BI](references/analytics-messaging-and-bi.md) | BigQuery SQL and administration, data preparation and pipelines, BigLake and Iceberg, transfers, sharing, Pub/Sub, Connected Sheets, clients |
| [Compute, networking, and edge](references/compute-networking-and-edge.md) | Regions, VPC ingress and egress, IPv6, Private NAT, allowlists, and flow logs |
| [Databases and migration](references/databases-and-migration.md) | Spanner and AlloyDB integration, CDC, database transfers, migration assessment, and SQL translation |
| [GKE and hybrid cloud](references/gke-and-hybrid-cloud.md) | Release channels, upgrades, Autopilot, Gateway, load balancing, accelerators, storage, security, and observability |
| [Security, operations, and developer tools](references/security-operations-and-developer-tools.md) | IAM, organization policy, encryption, governance, billing, audit, quotas, MCP enablement, and API controls |
| [Serverless and application platforms](references/serverless-and-application-platforms.md) | Cloud Run services, jobs, functions, worker pools, deployment, runtimes, probes, GPUs, and service health |
| [Storage, build, and artifacts](references/storage-build-and-artifacts.md) | Cloud Storage transfers, Artifact Registry, source artifacts, and continuous deployment |

## Apply this patch safely

- Check the relevant reference before choosing an API, flag, runtime, model, machine type, GKE patch, or IAM role.
- Treat GA, Preview, and temporary-disablement labels as part of the contract; do not present Preview behavior as universally available.
- Where a feature has several lifecycle entries, apply the latest status while retaining earlier migration requirements.
- Keep region and version gates in generated configuration. Do not generalize a feature beyond the regions, GatewayClasses, runtimes, or GKE builds named in the reference.
- For production changes, verify quotas, organization policies, service-agent permissions, and release-channel effects before deployment.

## Breaking changes and required migrations

### Cloud Run deployment and integrations

- Give the deploying principal explicit read access to every referenced container image. For Artifact Registry, grant `roles/artifactregistry.reader` on the repository or image project.
- For source deployments, ensure the Compute Engine default service account performing the build has `roles/run.builder` where that Preview role is required.
- Do not design around Cloud Run integrations in the console or CLI; they are discontinued. Configure connected products through their own product surfaces. Existing integration-backed services continue to work.
- Use Google Cloud SDK 511.0.0 or later when deploying Cloud Run functions or configuring automatic base-image updates.

### BigQuery client and workflow migrations

- Do not pin `google-cloud-bigquery` 3.28.0; it was yanked for incompatibility with `pandas-gbq`.
- Audit code before adopting BigQuery DataFrames 2.0 because it includes breaking API changes. Partial ordering mode is GA and can produce more efficient queries.
- BigQuery workflows now enforce strict act-as mode project-wide. Use a custom service account for every Dataform repository, notebook, pipeline, and data preparation.
- Grant `roles/iam.serviceAccountUser` to the default Dataform service agent and relevant principals when strict act-as releases would otherwise fail.

### Pub/Sub and Agent Engine clients

- Replace the Pub/Sub message-transform `enabled` field with `disabled` in Go 1.48.0, Java 1.138.0, and Python 2.29.0 or later.
- For Pub/Sub Go v2, migrate to the renamed generated admin clients and do not assume `acknowledge_confirmation` or `modify_ack_deadline_confirmation` is populated.
- Migrate Agent Engine Python code to the client-based `agent_engines` design introduced by Vertex AI SDK for Python 1.112.0.

### GKE platform changes

- Enroll no-channel clusters in a release channel before June 14, 2027. After removal, remaining no-channel clusters are enrolled in Stable.
- Do not assume `kubectl` exists at `/usr/bin/` on Container-Optimized OS milestone 129 or later; package or invoke it separately.
- Account for NodeLocal DNSCache being enabled by default on new Standard clusters at `1.34.1-gke.3720000` or later.
- During surge upgrades, keep `maxSurge + maxUnavailable` at or below 100.

### Lifecycle and billing deadlines

- Migrate Gemini 2.5 Pro, Flash, and Flash-Lite workloads before their October 16, 2026 retirement.
- Migrate Vertex AI Extensions to Agent Platform before the service shuts down after November 26, 2026.
- Expect new Legacy SQL workloads to be unavailable in organizations or projects that had no qualifying Legacy SQL use by June 1, 2026.
- On August 11, 2026, accept both `goog-bq-feature-type: DATA_TRANSFER_SERVICE` and `goog-bq-feature-type: data_transfer_service` in billing exports, dashboards, and queries. The new label also covers orchestration, load, and merge costs.

## Current availability exceptions

- Do not use combined semantic and lexical `VECTOR_SEARCH` hybrid search while support remains temporarily disabled.
- Do not depend on configurable daily token quotas for BigQuery generative AI functions while configuration support remains temporarily disabled.
- Expect Facebook Ads transfers to omit `AdInsightsMMM` while that report is paused for upstream schema changes.
- `AI.KEY_DRIVERS` and `AI.AGG` are available again in Preview after their temporary interruptions.
- BigQuery table parameters in table-valued functions are restored.

## Cloud Run quick reference

### Source and configuration

- Use `pyproject.toml` for dependency management in Cloud Run and Cloud Run functions source deployments across supported Python versions.
- Services, jobs, and worker pools can load multiple environment variables from a `.env` file in Preview.
- Direct source artifacts, Ubuntu 24 builders, the OS-only runtime, and current language runtime changes are detailed in the serverless reference.

### Compute and execution models

- GPU support for Cloud Run services is GA; jobs and worker pools also have GPU-specific support and region or machine constraints.
- Use worker pools for non-request workloads; check their Direct VPC ingress, GPU, volume, and scaling details before deployment.
- Use multi-container sidecars in Cloud Run jobs at GA.
- Use Cloud Run sandboxes in Preview when an application must execute untrusted or agent-generated code in an isolated service environment.

### Health and scaling

- HTTP and gRPC readiness probes are GA for Cloud Run services.
- Cloud Run service health can automatically fail over and fail back internal and external traffic for highly available multi-region services.
- Distinguish service-level maximum instances, manual scaling, scaling targets, and multi-region behavior; each has separate semantics in the reference.

## BigQuery quick reference

### SQL and runtimes

- The advanced runtime is the default for every project.
- Use a global default location when requests omit a location and BigQuery cannot infer one. Preview global queries can reference data stored in more than one region.
- Python UDFs are GA. JavaScript and SQL user-defined aggregate functions are also GA.
- Pipe syntax is GA and supports `WITH`, named windows, and `DISTINCT` operators.

```sql
FROM `project.dataset.events`
|> DISTINCT;
```

- Name-based set operations can align columns without relying on positional order.

```sql
SELECT 1 AS id, 'a' AS label
UNION ALL BY NAME
SELECT 'b' AS label, 2 AS id;
```

### Data preparation and pipelines

- Data preparation is GA, with later additions for JSON flattening, array unnesting, external files, and development runs using user credentials.
- Use trigger-based scheduling in Preview to run a pipeline when selected BigQuery tables change.
- Apply strict act-as IAM rules to scheduled preparations, notebooks, Dataform workflows, and pipelines.
- Consult the analytics reference for repository/workspace behavior, SQLX defaults, selective runs, notebook scheduling, code-asset folders, and table destinations.

### AI and search

- Preview managed functions `AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` apply natural-language criteria to text or multimodal data.
- GA BigQuery AI functions accept `ObjectRef` directly; do not call `OBJ.GET_ACCESS_URL` first unless another interface requires it.
- Autonomous embedding generation is GA for new and existing tables; BigQuery maintains the embedding column as source data changes.
- Conversational analytics is GA with verified-query parameters, citations, clarifying questions, model-stage selection, thinking mode, and multiple AI functions. Direct dataset conversation creation remains Preview.

## GKE quick reference

### Upgrade and storage safeguards

- Release-channel maintenance exclusions can be scoped per node pool, and the default **No upgrades** exclusion can last up to 90 days.
- For Cloud Storage FUSE mount failures during startup, upgrade to at least `1.34.8-gke.1218000`, `1.35.3-gke.2347000`, or `1.36.0-gke.1266000` on the matching minor branch.
- If an immediate upgrade is impossible, gate the Cloud Storage FUSE sidecar with an init container that waits for metadata-service availability.
- Review the GKE reference before selecting a channel target; creation defaults and automatic minor-upgrade targets changed repeatedly.

### Gateway security and observability

- Frontend mTLS validates client certificates at the Gateway.
- Backend mTLS additionally presents a load-balancer client certificate to backend Pods through `spec.tls.backend.clientCertificateRef`.
- Frontend and backend mTLS support `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, and `gke-l7-rilb` GatewayClasses.
- Use Vertical Pod Autoscaler decision logs, Pressure Stall Information metrics, JobSet metrics, and Managed OpenTelemetry only at their documented GKE gates.

## IAM, policy, and developer tooling

- After March 17, 2026, enabling BigQuery or GKE automatically enables that product's MCP server.
- Do not use `gcp.managed.allowedMCPServices` to control MCP after that migration; use IAM deny policies.
- Apply the new BigQuery dataset, routine, sharing, reservation, and organization-policy controls from the security reference instead of assuming older role bundles cover them.
- Treat data-policy, masking, CMEK, jurisdiction, and Access Transparency changes as resource-specific; read their exact permission and scope requirements before generating policy.

## Where to look next

- Read [AI, ML, and agents](references/ai-ml-and-agents.md) before selecting a Gemini, partner, media, embedding, or agent API.
- Read [Analytics, messaging, and BI](references/analytics-messaging-and-bi.md) before writing BigQuery SQL, transfer configuration, Pub/Sub code, or lakehouse DDL.
- Read [GKE and hybrid cloud](references/gke-and-hybrid-cloud.md) before choosing a GKE version, release channel, machine type, Gateway policy, or Cloud Storage FUSE workaround.
- Read [Serverless and application platforms](references/serverless-and-application-platforms.md) before generating Cloud Run deployment commands or service, job, function, and worker-pool configuration.
- Read [Security, operations, and developer tools](references/security-operations-and-developer-tools.md) before changing IAM, organization policy, encryption, billing attribution, or API enablement.
