---
name: gcp-knowledge-patch
description: Google Cloud Platform
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Google Cloud Platform Knowledge Patch

Use this skill to account for current Google Cloud behavior, APIs, lifecycle changes, defaults, and service availability.

Read the quick reference first. Then load only the topic reference needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [AI, ML, and agents](references/ai-ml-and-agents.md) | Gemini and partner models, Model Garden, Agent Engine, ADK, RAG, generative media, BigQuery AI and ML, evaluation, endpoint lifecycle |
| [Analytics, messaging, and BI](references/analytics-messaging-and-bi.md) | BigQuery SQL and administration, data preparation and pipelines, BigLake and Iceberg, transfers, sharing, Pub/Sub, Connected Sheets, clients |
| [Compute, networking, and edge](references/compute-networking-and-edge.md) | Compute Engine, managed instance groups, Hyperdisk, fleet extensions, regions, and infrastructure monitoring |
| [Databases and migration](references/databases-and-migration.md) | Spanner and AlloyDB integration, database transfers, migration assessment, SQL translation, and metadata movement |
| [GKE and hybrid cloud](references/gke-and-hybrid-cloud.md) | Release channels, upgrades, Autopilot, Gateway, load balancing, accelerators, storage, security, and observability |
| [Security, operations, and developer tools](references/security-operations-and-developer-tools.md) | IAM, organization policy, encryption, governance, billing, audit, quotas, MCP enablement, and API controls |
| [Serverless and application platforms](references/serverless-and-application-platforms.md) | Cloud Run services, jobs, functions, worker pools, deployments, runtimes, probes, GPUs, and service health |
| [Storage, build, and artifacts](references/storage-build-and-artifacts.md) | Cloud Storage transfers, Artifact Registry, public images, source artifacts, builders, and continuous deployment |

## Apply this patch safely

- Check the relevant reference before choosing an API, flag, runtime, model, machine type, GKE patch, IAM role, or organization-policy constraint.
- Treat GA, Preview, experimental, and temporary-disablement labels as part of the contract.
- When a feature has several lifecycle entries, apply the newest status while preserving any migration requirement.
- Keep region, runtime, GatewayClass, and GKE-build gates in generated configuration.
- Verify quotas, organization policies, service-agent permissions, and release-channel effects before production changes.
- Prefer explicit service accounts and least-privilege, resource-scoped roles.
- Do not infer feature availability from a similarly named service or earlier Preview.
- Recheck temporary exceptions immediately before depending on them.

## Breaking changes and required migrations

### Cloud Run deployment and integrations

- Give the deploying principal explicit read access to every referenced container image.
- For Artifact Registry, grant `roles/artifactregistry.reader` on the repository or image project.
- For source deployments that use the Compute Engine default service account, grant `roles/run.builder` when that role is required.
- Cloud Run integrations are discontinued in the console and CLI.
- Configure connected products through their own product surfaces.
- Existing integration-backed services continue to work.
- Use Google Cloud SDK 511.0.0 or later for Cloud Run functions and automatic base-image update workflows.
- Public GitHub Container Registry images can be imported directly at GA.

### BigQuery client and workflow migrations

- Do not pin `google-cloud-bigquery` 3.28.0; it was yanked for incompatibility with `pandas-gbq`.
- Audit code before adopting BigQuery DataFrames 2.0 because it has breaking API changes.
- Partial ordering mode is GA and can generate more efficient queries.
- BigQuery workflows enforce strict act-as mode project-wide.
- Use a custom service account for each Dataform repository, notebook, pipeline, and data preparation.
- Grant `roles/iam.serviceAccountUser` to the default Dataform service agent and relevant principals where automatic releases would otherwise fail.
- The Node.js BigQuery client 8.0.0 requires Node.js 18 or later.
- BigQuery Python client 3.31.0 no longer supports Python 3.7 or 3.8.

### Pub/Sub client migrations

- Replace the message-transform `enabled` field with `disabled` in Go 1.48.0, Java 1.138.0, and Python 2.29.0 or later.
- For Pub/Sub Go v2, migrate to the renamed generated admin clients.
- Do not assume `acknowledge_confirmation` or `modify_ack_deadline_confirmation` is populated.
- Review subscriber shutdown controls before changing streaming-pull behavior.

### Agent and model migrations

- Migrate Agent Engine Python code to the client-based `agent_engines` design introduced by Vertex AI SDK for Python 1.112.0.
- Gemini 2.5 Pro, Flash, and Flash-Lite retire on October 16, 2026.
- Vertex AI Extensions shuts down after November 26, 2026; migrate to Agent Platform.
- Replace retired or restricted partner-model endpoints before their shutdown dates.
- Use each endpoint's stated replacement rather than assuming model aliases remain stable.

