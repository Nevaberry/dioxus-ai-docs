# Server Configuration and Operations

## Preserving literal environment values

Values supplied through `KC_` environment variables undergo expression evaluation. This includes resolving `${...}` and collapsing `$$` to `$`, which can silently modify a secret.

Use the equivalent `KCRAW_` name when the value must preserve dollar characters exactly. Defining both forms for the same configuration key is a startup error.

```bash
export KCRAW_DB_PASSWORD='my$$pa${vault}word'
```

## Mapping environment keys exactly

Environment-key normalization cannot round-trip every option name, particularly logging categories that contain underscores. Pair an arbitrary `KC_` value variable with a same-suffix `KCKEY_` variable that supplies the exact option key.

```bash
export KC_MYKEY=debug
export KCKEY_MYKEY=log-level-package.class_name
```

## Optimized-build boundaries

Every build option is persisted in plaintext, including a build option supplied through the Java KeyStore configuration source. Never put a secret in a build option.

With `start --optimized`, a build option repeated at runtime is ignored when it matches the built value and rejected when it differs. Run another build to change it.

```bash
bin/kc.sh build --db=postgres
bin/kc.sh start --optimized
```

## Stable provider JAR timestamps

Container tooling can change a provider JAR's modification time between optimized build and runtime, causing startup to report that the provider changed. Assign provider files a deterministic timestamp before running the build.

```dockerfile
ADD --chown=keycloak:keycloak --chmod=644 some-jar.jar /opt/keycloak/providers/
RUN touch -m --date=@1743465600 /opt/keycloak/providers/*
RUN /opt/keycloak/bin/kc.sh build
```

## Bounded request queues

The HTTP request queue is unlimited by default. Set `http-max-queued-requests` to cap requests waiting for processing. Requests beyond the limit receive an immediate HTTP 503 response.

```bash
bin/kc.sh start --http-max-queued-requests=1000
```

## Bootstrap readiness semantics

When health endpoints are enabled, HTTP(S) and management endpoints can open while initialization continues. Startup and liveness may report UP while readiness remains DOWN.

Route traffic using `/health/ready`. Set `server-async-bootstrap=false` when endpoints must not open until initialization completes.

```bash
bin/kc.sh start --server-async-bootstrap=false
```

## Metrics and management-interface defaults

Keycloak 25 enables embedded-cache and HTTP server metrics by default. Health and metrics are served on the separate management listener at port `9000`, not on application ports.

`--legacy-observability-interface=true` temporarily restores the former listener placement. Control histogram output with `cache-metrics-histograms-enabled`, `http-metrics-histograms-enabled`, and `http-metrics-slos`.

## Outbound HTTP response cap

Since 25, HTTP responses consumed from brokers and other external services are capped at 10 MB by default. Change the byte limit with `spi-connections-http-client-default-max-consumed-response-size`.

```bash
bin/kc.sh start --spi-connections-http-client-default-max-consumed-response-size=1000000
```

## Bootstrap administrator recovery

Keycloak 26 deprecates `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD`. Use the general bootstrap options or the newer environment variables for initial access and recovery.

```bash
export KC_BOOTSTRAP_ADMIN_USERNAME=admin
export KC_BOOTSTRAP_ADMIN_PASSWORD=change-me
```

## Container heap sizing

Keycloak 24 container images replace fixed `-Xms` and `-Xmx` values with percentage-based sizing. The default maximum heap is 70% of available container memory.

Always set a container memory limit. Without one, the calculated heap can grow against the host's total memory.

## Secret confidentiality and rotation

The 26.7.2 fixes prevent Admin REST from leaking a vault-resolved rotated client secret and stop `show-config` from printing the vault keystore password in cleartext.

Disabling client-secret rotation now invalidates the rotated secret instead of leaving it accepted. Verify this behavior during any rotation rollback or policy change.
