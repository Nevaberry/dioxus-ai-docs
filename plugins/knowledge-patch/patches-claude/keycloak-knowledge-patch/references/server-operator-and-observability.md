# Server, Operator, and Observability

## Preserve exact and literal environment values

`KC_` values undergo expression evaluation: `${...}` is resolved and `$$`
collapses to `$`. Use the equivalent `KCRAW_` name to preserve dollar
characters exactly. Defining both forms for the same option is a startup error.

```bash
export KCRAW_DB_PASSWORD='my$$pa${vault}word'
```

Environment-key normalization cannot represent every option name, particularly
logging categories containing underscores. Pair an arbitrary `KC_` value
variable with the same-suffix `KCKEY_` variable containing the exact option key.

```bash
export KC_MYKEY=debug
export KCKEY_MYKEY=log-level-package.class_name
```

## Optimized-build boundaries

Every build option is persisted in plaintext, including values supplied by the
Java KeyStore configuration source. Never use build options for secrets. With
`start --optimized`, a repeated build option is ignored when it matches the
built value and rejected when it differs; rebuild to change it.

```bash
bin/kc.sh build --db=postgres
bin/kc.sh start --optimized
```

Docker can alter provider JAR modification times between optimized build and
runtime, making startup report a changed provider. Set deterministic timestamps
before building.

```dockerfile
ADD --chown=keycloak:keycloak --chmod=644 some-jar.jar /opt/keycloak/providers/
RUN touch -m --date=@1743465600 /opt/keycloak/providers/*
RUN /opt/keycloak/bin/kc.sh build
```

## Request queues and bootstrap readiness

The HTTP request queue is unlimited by default. Set
`http-max-queued-requests` to cap waiting requests; excess requests receive an
immediate HTTP 503.

```bash
bin/kc.sh start --http-max-queued-requests=1000
```

With health enabled, HTTP(S) and management endpoints open while initialization
continues. Startup and liveness can be UP while readiness is DOWN. Route traffic
using `/health/ready`, or set `--server-async-bootstrap=false` to delay opening
endpoints until initialization finishes.

## Datasources, transactions, and health

Exclude individual optional additional datasources from health checks when
their failure must not make the entire deployment unhealthy. (26.7.0)

Keycloak 25 defaults `transaction-xa-enabled` to false, enables transaction
recovery, and stores recovery logs under `data/transaction-logs`. From 26, a
deployment with multiple datasources can have at most one non-XA datasource.
Enable XA on the default datasource with `--transaction-xa-enabled=true` and
set each additional datasource's
`quarkus.datasource.<name>.jdbc.transactions=xa`.

From 26.7, PostgreSQL transactions touching only ephemeral session,
login-failure, or event tables use asynchronous commit; logout remains
synchronous. Disable this with
`--spi-connections-jpa--quarkus--async-commit=false`.

## Truststores, FIPS, and TLS verification

Replace 24-era `spi-truststore-file-*` and truststore-related
`https-trust-store-*` settings with `conf/truststores` or `truststore-paths`,
and replace the old hostname-verification policy with
`tls-hostname-verifier`. The always-populated truststore means direct WebAuthn
attestation requires the authenticator CA to be trusted.

The verifier default changes from `WILDCARD` to `DEFAULT` in 25. In 26,
keystore and truststore types are inferred from `.p12`, `.jks`, and `.pem`
extensions unless explicitly overridden.

Generated system truststores sourced from `conf/truststores` or
`--truststore-paths` use BCFKS in strict FIPS mode so BCFIPS loads them in
approved mode. Default and non-strict FIPS deployments keep using PKCS12 when
supported. (26.7.0)

## Hostname and reverse-proxy migration

Hostname v2 is the default from 25. `hostname` accepts a host or full URL;
`hostname-admin` requires a full URL. Remove separate path and port options.
Select HTTPS with a full HTTPS URL. Dynamic backchannel resolution requires
`hostname-backchannel-dynamic=true` and a full frontend URL.

Keycloak 26 removes hostname v1 and `proxy`. Replace edge or re-encrypt setups
with one trusted `proxy-headers` format and suitable hostname and HTTP settings.

```bash
bin/kc.sh start \
  --hostname=https://sso.example.com:8543/auth \
  --proxy-headers=xforwarded \
  --http-enabled=true
```

## Password hashing and garbage collection

Keycloak 24 changes the default password hash from PBKDF2-SHA256 to
PBKDF2-SHA512 with 210,000 iterations. Passwords without an explicit realm
policy rehash on login. Keycloak 25 makes Argon2 the non-FIPS default and
changes the collector from ParallelGC to G1GC; expect another one-time rehash
and temporary database activity.

## Preserve sessions across the 25-to-26 upgrade

To retain online sessions from 24, upgrade to 25 with preview
`persistent-user-sessions` enabled on that first upgrade. Only sessions already
backed by remote Infinispan or embedded-cache JDBC persistence can migrate.
Enabling it later cannot safely merge persisted and non-persisted sessions.

Keycloak 26 changes cache marshalling from JBoss Marshalling to incompatible
Protostream and clears every cache. A direct upgrade that skips the 25
persistence migration loses sessions.

