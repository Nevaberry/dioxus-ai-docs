# Deprecations and Known Issues

## Deprecation migrations

### ES|QL query logging is deprecated

Starting in 9.4.2, use of the ES|QL query log emits a deprecation message. Do
not introduce new operational dependencies on this log.

### The `logs` data-stream type is deprecated

Elasticsearch 9.4.0 deprecates the `logs` stream type. Avoid it in new data
streams and plan to migrate existing definitions.

### `aggregate_metric_double.default_metric` is deprecated

Elasticsearch 9.4.0 deprecates the `default_metric` mapping parameter. Omit it
from new mappings and prepare existing mappings for its removal.

### ILM's `max_size` rollover condition is deprecated

Elasticsearch 9.3.0 warns on the `max_size` rollover condition. Replace it with
supported rollover conditions rather than aggregate index size.

### Lenient boolean values are deprecated

Elasticsearch 9.3.0 warns about lenient booleans in third-party-plugin analysis
settings and boolean system properties. Use strict `true` or `false` values.

### `reporting_user` now uses reserved Kibana privileges

In 9.0.6 and 9.1.3, the built-in `reporting_user` role changed to derive
authorization from reserved Kibana privileges. Recheck custom assumptions that
depended on its former privilege composition.

### Merge-scheduler thread-pool setting is deprecated

`indices.merge.scheduler.use_thread_pool` is deprecated as of 9.0.3. Remove it
from configurations prepared for later releases.

### ES|QL `METADATA` no longer accepts brackets

Elasticsearch 9.0 drops bracketed `METADATA` syntax. List fields directly:

```esql
FROM my-index METADATA _id, _index
```

### Machine-learning flush API is deprecated

Elasticsearch 9.0 warns when the machine-learning flush API is called. Stop
treating the endpoint as a durable workflow dependency.

### The `elser` inference service is deprecated

Elasticsearch 9.0 deprecates the `elser` Inference API service. Do not create
new endpoints with it, and migrate existing endpoints.

### Behavioral Analytics CRUD APIs are deprecated

Elasticsearch 9.0 deprecates the Behavioral Analytics create, read, update,
and delete APIs. Prepare applications for their removal.

## Known issues: APIs and upgrades

### Trained-model request limits in 9.3.6

Elasticsearch 9.3.6 can reject valid create-trained-model requests because its
limits are too restrictive for `description`, `tags`,
`prefix_strings.ingest_prefix`, `prefix_strings.search_prefix`,
`input.field_names`, `default_field_map`, and `metadata`. Upgrade to 9.3.7.

### Direct upgrade from 9.1.10 to 9.2.4 can fail

A direct upgrade can prevent startup because 9.2.4 cannot parse a field in
stored node-shutdown metadata. Upgrade to 9.2.5 or later.

### Low disk can hang shard closure in 9.0.3

Insufficient merge space can prevent shard closure and leave index closure or
relocation hanging. Version 9.0.3 mitigates this by defaulting
`indices.merge.disk.check_interval` to `0s`; do not manually enable the disk
check on that version.

### Watcher may not start after an old 7.x upgrade

A 9.x cluster previously on 7.10.0 through 7.12.1 can retain templates that
prevent Watcher startup. Delete them and restart Watcher:

```http
DELETE _index_template/.triggered_watches
DELETE _index_template/.watches
POST /_watcher/_start
```

## Known issues: repositories and entitlements

### GCS repositories using ADC fail in 9.2.8 and 9.3.3

`repository-gcs` operations using Application Default Credentials can fail
because an entitlement exception escapes credential-path discovery. Upgrade
9.2.8 to 9.2.9 or 9.3.3 to 9.3.4. If an immediate upgrade is impossible,
create `${ES_CONF_PATH}/jvm_options/workaround-gcsadc.options` with the policy
matching the installed version:

