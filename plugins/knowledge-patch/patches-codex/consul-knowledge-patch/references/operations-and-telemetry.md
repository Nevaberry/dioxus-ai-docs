# Operations and Telemetry

## Snapshot storage and authentication

### Google Cloud Storage

Since 1.21.0, the Enterprise snapshot-agent sidecar for Consul on Kubernetes
can write snapshots to Google Cloud Storage. Local, Amazon S3, and Azure Blob
Storage targets remain available.

### Azure Managed Service Identity

Since 1.22.0, the Enterprise snapshot agent can authenticate to Azure Blob
Storage with Azure Managed Service Identity. Prefer managed identity when it
can replace static storage credentials.

## Manual Enterprise utilization reporting

Since 1.22.0, operators can generate and submit license-utilization data through
`/v1/operator/utilization`. Air-gapped environments can create a census
utilization bundle for manual submission:

```shell
consul operator utilization [-today-only] [-message] [-y]
```

Census metrics collection is always enabled; exporting the collected data for
reporting remains configurable.

## Agent HTTP timeout defaults

Since 2.0.0, agent `http_config` uses these defaults:

| Setting | Default |
| --- | --- |
| `read_timeout` | 15 minutes |
| `write_timeout` | 15 minutes |
| `read_header_timeout` | 10 seconds |
| `idle_timeout` | 120 seconds |

The longer read and write defaults prevent long-polling blocking queries from
being terminated after the former 30-second timeout. All four settings remain
configurable. Set them explicitly when surrounding proxies have tighter limits.

## Cluster-wide RPC rate limiting

Since 2.0.0, Enterprise provides a Raft-replicated `rate-limit` configuration
entry. It changes cluster-wide RPC limits at runtime without restarting every
server and supports exemptions for critical RPC methods.

List valid method names with `GET /v1/internal/rpc/methods`. The request needs an
ACL token with `operator:read`. Treat exemptions as availability controls and
keep their scope narrow.

## Product-usage telemetry

Since 2.0.0, self-managed Enterprise clusters can send anonymized product-usage
telemetry. Reporting is disabled by default and requires explicit opt-in.

## Certificate expiration telemetry

Since 2.0.0, `/agent/metrics` exposes Prometheus metrics for:

- active root and signing certificate authorities;
- agent TLS certificates; and
- leaf-certificate renewal health.

Metrics carry datacenter, partition, and namespace labels. Certificate
monitoring in the agent `telemetry` block can also emit structured logs with
configurable severity thresholds. The Connect CA API exposes root and
intermediate `NotAfter` values. Combine these signals into expiry and failed
renewal alerts.

## IBM Passport Advantage Online licenses

Since 2.0.0, Enterprise licensing and utilization reporting can parse and
report IBM Passport Advantage Online licenses.
