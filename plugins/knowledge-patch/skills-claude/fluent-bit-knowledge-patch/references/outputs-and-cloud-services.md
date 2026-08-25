# Outputs and Cloud Services

## JSON serialization and HTTP methods

Since 4.1.0, `escape_unicode` is applied consistently by every JSON-outputting
plugin. An upgrade may therefore change output from plugins that used to
ignore the setting. Capture representative payloads before and after the
upgrade and verify downstream byte-level assumptions.

The HTTP output supports `PUT` since 4.2.0. Choose it only when the destination
expects idempotent replacement semantics; method support does not change the
receiver's retry or authentication contract.

## Compression by output

Compression support added in 4.0.0 includes:

- zstd for OpenTelemetry output; and
- zstd and snappy for HTTP output.

The `5.0-guide` source batch expands cloud-output codecs:

- Kinesis Data Streams supports gzip, zstd, and snappy;
- Kinesis Data Firehose supports snappy;
- Amazon S3 supports snappy; and
- Azure Blob supports zstd transfer compression.

Compression affects CPU, bandwidth, and receiver compatibility differently.
Load-test the exact codec and destination combination rather than selecting a
codec globally.

## Amazon S3

Since 4.1.0, the S3 output can write Parquet through a pure-C Apache Arrow
backend and apply zstd compression in Parquet mode. Validate the resulting
schema and compression with the downstream reader.

Version 5.0.0 makes S3 output accounting represent logical records more
accurately. Recheck record-based delivery validation, billing, and chargeback
queries after an upgrade because old assumptions about accounting units can
produce discontinuities.

## OpenTelemetry output to AWS

The OpenTelemetry output supports AWS Signature Version 4 authentication since
4.1.0. Use SigV4 when the target AWS service requires signed requests and keep
the signing region, service, and credentials aligned with the destination.

## Forward output compatibility

Starting in v5.0.4, `retain_metadata_in_forward_mode` defaults to `true`. This
embeds event metadata in extended MessagePack. Fluentd receivers reject that
format, so explicitly disable metadata retention for Fluentd:

```yaml
pipeline:
  outputs:
    - name: forward
      match: "*"
      host: fluentd-host
      port: 24224
      retain_metadata_in_forward_mode: false
```

Keep the default only when the receiving Forward peer understands the extended
metadata representation.

## Structured and protocol metadata

The Splunk output can include OTLP metadata since 4.0.0. The Loki output adds
`structured_metadata_map_keys` in the same version, allowing selected map keys
to be emitted as structured metadata. Confirm that metadata cardinality and
receiver schemas remain bounded when enabling either feature.

## Exit output

The Exit output accepts `time_count` in seconds and `record_count` since
4.0.0. Use these thresholds to make a test or bounded pipeline exit by elapsed
time or record volume, and select the threshold that matches the intended
lifecycle.

## Azure Kusto and managed identity

Azure Kusto output supports Azure managed identity authentication since
4.0.0. Prefer the managed identity credential path when the runtime environment
provides it, and verify that the identity has access to the target Kusto
resource.

## InfluxDB tag keys

Version 5.0.4 fixes space-separated `tag_keys` entries in the InfluxDB output:
they are treated as strings rather than Boolean values. Revalidate line
protocol and tag cardinality if a configuration previously worked around the
incorrect coercion.

## CloudWatch missing streams

In 5.0.9, the CloudWatch Logs output treats a missing log stream as
unrecoverable for the current chunk and removes its stale cached stream state.
The affected chunk is not retried through that stale stream. Delivery alerts
must distinguish this terminal chunk outcome from normal retry exhaustion.
