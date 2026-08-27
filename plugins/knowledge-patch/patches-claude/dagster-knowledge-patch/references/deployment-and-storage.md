# Deployment and Storage

## Database migrations and pools

The 1.12.0 database changes require two explicit compatibility checks:

- MySQL users must run `dagster instance migrate` to apply the `LongText`
  migrations for bulk-action bodies and cached asset-status data.
- `dagster-postgres` no longer installs `psycopg2-binary` transitively. Declare
  that package directly when the deployment relies on it.

For development, `dg dev` and `dagster dev` accept database-pool settings such as
`--db-pool-recycle` and `--db-pool-pre-ping` (1.12.0).

## Storage behavior

### Component state

State-backed integration Components default to `LOCAL_FILESYSTEM` storage as of
1.13.0 rather than `legacy_code_server_snapshots`. Airbyte and Fivetran are
notable users. Configure storage explicitly if deployments cannot share or
persist the new local location.

### Event logs and object keys

In 1.13.0, the SQLite event-log `busy_timeout` default increased from 5 to 30
seconds. `PickledObjectS3IOManager` uses an empty key prefix when no prefix is
supplied.

### Empty tabular writes

As of 1.13.0, the BigQuery, Snowflake, and DuckDB IO managers skip writes for
empty DataFrames and log a warning. They no longer try to create a degenerate
table from inferred types. Treat the skipped write as a distinct empty-data path
when downstream code expects a table to exist.

## Kubernetes and Helm

### Chart controls

The 1.12.0 Dagster Helm chart supports image digests and a `concurrency` setting
for pools. Dagster and Dagster+ agent charts accept `k8sApiCaBundlePath` for a
custom Kubernetes API CA. Code-location Services accept arbitrary Kubernetes
Service overrides through `service_spec_config`. The Kubernetes dependency range
includes 35.x.

### Run-pod inheritance and replicas

With `includeConfigInLaunchedRuns.enabled`, launched run pods inherit
`nodeSelector`, `tolerations`, and `podSecurityContext` from the user deployment
as of 1.13.0.

User-code deployments accept `replicaCount`. Replicas share a stable gRPC server
ID, and `code_server.*` metrics identify the responding process through
`server_instance_id` (1.13.0).

### Owner references

Since 1.11.0, the Kubernetes executor's `enable_owner_references` option can tie
step jobs and pods to the run pod so Kubernetes garbage-collects them.

## ECS

### Container overrides and repository credentials

Since 1.12.0, jobs and Launchpad runs using `EcsRunLauncher` may set the
`ecs/container_overrides` tag for container settings such as GPU requirements.

In 1.13.0, `EcsUserCodeLauncher.repository_credentials` can configure ECR
credentials at agent or deployment scope rather than only per code location.

### Transient capacity failures

Dagster 1.13.0 classifies ECS stops caused by
`InsufficientFreeAddressesInSubnet` or “Task provisioning failed” as transient.
The affected run is retried instead of being marked permanently failed.

## Authentication and cloud endpoints

### Federated database and Databricks authentication

In 1.13.0, `DatabricksClientResource.credentials_strategy` accepts the
Databricks SDK `CredentialsStrategy` protocol for federated or custom
authentication.

PostgreSQL supports `auth_provider="azure_wif"`, `"gcp_wif"`, or `"aws_wif"`
with corresponding optional extras. The Helm switch for this mode is
`global.postgresqlAuthWifEnabled`.

### Sovereign Azure

ADLS2 and Blob Storage utilities, resources, Components, and compute logging
accept `endpoint_suffix` for sovereign Azure clouds as of 1.13.0. The related
compute-log Helm value is `endpointSuffix`.

## Code-location metadata and service behavior

Runs created with a remote job origin receive the `dagster/code_location` tag
automatically since 1.12.0. Use it for filtering and concurrency controls.

`DAGSTER_GRPC_PROXY_HEARTBEAT_TTL_SECONDS` controls proxy gRPC heartbeat expiry;
the default is 30 seconds (1.11.0).

## Deployment scaffolding

The 1.12.0 `dg scaffold build-artifacts` command generates Docker and deployment
configuration for ECR, DockerHub, GHCR, ACR, or GCR. `dg scaffold github-actions`
generates Serverless- or Hybrid-aware CI, while `dg plus deploy configure`
prepares an existing project and can scaffold GitLab CI.
