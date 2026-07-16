# Self-hosting and operations

- [Version 4 deployment boundary](#version-4-deployment-boundary)
- [Docker Compose deployment scope](#docker-compose-deployment-scope)
- [Docker Compose topology and overlays](#docker-compose-topology-and-overlays)
- [Runtime and bootstrap configuration layering](#runtime-and-bootstrap-configuration-layering)
- [Init, setup, and runtime phases](#init-setup-and-runtime-phases)
- [Managed PostgreSQL bootstrapping and credential changes](#managed-postgresql-bootstrapping-and-credential-changes)
- [Public endpoint and virtual-instance resolution](#public-endpoint-and-virtual-instance-resolution)
- [Reverse-proxy transport and Login routing](#reverse-proxy-transport-and-login-routing)
- [Proxy-specific failure modes](#proxy-specific-failure-modes)
- [Internal cache connector contract](#internal-cache-connector-contract)
- [Helm removal leaves hook resources](#helm-removal-leaves-hook-resources)
- [Runtime health and Login observability](#runtime-health-and-login-observability)
- [Mirror execution and scope contract](#mirror-execution-and-scope-contract)
- [Instance blocking and audit-query retention](#instance-blocking-and-audit-query-retention)
- [Per-instance request and Action quotas](#per-instance-request-and-action-quotas)

## Version 4 deployment boundary

The documented direct Linux installation does not work for ZITADEL 4, for which the container deployment is the supported path. The `stable` container tag is the production release while `latest` is the frequently updated pipeline build; Docker Compose requires the V2 `docker compose` plugin, and the Kubernetes guide assumes Kubernetes 1.30 or newer.

## Docker Compose deployment scope

ZITADEL presents Cloud, public-cloud, and self-hosted deployment choices but recommends Docker Compose for development rather than production. Do not treat the official Compose setup as a production deployment recommendation.

## Docker Compose topology and overlays

The official base stack is Traefik in front of separate ZITADEL API and Login containers backed by PostgreSQL. Add exactly one of the Let's Encrypt, externally terminated TLS, or local self-signed TLS overlays. The `cache` and `observability` profiles add Redis and an OpenTelemetry collector, while the `prodlike` overlay separates one-shot init and setup containers from the long-running API and is required before scaling API replicas.

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

## Runtime and bootstrap configuration layering

Runtime settings come from repeatable `--config` files, while database initialization and the first instance use repeatable `--steps` files; multiple files are merged so public and secret configuration can remain separate. Environment-variable forms flatten the documented keys below `ZITADEL_`, and the master key can be passed by value, from `ZITADEL_MASTERKEY` with `--masterkeyFromEnv`, or from a file with `--masterkeyFile`.

```sh
zitadel setup \
  --config runtime.yaml --config runtime-secrets.yaml \
  --steps bootstrap.yaml --steps bootstrap-secrets.yaml \
  --masterkeyFile /run/secrets/zitadel-masterkey
```

`FirstInstance` overrides `DefaultInstance` only when setup creates the first instance. Changing `ZITADEL_FIRSTINSTANCE_*` or `ZITADEL_DEFAULTINSTANCE_*` and restarting does not update an existing instance; use Admin Console or the Admin API instead.

## Init, setup, and runtime phases

`zitadel init` provisions the database identity and base schemas and is needed once per installation; `zitadel setup` creates or migrates projections and must run for every deployed version; only then should replicas run `zitadel start`. Init and setup are idempotent with the same binary version, but `start-from-init` is a quickstart convenience—existing installations should use `start-from-setup` or controlled one-shot jobs.

```sh
zitadel init --config config.yaml
zitadel setup --init-projections=true --config config.yaml
zitadel start --config config.yaml
```

Without `--init-projections=true`, runtime can become ready while stale projections continue replaying missed events in the background; enabling it shifts that catch-up into setup. The official Helm chart already implements init and setup as dedicated Jobs.

## Managed PostgreSQL bootstrapping and credential changes

Pre-provisioning the PostgreSQL role and database does not create ZITADEL's `eventstore`, `projections`, and `system` schemas. On a managed service without superuser access, run `zitadel init schema` (legacy alias `zitadel init zitadel`) with the database-owner service account, then run setup. `Database.postgres.Admin.ExistingDatabase` tells a normal init invocation to bypass database and user creation checks.

```sh
ZITADEL_DATABASE_POSTGRES_DSN='postgresql://zitadel:<password>@db.example.com:5432/zitadel?sslmode=require' \
  zitadel init schema
ZITADEL_DATABASE_POSTGRES_DSN='postgresql://zitadel:<password>@db.example.com:5432/zitadel?sslmode=require' \
  zitadel start-from-setup --masterkeyFile /run/secrets/zitadel-masterkey
```

Init never rotates a database password, replaces an existing user, or transfers object ownership. A password change must be propagated to every ZITADEL credential, while changing users requires manually reassigning all schemas, tables, ownership, and grants. The application itself is stateless, so database backups—especially the `eventstore.events` history—define the restore boundary.

## Public endpoint and virtual-instance resolution

`ExternalDomain`, `ExternalPort`, and `ExternalSecure` must describe the exact browser-visible endpoint because ZITADEL resolves the virtual instance from the request host. A reverse proxy must preserve the original `Host` or place it in the `Forwarded` host directive; mismatches produce `Instance not found`, and changing any of these three settings requires rerunning setup.

```yaml
ExternalDomain: auth.example.com
ExternalPort: 443
ExternalSecure: true
```

An organization domain is for login discovery, not automatically an address on which ZITADEL serves that organization. It can be registered as an additional instance domain through the System API, but accessing it still does not supply organization context.

## Reverse-proxy transport and Login routing

ZITADEL serves gRPC, HTTP APIs, and Console from one HTTP/2 port, `8080` by default. When a proxy terminates TLS, it must use unencrypted HTTP/2 (`h2c`) rather than HTTP/1.1 upstream; `--tlsMode external` advertises HTTPS while keeping the ZITADEL hop plain, whereas `enabled` requires ZITADEL's certificate and key and `disabled` advertises plain HTTP.

```text
/ui/v2/login    -> zitadel-login:3000
everything else -> zitadel:8080 over h2c
```

The Helm chart therefore creates separate API and Login ingresses, normally on the same host and certificate, and terminates TLS at the ingress controller.

## Proxy-specific failure modes

Caddy can hang indefinitely on error responses when it forwards the browser's `TE: trailers`; strip that upstream header on the ZITADEL route. Cloudflare supports gRPC only over TLS, and Cloudflare Tunnel cannot currently force HTTP/2 toward the origin.

```caddyfile
reverse_proxy h2c://zitadel:8080 {
    header_up -TE
}
```

## Internal cache connector contract

Internal object caches are an experimental beta and are disabled until each object names an enabled connector. The cacheable objects are instances, organizations, and setup milestones; each accepts `MaxAge`, usage-based `LastUsage`, and cache-specific logging.

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

The Redis connector accepts one standalone Redis or Valkey endpoint. Cluster and Sentinel routing, client-certificate authentication, and mTLS are unsupported, although `rediss://` performs server-authenticated TLS. The database number in the URL is ignored; ZITADEL derives separate indexes from `DBOffset` and cache purpose and may issue `FLUSHDB`, so those indexes must not contain another application's data.

The Redis circuit breaker temporarily bypasses a failed cache and falls back to database queries. PostgreSQL caching uses crash-discardable unlogged tables and needs auto-pruning, while local-memory caching is per process and can serve inconsistent values across replicas until `MaxAge` expires.

## Helm removal leaves hook resources

The chart's hook resources are not garbage-collected by `helm uninstall`. Remove its labeled Jobs, ConfigMaps, Secrets, Roles, RoleBindings, and ServiceAccounts explicitly if the namespace is being retained.

```sh
helm uninstall my-zitadel
for kind in job configmap secret rolebinding role serviceaccount; do
  kubectl delete "$kind" \
    --selector app.kubernetes.io/name=zitadel,app.kubernetes.io/managed-by=Helm
done
```

## Runtime health and Login observability

The built-in `zitadel ready` probe uses HTTP when `ZITADEL_TLS_ENABLED=false` and HTTPS otherwise, so a TLS-setting mismatch can make a healthy process appear unhealthy. Login has its own readiness endpoint and supports push-based OpenTelemetry logs, metrics, and traces; OpenTelemetry resources use the configured service name. The core process separately exposes `/debug/metrics` for scraping.

## Mirror execution and scope contract

A mirror destination must be initialized and set up without an instance, mirrored with the current deployment's master-key and TLS settings, set up again, and then verified. `--system` and `--instance` are mutually exclusive scopes that must remain consistent across runs; after choosing instance-scoped migration, later switching to `--system` can collide with already present instances.

```sh
zitadel init --config destination.yaml
zitadel setup --for-mirror --config destination.yaml
zitadel mirror --system --config mirror.yaml
zitadel setup --for-mirror --config destination.yaml
zitadel mirror verify --system --config mirror.yaml
```

Use `--replace` on repeated runs to replace the static system assets, auth requests, and unique constraints that events alone do not reconstruct. Mirror cannot use files as endpoints or change the deployment domain, and the source encryption keys must be copied. Verification can legitimately report fewer old projection states, locks, expired keys, failed events, and `auth.users2` rows in the destination.

## Instance blocking and audit-query retention

Self-hosters can block an existing instance through the System API or make new instances blocked by default. Most blocked requests return HTTP 429 or gRPC `Resource Exhausted`, while the System API remains reachable. Requests below `/ui/login` redirect to Console and blocked responses set a cookie that a WAF can reject earlier.

```yaml
AuditLogRetention: 0s
DefaultInstance:
  Limits:
    Block: false
    AuditLogRetention: 720h
```

`AuditLogRetention` limits how far back event and resource-history APIs may query rather than deleting the event store; `0s` is unlimited. A per-instance System API value, or the `DefaultInstance.Limits` value applied to a new instance, overrides the global default.

## Per-instance request and Action quotas

Quota accounting is disabled until `Quotas.Access.Enabled` or `Quotas.Execution.Enabled` is set, after which each virtual instance can receive quotas through the System API or `DefaultInstance.Quotas`. The only units are `requests.all.authenticated` and `actions.all.runs.seconds`; a quota defines its start, reset interval, amount, whether exhaustion blocks work, and optional percentage webhooks.

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

An exhausted request quota blocks further authenticated requests but not the System API and sets the exhaustion cookie for upstream filtering. Exhausting Action seconds makes both the Action crossing the limit and later Actions fail immediately with a context-timeout error.
