# Outputs and Integrations

## Compression matrix

Compression support is plugin-specific:

- OpenTelemetry output supports zstd (since 4.0.0).
- HTTP output supports zstd and snappy (since 4.0.0).
- Amazon S3 Parquet output supports zstd (since 4.1.0).
- Kinesis Data Streams supports gzip, zstd, and snappy (5.0-guide).
- Kinesis Data Firehose and Amazon S3 support snappy (5.0-guide).
- Azure Blob supports zstd transfer compression (5.0-guide).

Confirm that the destination accepts the selected content encoding or storage
codec. Parquet compression and transport compression solve different problems.

## Amazon S3 and AWS services

Amazon S3 can write Parquet through a pure-C Apache Arrow backend (since
4.1.0). Validate schema conversion, logical record counts, file boundaries,
compression, and destination-reader compatibility.

The OpenTelemetry output supports AWS Signature Version 4 authentication
(since 4.1.0). The AWS filter emits entity attributes for telemetry association
(since 4.0.6). Treat signing credentials and association attributes as separate
concerns and verify both at the receiving service.

The CloudWatch Logs output treats a missing log stream as unrecoverable for the
current chunk and evicts stale stream state (since 5.0.9). Monitoring must
account for the chunk not being retried through that stale stream.

## HTTP output

The HTTP output supports the `PUT` method (since 4.2.0). Verify idempotency,
body format, authentication, response handling, and retry policy with the
target endpoint.

For OAuth client-credentials acquisition and client authentication modes, see
[security-and-configuration.md](security-and-configuration.md).

## Forward output and Secure Forward

Forward output defaults `retain_metadata_in_forward_mode` to `true` starting in
v5.0.4 (5.0-guide). This places event metadata in extended MessagePack that a
Fluentd receiver rejects. Disable it for Fluentd:

```yaml
pipeline:
  outputs:
    - name: forward
      match: "*"
      host: fluentd-host
      port: 24224
      retain_metadata_in_forward_mode: false
```

Secure Forward validates input-side PING messages and output-side PONG server
digests more strictly (since 5.0.9). The output rejects username or password
configuration without a shared key. Chunk acknowledgment tokens are
base64-encoded 128-bit identifiers; custom Forward peers must accept that
format and complete the stricter handshake.

## Splunk and Loki metadata

The Splunk output can include OTLP metadata (since 4.0.0). Confirm that the
destination indexing and field strategy intentionally handles the added
metadata.

The Loki output provides `structured_metadata_map_keys` (since 4.0.0) to select
map keys as structured metadata. Keep high-cardinality data out of labels and
validate how selected maps are represented at the destination.

## Azure Kusto

The Azure Kusto output supports Azure managed identity authentication (since
4.0.0). Grant only the required identity permissions and test token acquisition
in the actual hosting environment.

## InfluxDB

The InfluxDB output treats space-separated `tag_keys` entries as strings rather
than booleans (since 5.0.4). Recheck configurations that worked around the old
parsing behavior and verify the resulting series cardinality.

## Vivo Exporter

The Vivo Exporter uses `/api/v1/` endpoints and supports groups (since 4.2.0).
Update endpoint assumptions and validate group selection and authentication
against the deployed Vivo API.
