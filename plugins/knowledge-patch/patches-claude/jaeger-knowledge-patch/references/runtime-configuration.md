# Runtime and Configuration

## Unified binary and roles

- Since **2.0.0**, v2 is distributed as the `jaeger` binary and image. The
  `jaeger-agent` artifact is absent, so packaging, process supervisors, and
  launch manifests must stop installing or starting it.
- Since **2.14.0**, the v1 `collector`, `query`, `ingester`, and `all-in-one`
  components are no longer published, and v1 Kafka-ingester code is removed.
  Remaining v1 utilities carry v2.x.x versions. Move service and Compose
  definitions to the unified v2 binary.
- The **v2-runtime-model** defines collector, query, Kafka ingester, all-in-one,
  and agent as configurations of that runtime. Collector receives and stores
  traces; query serves APIs and UI; ingester consumes Kafka and stores traces;
  all-in-one combines collector and query. For an agent that must also process
  metrics and logs, prefer the standard OpenTelemetry Collector.
- Jaeger is itself a customized OpenTelemetry Collector distribution containing
  upstream, contrib, and Jaeger components. A separate Collector is optional,
  not mandatory. Use one as a sidecar, host agent, or remote preprocessing tier
  for enrichment and sampling. Use OpenTelemetry Collector Builder when a
  custom Jaeger distribution needs a different component set.

## Collector-style configuration

- In the **v2-runtime-model**, v2 uses Collector-style YAML and does not
  automatically map v1 Jaeger environment variables to new settings.
  Interpolate deploy-time values with environment expressions and use `--set`
  to override dotted paths, including paths in the built-in all-in-one config.

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "${env:JAEGER_LISTEN_HOST:-localhost}:4317"
```

```sh
jaeger --config config.yaml \
  --set=receivers.otlp.protocols.grpc.endpoint=0.0.0.0:4317
```

- Since **2.1.0**, a container listen host can be parameterized and overridden.
  Review explicit bindings when reusing one configuration inside and outside a
  container.
- Since **2.0.0**, query HTTP/TLS server settings use OpenTelemetry
  configuration and the broader query configuration was refactored. Review
  every v1 query-server setting during migration.
- Since **2.4.0**, query HTTP and gRPC servers cannot share a listen port.
  Assign distinct ports.

## Reverse proxies and paths

In the **v2-runtime-model**, `jaeger_query.base_path` is the prefix on requests
that reach Jaeger. Leave it `/` when a reverse proxy strips the externally
visible prefix, or set it to the forwarded prefix. The value must start with
`/` and cannot contain `..` or duplicate slashes.

```yaml
extensions:
  jaeger_query:
    base_path: /jaeger
```

Frontend discovery and API routing behavior are detailed in [ui.md](ui.md).

## Feature and command changes

- The `jaeger features` feature-gate discovery command appeared in **2.3.0**
  but was reverted in **2.4.0**. Do not build scripts or runbooks around it.
- Since **2.3.0**, `esmapping-generator` is a subcommand of `jaeger`, not a
  separate executable. Backend-specific generation options are covered in
  [storage-backends.md](storage-backends.md).

## Images and deployment inputs

- Since **2.0.0**, v2 images do not use `v1` or `v1.x` tags. Publishing avoids
  an unversioned image tag, and `latest` is attached only to versioned images
  produced from the main branch. Pin an explicit version for reproducibility.
- Since **2.8.0**, shipped Compose examples pull Jaeger images from
  `cr.jaegertracing.io`; allow that registry in mirrors, policies, and firewalls.
- Since **2.7.0**, `docker-compose-elasticsearch.yml` provides a shipped v2
  Elasticsearch example. Treat it as a starting point and supply production
  persistence, credentials, resource limits, and exposure controls.

## Source builds and downstream code

- Since **2.5.0**, many repository packages moved under Go `internal`
  boundaries: `pkg/{testutils,otelsemconv,cassandra,adjuster,es,distributedlock,
  httpmetrics,gogocodec,httpfs,bearertoken,boundqueue,metrics,kafka,prometheus,
  version,gzipfs,jtracer,telemetry,fswatcher,config,healthcheck,hostname,
  recoveryhandler,tenancy}`, `model/proto`, `model/converter`,
  `model/json/model.go`, and `proto-gen`. `pkg/netutils` was removed and
  `pkg/normalizer` moved into the collector. External modules must replace,
  copy, or own dependencies on those non-public paths.
- Since **2.12.0**, release binaries include `riscv64`.
- Since **2.16.0**, source builds require Go 1.25.7 consistently across the
  codebase.
- Since **2.20.0**, Jaeger UI and embedded-UI builds use pnpm rather than npm.
  Update local development and build automation accordingly.
