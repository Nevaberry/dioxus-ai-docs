# Platform and compute integrations

## Kubernetes and Helm

### Owner references and proxy heartbeat (since 1.11.0)

The Kubernetes executor's `enable_owner_references` option ties step jobs and
pods to the run pod so Kubernetes can garbage-collect them.
`DAGSTER_GRPC_PROXY_HEARTBEAT_TTL_SECONDS` changes the proxy gRPC heartbeat TTL
from its 30-second default.

### Chart and Service controls (since 1.12.0)

- The Dagster Helm chart supports image digests and a `concurrency` setting
  for pools.
- Dagster and Dagster+ agent charts accept `k8sApiCaBundlePath` for a custom
  Kubernetes API CA.
- Code-location Services accept arbitrary Kubernetes Service overrides through
  `service_spec_config`.
- The supported Kubernetes dependency range includes 35.x.

### Launched runs and replicated code servers (since 1.13.0)

When `includeConfigInLaunchedRuns.enabled` is set, launched run pods inherit
`nodeSelector`, `tolerations`, and `podSecurityContext` from the user
deployment.

User-code deployments accept `replicaCount`. Replicas share a stable gRPC
server ID, and `code_server.*` metrics distinguish the responding process with
`server_instance_id`.

## ECS

### Per-run container overrides (since 1.12.0)

Jobs and launchpad runs launched by `EcsRunLauncher` can carry the
`ecs/container_overrides` tag for container settings such as GPU requirements.

### Repository credentials (since 1.13.0)

`EcsUserCodeLauncher.repository_credentials` configures ECR credentials at
agent or deployment scope, rather than requiring per-code-location settings.

### Transient capacity failures (since 1.13.0)

ECS stops reporting `InsufficientFreeAddressesInSubnet` or "Task provisioning
failed" are classified as transient. Dagster retries the run rather than
marking it permanently failed.

## Azure and cloud identity

### Azure compute and storage Components (since 1.12.0)

Dagster Pipes includes `PipesAzureMLClient` and Azure Blob Storage support.
AWS, Azure, and GCP also provide declarative resource Components.

### Sovereign Azure endpoints (since 1.13.0)

ADLS2 and Blob Storage utilities, resources, Components, and compute logging
accept `endpoint_suffix` for sovereign clouds. The corresponding compute-log
Helm setting is `endpointSuffix`.

### Workload identity federation (since 1.13.0)

PostgreSQL accepts `auth_provider="azure_wif"`, `"gcp_wif"`, or
`"aws_wif"`, with matching optional extras. The Helm switch is
`global.postgresqlAuthWifEnabled`.

`DatabricksClientResource.credentials_strategy` accepts the Databricks SDK
`CredentialsStrategy` protocol for federated or custom authentication.

## Dagster Pipes

### Concurrent message streams (since 1.13.0)

The preview `PipesCompositeMessageReader` handles multiple concurrent message
streams in one Pipes session.

`PipesK8sClient.run(delete_pod_on_completion=False)` retains its pod after
completion. `PipesEMRServerlessClient.dashboard_refresh_interval` controls
Spark-dashboard refreshes and now has a longer default so UI URLs remain valid
during runs.

## Collaboration and platform APIs

### Microsoft Teams and PowerAutomate (since 1.10.0)

`dagster-msteams` can send Adaptive Card-formatted messages to PowerAutomate
flows.

### SCIM group-member filter (since 1.13.0)

Dagster+ SCIM Groups queries support the `members.value eq` filter.

## Notebook and Airflow compatibility

### Dagstermill (since 1.13.0)

`dagstermill` requires `papermill>=2.0.0`. Its default Jupyter kernel startup
timeout increased from 60 to 120 seconds.

### Airlift (since 1.13.0)

`dagster-airlift` supports Python 3.12, 3.13, and 3.14.
