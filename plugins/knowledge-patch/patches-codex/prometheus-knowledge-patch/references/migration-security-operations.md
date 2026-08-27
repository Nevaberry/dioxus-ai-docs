# Migration, Security, and Operations

Use this reference for binary upgrades, startup flags, container changes,
security patch levels, and process-level behavior.

## Major-upgrade preparation

### Replace promoted feature flags and old mode switches (3.0-migration)

Remove `promql-at-modifier`, `promql-negative-offset`,
`new-service-discovery-manager`, `expand-external-labels`, and
`no-default-scrape-port` from `--enable-feature`; those behaviors are default.
External labels expand `$var` and `${var}`, undefined variables become empty,
and `$$` escapes a dollar. Scrape target labels no longer gain
scheme-derived ports.

Replace the `agent` feature flag with `--agent`, and
`remote-write-receiver` with `--web.enable-remote-write-receiver`. Automatic
`GOMEMLIMIT` and `GOMAXPROCS` sizing is default; disable it only with
`--no-auto-gomemlimit` or `--no-auto-gomaxprocs`.

### Respect the TSDB downgrade floor (3.0-migration)

The format prepared in v2.55 means a v3 data directory is readable only by
v2.55 or newer. Upgrade through v2.55 as a safety step. Downgrading below it
requires abandoning the v3 persistent data.

### Update structured-log consumers (3.0-migration)

Prometheus emits `log/slog` output rather than the former `go-kit/log` shape.
Parsers expecting `ts`, `caller`, or lowercase levels must accept fields such
as `time`, `source`, and `level=INFO`.

### Require Alertmanager v2 (3.0-migration)

Alertmanager's v1 API is unsupported. Use Alertmanager 0.16.0 or later and
replace explicit `api_version: v1` with `api_version: v2`.

### Remove deleted startup flags (3.0.0)

Delete `storage.tsdb.allow-overlapping-blocks`, `alertmanager.timeout`, and
`storage.tsdb.retention` from startup arguments; they are no longer accepted.

### Supply console assets explicitly (3.0.0)

The bundled example JavaScript and templates for the console feature were
removed. Console users must provide their own files.

## Configuration reload behavior

### Enable automatic reload where still experimental (3.0.0)

On releases where it is gated, use
`--enable-feature=auto-reload-config` to reload configuration automatically.

### Watch referenced files too (3.4.0)

Automatic reload reacts to changes in rule files and scrape configuration
files as well as the main configuration file.

### Treat automatic reload as stable (3.12.0)

The `auto-reload-config` capability is stable rather than experimental on
current releases. Do not retain a no-longer-needed experimental assumption in
deployment logic.

## Release-specific operational safeguards

### Container data directory is writable (3.3.0)

The container image's `/prometheus` directory is writable. Mounts and runtime
policies can rely on that path being writable by the image user.

### Prefer the maintenance fix over 3.9.0 (3.9.0)

Prometheus 3.9.1 fixes an Agent-mode crash shortly after startup and restores
scrape relabel `keep` and `drop`, which were broken in 3.9.0. Deployments using
either behavior should not remain on 3.9.0.

### Choose the container variant deliberately (3.10.0)

Both `-busybox` and `-distroless` images are published; the unsuffixed image is
still the busybox variant. Distroless runs as UID/GID 65532 and declares no
`VOLUME`. Adjust ownership of existing named volumes or bind mounts before
migration, for example:

```text
docker run --rm -v prometheus-data:/prometheus alpine chown -R 65532:65532 /prometheus
docker run -v prometheus-data:/prometheus prom/prometheus:latest-distroless
```

### Account for independent Alertmanager send loops (3.10.0)

Configured Alertmanagers have independent notification send loops instead of
sharing one. Expect delivery scheduling across multiple Alertmanagers to
change.

### Use shutdown-aware readiness handling (3.10.0)

`/-/ready` again returns `X-Prometheus-Stopping` while `NotReady`. Health-check
clients can use the header to distinguish shutdown from other readiness loss.

### Build for AIX when required (3.12.0)

The supported compilation targets include `aix/ppc64`.

### Use the maintenance UI carefully (3.12.0)

The Status menu includes actions for deleting time series and cleaning
tombstones. Treat these as destructive data-maintenance operations.

### Read embedded third-party licenses (3.13.0)

Third-party npm licenses are served from
`/assets/third-party-licenses.txt`; tarballs and images no longer include
`npm_licenses.tar.bz2`.

### Pull images from GitHub Container Registry (3.13.0)

Prometheus container images are also published through `ghcr.io`.

### Shutdown loops no longer spin (3.13.2-3.14.0)

Alerting and scrape managers no longer consume 100% CPU during shutdown. The
old alerting behavior could delay graceful shutdown until an external timeout
killed the process.

## Security patch decisions

### Patch the 3.11 line (3.11.0)

Deploy at least 3.11.3 on the 3.11 line. It prevents AzureAD remote-write OAuth
`client_secret` exposure through `/-/config` (CVE-2026-42151), enforces the
declared-length limit for Snappy remote-read requests (CVE-2026-42154), and
closes stored-XSS paths in the current and old UIs involving metric or label
values (CVE-2026-40179 and GHSA-fw8g-cg8f-9j28).

### Protect STACKIT discovery credentials (3.12.0)

Fixed releases no longer show STACKIT service-discovery secrets in plaintext
through `/-/config`. STACKIT users should upgrade rather than expose the
affected endpoint on an unfixed release.

### Patch the UI sanitizer (3.13.0)

Prometheus 3.13.0 updates `sanitize-html` for CVE-2026-44990. UI-exposing
deployments should run that release or later.

### Strip credentials on cross-host redirects (3.13.0)

HTTP clients no longer forward authorization headers, basic or bearer
credentials, OAuth2 credentials, or configured headers when a redirect changes
host. This applies to scraping, remote read/write, alerting, and service
discovery and closes CVE-2025-4673 and CVE-2023-45289.

### Apply dependency security updates (3.13.2-3.14.0)

Prometheus 3.13.2 updates `golang.org/x/text` to v0.39.0 for CVE-2026-56852 and
`google.golang.org/grpc` to v1.82.1 for GHSA-hrxh-6v49-42gf. Use 3.13.2 or later
when either advisory affects the deployment.
