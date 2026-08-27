# Compatibility, Deprecations, and Known Issues

Use this reference before upgrading nodes, changing defaults, or removing a
workaround. A workaround is scoped to the affected release and should be
removed after reaching the stated fixed version.

## Request and response compatibility

### Partial results and remote failures

ES|QL permits partial results by default. Callers must inspect `is_partial` and
can require completeness with `allow_partial_results=false` per request or
`esql.query.allow_partial_results: false` cluster-wide. EQL similarly defaults
`allow_partial_search_results` to `true`. With `skip_unavailable: true`, any
remote runtime error, including a missing index, is non-fatal and reports the
remote cluster as skipped or partial.

ES|QL remote index quoting is all-or-nothing. Parentheses are invalid in an
unquoted pattern. `FROM "remote:index"` and `FROM remote:index` are valid;
`FROM remote:"index"` is not.

### Status codes and parsing

- Elasticsearch timeouts return HTTP 429 rather than a 5xx response.
- Byte-size values accept at most two decimal places.
- Invalid processors in ingest simulation return HTTP 400.
- `date_histogram` no longer accepts boolean values.
- Inference timeouts return HTTP 504.
- Inference requests cannot override `secret_parameters` in 9.3.8 and 9.4.4.

### Removed request and API surface

- Highlighting no longer accepts `force_source`.
- Alias APIs no longer accept `local`.
- Frozen indices cannot be read, and the unfreeze endpoint is removed.
- `_fleet/_fleet_search` and `_fleet/_fleet_msearch` are local-only.
- Connector APIs require `manage_connector` or `monitor_connector`.
- The technical-preview `_knn_search` API is removed.
- Watcher searches no longer accept `types`.
- The `user_agent` ingest processor no longer accepts `ecs`; the ignored GeoIP
  fallback option is removed.
- Machine learning is disabled on macOS x86_64, and the old
  `data_frame_transforms` roles are removed.

## Configuration, mapping, and default changes

### Index and mapping defaults

- `exclude_source_vectors` is enabled by default for new indices.
- LogsDB and TSDB text fields omit norms.
- Eligible `logs-*-*` streams enable LogsDB by default.
- Normalized `keyword` fields use native synthetic source.
- Metadata field definitions reject `type`, `fields`, `copy_to`, and `boost`.
- `_source.mode` is a no-op.
- `random_score` without a field uses `_seq_no`.
- OTLP histograms map to `exponential_histogram` by default.

### Lifecycle and allocation

Since 9.4.0, ILM downsampling leaves the output unmerged by default. Add a
force-merge action or set `force_merge_index: true` on the downsample action to
retain the earlier behavior. The setting
`cluster.routing.allocation.disk.watermark.enable_for_single_data_node` is
removed, and `/_cluster/reroute` responses no longer include cluster state.

### Removed node settings

Remove `client.type`, `tracing.apm.*`, and
`xpack.searchable.snapshot.allocate_on_rolling_restart`. LDAP or Active
Directory configuration that supplies a bind DN without a bind password now
prevents node startup. The deprecation-log keyword is
`elasticsearch.deprecation`, replacing `deprecation.elasticsearch`.

### Analyzer and TLS output changes

Snowball stemmers and the Nori Korean dictionary changed. `german2` is now an
alias for the `german` Snowball stemmer, and the `persian` analyzer stems by
default. JDK 24 installations do not support `TLS_RSA` ciphers, and TLSv1.1 is
absent from the default protocol list.

### EC2 discovery migration

`discovery-ec2` uses AWS SDK v2, requires IMDSv2, and ignores
`discovery.ec2.protocol`. Include `http://` directly in
`discovery.ec2.endpoint` when needed. The plugin no longer supports
`aws.secretKey` or `com.amazonaws.sdk.ec2MetadataServiceEndpointOverride`.
Configure `discovery.ec2.access_key` and `discovery.ec2.secret_key` together or
omit both.

## Deprecations to remove from new work

- ES|QL query logging emits a deprecation message from 9.4.2.
- The `logs` data-stream type and
  `aggregate_metric_double.default_metric` are deprecated in 9.4.0.
- ILM `max_size` rollover is deprecated in 9.3.0; use supported rollover
  conditions rather than aggregate index size.
- Lenient booleans in third-party analysis settings and boolean system
  properties warn in 9.3.0; use `true` or `false`.
- The built-in `reporting_user` role derives authorization from reserved Kibana
  privileges in 9.0.6 and 9.1.3; recheck assumptions about its former privilege
  composition.
- `indices.merge.scheduler.use_thread_pool` is deprecated from 9.0.3.
- ES|QL `METADATA` no longer accepts brackets in 9.0; write
  `FROM my-index METADATA _id, _index`.
- The machine-learning flush API, the `elser` inference service, and Behavioral
  Analytics CRUD APIs are deprecated in 9.0.

## Upgrade blockers and workarounds

### Trained-model request limits

Elasticsearch 9.3.6 can reject otherwise valid create-trained-model requests
because of overly restrictive limits on `description`, `tags`,
`prefix_strings.ingest_prefix`, `prefix_strings.search_prefix`,
`input.field_names`, `default_field_map`, and `metadata`. Upgrade to 9.3.7.

### GCS Application Default Credentials

`repository-gcs` operations using Application Default Credentials can fail in
9.2.8 and 9.3.3 because credential-path discovery raises an entitlement
exception. Upgrade to 9.2.9 or 9.3.4 respectively. If an immediate upgrade is
not possible, create `${ES_CONF_PATH}/jvm_options/workaround-gcsadc.options`
with the value for the installed release:

