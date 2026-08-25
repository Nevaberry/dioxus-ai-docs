---
name: gcp-knowledge-patch
description: Google Cloud Platform
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Google Cloud Platform Knowledge Patch

Use this skill to account for current Google Cloud behavior, APIs, lifecycle changes, defaults, and service availability. Read the quick reference first, then load only the topic reference needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [AI, ML, and agents](references/ai-ml-and-agents.md) | Gemini and partner models, Model Garden, Agent Engine, ADK, RAG, generative media, evaluation, and endpoint lifecycle |
| [Analytics, messaging, and BI](references/analytics-messaging-and-bi.md) | BigQuery SQL and administration, data preparation, pipelines, sharing, transfers, Pub/Sub, Connected Sheets, clients, and observability |
| [Compute, networking, and edge](references/compute-networking-and-edge.md) | Compute Engine, regions, VPC connectivity, IPv6, Private NAT, managed instance groups, Hyperdisk, and VM fleet management |
| [Databases and migration](references/databases-and-migration.md) | Spanner and AlloyDB integration, federation, CDC, database transfers, migration assessment, and SQL translation |
| [GKE and hybrid cloud](references/gke-and-hybrid-cloud.md) | Release channels, upgrades, Autopilot, Gateway, load balancing, accelerators, storage, security, and observability |
| [Security, operations, and developer tools](references/security-operations-and-developer-tools.md) | IAM, organization policy, encryption, governance, billing, quotas, diagnostics, and API controls |
| [Serverless and application platforms](references/serverless-and-application-platforms.md) | Cloud Run services, jobs, functions, worker pools, deployment, runtimes, probes, GPUs, scaling, and service health |
| [Storage, build, and artifacts](references/storage-build-and-artifacts.md) | Cloud Storage transfers, Artifact Registry, source artifacts, Lakehouse storage, Iceberg, and catalogs |

## Apply this patch safely

- Check the relevant reference before choosing an API, flag, runtime, model, machine type, GKE patch, IAM role, or endpoint.
- Treat GA, Preview, experimental, and temporary-disablement labels as part of the contract.
- Apply the latest lifecycle status while retaining earlier migration requirements and deadlines.
- Keep region, runtime, GatewayClass, and GKE-version gates in generated configuration.
- Verify quotas, organization policies, service-agent permissions, data jurisdiction, and release-channel effects before production changes.
- Prefer current product names in prose, but preserve API, CLI, client-library, and IAM identifiers where renames do not change them.

## Breaking changes and required migrations

### Cloud Run deployment and integrations

- Give the deploying principal explicit read access to every referenced container image. For Artifact Registry, grant `roles/artifactregistry.reader` on the repository or image project.
- For source deployments, ensure the Compute Engine default service account performing the build has `roles/run.builder` where that Preview role is required.
- Do not design around Cloud Run integrations in the console or CLI; they are discontinued. Configure connected products through their own product surfaces.
- Use Google Cloud SDK 511.0.0 or later when deploying Cloud Run functions or configuring automatic base-image updates.
- Use `pyproject.toml` for supported Python source deployments; later Python buildpacks default to `uv`, with `GOOGLE_PYTHON_PACKAGE_MANAGER=pip` available when pip is required.
- Treat direct source artifacts, Ubuntu 24 builders, OS-only runtimes, and framework or ADK entrypoint detection as separate deployment modes with their documented availability.

### BigQuery client and workflow migrations

- Do not pin `google-cloud-bigquery` 3.28.0 or 3.32.0; both releases were yanked.
- BigQuery DataFrames 2.0 includes breaking API changes; audit code before adopting it.
- BigQuery workflows enforce strict act-as mode project-wide. Use a custom service account for every Dataform repository, notebook, pipeline, and data preparation.
- Grant `roles/iam.serviceAccountUser` to the default Dataform service agent and relevant principals when strict act-as releases would otherwise fail.
- Requests requiring Legacy SQL must select it explicitly; new Legacy SQL workloads can be unavailable where there was no qualifying prior use.
- Accept both `goog-bq-feature-type: DATA_TRANSFER_SERVICE` and `goog-bq-feature-type: data_transfer_service` during the billing-label transition.

