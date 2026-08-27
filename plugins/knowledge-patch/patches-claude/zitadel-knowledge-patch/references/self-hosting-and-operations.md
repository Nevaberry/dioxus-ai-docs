# Self-hosting and operations

## Choose a deployment topology

### Use containers for version 4

The documented direct Linux installation does not work for version 4; use containers. The `stable` tag is the production release and `latest` is the frequently updated pipeline build. Docker Compose needs the V2 `docker compose` plugin; the Kubernetes guide assumes Kubernetes 1.30 or newer. Compose is presented for development, not as an automatic production recommendation.

### Compose overlays explicitly

The official base stack puts Traefik in front of separate API and Login containers backed by PostgreSQL. Add exactly one of the Let's Encrypt, externally terminated TLS, or local self-signed TLS overlays. The `cache` and `observability` profiles add Redis and an OpenTelemetry collector. The `prodlike` overlay separates one-shot init/setup containers from the API and is required before scaling replicas.

```sh
docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.mode-external-tls.yml \
  up -d --wait

docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prodlike.yml \
  up -d --scale zitadel-api=3
```

## Layer runtime and bootstrap configuration

Runtime uses repeatable `--config` files; database initialization and the first instance use repeatable `--steps` files. Multiple files merge so public and secret values can remain separate. Environment variables flatten documented keys below `ZITADEL_`. Supply the 32-byte master key by value, via `ZITADEL_MASTERKEY` with `--masterkeyFromEnv`, or via `--masterkeyFile`.

```sh
zitadel setup \
  --config runtime.yaml --config runtime-secrets.yaml \
  --steps bootstrap.yaml --steps bootstrap-secrets.yaml \
  --masterkeyFile /run/secrets/zitadel-masterkey
```

`FirstInstance` overrides `DefaultInstance` only when setup creates the first instance. Restarting with changed `ZITADEL_FIRSTINSTANCE_*` or `ZITADEL_DEFAULTINSTANCE_*` does not update an existing instance; use Admin Console or Admin API.

Feature flags can be set through environment variables. PostgreSQL and Redis accept DSN/URL connection strings. Login supports `LOGIN_SERVICE_KEY_FILE`, optional TLS termination, OpenSSL CA validation, a private-key file through environment configuration, `SSL_CERT_DIR` entries without hashed filenames, PKCS#1 client keys, and `ZITADEL_API_AWAITINITIALCONN`.

```sh
LOGIN_SERVICE_KEY_FILE=/path/to/service-key
```

## Run init, setup, and start in order

`zitadel init` provisions database identity and base schemas once per installation. `zitadel setup` creates or migrates projections and must run for every deployed version. Only then run `zitadel start`. Init and setup are idempotent with the same binary. `start-from-init` is a quickstart convenience; existing installations should use `start-from-setup` or controlled one-shot jobs.

```sh
zitadel init --config config.yaml
zitadel setup --init-projections=true --config config.yaml
zitadel start --config config.yaml
```

Without `--init-projections=true`, runtime can become ready while stale projections replay in the background. Enabling it shifts catch-up into setup. The official Helm chart uses dedicated init and setup Jobs. Interrupted setup steps are cleaned up automatically; maintained releases also correct setup connection handling after migration steps 40, 64, and 70.

## Bootstrap and protect PostgreSQL

Pre-provisioning a role and database does not create the `eventstore`, `projections`, and `system` schemas. On a managed service without superuser access, run `zitadel init schema` (legacy alias `zitadel init zitadel`) as the database owner, then setup. `Database.postgres.Admin.ExistingDatabase` lets normal init bypass database/user creation checks. PostgreSQL 18 is supported.

```sh
ZITADEL_DATABASE_POSTGRES_DSN='postgresql://zitadel:<password>@db.example.com:5432/zitadel?sslmode=require' \
  zitadel init schema
ZITADEL_DATABASE_POSTGRES_DSN='postgresql://zitadel:<password>@db.example.com:5432/zitadel?sslmode=require' \
  zitadel start-from-setup --masterkeyFile /run/secrets/zitadel-masterkey
```

