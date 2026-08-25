# Remote I/O and Authentication

Use this reference for remote read/write compatibility, transport defaults,
protocol versions, self-metrics, and authentication configuration.

## Contracts and transport behavior

### Opt into remote-write HTTP/2 (3.0-migration)

Remote-write HTTP clients default `http_config.enable_http2` to `false`, letting
parallel queues use multiple sockets. Set it explicitly to `true` only to
retain the earlier HTTP/2 behavior.

### Enforce selectors in remote-read storage (3.0-migration)

TSDB-compatible storage must return only results matching the requested
selectors. Third-party `remote_read` implementations can trigger undefined
behavior when they return extra series even though the contract is not
explicitly enforced.

### Randomize multi-address DNS selection (3.1.0)

Remote-write clients can opt into a DNS resolver that selects a random returned
IP. Use it when a multi-address endpoint should not always receive traffic at
the same address.

### Constrain custom-bucket transport (3.7.0)

Federation supports custom-bucket native histograms. Remote Write 1.0 does not;
Prometheus prevents sending them over that protocol and logs a warning.

### Validate remote-read histograms (3.9.0)

Histograms received by remote read are validated rather than silently accepting
invalid data.

### Validate queue configuration early (3.12.0)

Prometheus validates `remote_write.queue_config` while loading configuration,
rejecting invalid fields before they can panic or silently misconfigure the
runtime.

## Remote Write 2

### Include type and unit labels (3.7.0)

With `--enable-feature=type-and-unit-labels`, outgoing Remote Write 2 series
include `__type__` and `__unit__` labels.

### Use start-timestamp terminology (3.8.0)

The receiver follows the Remote Write 2.0-rc.4 schema, which renames the
created timestamp to the start timestamp. Senders and receiver integrations
must use the updated terminology and fields.

### Return permanent errors for too-old histograms (3.11.0)

Too-old samples in Remote Write 2 histogram paths return HTTP 400 rather than
500, preventing indefinite client retries.

## Self-metric migrations

### Replace deprecated remote-write metrics (3.7.0)

Update dashboards and alerts as follows:

- `prometheus_remote_storage_samples_in_total` becomes
  `prometheus_wal_watcher_records_read_total{type="samples"}` plus
  `prometheus_remote_storage_samples_dropped_total`.
- `prometheus_remote_storage_histograms_in_total` becomes
  `prometheus_wal_watcher_records_read_total{type=~".*histogram_samples"}` plus
  `prometheus_remote_storage_histograms_dropped_total`.
- `prometheus_remote_storage_exemplars_in_total` becomes
  `prometheus_wal_watcher_records_read_total{type="exemplars"}` plus
  `prometheus_remote_storage_exemplars_dropped_total`.
- `prometheus_remote_storage_highest_timestamp_in_seconds` becomes
  `prometheus_remote_storage_queue_highest_timestamp_seconds`, which accounts
  for relabeling and is more accurate.

### Measure batch duration after send (3.11.0)

`prometheus_remote_storage_sent_batch_duration_seconds` is measured after the
request is sent rather than before it.

## Azure authentication

### Use system-assigned managed identity (3.5.0)

An empty AzureAD managed-identity `client_id` selects the system-assigned
identity:

```yaml
remote_write:
  - url: https://example.invalid/api/v1/write
    azuread:
      managed_identity:
        client_id: ""
```

### Use Azure Workload Identity (3.7.0)

Remote write supports Azure Workload Identity as an authentication method.

### Request custom AzureAD scopes (3.9.0)

AzureAD authentication for remote write can request a custom scope.

### Authenticate to Azure Monitor with a certificate (3.13.0)

Remote write can use a certificate when sending data to an Azure Monitor
Workspace.

### Respect the federated-token environment path (3.13.2-3.14.0)

Azure workload-identity authentication reads `AZURE_FEDERATED_TOKEN_FILE`
instead of relying on a hard-coded token path.

## OAuth2 and AWS SigV4

### Use JWT bearer grants (3.8.0)

OAuth2 supports the JWT bearer grant type from RFC 7523 section 3.1.

### Select FIPS STS endpoints (3.8.0)

When AWS authentication requires a FIPS-compliant STS endpoint:

```yaml
sigv4:
  use_fips_sts_endpoint: true
```

### Add a SigV4 external ID (3.11.0)

HTTP-client SigV4 configuration accepts an AWS `external_id`.