### Pub/Sub clients

- Replace the message-transform `enabled` field with `disabled` in Go 1.48.0, Java 1.138.0, and Python 2.29.0 or later.
- For Pub/Sub Go v2, migrate to the renamed generated admin clients.
- Do not assume `acknowledge_confirmation` or `modify_ack_deadline_confirmation` is populated.
- Account for subscriber shutdown controls, protocol-version changes, and the Java 1.144.1 rollback of keepalive behavior when upgrading clients.
- Avoid the Alpha Go v2 line for production until a production-ready release is selected.

### AI and model endpoints

- Migrate retired and discontinued Imagen, Veo, Gemini, Claude, Mistral, Codestral, MedLM, and LearnLM endpoints before their recorded deadlines.
- Migrate Gemini 2.5 Pro, Flash, and Flash-Lite workloads before their October 16, 2026 retirement.
- Migrate Vertex AI Extensions to Agent Platform before shutdown after November 26, 2026.
- Migrate Agent Engine Python code to the client-based `agent_engines` design introduced by Vertex AI SDK for Python 1.112.0.
- Treat model availability, context limits, Provisioned Throughput, region support, and GA or Preview endpoint IDs as model-specific.

### GKE platform changes

- Enroll no-channel clusters in a release channel before June 14, 2027. Remaining no-channel clusters are enrolled in Stable after removal.
- Do not assume `kubectl` exists at `/usr/bin/` on Container-Optimized OS milestone 129 or later.
- New Standard clusters at `1.34.1-gke.3720000` or later enable NodeLocal DNSCache by default.
- During surge upgrades, keep `maxSurge + maxUnavailable` at or below 100.
- On GKE 1.36, account for CoreDNS-backed `kube-dns`, default subsetting and NEGs for new L4 internal load balancers, and GA Mutating Admission Policies.
- Validate `HealthCheckPolicy` type and health-check fields on GKE 1.34 and later.

### Compute Engine lifecycle

- Customer-supplied encryption keys for disks, snapshots, images, and machine images are deprecated and disabled on July 20, 2027; migrate affected resources first.
- `iam.serviceAccounts.actAs` is no longer required for the listed boot-disk snapshot, clone, image, replication, and instant-snapshot operations.
- Use VM Extension Manager policies for consistent fleet-wide extension installation and enforcement.

## Current availability exceptions

- Combined semantic and lexical `VECTOR_SEARCH` hybrid search is temporarily disabled.
- Configurable daily token quotas for BigQuery generative AI functions are temporarily unavailable.
- Facebook Ads transfers omit `AdInsightsMMM` while that report is paused for upstream schema changes.
- `AI.KEY_DRIVERS` and `AI.AGG` are available again in Preview after temporary interruptions.
- BigQuery table parameters in table-valued functions are restored.
- Existing Cloud Run integrations continue to work even though new console and CLI integration workflows are discontinued.

## Cloud Run quick reference

### Source, configuration, and runtimes

- Services, jobs, and worker pools can load multiple environment variables from a `.env` file in Preview.
- Cloud Run and Cloud Run functions support `pyproject.toml` dependency management across supported Python versions.
- Compose deployment is GA, direct source artifacts remain Preview, and public GitHub Container Registry images can be imported at GA.
- Review the serverless reference before selecting a runtime, builder, package manager, framework entrypoint, or automatic base-image update.

### Compute and execution models

- GPU support for services is GA; jobs and worker pools also have GPU-specific support and region or machine constraints.
- Use worker pools for non-request workloads and review Direct VPC ingress, GPU, volume, and scaling details.
- Multi-container sidecars in Cloud Run jobs are GA.
- Cloud Run sandboxes are Preview for isolated execution of untrusted or agent-generated code.
- Ephemeral disk and custom CPU or concurrency scaling targets are Preview.

### Health and networking

- HTTP and gRPC readiness probes are GA.
- Service health can fail over and fail back internal and external traffic for highly available multi-region services.
- Distinguish service-level maximum instances, manual scaling, scaling targets, and multi-region behavior.
- Direct VPC egress supports internal and external IPv6 as documented; Private NAT and VPC Flow Logs retain their availability gates.

