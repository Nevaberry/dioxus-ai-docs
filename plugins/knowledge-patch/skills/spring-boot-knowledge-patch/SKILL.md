---
name: spring-boot-knowledge-patch
description: Spring Boot 4.1.0 compatibility. Use for Spring Boot work.
license: MIT
version: 4.1.0
metadata:
  author: Nevaberry
---

# Spring Boot Knowledge Patch

Check the relevant topic reference before changing applications, libraries,
starters, build plugins, tests, container images, or operational configuration.
Do not rely on older package names, defaults, property keys, or extension points.

## Working method

1. Identify the affected layer: build/runtime, configuration, web, data, security,
   observability, testing, local infrastructure, or Spring AI.
2. Read the matching reference file from the index. Read more than one when a change
   crosses layers, such as an HTTP client carrying OAuth credentials or a data client
   using an SSL bundle.
3. Apply removals and renamed properties before adding features. Old compatibility
   paths often no longer exist.
4. Re-check defaults that affect exposure, redirects, proxy trust, serialization,
   bean selection, context propagation, or resource loading.
5. Keep version-sensitive workarounds only when the reference explicitly limits
   them to a particular release.

## Reference index

| Reference | Topics |
| --- | --- |
| [configuration-and-container.md](references/configuration-and-container.md) | Property binding and imports, bean selection, proxies, tasks, Docker Compose, service connections |
| [data-and-messaging.md](references/data-and-messaging.md) | JDBC, JPA, MongoDB, Cassandra, Redis, Spring Data, Batch, JMS, Kafka, Pulsar, RabbitMQ |
| [observability-and-operations.md](references/observability-and-operations.md) | Actuator access, health, SSL, structured logging, Micrometer, OpenTelemetry, Prometheus |
| [runtime-build-and-migration.md](references/runtime-build-and-migration.md) | Platform requirements, removed APIs, dependencies, Gradle, Maven, native images, Buildpacks |
| [security.md](references/security.md) | Security DSL migrations, OAuth, JWT, MFA, WebAuthn, SAML, CSRF, LDAP, trusted proxies |
| [spring-ai.md](references/spring-ai.md) | Spring AI BOM, advisors, RAG, memory, tools, evaluation, observability, MCP |
| [testing.md](references/testing.md) | MockMvc, RestTestClient, context lifecycle, bean overrides, Testcontainers, HtmlUnit, Spock |
| [web-and-http-clients.md](references/web-and-http-clients.md) | MVC, WebFlux, Jackson, HTTP clients, API versions, routing, binding, cookies, Gateway |

## Breaking changes and migration priorities

### Platform and namespace

- Use `jakarta.annotation` and `jakarta.inject`. The container no longer recognizes
  the corresponding `javax` annotations.
- Target Jakarta EE 11-compatible web containers. Servlet applications require the
  newer Servlet API and compatible Tomcat or Jetty generations.
- Treat Undertow as servlet-only when a compatible implementation is available;
  Undertow-specific WebSocket and low-level WebFlux integrations are gone.
- Check the build tool floor before upgrading. Recent Gradle 8 builds require a late
  8.x release, while Gradle 9 is supported.
- Require Java 21 for projects using the managed jOOQ line, even when the rest of the
  application can use the lower runtime floor.

### Removed and deprecated APIs

- Replace `ListenableFuture`, OkHttp 3 integration, theme support, JUnit 4
  TestContext support, legacy MVC XML configuration, and removed path-extension or
  optional-trailing-separator switches.
- Migrate `RestTemplate` callers toward `RestClient` or HTTP service interfaces.
- Stop treating `HttpHeaders` as a `MultiValueMap`; use header-specific operations.
- Move native Hibernate integration from the old `hibernate5` package to
  `org.springframework.orm.jpa.hibernate`.
- Replace Spring Security's `check` calls with `authorize`, remove DSL `and()` calls,
  and use `PathPatternRequestMatcher`.
- Use jar `tools` mode instead of removed `layertools` mode.

### Jackson and JSON

- Prefer Jackson 3. Most implementation classes moved to `tools.jackson` while
  annotations remain in `com.fasterxml.jackson`.
- Build mappers with `JsonMapper.builder()`, `CBORMapper.builder()`, or the matching
  mapper builder; there is no Jackson 3 equivalent of
  `Jackson2ObjectMapperBuilder`.
- Remember that the Kotlin Serialization converter is placed ahead of other JSON
  converters but handles annotated serializable types by default.
- Use the centralized servlet message-converter builder when MVC and blocking HTTP
  clients must share converter configuration.

### Configuration and bean selection

- Put `@Valid` on nested configuration-property fields that require cascaded
  validation.
- Supply only literal `true` or `false` to `.enabled` properties.
- Expect constructor-bound `Optional` values to become `Optional.empty()` rather
  than `null`.
