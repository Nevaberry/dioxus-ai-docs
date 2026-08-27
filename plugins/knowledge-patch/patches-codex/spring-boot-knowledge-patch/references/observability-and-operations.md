# Observability, Logging, Actuator, and Operations

## Contents

- [Actuator access and operational endpoints](#actuator-access-and-operational-endpoints)
- [SSL health, info, and metrics](#ssl-health-info-and-metrics)
- [OpenTelemetry and context propagation](#opentelemetry-and-context-propagation)
- [Prometheus and structured logging](#prometheus-and-structured-logging)
- [Application and runtime information](#application-and-runtime-information)

## Actuator access and operational endpoints

### Endpoint access levels

Endpoint enablement is replaced by the access levels `none`, `read-only`, and
`unrestricted`. Configure the default with `management.endpoints.access.default`
and one endpoint with `management.endpoint.<id>.access`. Cap every endpoint with
`management.endpoints.access.max-permitted` (since `3.4.0`).

The older `enabled-by-default`, per-endpoint `enabled`, and
`@Endpoint(enableByDefault=...)` forms are deprecated. Web exposure and endpoint
access are separate decisions.

### Heapdump

The `heapdump` endpoint defaults to `access=none`. Merely exposing it over HTTP is
insufficient (since `3.5.0`):

~~~yaml
management:
  endpoints:
    web:
      exposure:
        include: heapdump
  endpoint:
    heapdump:
      access: unrestricted
~~~

### Quartz, mappings, SSL operations, and matchers

Since `3.5.0`:

- trigger a Quartz job with
  `POST /actuator/quartz/jobs/{groupName}/{jobName}`;
- `ssl.chains` and `ssl.chain.expiry` report SSL-bundle validity and time to
  expiry;
- the mappings endpoint includes WebMvc functional routes; and
- servlet and reactive `EndpointRequest` matchers can restrict by HTTP method.

## SSL health, info, and metrics

### Certificate reporting

Since `3.4.0`, `/actuator/info` reports SSL-bundle certificate validity, issuer,
and subject. The SSL health indicator marks invalid certificates
`OUT_OF_SERVICE`. Configure the expiry-warning window with
`management.health.ssl.certificate-validity-warning-threshold`.

### Revised expiry semantics

Since `4.0.0`, SSL info does not apply the warning threshold: a certificate near
expiry remains `VALID` rather than `WILL_EXPIRE_SOON`. SSL health also keeps the
status `VALID` while listing affected chains in `expiringChains`. The warning
threshold still determines which chains enter that list.

Since `4.1.0`, certificate-expiry metrics include truststores as well as other SSL
material. The info endpoint also reports truststore certificates.

## OpenTelemetry and context propagation

### Application grouping

`spring.application.group` groups related applications and appears in log messages
and the OpenTelemetry `Resource`. Suppress it from logs with
`logging.include-application.group=false` (since `3.4.0`).

Since `3.5.0`, the group supplies the OpenTelemetry `service.namespace` resource
attribute instead of the deprecated `service.group`.

### OTLP transport, logs, and switches

Since `3.4.0`:

- `management.otlp.tracing.transport=grpc` sends spans over gRPC rather than HTTP;
- `management.otlp.logs.*` auto-configures the OTLP log exporter and logger
  provider;
- logging and tracing support `management.otlp.logging.connect-timeout` and
  `management.otlp.tracing.connect-timeout`;
- export controls include `management.logging.export.enabled`,
  `management.otlp.logging.export.enabled`, and
  `management.otlp.tracing.export.enabled`; and
- OTLP log shipping also supports gRPC.

When virtual threads are enabled, the OTLP meter registry uses them (since
`3.4.0`).

### Environment and exporter configuration

Since `3.5.0`, Boot reads `OTEL_RESOURCE_ATTRIBUTES` and `OTEL_SERVICE_NAME`;
configuration properties take precedence. Custom `BatchSpanProcessor` beans and
settings under `management.tracing.opentelemetry.export` are supported.

### Starter and tracing property migration

`spring-boot-starter-opentelemetry` includes OTLP metrics and tracing dependencies
and auto-configures the OpenTelemetry SDK (since `4.0.0`).

The tracing export switch is `management.tracing.export.enabled`, replacing
`management.tracing.enabled`. `ConditionalOnEnabledTracing` was renamed to
`ConditionalOnEnabledTracingExport`. Boot also supports `@MeterTag` with a SpEL
`ValueExpressionResolver` and `@ObservationKeyValue`.

### Expanded SDK controls

`management.opentelemetry.enabled=false` installs no-op SDK providers, retains
propagators, and omits unnecessary tracing and logging beans (since `4.1.0`).
Boot also configures:

- batch log processing;
- samplers;
- span and log limits;
- most standard OpenTelemetry environment variables;
- SSL bundles for OTLP exporters;
- OTLP metric compression and exemplars; and
- truststore-certificate expiry metrics.

### Context propagation and observation conventions

Framework tracing context propagates automatically into Kotlin coroutines through
`PropagationContextElement` (since `4.0.0-framework-7`).

Since `4.1.0`, observability context also propagates automatically into `@Async`
methods. Custom Kafka and Rabbit listener/template observation conventions and JVM
memory, thread, class-loading, and CPU meter conventions are applied automatically
to auto-configured components.

## Prometheus and structured logging

### Pushgateway migration

Pushgateway export requires
`io.prometheus:prometheus-metrics-exporter-pushgateway`. Replace `base-url` with the
host-and-port `address` property. The current client also supports HTTPS, token
authentication, and text output instead of protobuf (since `3.5.0`):

~~~properties
management.prometheus.metrics.export.pushgateway.address=pushgateway:9091
management.prometheus.metrics.export.pushgateway.scheme=https
management.prometheus.metrics.export.pushgateway.token=${PUSHGATEWAY_TOKEN}
management.prometheus.metrics.export.pushgateway.format=text
~~~

### Structured JSON

ECS JSON uses the nested representation and stores Logback and Log4j markers in
`tags`. Configure stack traces and context placement under
`logging.structured.json.stacktrace.*` and `logging.structured.json.context.*`.
More than one JSON customizer may be configured (since `3.5.0`).

### Log4j rotation

Boot's Log4j setup supports `size` (the default), `time`, `size-and-time`, and
`cron` file-rotation strategies (since `4.1.0`).

## Application and runtime information

### Info endpoint additions

Since `4.1.0`, the info endpoint can report process timing, locale, timezone,
working directory, and truststore certificates.

### Console logging

Disable console output with `logging.console.enabled=false` (since `4.0.0`).

### Dynatrace migration

Dynatrace V1 configuration is deprecated in favor of Dynatrace V2 (since
`4.1.0`).
