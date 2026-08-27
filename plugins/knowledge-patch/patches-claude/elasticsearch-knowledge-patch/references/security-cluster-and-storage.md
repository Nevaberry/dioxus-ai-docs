# Security, Cluster Operations, and Storage

## Credentials and secure settings

### API keys and keystore usage

API-key credential hashes may use `SSHA-256` from 9.0.0. Secure settings are no
longer accepted in YAML; supply them through Elasticsearch's secure-settings
mechanism. Secure-settings reload responses include setting names and the
keystore modification time in 9.3.0.

API keys can be cloned through a dedicated endpoint in 9.4.0. Service-account
token APIs are available in Serverless. Connector APIs require
`manage_connector` or `monitor_connector`.

### Connector lifecycle

Connector APIs add soft and hard deletion through a delete URL parameter in
9.0.0. Managed connector indices must use the required prefix.

## Realms, federation, and authorization

### Extension points and token formats

Since 9.1.0, `SecurityExtensions` can provide a custom
`ServiceAccountTokenStore`. SAML identity providers accept custom attributes,
JWT access tokens may use `typ: at+jwt`, and a Microsoft Graph delegated
authorization realm plugin is available.

SAML private attributes become configurable in 9.2.0. URL-based SAML metadata
resolution has configurable HTTP read and connection timeouts.

In 9.3.0, JWT realms can periodically reload PKC JWK sets. Successful SAML
responses include in-response-to metadata. Cross-cluster API keys carry and
validate certificate identities.

### Privilege behavior

The built-in `reporting_user` role derives authorization from reserved Kibana
privileges in 9.0.6 and 9.1.3. The `read` index privilege consistently
authorizes cross-cluster search in 9.4.0 regardless of
`ccs_minimize_roundtrips`.

ES|QL views cannot be queried with document-level or field-level security.
View CRUD is authorized as index actions.

### LDAP and Active Directory

A bind DN without a corresponding bind password prevents startup. The 9.0
`x-pack-core` entitlement policy also blocks the LDAP library's outbound
connection for Active Directory; use the scoped workaround in the compatibility
reference until moving to a fixed release.

## TLS, entitlements, and runtime

### Java runtime transition

Elasticsearch 9.0.0 bundles JDK 24, uses Lucene 10.1.0, and changes its default
container base from Ubuntu to UBI minimal. Startup ignores `_JAVA_OPTIONS`.
Elasticsearch Entitlements permanently replaces the Java SecurityManager,
which Java 24 disables.

JDK 24 does not support `TLS_RSA` ciphers, and TLSv1.1 is absent from default
protocols. Windows paths remain case-sensitive to 9.0 entitlements even when
the filesystem is not; preserve exact path casing.

### Reloads and TLS extension points

File-backed configuration reload detects Kubernetes CSI-style `..data`
symlink switches in 9.1.0. TLS reload watches individual SSL files rather than
their parent directories.

In 9.2.0, transport TLS handshake timeout is configurable.
`SslProfileExtension` lets extensions customize TLS profiles, and an
`SslProfile` listener receives reload notifications. Cross-cluster API keys add
signing and trust configuration.

Elasticsearch can cap concurrent TLS handshakes in 9.3.0.

## Cluster discovery, routing, and resolution

### Per-tier allocation

Shard-allocation balancing weights can be configured independently per data
tier from 9.1.0. The old
`cluster.routing.allocation.disk.watermark.enable_for_single_data_node` setting
is removed. Cluster reroute responses no longer include cluster state.

### Cluster and index resolution

The `_resolve/cluster` API can return cluster information without an index
expression and accepts a user-configurable timeout in 9.0.0. `_resolve/index`
can filter by index mode and includes mode in its response from 9.2.0.

### Cross-project routing

Cross-project search and `project_routing` extend in 9.3.0 to `_search`,
`_async_search`, `_msearch`, EQL, field capabilities, SQL, and JDBC. Point in
time creation and closure can span projects, and cross-project searches default
to minimizing round trips.

In 9.4.0, project routing extends to templated searches, data streams, scrolls,
and the SQL CLI. The SQL CLI and JDBC authenticate with API keys.

### Partial and stateful distributed operations

In-progress cross-cluster ES|QL responses include CCS metadata. With
`skip_unavailable: true`, remote runtime failures become skipped or partial
outcomes. Stateful cross-cluster use disables `_delete_by_query` and
`_update_by_query`.

## Snapshots, archives, and cloud repositories

### Archive compatibility

Archive and searchable-snapshot indices may come from N-2 versions starting in
9.0.0, including supported 7.x segment cases used as archives in 8.x or 9.x.
The get snapshots API accepts a `state` filter from 9.1.0.

### S3 SDK and metadata service

`repository-s3` supports IMDSv2 in 9.0.0. In 8.19.0 it moves from AWS SDK v1
to v2; test production repository settings because behavior and configuration
differ between SDK generations.

In 9.2.0, S3 repositories use conditional writes to prevent accidental object
overwrite and repository corruption, including on fully compatible S3
implementations. Maximum idle connection time is configurable.

S3 repositories gain an API-call timeout setting in 9.3.0. Before 9.3.0,
repository analysis can falsely fail linearizable-register checks; use one node
with `register_operation_count=1` or upgrade.

### GCS repositories

Application Default Credentials fail under `repository-gcs` entitlement path
discovery in 9.2.8 and 9.3.3. Upgrade to 9.2.9 or 9.3.4, or use the exact
temporary JVM policy from the compatibility reference.

## Cluster administration and diagnostics

### Synonym refresh

Synonyms PUT and delete APIs accept `refresh` from 9.1.0. It waits for updated
synonyms to become accessible and reloads affected analyzers.

### Health, breakers, and shutdown

The cat APIs add a circuit-breakers endpoint in 9.3.0, and shard-capacity
health thresholds become configurable. In 9.4.0, persistent-task reassignment
during node shutdown is opt-in, and shutdown status reports shard snapshot
pauses.

### Packaging and Lucene

The `cloud-ess-fips` package defaults to FIPS 140-3 in 9.4.0. Elasticsearch
upgrades to Apache Lucene 10.4.
