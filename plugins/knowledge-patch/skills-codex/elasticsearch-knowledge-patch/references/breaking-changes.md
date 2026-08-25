# Breaking Changes

Resolve every applicable item before upgrading clients, plugins, policies, or
cluster configuration.

## Query and response behavior

### ES|QL partial results are now the default

An ES|QL response may be partial by default. Callers must inspect `is_partial`.
Require complete results with request-level `allow_partial_results=false` or
cluster-level `esql.query.allow_partial_results: false`.

### ES|QL index-pattern quoting is all-or-nothing

Parentheses are rejected in unquoted index patterns. A remote-cluster and index
pattern must be wholly quoted or wholly unquoted: `FROM "remote:index"` and
`FROM remote:index` are valid; `FROM remote:"index"` is invalid.

### ES|QL `skip_unavailable` suppresses runtime errors

When `skip_unavailable: true`, every runtime error from a remote cluster,
including a missing index, is non-fatal. The remote is reported as skipped or
partial instead.

### EQL allows partial search results by default

EQL defaults `allow_partial_search_results` to `true`. Set it to `false` when
all shards must succeed.

### Fleet search endpoints are local-only

`_fleet/_fleet_search` and `_fleet/_fleet_msearch` no longer support
cross-cluster operation.

### Date histograms reject boolean values

The `date_histogram` aggregation no longer accepts boolean values.

### `random_score` defaults to `_seq_no`

When `random_score` has no field, it now uses `_seq_no`.

### Timeout responses and byte-size parsing

Elasticsearch timeouts now return HTTP 429 rather than a 5xx response. Byte
sizes accept no more than two decimal places.

## Lifecycle, mappings, and ingest

### ILM downsampling no longer force-merges by default

Starting in 9.4.0, ILM downsampling leaves the downsampled index unmerged by
default. Add a force-merge action or set the downsample action's
`force_merge_index` to `true` when the policy depends on merged output.

### OTLP uses exponential histograms by default

The OTLP endpoint maps histograms as `exponential_histogram` fields by default.

### Native synthetic source for normalized keywords

Normalized `keyword` fields use the native synthetic-source implementation.

### LogsDB and TSDB text fields omit norms

Text fields in LogsDB or TSDB index mode no longer have norms enabled.

### LogsDB is conditionally enabled for log data streams

LogsDB is enabled by default for `logs-*-*` data streams when its enabling
conditions are satisfied.

### New indices exclude vectors from `_source`

`exclude_source_vectors` is enabled by default for new indices.

### Invalid ingest simulation returns HTTP 400

The simulate ingest API returns `400 Bad Request` when a request contains an
invalid processor.

### Ingest processor option removals

The `user_agent` processor no longer accepts `ecs`. The GeoIP processor's
ignored fallback option has also been removed.

### Mapping-definition restrictions

Metadata field definitions no longer support `type`, `fields`, `copy_to`, or
`boost`. The `_source` meta-field's `mode` attribute is a no-op.

## Search and index API removals

### Highlighting and index API removals

Highlighting no longer accepts `force_source`, alias APIs no longer accept
`local`, frozen indices cannot be read, and the unfreeze endpoint is removed.

### Platform and legacy API removals

Machine learning is disabled on macOS x86_64. The `data_frame_transforms`
roles, technical-preview `_knn_search` API, and `types` field in Watcher
searches are removed.

## Security, discovery, and connectors

### Inference secret parameters cannot be overridden

In 9.3.8 and 9.4.4, Inference API requests can no longer override
`secret_parameters`.

### `discovery-ec2` uses AWS SDK v2

The plugin requires IMDSv2, ignores `discovery.ec2.protocol`, and no longer
supports `aws.secretKey` or
`com.amazonaws.sdk.ec2MetadataServiceEndpointOverride`. Put `http://` directly
in `discovery.ec2.endpoint` when necessary. Configure both
`discovery.ec2.access_key` and `discovery.ec2.secret_key`, or configure neither.

### LDAP and Active Directory bind credentials

A bind DN without a corresponding bind password prevents node startup.

### Connector API privileges

Connector APIs require `manage_connector` or `monitor_connector`.

### TLS defaults remove legacy protocols and ciphers

JDK 24 installations no longer support `TLS_RSA` ciphers, and TLSv1.1 is no
longer in the default protocol list.

## Cluster configuration and analysis

### Allocation API removals

`cluster.routing.allocation.disk.watermark.enable_for_single_data_node` is
removed. `/_cluster/reroute` responses no longer include cluster state.

### Analyzer output changes

Snowball stemmers and the Nori Korean dictionary were updated. `german2` is an
alias of the `german` Snowball stemmer, and the `persian` analyzer stems by
default.

### Removed settings and renamed deprecation field

Remove `client.type`, `tracing.apm.*`, and
`xpack.searchable.snapshot.allocate_on_rolling_restart`. The deprecation-log
keyword is `elasticsearch.deprecation`, replacing `deprecation.elasticsearch`.
