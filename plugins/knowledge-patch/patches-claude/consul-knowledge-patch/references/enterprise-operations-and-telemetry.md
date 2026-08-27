# Enterprise Operations and Telemetry

## Choose a support cadence

Consul 1.21.0 is an Enterprise long-term support release with two years of support. This lets operators remain on that line while receiving patches and fixes.

The 2.0.0 version number also introduces Enterprise support options for longer contract periods. Earlier Enterprise releases remain governed by their existing long-term-support contracts; do not infer a changed maintenance term for an already-deployed earlier line.

## Generate utilization reports manually

Since 1.22.0, Enterprise operators can generate and submit license-utilization data through `/v1/operator/utilization`. Air-gapped environments can create a census utilization bundle for manual submission:

```shell
consul operator utilization [-today-only] [-message] [-y]
```

Census metrics collection is always enabled. Exporting the metrics for reporting remains configurable.

## Change cluster-wide RPC limits at runtime

Since 2.0.0, Enterprise provides a Raft-replicated `rate-limit` configuration entry. Use it to change cluster-wide RPC limits without restarting every server, and add exemptions for RPC methods that must remain available under pressure.

`GET /v1/internal/rpc/methods` lists the method names that can be targeted. The request requires an ACL token with `operator:read`.

## Configure agent HTTP timeouts

Since 2.0.0, agent `http_config` defaults are:

| Setting | Default |
| --- | --- |
| `read_timeout` | 15 minutes |
| `write_timeout` | 15 minutes |
| `read_header_timeout` | 10 seconds |
| `idle_timeout` | 120 seconds |

The longer read and write defaults prevent blocking long-poll queries from being terminated at the former 30-second boundary. All four values remain configurable. Coordinate them with reverse proxies and client timeouts.

## Decide whether to export product telemetry

Since 2.0.0, self-managed Enterprise clusters can send anonymized product-usage telemetry. Reporting is disabled by default and requires explicit enablement. Treat enablement as an operator choice and document it with the cluster's data-handling policy.

## Monitor certificate expiration and renewal

Since 2.0.0, `/agent/metrics` exports Prometheus metrics for:

- Active root and signing certificate authorities.
- Agent TLS certificates.
- Leaf-certificate renewal health.

Metrics carry datacenter, partition, and namespace labels. The agent `telemetry` block can also emit structured certificate-monitoring logs with configurable severity thresholds. The Connect CA API exposes `NotAfter` for root and intermediate certificates.

Build alerts around both expiration horizon and renewal health. Preserve the scope labels in alerts so responders can identify the affected trust domain.

## Parse IBM PAO licenses

Since 2.0.0, Enterprise licensing and utilization reporting can parse and report IBM Passport Advantage Online licenses. Ensure downstream reporting workflows accept this license source rather than treating it as unknown input.
