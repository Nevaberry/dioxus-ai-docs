# Security, Access, and Integrations

Use this reference for authorization rules, identity-provider migration, HTTP
and Java contracts, CDC clients, GenAI procedures, TLS keys, and seed or object
storage integrations.

## Attribute-based and property-based access

### ABAC user metadata

Attribute-Based Access Control applies to native users and native linked LDAP
users as well as externally authenticated SSO users (since `2026.06.0`).
Administrators can tag native DBMS users and reference those tags in ABAC rules
for dynamic role assignment. Managing this data requires:

```text
DBMS USER METADATA MANAGEMENT
```

### PBAC and user-defined functions

A user-defined function can no longer be defined as part of a Property-Based
Access Control privilege. The combination is unsupported and did not behave as
its definition implied. Remove UDF calls from PBAC privilege definitions.

### Auth-rule validation

Creating an auth rule with an invalid time function now fails immediately
instead of deferring the error until authorization-time evaluation.

## Server-management privilege

`dbms.cluster.cordonServer()`,
`dbms.cluster.setAutomaticallyEnableFreeServers()`, and
`dbms.cluster.uncordonServer()` require `SERVER MANAGEMENT`. Relying on a broad
admin privilege is deprecated; grant the specific privilege.

The procedure-level migration also replaces `dbms.cluster.uncordonServer()`
with the `ENABLE SERVER` command.

## OIDC migration

`dbms.security.oidc.<provider>.auth_flow` supports PKCE and Implicit, with PKCE
as the default. Implicit flow is deprecated and will be removed; migrate
providers to PKCE.

`dbms.security.oidc.<provider>.auth_params` and
`dbms.security.oidc.<provider>.client_id` are also deprecated configuration
entry points.

## HTTP APIs

### Query API transaction identifiers

Query API transaction IDs are six characters rather than four (since
`2026.04.0`). Integrations that validate, persist, or size these identifiers
must accept the longer value.

### Transactional HTTP API replacement

The transactional HTTP API is deprecated in 5.26 in favor of the HTTP Query
API. The Query API is enabled by default from 5.26. On earlier releases, enable
it by adding `QUERY_API_ENDPOINTS` to `server.http_enabled_modules`.

### Stable error handling

Error-message text is not a programmatic contract. Parse and branch on
GQLSTATUS error codes; message text can change.

## Change Data Capture

`db.cdc.current()` returns `txCommitTime`, letting a CDC client retrieve its
most recent transaction's commit time together with its transaction identifier.

Replace beta namespace procedures as follows:

```text
cdc.current() -> db.cdc.current()
cdc.earliest() -> db.cdc.earliest()
cdc.query() -> db.cdc.query()
```

## GenAI integrations

### Azure OpenAI base URL

The GenAI plugin adds `GENAI_AZURE_OPENAI_BASE_URL`, which changes the base URL
used by `ai.text` calls.

### Token-aware text handling

The plugin adds:

- `ai.text.chunkByTokenLimit` to split an input into chunks within a token
  limit.
- `ai.text.countToken` to estimate the token count of an input.

### File-based batch embeddings

`ai.file.embedBatch` reads text from a local or remote file and generates
embeddings (since `2026.05.0`). It can split input into chunks and returns one
row per chunk with its index, content, and embedding vector.

## Java integration contracts

The server-side Notification API and Result Core API's `getNotifications()`
are deprecated from 5.26. Java integrations must stop depending on those
notification entry points.

Neo4j 2025.01 removes public Java APIs related to allocators, groups,
discovery, Raft, transaction memory, and query annotations. In particular,
replace removed `com.neo4j.dbms.seeding.SeedProvider` with
`DatabaseSeedProvider`; consult the upgrade reference for the complete removed
surface.

`CREATE DATABASE` in Cypher 25 accepts Java `Long` parameters in addition to
`Int`.

## Cloud and object-storage integration

`S3SeedProvider` is replaced by `CloudSeedProvider` from 5.26. Cypher 25 also
removes the `seedCredentials` database option; cloud credentials must come from
the provider's built-in mechanism.

Support for non-TLS/SSL MinIO endpoints in the `neo4j/neo4j-admin` Helm charts
is deprecated. Configure the replacement `s3Endpoint`.

## TLS key migration

Neo4j can still load PKCS #1 private keys whose header is:

```text
-----BEGIN RSA PRIVATE KEY-----
```

That legacy form is deprecated and will be removed. Replace affected server
keys before removal.

With OpenSSL provider 3.5 or later, `X25519MLKEM768` combines X25519 with
ML-KEM-768 for post-quantum hybrid key exchange. Separately, hostname
verification defaults to `true` after the breaking TLS-policy change, so ensure
certificates match configured peer names.

## Cluster procedure integrations

Update callers to the current entry points:

```text
dbms.cluster.recreateDatabase() -> dbms.recreateDatabase()
dbms.cluster.routing.getRoutingTable() -> dbms.routing.getRoutingTable()
dbms.cluster.uncordonServer() -> ENABLE SERVER
dbms.cluster.readReplicaToggle() -> dbms.cluster.secondaryReplicationDisable()
dbms.quarantineDatabase() -> dbms.unquarantineDatabase()
```

Cypher 25 removes `dbms.upgrade()` and `dbms.upgradeStatus()`. Do not invoke
them from automation.
