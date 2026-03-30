# Self-Hosting & Deployment

## v4 Architecture: Separate Login Container

Login V2 runs as a **separate Next.js container** (`ghcr.io/zitadel/login`), not embedded in the Go binary.

Stack: Reverse Proxy → ZITADEL API (Go, port 8080) + ZITADEL Login (Next.js, port 3000) → PostgreSQL.

Reverse proxy routing:
- `/ui/v2/login` → Login container (port 3000)
- All other paths → API container (port 8080)

Helm chart example:
```yaml
ingress:
  enabled: true
  className: traefik
  hosts:
    - host: zitadel.example.com
      paths:
        - path: /
          pathType: Prefix

login:
  image:
    repository: ghcr.io/zitadel/login
    tag: "v4.9.1"
  ingress:
    enabled: true
    className: traefik
    hosts:
      - host: zitadel.example.com
        paths:
          - path: /ui/v2/login
            pathType: Prefix
```

## Login Client PAT for Existing Installations

When upgrading to Login V2, manually configure:
1. Create service account (machine user)
2. Create PAT for it
3. Grant `IAM_LOGIN_CLIENT` role ("Instance Login Client" in Console)
4. Pass PAT via `ZITADEL_SERVICE_USER_TOKEN` env var or `ZITADEL_SERVICE_USER_TOKEN_FILE`

## `zitadel init schema` for Managed Databases

For managed PostgreSQL (RDS, Cloud SQL, Azure) without superuser:
```bash
# Pre-create as superuser:
# CREATE ROLE zitadel LOGIN PASSWORD '<password>';
# CREATE DATABASE zitadel WITH OWNER zitadel;

# Bootstrap schemas (no admin privileges needed):
ZITADEL_DATABASE_POSTGRES_DSN=postgresql://zitadel: <pw >@host:5432/zitadel?sslmode=require \
  zitadel init schema

# Start:
ZITADEL_DATABASE_POSTGRES_DSN=postgresql://zitadel: <pw >@host:5432/zitadel?sslmode=require \
  zitadel start-from-setup --masterkey "<32-char-key>"
```
`zitadel init zitadel` also works for backward compatibility.

## CLI Phases

| Command | Phases | Use Case |
|---------|--------|----------|
| `start-from-init` | init → setup → start | Fresh installs only |
| `start-from-setup` | setup → start | Upgrades (recommended) |
| `zitadel setup` + `zitadel start` | Separate | Production |

Setup runs database migrations. Use `--init-projections=true` to pre-compute projections before starting.

## Database Schema Layout

| Schema | Purpose |
|--------|---------|
| `system` | Cross-instance data (assets, encryption keys) |
| `eventstore` | Single source of truth — events, sequences, unique constraints |
| `projections` | Computed read models for query APIs |
| `auth` | Auth API projections (migrating to `projections`) |
| `adminapi` | Admin API projections (migrating to `projections`) |
| `notification` | Notification projections (migrating to `projections`) |

IDs use **sonyflake** format (e.g., `168096909691353697`). Projection lag: check `{schema}.current_sequences`. Failed events: `{schema}.failed_events`.

## Readiness Endpoint

`/debug/ready` — signals instance is ready for traffic. Used for Kubernetes probes and zero-downtime rolling updates.

## Cache System (Beta)

**Connectors:**
| Connector | Pros | Cons |
|-----------|------|------|
| Redis (standalone only) | Fast, built-in expiry, circuit breaker | Extra infra, no Cluster/Sentinel |
| PostgreSQL (unlogged tables) | No extra infra, reuses DB pool | Slowest, adds DB load |
| Local memory | Fastest, no overhead | Inconsistent across replicas |

**Cacheable Objects:** Instance, Organization, Milestones.

Single-server config:
```yaml
Caches:
  Connectors:
    Memory:
      Enabled: true
  Instance:
    Connector: "memory"
    MaxAge: 1h
  Organization:
    Connector: "memory"
    MaxAge: 1h
```

Redis with circuit breaker:
```yaml
Caches:
  Connectors:
    Redis:
      Enabled: true
      URL: redis://user:password@localhost:6379
      CircuitBreaker:
        MaxConsecutiveFailures: 5
        Timeout: 60s
  Instance:
    Connector: "redis"
    MaxAge: 1h
    LastUsage: 10m
```

**Warning**: Redis issues `FLUSHDB` — never share a DB index with other apps. Set `DBOffset` to avoid conflicts.

## Docker Compose Overlay Model

```bash
# Base stack (Traefik → ZITADEL + Login → PostgreSQL)
docker compose up -d --wait

# Add TLS
docker compose -f docker-compose.yml -f docker-compose.mode-letsencrypt.yml up -d --wait

# Add caching (Redis)
docker compose --profile cache up -d --wait

# Production-like init/setup/start split
docker compose -f docker-compose.yml -f docker-compose.prodlike.yml up -d --wait
```

Prodlike overlay: `zitadel-init` (one-shot migrations) + `zitadel-setup` (one-shot config) + `zitadel-api` (long-running).

## Caddy Reverse Proxy: TE Header Bug

The `TE: trailers` header causes requests to hang. Strip it:
```
reverse_proxy h2c://zitadel:8080 {
    header_up -TE
}
```

## Usage Control: Quotas and Instance Blocking

Self-hosted multi-tenant via System API:
- **Block instances**: Returns 429 for all requests except System API
- **Audit log retention**: Limit event query age per instance
- **Quotas**: Limit authenticated requests and action run seconds per period

```yaml
Quotas:
  Access:
    Enabled: true
  Execution:
    Enabled: true
```

## Password Hash Verifier Configuration

Only `bcrypt` enabled by default. For imports, enable verifiers in config:
- Supported: argon2i/id, bcrypt, md5 (crypt/plain/salted), phpass, drupal7, sha2, scrypt, pbkdf2
- argon2 disabled on Zitadel Cloud (memory requirements)
- md5 and drupal7 are import/verify only — cannot hash new passwords

Stored hashes auto-upgrade on next successful verification. Configure default:
```
ZITADEL_SYSTEMDEFAULTS_PASSWORDHASHER_HASHER_ALGORITHM='pbkdf2'
```