## BigQuery quick reference

### SQL and execution

- The advanced runtime is the default for every project.
- Use a global default location when requests omit a location and BigQuery cannot infer one.
- Preview global queries can reference data stored in more than one region.
- Python UDFs, JavaScript and SQL aggregate UDFs, pipe syntax, chained function calls, and `WITH` expressions are GA.
- Name-based set operations align columns without relying on positional order.
- `MATCH_RECOGNIZE` is GA; multi-level aggregation remains Preview.
- External-data loading options for time formats, time zones, multiple null markers, and source-column matching are GA.

### Data preparation and pipelines

- Data preparation is GA, including JSON flattening, array unnesting, external files, and Gemini-assisted aggregation and deduplication.
- Trigger-based scheduling can run a pipeline when selected BigQuery tables change in Preview.
- Apply strict act-as IAM rules to scheduled preparations, notebooks, Dataform workflows, and pipelines.
- Pipelines support selective runs, default SQLX project and dataset options, and user-credential access with explicit availability limits.

### AI and search

- Managed functions `AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` apply natural-language criteria to text or multimodal data in Preview.
- BigQuery AI functions accept `ObjectRef` directly at GA.
- Autonomous embedding generation is GA for new and existing tables.
- Conversational analytics is GA with verified-query parameters, citations, clarifying questions, model-stage selection, thinking mode, and multiple AI functions.
- Direct dataset conversation creation remains Preview.
- Read the analytics reference before using TimesFM, remote models, vector indexes, hybrid search, or multimodal embeddings.

## GKE quick reference

### Upgrade and storage safeguards

- Release-channel maintenance exclusions can be scoped per node pool, and the default **No upgrades** exclusion can last up to 90 days.
- For Cloud Storage FUSE startup mount failures, upgrade to at least `1.34.8-gke.1218000`, `1.35.3-gke.2347000`, or `1.36.0-gke.1266000` on the matching branch.
- If immediate upgrade is impossible, gate the Cloud Storage FUSE sidecar with an init container that waits for metadata-service availability.
- Review the GKE reference before selecting a release-channel target; creation defaults and auto-upgrade targets change frequently.

### Gateway, security, and observability

- Frontend mTLS validates client certificates at the Gateway.
- Backend mTLS presents a load-balancer client certificate to backend Pods through `spec.tls.backend.clientCertificateRef`.
- Frontend and backend mTLS support `gke-l7-global-external-managed`, `gke-l7-regional-external-managed`, and `gke-l7-rilb`.
- Use VPA decision logs, Pressure Stall Information metrics, JobSet metrics, and Managed OpenTelemetry only at their documented GKE gates.

## IAM, policy, and developer tooling

- After March 17, 2026, enabling BigQuery or GKE automatically enables that product's MCP server.
- Do not use `gcp.managed.allowedMCPServices` to control MCP after that migration; use IAM deny policies.
- Apply resource-specific BigQuery dataset, routine, sharing, reservation, and organization-policy controls.
- Treat data policy, masking, CMEK, jurisdiction, Access Transparency, billing, and quotas as resource-specific.
- Verify required service-agent permissions and API enablement rather than assuming older role bundles cover new workflows.

## Where to look next

- Read [AI, ML, and agents](references/ai-ml-and-agents.md) before selecting a Gemini, partner, media, embedding, or agent API.
- Read [Analytics, messaging, and BI](references/analytics-messaging-and-bi.md) before writing BigQuery SQL, transfer configuration, Pub/Sub code, or lakehouse DDL.
- Read [GKE and hybrid cloud](references/gke-and-hybrid-cloud.md) before choosing a GKE version, release channel, machine type, Gateway policy, or Cloud Storage FUSE workaround.
- Read [Serverless and application platforms](references/serverless-and-application-platforms.md) before generating Cloud Run deployment commands or configuration.
- Read [Security, operations, and developer tools](references/security-operations-and-developer-tools.md) before changing IAM, organization policy, encryption, billing attribution, or API enablement.