Init never rotates a password, replaces an existing user, or transfers object ownership. Propagate a changed password to every credential. When changing database users, manually reassign schemas, tables, ownership, and grants. Application containers are stateless; PostgreSQL backups, especially `eventstore.events`, define the restore boundary.

## Preserve the public endpoint

`ExternalDomain`, `ExternalPort`, and `ExternalSecure` must match the browser-visible endpoint because the request host resolves the virtual instance. Preserve the original `Host` or put it in the `Forwarded` host directive. A mismatch causes `Instance not found`; changing these settings requires setup again.

```yaml
ExternalDomain: auth.example.com
ExternalPort: 443
ExternalSecure: true
```

An organization domain is for login discovery, not automatically an address that serves that organization. It may be registered as an additional instance domain through System API, but accessing it still supplies no organization context. Trusted domains can be added during instance setup and listings can be sorted.

## Configure the reverse proxy

ZITADEL serves gRPC, HTTP APIs, and Console from one HTTP/2 port, default `8080`. When a proxy terminates TLS, use unencrypted HTTP/2 (`h2c`) upstream, not HTTP/1.1. `--tlsMode external` advertises HTTPS over a plain core hop; `enabled` requires a core certificate/key; `disabled` advertises plain HTTP.

```text
/ui/v2/login   -> zitadel-login:3000
everything else -> zitadel:8080 over h2c
```

The Helm chart creates separate API and Login ingresses, normally with one host and certificate, and terminates TLS at ingress. Login centralizes host-header resolution and forwards resolved proxy headers to API calls; custom proxy headers can come from environment configuration. Multi-domain deployments can configure redirects.

Validate protocol headers and enforce HTTPS. In Development Mode, account for Safari cookie behavior. Login derives its public host behind proxies and passes email verification before continuing callbacks.

### Avoid proxy-specific traps

Caddy can hang on errors when it forwards `TE: trailers`; strip that header. Cloudflare supports gRPC only over TLS, and Cloudflare Tunnel cannot force HTTP/2 to the origin.

```caddyfile
reverse_proxy h2c://zitadel:8080 {
    header_up -TE
}
```

## Configure internal caches cautiously

Internal object caches are experimental beta and disabled until each object names an enabled connector. Cacheable objects are instances, organizations, and setup milestones; each supports `MaxAge`, usage-based `LastUsage`, and cache-specific logging.

```yaml
Caches:
  Connectors:
    Redis:
      Enabled: true
      URL: rediss://cache-user:password@redis.example.com:6380
  Instance:
    Connector: redis
    MaxAge: 1h
    LastUsage: 10m
  Organization:
    Connector: redis
    MaxAge: 1h
```

Redis accepts one standalone Redis or Valkey endpoint. Cluster/Sentinel routing, client-certificate authentication, and mTLS are unsupported; `rediss://` provides server-authenticated TLS. URL database numbers are ignored. ZITADEL derives indexes from `DBOffset` and purpose and may issue `FLUSHDB`, so do not share those indexes with other applications.

The circuit breaker bypasses failed cache and falls back to database queries. PostgreSQL caching uses crash-discardable unlogged tables and needs auto-pruning. Local memory is per process and can differ across replicas until `MaxAge` expires. Maintenance releases prevent cross-instance organization-cache overwrite.

## Remove Helm hook resources explicitly

Hook resources survive `helm uninstall`. If retaining the namespace, delete labeled Jobs, ConfigMaps, Secrets, Roles, RoleBindings, and ServiceAccounts.

```sh
helm uninstall my-zitadel
for kind in job configmap secret rolebinding role serviceaccount; do
  kubectl delete "$kind" \
    --selector app.kubernetes.io/name=zitadel,app.kubernetes.io/managed-by=Helm
done
```