### GKE platform migrations

- Enroll no-channel clusters in a release channel before June 14, 2027.
- After removal, remaining no-channel clusters are enrolled in Stable.
- Container-Optimized OS milestone 129 and later no longer includes `kubectl` in `/usr/bin/`.
- Package or invoke `kubectl` separately.
- New Standard clusters at `1.34.1-gke.3720000` or later enable NodeLocal DNSCache by default.
- During surge upgrades, keep `maxSurge + maxUnavailable` at or below 100.

### Compute Engine encryption migration

- Customer-supplied encryption keys for disks, snapshots, images, and machine images are deprecated.
- Migrate those resources before customer-supplied encryption keys are disabled on July 20, 2027.
- Do not require `iam.serviceAccounts.actAs` for the boot-disk operations from which that permission was removed.

## Current availability exceptions

- Combined semantic and lexical `VECTOR_SEARCH` hybrid search is temporarily disabled.
- Do not depend on configurable daily token quotas for BigQuery generative AI functions while configuration support is disabled.
- Facebook Ads transfers continue to run but currently omit `AdInsightsMMM`.
- `AI.KEY_DRIVERS` is available again in Preview after its temporary suspension.
- `AI.AGG` is available again in Preview.
- BigQuery table parameters in table-valued functions are restored.
- Legacy SQL may be unavailable for new workloads in projects without qualifying prior use.
- Treat direct dataset creation for conversational analytics as Preview even though conversational analytics is GA.

## Cloud Run quick reference

### Source and configuration

- Use `pyproject.toml` for dependency management in supported Python source deployments.
- Services, jobs, and worker pools can load multiple environment variables from a `.env` file in Preview.
- Direct source artifacts, Ubuntu 24 builders, and the OS-only runtime have distinct deployment paths.
- ADK entrypoint detection in the Python buildpack is GA.
- Go runtime support dates align more closely with the community cycle beginning with Go 1.26.

### Compute and execution models

- GPU support for Cloud Run services is GA.
- Jobs and worker pools have separate GPU availability, machine, region, and driver constraints.
- NVIDIA L4 workloads can use driver version `580.x.x`.
- Use worker pools for non-request workloads and verify their networking, volume, GPU, and scaling gates.
- Multi-container sidecars in Cloud Run jobs are GA.
- Cloud Run sandboxes are Preview for isolated execution of untrusted or agent-generated code.
- Preview ephemeral disks persist only for the lifetime of an instance.

### Networking, health, and scaling

- Direct VPC egress supports IPv4 and internal IPv6 through dual-stack subnets in Preview.
- External IPv6 and Private NAT each have their own availability and configuration requirements.
- HTTP and gRPC readiness probes are GA.
- Service health can automate failover and failback for highly available multi-region services.
- Distinguish service-level maximum instances, manual scaling, scaling targets, and multi-region behavior.
- Direct VPC egress address consumption and memory metrics have changed; use the current semantics from the serverless reference.

## BigQuery quick reference

### SQL and runtimes

- The advanced runtime is the default for every project.
- Set a global default location when requests omit a location and BigQuery cannot infer one.
- Preview global queries can reference data stored in multiple regions.
- Python UDFs, JavaScript aggregate UDFs, and SQL aggregate UDFs are GA.
- Pipe syntax is GA and supports linear operators including `WITH`, named windows, and `DISTINCT`.
- Name-based set operations align columns without positional coupling.

```sql
SELECT 1 AS id, 'a' AS label
UNION ALL BY NAME
SELECT 'b' AS label, 2 AS id;
```

- External-data date/time formats, `null_markers`, `source_column_match`, and `time_zone` are GA.
- Multi-level aggregation is Preview.

### Data preparation and pipelines

- Data preparation is GA and includes visual pipelines plus Dataform scheduling.
- Later Preview additions cover JSON flattening, array unnesting, external files, and runs using user credentials.
- Trigger-based scheduling can run a pipeline when selected BigQuery tables change.
- Apply strict act-as rules to scheduled preparations, notebooks, Dataform workflows, and pipelines.
- Read the analytics reference for SQLX defaults, selective runs, code-asset folders, destinations, and user-credential access.
- Dataform-managed BigLake Iceberg tables and transaction behavior have separate lifecycle gates.

### AI, search, and conversational analytics

