# Security, Cluster APIs, and Operations

## Credentials, authorization, and federation

### API-key hashes and secure settings (9.0.0)

API-key credential hashes may use `SSHA-256`. Secure settings are not accepted
in YAML; supply them through Elasticsearch's secure-settings mechanism.

### Connector deletion modes (9.0.0)

Connector APIs support soft and hard deletion through a delete URL parameter.
Managed connector indices must use the required prefix.

### Security extensions and federation (9.1.0)

`SecurityExtensions` can provide a custom `ServiceAccountTokenStore`. The SAML
identity provider supports custom attributes. JWT access tokens may use an
`at+jwt` `typ` header. A Microsoft Graph delegated-authorization realm plugin
is available.

### Security statistics (9.2.0)

`/_security/stats` reports document-level-security metrics, including DLS cache
usage, hits, misses, and timing.

### SAML configuration (9.2.0)

SAML private attributes are configurable. URL-based metadata resolution has
configurable HTTP connect and read timeouts.

### Cross-cluster keys and TLS extensibility (9.2.0)

Cross-cluster API keys support signing and trust configuration. The transport
TLS handshake timeout is adjustable. TLS extensions can implement
`SslProfileExtension` and receive reload notifications through an `SslProfile`
listener.

### Security and federation changes (9.3.0)

JWT realms can periodically reload PKC JWK sets. Successful SAML responses
include in-response-to metadata. Cross-cluster API keys carry and validate
certificate identities. Secure-settings reload responses include setting names
and the keystore modification time.

### Security API changes (9.4.0)

API keys can be cloned through a dedicated endpoint. Service-account-token APIs
are available in Serverless. The `read` index privilege consistently
authorizes cross-cluster search regardless of `ccs_minimize_roundtrips`.

## Runtime, plugins, and configuration reload

### Java, Lucene, and container baseline (9.0.0)

Elasticsearch bundles JDK 24, uses Lucene 10.1.0, and bases its default Docker
image on UBI minimal rather than Ubuntu. Startup ignores `_JAVA_OPTIONS`.

### Entitlements replace the SecurityManager (9.0.0)

Elasticsearch Entitlements permanently replaces the Java SecurityManager,
which Java 24 disables.

### File-backed configuration reloads (9.1.0)

Configuration reload detects Kubernetes CSI-style `..data` symlink switches.
TLS reload watches SSL files rather than containing directories.

### Operational baselines (9.4.0)

The `cloud-ess-fips` package defaults to FIPS 140-3. Elasticsearch uses Apache
Lucene 10.4.

## Cluster and index administration

### Cluster-only resolution (9.0.0)

`_resolve/cluster` can return cluster information without an index expression
and accepts a caller-configurable timeout.

### Per-tier shard balancing (9.1.0)

Shard-allocation balancing weights can be configured independently for each
data tier.

### Synonyms refresh control (9.1.0)

Synonyms PUT and delete accept `refresh`, which waits for updated synonyms to
be accessible and reloads affected analyzers.

### Operational endpoints and settings (9.3.0)

Cat APIs add a circuit-breakers endpoint. Shard-capacity health thresholds are
configurable. Elasticsearch can limit concurrent TLS handshakes.

## Resource controls, scripting, and telemetry

### Mustache output limits (9.0.0)

`mustache.max_output_size_bytes` limits Mustache script result length.

### Operational defaults and metrics (9.0.0)

`replica_unassigned_buffer_time` defaults to five seconds instead of three.
Reindex metrics report seconds rather than milliseconds.

### Indexing safeguards and thread-pool metrics (9.1.0)

`IndexingPressureMonitor` accounts for document-expansion memory, and a maximum
document-size limit is available. Thread-pool telemetry includes utilization
and queue latency.

## Connector and API privilege migration

Connector APIs are restricted to `manage_connector` and `monitor_connector` in
the breaking-change set. Review
[breaking-changes.md](breaking-changes.md) before changing connector roles.
