# Operations and Observability

## Telemetry

### OpenTelemetry attribute changes

Since 1.93.0, LiteLLM-specific error details use the `litellm.*` namespace;
update queries that use the old keys. Streaming spans include
`gen_ai.response.time_to_first_chunk`, failed calls emit
`gen_ai.client.operation.exception`, and v2 error spans again expose `error.*`
attributes.

### OpenTelemetry service-tier attributes

Since 1.97.0, inference spans include service-tier attributes so traces can
distinguish the service tier used for a request.

## Redis coordination and resilience

### Independent coordination Redis

Since 1.93.0, coordination Redis can be configured separately from the
response cache. The usage cache can be constructed from `REDIS_*` environment
variables. The request allowlist under `general_settings` is applied to
LiteLLM globals.

### Redis circuit breaker defaults

The Redis circuit breaker is on by default. It opens after five consecutive
failures and attempts recovery after 60 seconds. Override these with
`REDIS_CIRCUIT_BREAKER_ENABLED`, `REDIS_CIRCUIT_BREAKER_FAILURE_THRESHOLD`,
and `REDIS_CIRCUIT_BREAKER_RECOVERY_TIMEOUT`.

## Database topology and capacity

### Database topology and config convergence

`DATABASE_URL_READ_REPLICA` sends read-only Prisma operations to a reader while
writes stay on `DATABASE_URL`. With `IAM_TOKEN_DB_AUTH=true`, tokens for both
connections are refreshed.

`database_disable_prepared_statements` adds `pgbouncer=true`, unless
`database_extra_connection_params` overrides it. `supported_db_objects`
restricts which stored object classes are loaded.
`proxy_config_reload_interval_seconds` controls cross-pod database config
refresh and defaults to 30 seconds.

### Per-worker database pools and timeouts

`database_connection_pool_limit` applies to each worker. Maximum aggregate
capacity is instances multiplied by workers multiplied by the configured
limit. The general connection-call timeout, time allowed to open a connection,
and idle or silent socket timeout are independent.

```yaml
general_settings:
  database_connection_pool_limit: 10
  database_connection_timeout: 60
  database_connect_timeout: 15
  database_socket_timeout: 300
```

## Configuration and credentials

### Reusable named credentials

Top-level `credential_list` entries let multiple deployments share a rotatable
credential set through `litellm_credential_name`. Every credential entry must
include a `credential_info` mapping, even when it is empty.

```yaml
model_list:
  - model_name: chat
    litellm_params:
      model: azure/gpt-4o
      litellm_credential_name: azure-prod
credential_list:
  - credential_name: azure-prod
    credential_values:
      api_key: os.environ/AZURE_API_KEY
      api_base: os.environ/AZURE_API_BASE
    credential_info: {}
```

### Config discovery without a CLI path

`CONFIG_FILE_PATH` starts `litellm` from a mounted configuration file without
`--config`. Alternatively, bucket-name and object-key variables load config
from S3; `LITELLM_CONFIG_BUCKET_TYPE=gcs` changes that source to GCS.

```shell
CONFIG_FILE_PATH=/path/to/config.yaml

LITELLM_CONFIG_BUCKET_NAME=litellm-proxy
LITELLM_CONFIG_BUCKET_OBJECT_KEY=proxy_config.yaml
LITELLM_CONFIG_BUCKET_TYPE=gcs
```

## Outbound HTTP behavior

### Outbound HTTP environment controls

The aiohttp transport ignores `HTTP_PROXY` and `HTTPS_PROXY` by default. Set
`AIOHTTP_TRUST_ENV=true` to use them. Connector limits default to unlimited
(`0`). Socket keepalive is off unless `AIOHTTP_SO_KEEPALIVE` is enabled; its
idle, interval, and probe-count defaults are 60 seconds, 30 seconds, and 5.

## Packaging and supply chain

### Python 3.14 installation support

Since 1.93.0, package metadata permits Python 3.14 by setting the upper bound
to `<3.15`. Compatible `redisvl`, `pypdf`, `openapi-core`, and native-bridge
dependencies are included for that runtime.

### Cosign verification for Docker images

Since 1.97.0, all LiteLLM Docker images use the same Cosign signing key
introduced at commit `0112e53`. Pin the immutable commit when verifying an
image:

```shell
cosign verify \
  --key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub \
  ghcr.io/berriai/litellm:v1.97.0
```

The tag-relative `v1.97.0/cosign.pub` URL is easier to read but depends on
repository tag protection.

## Administration UI

### Admin UI controls

Since 1.97.0, the Playground can make non-streaming requests. Administrators
can configure a user-visible banner, and the auto-router form includes a
routing-test action.

### Admin UI build runtime

Since 1.97.0, the Admin UI toolchain targets Node.js 24. Its bootstrap selects
that dashboard version floor through nvm or fnm.
