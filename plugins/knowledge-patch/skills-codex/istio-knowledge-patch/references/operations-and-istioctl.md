# Operations and istioctl

Use this reference for command changes, control-plane runtime settings, debug
authorization, revision selection, proxy administration, and diagnostics.

## Contents

- [Configuration processing and control-plane behavior](#configuration-processing-and-control-plane-behavior)
- [Command removals and shared flags](#command-removals-and-shared-flags)
- [Revisions and administrative commands](#revisions-and-administrative-commands)
- [Debug endpoint authorization](#debug-endpoint-authorization)
- [Output and diagnostics](#output-and-diagnostics)

## Configuration processing and control-plane behavior

### Injection configuration errors are returned (1.25.0)

Sidecar injection configuration errors are returned to the user instead of
being logged while processing continues with faulty configuration.

### Proxy-to-pod lookup by IP (1.27.0)

`ENABLE_PROXY_FIND_POD_BY_IP` allows Istio to associate a proxy with its Pod by
IP address when matching by Pod name and namespace fails.

### Istiod memory-limit headroom (1.29.0)

Istiod sets `GOMEMLIMIT` to 90% of its container memory limit instead of 100%.
Override the limit with `GOMEMLIMIT`, or change the automatic ratio with
`AUTOMEMLIMIT`, such as `AUTOMEMLIMIT=0.85`.

### Pilot resource watch filtering (1.29.0)

`PILOT_IGNORE_RESOURCES` accepts a comma-separated list of resources or
prefixes that Pilot's Istio CRD watcher should ignore.
`PILOT_INCLUDE_RESOURCES` explicitly restores matches, enabling installations
such as Gateway API-only or HTTPRoute-only controllers.

### Control-plane configuration diagnostics (1.30.0)

Istiod logs configuration-analysis warnings and errors for every Istio resource
type. `WorkloadEntry` status includes `WaypointBound` to report successful
waypoint attachment or a binding error.

## Command removals and shared flags

### Breaking istioctl flag changes (1.25.0)

`istioctl analyze` is always recursive and no longer accepts `--recursive`.
The experimental `--xds-via-agents` flag is removed from
`istioctl proxy-status`.

### istioctl Kubernetes-client timeout (1.27.0)

The root `--kubeclient-timeout` flag accepts a Go `time.Duration` and overrides
the default `15s` timeout for Kubernetes-client calls across `istioctl`. It does
not change installation or other command-specific timeouts:

```bash
istioctl --kubeclient-timeout=30s proxy-status
```

### Proxy admin port override (1.28.0)

Use `--proxy-admin-port` to select a non-default proxy admin port for
`istioctl experimental authz`, `istioctl proxystatus`,
`istioctl bug-report`, and `istioctl experimental describe`.

### ztunnel-config proxy admin port (1.29.0)

`istioctl ztunnel-config` accepts `--proxy-admin-port` when the proxy admin
endpoint does not use the default port.

## Revisions and administrative commands

### Service-backed revision tags (1.28.0)

Revision tags created by `istioctl tag set <tag> --revision <rev>` or the
`revisionTags` Helm value also create a cluster-IP `Service` labeled with
`istio.io/tag` to store the mapping, alongside the mutating webhook
representation.

### Automatic default-revision selection (1.28.0)

When `--revision` is omitted, `istioctl` commands automatically use the revision
assigned by `istioctl tag set default`.

### Combined istioctl log levels (1.28.0)

`istioctl admin log` accepts `--level` and `--stack-trace-level` together.

### Waypoint status controls (1.29.0)

`istioctl waypoint status --wait=false` reports status without waiting for
readiness. Add `--all-namespaces` to display waypoints across every namespace.

## Debug endpoint authorization

### Debug endpoint authorization by default (upgrade-1.29)

Clients in non-system namespaces can access only `config_dump`, `ndsz`, and
`edsz`, and only for proxies in their own namespace. This can affect Kiali and
custom monitoring. Set `ENABLE_DEBUG_ENDPOINT_AUTH=false` to restore previous
unrestricted behavior.

### Authentication for plaintext XDS debug endpoints (upgrade-1.30)

The `syncz` and `config_dump` XDS debug endpoints on port 15010 require
authentication, affecting `istioctl --plaintext` and custom plaintext XDS
clients. Set `ENABLE_DEBUG_ENDPOINT_AUTH=false` to restore unauthenticated
behavior.

### Debug endpoint namespace allowlist (1.30.0)

When `ENABLE_DEBUG_ENDPOINT_AUTH=true`,
`DEBUG_ENDPOINT_AUTH_ALLOWED_NAMESPACES` accepts a comma-separated list of
namespaces authorized to use debug endpoints. The system namespace remains
authorized regardless of the list.

## Output and diagnostics

### Headers in combined configuration output (1.29.0)

`istioctl ztunnel-config all` and `istioctl proxy-config all` print headers.
Consumers of tabular output must account for the header row.

### Expanded istioctl diagnostics and structured output (1.30.0)

`istioctl bug-report` can skip expensive sections with
`--skip-cluster-dump`, `--skip-analyze`, `--skip-proxy-debug`,
`--skip-netstat`, and `--skip-coredumps`; `--tail` limits log lines per
container. `istioctl proxy-status` supports JSON and YAML output, including
namespace-scoped listings. `ztunnel-config workload` and
`ztunnel-config connections` can filter by workload pod name.