```text
# 9.2.8
-Des.entitlements.policy.repository-gcs=dmVyc2lvbnM6CiAgLSA5LjIuOApwb2xpY3k6CiAgQUxMLVVOTkFNRUQ6CiAgICAtIHNldF9odHRwc19jb25uZWN0aW9uX3Byb3BlcnRpZXMKICAgIC0gb3V0Ym91bmRfbmV0d29yawogICAgLSBmaWxlczoKICAgICAgICAtIHJlbGF0aXZlX3BhdGg6ICIuY29uZmlnL2djbG91ZCIKICAgICAgICAgIHJlbGF0aXZlX3RvOiBob21lCiAgICAgICAgICBtb2RlOiByZWFkCg==
# 9.3.3
-Des.entitlements.policy.repository-gcs=dmVyc2lvbnM6CiAgLSA5LjMuMwpwb2xpY3k6CiAgQUxMLVVOTkFNRUQ6CiAgICAtIHNldF9odHRwc19jb25uZWN0aW9uX3Byb3BlcnRpZXMKICAgIC0gb3V0Ym91bmRfbmV0d29yawogICAgLSBmaWxlczoKICAgICAgICAtIHJlbGF0aXZlX3BhdGg6ICIuY29uZmlnL2djbG91ZCIKICAgICAgICAgIHJlbGF0aXZlX3RvOiBob21lCiAgICAgICAgICBtb2RlOiByZWFkCg==
```

### Windows paths must match filesystem casing in 9.0

Entitlements treat paths as case-sensitive even on Windows. Match exact
filesystem casing in command-line paths, configuration, environment variables,
and secure settings to avoid startup failures or `NotEntitledException`.

### Active Directory authentication is blocked in 9.0

The `x-pack-core` entitlement policy blocks the LDAP library's outbound
connection. As a temporary workaround, create
`${ES_CONF_PATH}/jvm_options/workaround-127061.options` containing:

```text
-Des.entitlements.policy.x-pack-core=dmVyc2lvbnM6CiAgLSA4LjE4LjAKICAtIDkuMC4wCnBvbGljeToKICB1bmJvdW5kaWQubGRhcHNkazoKICAgIC0gc2V0X2h0dHBzX2Nvbm5lY3Rpb25fcHJvcGVydGllcwogICAgLSBvdXRib3VuZF9uZXR3b3Jr
```

### S3 repository analysis can fail before 9.3

Before 9.3.0, analysis can incorrectly fail S3 linearizable-register checks
because multipart-upload semantics do not always meet the assumed guarantees.
Run analysis on one node with `?register_operation_count=1`, or upgrade to
9.3.0 or later.

## Known issues: vector and GPU workloads

### Mixed-GPU clusters flood logs in 9.3.1

On a multi-node 9.3.1 cluster where some nodes lack a GPU, `_xpack/usage` cannot
collect their GPU stats and repeatedly logs `OutboundHandler` serialization
warnings. Other usage data and single-node clusters are unaffected. Upgrade to
9.3.2, or temporarily suppress the flood:

```http
PUT /_cluster/settings
{
  "persistent": {
    "logger.org.elasticsearch.transport.OutboundHandler": "ERROR"
  }
}
```

### DiskBBQ licensing changes after 9.2

Elasticsearch 9.2.0 failed to enforce the Enterprise requirement for
`bbq_disk` indices. After upgrade to 9.3 or later, existing indices created in
9.2 remain queryable and updatable, but creating new indices of this type
requires an Enterprise license.

### Direct I/O slows `bbq_hnsw` search in 9.1.0

In 9.1.0, `vector.rescoring.directio` defaults to `true` and can raise kNN
latency by as much as tenfold for `bbq_hnsw` when vectors fit in memory. Set it
to `false` on every search node and restart. Remove the override in 9.1.1 or
later. New 9.1 indices with dense vectors over 384 dimensions default to
`bbq_hnsw`.

```text
-Dvector.rescoring.directio=false
```

## Known issues: time-series and ES|QL

### Shrunk TSDB and LogsDB merges fail in 9.1.0 and 9.1.1

An optimized merge path can fail after shrinking TSDB or LogsDB indices.
Upgrade to 9.1.2. Until then, omit the post-shrink ILM force merge or set the
following property on every data node and perform a rolling restart. Remove it
after upgrading because it slows merges.

```text
-Dorg.elasticsearch.index.codec.tsdb.es819.ES819TSDBDocValuesConsumer.enableOptimizedMerge=false
```

### ES|QL `STATS` can return wrong two-key groups

From 8.16.0 until fixes in 8.17.9, 8.18.7, and 9.0.4,
`STATS ... BY keyword1, keyword2` can return incorrect results when there are
exactly two keyword grouping fields and the first exceeds 65,000 distinct
values. Upgrade, put the lower-cardinality field first, or filter to reduce
cardinality before `STATS`.