- Managed functions `AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` apply natural-language criteria to text or multimodal data.
- GA BigQuery AI functions accept `ObjectRef` directly; do not call `OBJ.GET_ACCESS_URL` first unless another interface requires it.
- Autonomous embedding generation is GA for new and existing tables.
- BigQuery maintains the embedding column as source data changes.
- Conversational analytics is GA with model-stage selection, thinking mode, clarifying questions, citations, and verified-query parameters.
- Direct dataset conversation creation remains Preview.
- Check the current exceptions before generating hybrid-search or daily-token-quota configuration.

### Reservations and billing

- Fluid scaling bills autoscaling reservations per second without a minimum duration.
- Reservation groups are GA.
- Identity-based routing can assign queries by executing principal.
- On August 11, 2026, billing integrations must accept both uppercase and lowercase Data Transfer Service feature labels.
- The lowercase label also covers orchestration, load, and merge costs.
- BigQuery may re-execute side-effect-free instructions for regression detection under a system audit identity.

## GKE quick reference

### Upgrade and storage safeguards

- Release-channel maintenance exclusions can be scoped per node pool.
- The default **No upgrades** exclusion can last up to 90 days.
- Consult the GKE reference before choosing a channel target because creation defaults and auto-upgrade targets change frequently.
- For Cloud Storage FUSE startup mount failures, upgrade to at least `1.34.8-gke.1218000`, `1.35.3-gke.2347000`, or `1.36.0-gke.1266000` on the matching branch.
- If an immediate upgrade is impossible, gate the sidecar with an init container that waits for metadata-service availability.
- Check separate fixed versions for streaming-write failures and incomplete reads on 64 KiB ARM64 nodes.
- Dedicated clusters require the Cloud Storage FUSE `custom-endpoint` option.

### Gateway security and networking

- Frontend mTLS validates client certificates at the Gateway.
- Backend authenticated TLS secures Gateway-to-Pod or Gateway-to-InferencePool traffic.
- Backend mTLS additionally presents a load-balancer client certificate through `spec.tls.backend.clientCertificateRef`.
- The documented mTLS features support `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, and `gke-l7-rilb`.
- GKE 1.36 changes the internal load-balancer default; read the exact gate before generating a Service.
- Use the `L4LBConfig` CRD only at its documented GKE version gate.

### Compute, security, and observability

- Accelerator and machine families are gated by cluster mode, GKE build, and sometimes confidentiality settings.
- Confidential Autopilot settings support cluster-level AMD SEV-SNP and Intel TDX enablement.
- Managed OpenTelemetry, Pressure Stall Information, VPA decision logs, and JobSet metrics have separate version and availability gates.
- Workload Identity can see transient metadata-server failures immediately after node startup on GKE 1.35 and later.
- Privileged Autopilot allowlists and security-bulletin fixes must be applied at their exact documented versions.

## IAM, policy, and developer tooling

- Enabling BigQuery or GKE after March 17, 2026 automatically enables that product's MCP server.
- Do not use `gcp.managed.allowedMCPServices` to control MCP after that migration.
- Use IAM deny policies instead.
- Apply resource-specific BigQuery dataset, routine, sharing, reservation, and organization-policy controls.
- Do not assume older role bundles include newer permissions.
- Treat row-level access, data policies, masking, CMEK, jurisdiction, and Access Transparency as separate resource-scoped controls.
- Verify the Dataform service-agent and principal grants required by strict act-as.
- Use the security reference before changing API enablement, billing attribution, or quota controls.

## Where to look next

- Read [AI, ML, and agents](references/ai-ml-and-agents.md) before selecting a model, media endpoint, embedding, evaluation API, or agent runtime.
- Read [Analytics, messaging, and BI](references/analytics-messaging-and-bi.md) before writing BigQuery SQL, pipeline configuration, Pub/Sub code, or lakehouse DDL.
- Read [GKE and hybrid cloud](references/gke-and-hybrid-cloud.md) before choosing a GKE version, channel, machine type, Gateway policy, or storage workaround.
- Read [Serverless and application platforms](references/serverless-and-application-platforms.md) before generating Cloud Run deployment commands or service, job, function, and worker-pool configuration.
- Read [Security, operations, and developer tools](references/security-operations-and-developer-tools.md) before changing IAM, organization policy, encryption, billing, or API enablement.
- Read [Databases and migration](references/databases-and-migration.md) before assessing or translating a source database or configuring reverse ETL.
- Read [Compute, networking, and edge](references/compute-networking-and-edge.md) before changing instance-group repair, disk encryption, Hyperdisk, or fleet-extension policy.
- Read [Storage, build, and artifacts](references/storage-build-and-artifacts.md) before selecting source-artifact, image-import, builder, or continuous-deployment behavior.
