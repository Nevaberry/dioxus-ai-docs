# Deployment and Storage Migrations

## Additional-datasource health exclusions

Since 26.7.0, an individual additional datasource can be excluded from health checks. Use this for an optional datasource whose failure should not mark the entire deployment unhealthy.

## FIPS-compatible generated truststores

Generated system truststores sourced from `conf/truststores` or `--truststore-paths` use BCFKS in strict FIPS mode, allowing BCFIPS to load them in approved mode. Default and non-strict FIPS deployments continue to use PKCS12 where supported.

## Multi-cluster v2

The preview multi-cluster v2 architecture removes the external Infinispan cluster and fencing infrastructure. Keycloak nodes connect directly using embedded caches, treat the synchronously replicated database as the source of truth, and propagate invalidations through a database-backed outbox.

Enable this architecture with the `stateless` feature.

## Installing the Operator with kustomize

The Keycloak Operator can be installed declaratively on vanilla Kubernetes with kustomize rather than by applying separate manifest files.

Preview cluster-wide mode lets one Operator reconcile `Keycloak` resources in every namespace. Select OLM's `AllNamespaces` install mode, or use the `cluster-wide` kustomization overlay for non-OLM installations.

## Truststore and hostname-verification migration

For Keycloak 24, replace `spi-truststore-file-*` and truststore-related `https-trust-store-*` settings with `conf/truststores` or `truststore-paths`. Replace the old hostname-verification policy with `tls-hostname-verifier`.

The always-populated truststore means direct WebAuthn attestation now requires the authenticator CA to be trusted.

In 25, the hostname-verifier default changes from `WILDCARD` to `DEFAULT`. In 26, keystore and truststore type is inferred from extensions such as `.p12`, `.jks`, and `.pem` unless explicitly overridden.

## Hostname and reverse-proxy migration

Hostname v2 becomes the default in 25. `hostname` accepts either a host or a full URL, while `hostname-admin` requires a full URL. Separate hostname path and port options are removed. A full HTTPS URL selects HTTPS.

Dynamic backchannel resolution requires `hostname-backchannel-dynamic=true` together with a full frontend URL.

Keycloak 26 removes hostname v1 and `proxy`. Replace edge and re-encrypt arrangements with one trusted `proxy-headers` format and the matching hostname and HTTP settings.

```bash
bin/kc.sh start \
  --hostname=https://sso.example.com:8543/auth \
  --proxy-headers=xforwarded \
  --http-enabled=true
```

## Password-hashing transition

Keycloak 24 changes the password-hashing default from PBKDF2-SHA256 to PBKDF2-SHA512 with 210,000 iterations. Passwords in realms without an explicit policy are rehashed on login.

Keycloak 25 makes Argon2 the non-FIPS default and changes the default garbage collector from ParallelGC to G1GC. Expect another one-time password rehash and temporary database load.

## Preserving sessions through the 25-to-26 upgrade

To retain online sessions originating in 24, upgrade to 25 with preview `persistent-user-sessions` enabled on that first upgrade. Only sessions already backed by remote Infinispan or embedded-cache JDBC persistence can migrate. Enabling the feature later cannot safely merge persisted and non-persisted sessions.

Keycloak 26 switches cache marshalling from JBoss Marshalling to incompatible Protostream and clears every cache. A direct upgrade that skips the 25 persistence migration loses sessions.

## Persistent-session cache and expiry semantics

In 26, all sessions are persisted by default. The standard cache file limits each session cache to 10,000 entries with one owner; custom cache XML should apply equivalent limits.

The former two-minute idle-time grace period is removed. Revoked access tokens are persisted across embedded-cache restarts by default. Opt out with `spi-single-use-object-infinispan-persist-revoked-tokens` only when that behavior is intentional.

## Runtime cache configuration

Since 25, `cache`, `cache-stack`, and `cache-config-file` are runtime options, not build options. Remove them from image-build commands; otherwise the server can silently use its runtime cache defaults.

## XA defaults and additional datasources

Keycloak 25 changes `transaction-xa-enabled` to default `false`, enables transaction recovery, and stores transaction logs under `data/transaction-logs`.

From 26, a deployment with multiple datasources may have at most one non-XA datasource. Enable XA for the default datasource with `--transaction-xa-enabled=true`. Configure each additional datasource with `quarkus.datasource.<name>.jdbc.transactions=xa`.

## Large-table index migrations

Automatic migration skips some indexes and prints SQL for manual execution when the affected table already exceeds 300,000 rows:

- In 24, inspect `USER_ATTRIBUTE` and `FED_USER_ATTRIBUTE`.
- In 25, inspect `RESOURCE_SERVER_PERM_TICKET`.
- In 26, inspect `IDENTITY_PROVIDER`.

Plan to execute the emitted statements after startup. Do not assume the schema migrator created these indexes.

## Operator upgrade defaults

From 24, referenced Secrets and ConfigMaps are polled instead of watched, so changes can take about one minute. Advanced property keys move from `operator.keycloak` to `kc.operator.keycloak`.

When the custom resource omits resource settings, the Operator defaults to a `1700MiB` memory request and `2GiB` limit. Keycloak 26 adds default pod affinities and no longer implicitly supplies `proxy=passthrough`.

## External Infinispan deployment boundaries

Keycloak 25 requires Infinispan 15 or newer and supports an external server for multi-site deployments.

In 26, multi-site mode ignores distributed-cache and remote-store XML. Use `cache-remote-*` options or equivalent custom-resource fields. A single-site external store is rejected unless temporary experimental `cache-embedded-remote-store` is enabled; use persistent sessions for restart survival instead.

## LDAP pool and binary decoding

In 26, realm-level LDAP connection-pool settings are ignored because pooling is JVM-wide. Move them to the documented system properties.

In 26.7, existing binary user-attribute mappers migrate to `base64`; new mappers default to `auto` and may explicitly select `base64` or `uuid`. Existing group mappers retain base64 behavior, while new group mappers enable UUID decoding.

## Graceful shutdown timeout

In 26.7, the default shutdown timeout increases from one second to ten seconds. Clustered nodes also wait for cache rebalance. Apply rolling changes one node at a time, and set `shutdown-timeout=1s` only when the former behavior is intentional.

## PostgreSQL asynchronous commit

In 26.7, PostgreSQL transactions that touch only ephemeral session, login-failure, or event tables use asynchronous commit. Logout remains synchronous.

Disable this optimization with `--spi-connections-jpa--quarkus--async-commit=false`.

## Stateless upgrade and organization corrections

The 26.7.2 fixes prevent upgrades involving preview features from failing when the stateless cluster provider initializes. They also allow organization members to be added while `stateless:v1` is enabled.