```text
# 9.2.8
-Des.entitlements.policy.repository-gcs=dmVyc2lvbnM6CiAgLSA5LjIuOApwb2xpY3k6CiAgQUxMLVVOTkFNRUQ6CiAgICAtIHNldF9odHRwc19jb25uZWN0aW9uX3Byb3BlcnRpZXMKICAgIC0gb3V0Ym91bmRfbmV0d29yawogICAgLSBmaWxlczoKICAgICAgICAtIHJlbGF0aXZlX3BhdGg6ICIuY29uZmlnL2djbG91ZCIKICAgICAgICAgIHJlbGF0aXZlX3RvOiBob21lCiAgICAgICAgICBtb2RlOiByZWFkCg==
# 9.3.3
-Des.entitlements.policy.repository-gcs=dmVyc2lvbnM6CiAgLSA5LjMuMwpwb2xpY3k6CiAgQUxMLVVOTkFNRUQ6CiAgICAtIHNldF9odHRwc19jb25uZWN0aW9uX3Byb3BlcnRpZXMKICAgIC0gb3V0Ym91bmRfbmV0d29yawogICAgLSBmaWxlczoKICAgICAgICAtIHJlbGF0aXZlX3BhdGg6ICIuY29uZmlnL2djbG91ZCIKICAgICAgICAgIHJlbGF0aXZlX3RvOiBob21lCiAgICAgICAgICBtb2RlOiByZWFkCg==
```

### Mixed-GPU usage warnings

In a multi-node 9.3.1 cluster where some nodes lack a GPU, `_xpack/usage` can
repeatedly log `OutboundHandler` serialization warnings. Other usage data and
single-node clusters are unaffected. Upgrade to 9.3.2 or temporarily suppress
the flood:

```http
PUT /_cluster/settings
{
  "persistent": {
    "logger.org.elasticsearch.transport.OutboundHandler": "ERROR"
  }
}
```

### Unsafe direct upgrade

A direct upgrade from 9.1.10 to 9.2.4 can fail at boot because stored
node-shutdown metadata contains a field that 9.2.4 cannot parse. Upgrade to
9.2.5 or later instead.

### DiskBBQ licensing after 9.2

Elasticsearch 9.2.0 did not enforce the Enterprise license requirement for
`bbq_disk` indices. After upgrading to 9.3 or later, existing indices remain
queryable and updatable, but creation of new indices of this type requires an
Enterprise license.

### Shrunk TSDB and LogsDB merge failures

An optimized merge path can break merges after shrinking a TSDB or LogsDB index
in 9.1.0 and 9.1.1. Upgrade to 9.1.2. Until then, omit post-shrink force merge
from ILM, or add this property on every data node and rolling-restart. Remove it
after upgrading because it slows merges:

```text
-Dorg.elasticsearch.index.codec.tsdb.es819.ES819TSDBDocValuesConsumer.enableOptimizedMerge=false
```

### Direct I/O latency on `bbq_hnsw`

In 9.1.0, `vector.rescoring.directio` defaults to `true` and can make
`bbq_hnsw` kNN searches up to ten times slower when vectors fit in memory. Set
it to `false` on every search node and restart. Remove the override in 9.1.1.
New 9.1 indices with dense vectors over 384 dimensions default to `bbq_hnsw`.

```text
-Dvector.rescoring.directio=false
```

### Low-disk shard closure

In 9.0.3, a merge with insufficient space can leave index closure or relocation
hanging. Keep `indices.merge.disk.check_interval` at its release default of
`0s`; do not manually enable the disk-space check on this version.

### Incorrect ES|QL two-key groups

From 8.16.0 until fixes in 8.17.9, 8.18.7, and 9.0.4,
`STATS ... BY keyword1, keyword2` can return incorrect groups when the first
keyword has more than 65,000 distinct values. Upgrade, put the lower-cardinality
field first, or filter before `STATS`.

### Windows entitlement paths

Elasticsearch 9.0 entitlements treat paths as case-sensitive even on Windows.
Match filesystem casing exactly in command-line paths, configuration,
environment variables, and secure settings to avoid startup failures or
`NotEntitledException`.

### Active Directory in 9.0

The 9.0 `x-pack-core` entitlement policy blocks the LDAP library's outbound
connection and prevents Active Directory authentication. As a temporary
workaround, create `${ES_CONF_PATH}/jvm_options/workaround-127061.options`:

```text
-Des.entitlements.policy.x-pack-core=dmVyc2lvbnM6CiAgLSA4LjE4LjAKICAtIDkuMC4wCnBvbGljeToKICB1bmJvdW5kaWQubGRhcHNkazoKICAgIC0gc2V0X2h0dHBzX2Nvbm5lY3Rpb25fcHJvcGVydGllcwogICAgLSBvdXRib3VuZF9uZXR3b3Jr
```

### Watcher after an old 7.x upgrade

A 9.x cluster that once ran 7.10.0 through 7.12.1 can retain templates that
prevent Watcher from starting. Delete them and restart Watcher:

```http
DELETE _index_template/.triggered_watches
DELETE _index_template/.watches
POST /_watcher/_start
```

### S3 repository analysis before 9.3

Before 9.3.0, repository analysis can incorrectly fail S3
linearizable-register checks because multipart-upload semantics do not always
meet the assumed guarantees. Run the analysis on one node with
`?register_operation_count=1`, or upgrade to 9.3.0 or later.