- Re-evaluate bean-condition matching when generic return types, annotations,
  `@Primary`, `@Fallback`, `defaultCandidate=false`, qualifiers, or parameter names
  are involved.
- Remove invalid `void @Bean` methods, `@Autowired @Bean` methods, and conditional
  component scans that depend on bean-registration-time conditions.
- Use `spring.config.import=env:NAME` for a multiline environment variable and add
  an `encoding` option when an imported properties resource is not ISO-8859-1.

### HTTP behavior

- Finish a `RestClient.retrieve()` chain with a terminal response operation; calling
  `retrieve()` alone sends nothing.
- Assume auto-configured blocking and reactive clients follow redirects unless
  redirects are explicitly disabled.
- Select a request factory explicitly when classpath ordering is not acceptable.
- Account for cookies through the common cookie-handling setting and apply an
  `InetAddressFilter` when resolved destinations need SSRF controls.
- Migrate trailing-slash behavior to `UrlHandlerFilter` and request mappings to
  `PathPattern`.
- Configure API-version resolution and deprecation centrally, then use the same
  version contract in clients and tests.

### Security behavior

- Do not trust forwarded headers at a gateway until a trusted-proxy regular
  expression is configured.
- Expect relative login redirects by default and update assertions that compare
  absolute `Location` values.
- Use the dedicated SPA CSRF mode for browser single-page applications.
- Account for authorization-server PKCE defaults and removed password-grant support.
- Configure JWT authority claim expressions instead of a claim name when authorities
  require SpEL transformation; the two forms are mutually exclusive.

### Operations and exposure

- Configure Actuator endpoint access with `none`, `read-only`, or `unrestricted`.
  Exposure alone does not grant access.
- Explicitly grant unrestricted access to `heapdump` when it is intentionally
  exposed.
- Use `management.tracing.export.enabled` for tracing export. The older generic
  tracing enablement switch is not the export control.
- Revisit SSL dashboards: soon-expiring chains remain `VALID` and are reported
  separately as expiring chains.
- Use the current Prometheus Pushgateway client, an `address` property, and the
  current structured-logging field layout.

## High-use additions

### Dependency injection, tasks, and resilience

- Use background bean bootstrapping for expensive beans and JPA initialization only
  when a suitable executor is available.
- Compose multiple ordered `TaskDecorator` beans; decorators apply to both task
  execution and scheduling.
- Use `BeanRegistrar` for programmatic multi-bean registration.
- Enable core `@Retryable` and `@ConcurrencyLimit` support with
  `@EnableResilientMethods`.
- Override the global proxy strategy per bean with `@Proxyable`.

### HTTP services and web APIs

- Group annotated HTTP service interfaces with `@ImportHttpServices` and customize
  each group through an `AbstractHttpServiceRegistrar`.
- Use HTTP service interfaces with OAuth and Boot auto-configuration where a
  declarative client is preferable.
- Stream HTTP interface request or response bodies without forcing full buffering.
- Render multiple MVC or WebFlux fragments for HTML-over-the-wire applications.
- Use Spring gRPC integration for standalone Netty or servlet HTTP/2 clients and
  servers.

### Data and messaging

- Use Spring Data's portable `Vector` type across supported stores.
- Build MongoDB vector indexes and `$vectorSearch` pipelines, or Cassandra SAI vector
  indexes and ANN sorts.
- Generate Spring Data JDBC identifiers with `@Sequence` and stream aggregates from
  `JdbcAggregateOperations`.
- Delay pooled JDBC checkout with `spring.datasource.connection-fetch=lazy` when a
  transaction may not execute SQL.
- Use the MongoDB-backed Spring Batch starter when job metadata belongs in MongoDB.
- Let Boot discover `@RedisListener` endpoints or configure static Lettuce
  master/replica nodes.

### Testing

- Prefer AssertJ-based `MvcTester` for fluent MockMvc assertions.
- Use `RestTestClient` for synchronous live-server or MVC-bound REST tests.
- Register context-derived dynamic properties with `DynamicPropertyRegistrar` beans.
- Expect cached test contexts to pause background work while inactive unless that
  behavior is configured otherwise.
- Use `@AutoConfigureWebServer` when a test needs an embedded server factory without
  starting the full application.

### Spring AI

- Import the Spring AI BOM for aligned dependencies.
- Compose prompt enrichment, memory, retrieval, and evaluation through advisors and
  their dedicated SPIs.
- Prefer portable vector-store filters and the ETL document pipeline for ingestion.
- Expose or consume tools over MCP with the dedicated client and server starters.

## Final checks

- Search configuration for removed or renamed keys before running tests.
- Verify generated configuration metadata when external property types are used.
- Exercise redirect, proxy, cookie, JSON, and security behavior with integration
  tests rather than assuming earlier defaults.
- Check Actuator access separately from web exposure.
- Validate native resource globs and reflection hints after migrating runtime hints.
- Inspect container-image builder assumptions: minimal builders may contain no shell.