## Observe readiness, logs, traces, and metrics

`zitadel ready` uses HTTP when `ZITADEL_TLS_ENABLED=false` and HTTPS otherwise; a mismatch can make a healthy process look unhealthy. The separate Login container writes stdout logs but exposes neither tracing nor metrics. Login has a readiness endpoint and can push OpenTelemetry logs, metrics, and traces. The core supports standard OpenTelemetry environment variables, cross-application API tracing, ConnectRPC tracing, log streams, and GCP Error Reporting.

Metrics/tracing service name is configurable; OpenTelemetry resources use it. Projection handlers and the River queue emit metrics. Maintenance releases remove default metric scope metadata, correct River units, fix gRPC status mapping, and label HTTP metrics by route pattern rather than raw path. Revisit dashboards and cardinality assumptions after those changes.

## Migrate with mirror

A destination must be initialized and set up without an instance, mirrored using current master-key and TLS settings, set up again, and verified. `--system` and `--instance` are mutually exclusive and must remain consistent; switching from instance to system scope later can collide with existing instances.

```sh
zitadel init --config destination.yaml
zitadel setup --for-mirror --config destination.yaml
zitadel mirror --system --config mirror.yaml
zitadel setup --for-mirror --config destination.yaml
zitadel mirror verify --system --config mirror.yaml
```

Use `--replace` on repeated runs to replace static system assets, auth requests, and unique constraints that events do not reconstruct. Mirror cannot use files as endpoints or change deployment domain. Copy source encryption keys. Verification can legitimately find fewer old projection states, locks, expired keys, failed events, and `auth.users2` rows at destination. Mirror is safely repeatable, supports a maximum auth-request age, includes required fields, skips notification projections, and represents event-store values as decimals where required.

## Block instances and bound audit queries

Self-hosters can block existing instances through System API or make new instances blocked by default. Most blocked requests return HTTP 429 or gRPC `Resource Exhausted`; System API remains available. `/ui/login` requests redirect to Console and blocked responses set a cookie a WAF can reject earlier.

```yaml
AuditLogRetention: 0s
DefaultInstance:
  Limits:
    Block: false
    AuditLogRetention: 720h
```

`AuditLogRetention` bounds how far event and resource-history APIs may query; it does not delete the event store. `0s` is unlimited. Per-instance System API values or `DefaultInstance.Limits` for new instances override the global default.

## Apply per-instance quotas

Accounting is disabled until `Quotas.Access.Enabled` or `Quotas.Execution.Enabled` is set. Each virtual instance can receive quotas through System API or `DefaultInstance.Quotas`. Units are `requests.all.authenticated` and `actions.all.runs.seconds`; each quota defines start, reset interval, amount, whether exhaustion blocks, and optional percentage webhooks.

```yaml
Quotas:
  Access:
    Enabled: true
  Execution:
    Enabled: true
DefaultInstance:
  Quotas:
    Items:
      - Unit: requests.all.authenticated
        From: 2026-01-01T00:00:00Z
        ResetInterval: 720h
        Amount: 25000
        Limit: true
        Notifications:
          - Percent: 80
            Repeat: false
            CallURL: https://billing.example.com/zitadel-quota
```

An exhausted request quota blocks authenticated requests but not System API and sets an exhaustion cookie for upstream filtering. Exhausting Action seconds makes the Action crossing the limit and later Actions fail immediately with context timeout.

## Apply operational hardening

- Use the FIPS 140-3-compliant build and runtime checks when FIPS requirements apply.
- Use the protected HTTP client and target restrictions for outbound Actions, IdPs, and providers.
- Event resource owners can be reassigned by event-store operations that explicitly overwrite ownership.
- Projections can be disabled per instance and their locking behavior follows configuration.
- Service Ping is opt-out, sends anonymized resource and usage metrics to the customer portal, randomizes and validates its interval, and reports expanded resource counts and body sizes.