## Persistent-session cache and expiry semantics

All sessions persist by default in 26. The standard cache file limits every
session cache to 10,000 entries with one owner; custom cache XML should apply
equivalent bounds. The two-minute idle-time grace period is removed. Revoked
access tokens persist across embedded-cache restarts by default; opt out with
`spi-single-use-object-infinispan-persist-revoked-tokens`.

## Metrics and management-interface defaults

Keycloak 25 enables embedded-cache and HTTP server metrics by default and puts
health and metrics on the management listener at port `9000`, not application
ports. `--legacy-observability-interface=true` temporarily restores the old
placement. Configure histograms with `cache-metrics-histograms-enabled`,
`http-metrics-histograms-enabled`, and `http-metrics-slos`.

## Outbound HTTP response cap

Responses consumed from brokers and other external services are capped at 10
MB by default from 25. Change the byte limit with
`spi-connections-http-client-default-max-consumed-response-size`.

```bash
bin/kc.sh start --spi-connections-http-client-default-max-consumed-response-size=1000000
```

## Runtime cache configuration and external Infinispan

`cache`, `cache-stack`, and `cache-config-file` stop being build options in 25
and are runtime-only. Remove them from image-build commands or the server can
silently fall back to runtime cache defaults.

External multi-site deployments require Infinispan 15 or later from 25. In 26,
multi-site mode ignores distributed-cache and remote-store XML; use
`cache-remote-*` options or equivalent custom-resource fields. A single-site
external store is rejected unless experimental `cache-embedded-remote-store`
is enabled. Use persistent sessions for normal single-site restart survival.

## Multi-cluster v2

Enable preview multi-cluster v2 with `stateless`. It removes the external
Infinispan cluster and fencing infrastructure. Nodes connect directly through
embedded caches, use the synchronously replicated database as the source of
truth, and propagate invalidations through a database-backed outbox. (26.7.0)

The 26.7.2 fixes allow upgrades involving preview features to initialize the
stateless cluster provider successfully.

## Large-table index migrations

Automatic migration skips selected new indexes and prints SQL for manual
execution when a table already exceeds 300,000 rows: `USER_ATTRIBUTE` and
`FED_USER_ATTRIBUTE` in 24, `RESOURCE_SERVER_PERM_TICKET` in 25, and
`IDENTITY_PROVIDER` in 26. Run the emitted statements after startup; do not
assume schema migration created those indexes.

## Operator installation and upgrade behavior

Install the Operator declaratively on vanilla Kubernetes with kustomize rather
than applying separate manifests. (26.7.0)

Preview cluster-wide mode lets one Operator reconcile `Keycloak` resources in
all namespaces. Use OLM `AllNamespaces` or, outside OLM, the `cluster-wide`
kustomization overlay. (26.7.0)

From 24, referenced Secrets and ConfigMaps are polled rather than watched, so
changes may take about one minute. Advanced properties move from
`operator.keycloak` to `kc.operator.keycloak`. Missing custom-resource settings
default to a `1700MiB` memory request and `2GiB` limit. Version 26 adds default
pod affinities and stops implicitly supplying `proxy=passthrough`.

## Container heap sizing

Keycloak 24 container images use percentage heap sizing instead of fixed
`-Xms` and `-Xmx`; maximum heap defaults to 70% of available container memory.
Always set a container memory limit or the calculation can use total host
memory.

## Removed bundled runtime components

Keycloak 25 stops bundling the Oracle JDBC driver and removes the legacy
LinkedIn OAuth provider. Install a compatible Oracle driver and use the
remaining LinkedIn OIDC provider. Keycloak 26 removes the GELF handler, adapter
and miscellaneous BOMs, `keycloak-test-helper`, and the JEE admin client while
retaining the Jakarta admin client.

## LDAP pool and binary decoding

In 26, realm-level LDAP connection-pool settings are ignored because pooling is
JVM-wide; move them to the documented system properties. From 26.7, existing
binary user-attribute mappers migrate to `base64`, while new mappers default to
`auto` and can explicitly use `base64` or `uuid`. Existing group mappers retain
base64 behavior and new group mappers enable UUID decoding.

## Bootstrap administrator recovery

Keycloak 26 deprecates `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD`. Use the
general bootstrap options or their new environment variables for initial
access and recovery.

```bash
export KC_BOOTSTRAP_ADMIN_USERNAME=admin
export KC_BOOTSTRAP_ADMIN_PASSWORD=change-me
```

## Graceful shutdown

From 26.7, the default shutdown timeout is ten seconds instead of one second;
clustered nodes also wait for cache rebalance. Roll one node at a time. Set
`shutdown-timeout=1s` only when the earlier behavior is intentional.

## Secrets and generated AES keys

New client secrets generated from 26.7 are always 86 characters, so downstream
stores must accept that length. Newly generated `aes-generated` providers use
256-bit keys; existing providers stay unchanged. Rotate by adding a 32-byte,
higher-priority provider and retain the old provider until earlier sessions
expire.

In 26.7.2, Admin REST no longer exposes vault-resolved rotated client secrets,
`show-config` no longer prints the vault keystore password, and disabling
client-secret rotation invalidates the rotated secret immediately.
