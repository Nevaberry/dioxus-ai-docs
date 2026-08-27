# Migration, Security, and Deployment

## Major-version migration checklist (`3.0-migration`)

### Remove promoted feature gates

Do not pass `promql-at-modifier`, `promql-negative-offset`,
`new-service-discovery-manager`, `expand-external-labels`, or
`no-default-scrape-port` in `--enable-feature`; those behaviors are default.
External labels expand `$var` and `${var}`, undefined variables become empty,
and `$$` escapes a dollar. Scrape target labels no longer gain ports inferred
from their schemes.

Replace the former `agent` and `remote-write-receiver` gates with `--agent` and
`--web.enable-remote-write-receiver`. Automatic `GOMEMLIMIT` and `GOMAXPROCS`
sizing is default; opt out with `--no-auto-gomemlimit` or
`--no-auto-gomaxprocs`.

### Respect the TSDB downgrade floor

The data format prepared in v2.55 means a v3 data directory is readable only
by v2.55 or newer. Upgrade through v2.55 as a safety step. Downgrading below it
requires abandoning the v3 persistent data.

### Choose UTF-8 validation deliberately

Metric and label names accept UTF-8, so an upgrade can ingest formerly invalid
names and change exposed names. Preserve the old validation globally or per
scrape job with `metric_name_validation_scheme: legacy`; use `utf8` when the
new behavior is intended.

### Update logs and normalized labels

Logging uses `log/slog`, not the former `go-kit/log` shape. Parsers should
accept `time`, `source`, and uppercase levels such as `level=INFO` rather than
assuming `ts`, `caller`, and lowercase levels.

Classic histogram `le` and summary `quantile` label values are normalized to
float-like strings across scrape protocols. Update exact matchers such as
`le="1"` to `le="1.0"`; queries spanning the transition can still be uneven.

### Require Alertmanager API v2

Alertmanager API v1 configuration is unsupported. Run Alertmanager 0.16.0 or
later and replace explicit `api_version: v1` with `api_version: v2`.

## Removed and changed v3 assets (`3.0.0`)

Remove `storage.tsdb.allow-overlapping-blocks`, `alertmanager.timeout`, and
`storage.tsdb.retention` from startup arguments because they are rejected.
The bundled console JavaScript and templates are also gone; console users must
supply their own files.

## Container filesystem changes (`3.3.0`)

The container image's `/prometheus` directory is writable, so workloads do not
need a custom image solely to make the data directory writable.

## Distroless deployment (`3.10.0`)

Prometheus publishes `-busybox` and `-distroless` variants; the unsuffixed image
remains the busybox variant. Distroless runs as UID/GID 65532 and declares no
`VOLUME`. Adjust named-volume or bind-mount ownership before switching:

```text
docker run --rm -v prometheus-data:/prometheus alpine chown -R 65532:65532 /prometheus
docker run -v prometheus-data:/prometheus prom/prometheus:latest-distroless
```

## Required 3.11 patch level (`3.11.0`)

Deploy at least 3.11.3 on the 3.11 line. It prevents AzureAD remote-write
OAuth `client_secret` disclosure through `/-/config` (CVE-2026-42151), enforces
the declared-length limit for Snappy remote-read requests (CVE-2026-42154), and
closes stored-XSS paths involving metric or label values in current and old UIs
(CVE-2026-40179 and GHSA-fw8g-cg8f-9j28).

## Platform and credential fixes (`3.12.0`)

STACKIT service-discovery secrets are no longer exposed in plaintext through
`/-/config`; users of that discovery should upgrade to a fixed release.
Prometheus also supports the `aix/ppc64` build target.

## UI and redirect security (`3.13.0`)

Prometheus 3.13.0 updates `sanitize-html` to fix CVE-2026-44990. Upgrade any
deployment that exposes the UI.

HTTP clients strip authorization headers, basic and bearer credentials, OAuth2
credentials, and configured headers when a redirect changes host. This applies
to scraping, remote read and write, alerting, and service discovery and closes
CVE-2025-4673 and CVE-2023-45289. Do not depend on cross-host credential
forwarding.

Relative paths inside the file supplied to `promtool --http.config.file` now
resolve from that file's directory, not its parent. Fix layouts that relied on
the former extra parent traversal.

Third-party npm licenses are served at `/assets/third-party-licenses.txt` from
the binary. Tarballs and images no longer include `npm_licenses.tar.bz2`.
Container images are also published through GitHub Container Registry.

## Security and resilience follow-ups (`3.13.2-3.14.0`)

Prometheus 3.13.2 updates `golang.org/x/text` to v0.39.0 for CVE-2026-56852 and
`google.golang.org/grpc` to v1.82.1 for GHSA-hrxh-6v49-42gf. Use 3.13.2 or
later when either advisory affects the deployment.

The active query tracker is now preallocated, avoiding SIGBUS crashes when the
data disk fills. Alerting and scrape managers also stop cleanly instead of
spinning at 100% CPU during shutdown; the older alerting loop could postpone a
graceful shutdown until an external timeout killed the process.
