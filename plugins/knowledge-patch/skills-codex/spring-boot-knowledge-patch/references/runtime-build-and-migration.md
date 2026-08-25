# Runtime, Build, Dependencies, and Migration

## Contents

- [Platform baselines](#platform-baselines)
- [Build tool requirements](#build-tool-requirements)
- [Framework removals and source breaks](#framework-removals-and-source-breaks)
- [Deprecation directions](#deprecation-directions)
- [Native images and runtime hints](#native-images-and-runtime-hints)
- [OCI images and packaging](#oci-images-and-packaging)
- [Managed dependency generations](#managed-dependency-generations)
- [Extension API migrations](#extension-api-migrations)
- [Runtime controls](#runtime-controls)

## Platform baselines

### JDK and library constraints before Jakarta EE 11

The `3.4.0-framework-6.2` batch targets JDK 17–23 and Jakarta EE 9–10.
Its relevant library constraints are:

- FreeMarker 2.3.33;
- HtmlUnit 4.2;
- Protobuf 3.29, with codec and converter support for Protobuf 4.x;
- Hibernate 6.5 specifically for GraalVM native images; and
- Jackson 2.18 or 2.19 recommended, with runtime compatibility at 2.15 or newer.

### Jakarta EE 11 platform

The `4.0.0-framework-7` batch retains JDK 17 as the floor and recommends JDK 25.
It moves to:

- Jakarta EE 11;
- Servlet 6.1 and WebSocket 2.2;
- JPA 3.2 and Bean Validation 3.1;
- GraalVM 25 exact reachability metadata;
- Netty 4.2;
- Kotlin 2.2; and
- JUnit 6.

Web applications need compatible containers such as Tomcat 11 or Jetty 12.1.

## Build tool requirements

### Gradle

For `3.4.0`, the Boot Gradle plugin requires Gradle 7.6.4+ or 8.4+; Gradle 7.5 and
8.0 through 8.3 are unsupported.

For `4.0.0`, Gradle 9 is supported and Gradle 8.x builds require 8.14 or newer.
Milestones and release candidates from the 4.0 line onward are published to Maven
Central.

Since `4.1.0`:

- `bootBuildImage` accepts repeatable `--environment` options, and command-line
  values override build-script values; and
- `bootBuildInfo` writes `META-INF/build-info.properties` beneath its destination
  rather than `build-info.properties`. Set `filename` to restore or customize the
  layout.

### Maven test skipping

The Maven plugin no longer treats `-DskipTests` as a request to skip test AOT
processing. Use `-Dmaven.test.skip=true` to skip both tests and test AOT processing
(since `4.1.0`).

### Internal parent POM

`spring-boot-parent` is no longer published (since `3.5.0`). It was internal
dependency management; any project that consumed it must provide its own dependency
management.

## Framework removals and source breaks

### Logging, server, and legacy integrations

In `4.0.0-framework-7`:

- `spring-jcl` is replaced by Apache Commons Logging 1.3.0;
- `ListenableFuture`, OkHttp 3 client integration, and theme support are removed;
- Undertow-specific WebSocket and low-level WebFlux support are removed because
  Undertow does not meet Servlet 6.1; and
- MVC may use a future Servlet 6.1-compatible Undertow through standard Servlet
  integration.

### Annotation and path-matching removals

The container no longer recognizes `javax.annotation` or `javax.inject`; use their
`jakarta` equivalents. The following web switches and strategies are removed in
`4.0.0-framework-7`:

- `suffixPatternMatch`;
- `registeredSuffixPatternMatch`;
- `favorPathExtension`;
- `ignoreUnknownPathExtensions`;
- servlet path-extension content-negotiation strategies; and
- `matchOptionalTrailingSeparator`.

### Additional source breaks

Also in `4.0.0-framework-7`:

- `HttpComponentsClientHttpRequestFactory#setConnectTimeout` is removed;
- Kotlin `JdbcOperations.queryForObject` and `queryForList` extensions accepting
  `Array<out Any>` are replaced with vararg forms; and
- protected `RequestContext#jstPresent` was renamed to `JSTL_PRESENT`.

### Boot upgrade removals

APIs and properties deprecated in Boot 4.0 are removed in `4.1.0`. The deprecated
`layertools` jar mode is also removed; use `tools` mode.

## Deprecation directions

### Framework migrations

The `4.0.0-framework-7` line establishes these directions:

| Deprecated area | Migration |
| --- | --- |
| `RestTemplate` documentation | `RestClient` or HTTP service clients; an `@Deprecated` annotation is scheduled for Framework 7.1 |
| MVC `<mvc:*>` XML namespace | MVC Java configuration |
| JUnit 4 TestContext support | JUnit Jupiter |
| Kotlin JSR 223 templates | another supported template approach |
| Jackson 2 | Jackson 3 |
| MVC `PathMatcher` | `PathPattern` |
| `HandlerMappingIntrospector` | path-pattern-native request matching |

### JSpecify nullness

Spring's JSR 305-style nullness annotations are deprecated. Framework APIs now use
JSpecify, including nullness of type arguments, array elements, and varargs. This
can reveal Kotlin source incompatibilities. `MethodParameter#isOptional()` now
considers only locally declared `@Nullable` annotations, not inherited ones (since
`4.0.0-framework-7`).

### Other current deprecations

Since `4.1.0`:

- Apache Derby integration is deprecated in favor of H2 or HSQL;
- Dynatrace V1 configuration is deprecated in favor of V2; and
- DevTools LiveReload is deprecated without replacement.

## Native images and runtime hints

### Reflection annotations

`@RegisterReflection` registers reflection hints for arbitrary types, while
`@ReflectionScan` discovers hint annotations on classes that are not Spring beans
(since `3.4.0-framework-6.2`).

### Unified hint semantics

Resource hints use globs, not regular expressions (since
`4.0.0-framework-7`):

- `"/files/*.ext"` matches direct children only;
- `"/files/**/*.ext"` also matches nested paths; and
- exclusions are no longer supported.

A reflection type hint implies field, constructor, and method introspection.
Non-invocation `MemberCategory` values and `ExecutableMode.INTROSPECT` are obsolete:

~~~java
hints.reflection().registerType(MyType.class);
~~~

### Netty metadata workaround

Boot `3.4.0`'s Netty version needs GraalVM reachability metadata repository
`0.3.14`. The override is unnecessary from 3.4.1 onward:

~~~groovy
graalvmNative {
    metadataRepository { version = '0.3.14' }
}
~~~

### Native test execution

Since `3.5.0`, Maven's `nativeTest` profile runs only when both the Spring Boot and
Native Build Tools plugins are declared. This avoids unintended native tests in
multimodule builds.

## OCI images and packaging

### Builder changes

The default JVM builder in `3.4.0` is
`paketobuildpacks/builder-jammy-java-tiny`. It supports ARM and x64 but contains no
shell and fewer system libraries. Maven and Gradle add `trustBuilder` and
`imagePlatform`. The plugins no longer inject `BP_NATIVE_IMAGE=true`, and native
SBOMs produced with `--enable-sbom=sbom` are detected automatically.

Since `3.5.0`, the default builder is
`paketobuildpacks/builder-noble-java-tiny`, also without a shell. Maven and Gradle
read Docker `config.json` credentials and credential helpers.

### Development-tool marker

A dependency with this manifest entry is excluded from an uber jar (since
`4.0.0`):

~~~text
Spring-Boot-Jar-Type: development-tool
~~~

### Maven layer configuration

The Maven plugin can load layer definitions from a plugin dependency at
`META-INF/spring/layers/<name>.xml` (since `4.1.0`).

## Managed dependency generations

### Spring ecosystem alignment

The `3.5.0` platform aligns Spring Authorization Server 1.5, Spring Data 2025.0,
Spring GraphQL 1.4, Spring Integration 6.5, Spring Security 6.5, Spring Session 3.5,
and Spring WS 4.1. Notable dependency moves include Pulsar 4.0, Flyway 11.7,
Quartz 2.5, and Testcontainers 1.21.

The `4.0.0` platform moves to Spring AMQP 4, Batch 6, Data 2025.1, GraphQL 2,
HATEOAS 3, Integration 7, Kafka 4, LDAP 4, Pulsar 2, REST Docs 4, Session 4, and
WS 5.

Notable third-party major lines are Elasticsearch Client 9.1, Groovy 5, HikariCP 7,
Liquibase 5, Neo4j Java Driver 6, and Testcontainers 2.

### Spring Cloud Kubernetes

Spring Cloud Kubernetes 3.3 upgrades Fabric8 from 6.13.x to 7.3.1 for compatibility
with Boot 3.5's Jackson 2.19.x line (batch `spring-cloud-2025.0.0`).

## Extension API migrations

Since `4.0.0`:

- `EnvironmentPostProcessor` moved from `org.springframework.boot.env` to
  `org.springframework.boot`; the old interface is deprecated;
- the two-argument `OperationMethod` constructor is deprecated in favor of the
  overload accepting a `Predicate<Parameter>` for optional parameters; and
- constructing `SanitizableData` with a null key fails instead of allowing its key
  accessors to return null.

Library authors can replace deprecated auto-configuration classes through
`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.replacements`
(since `3.4.0`).

## Runtime controls

### Virtual-thread integrations

With `spring.threads.virtual.enabled=true`:

- Undertow and the OTLP meter registry use virtual threads;
- Spring Integration's `TaskScheduler` is virtual-thread aware without
  `@EnableScheduling` (since `3.4.0`); and
- JDK `HttpClient`-backed clients use virtual threads (since `4.0.0`).

### Additional runtime switches

Since `4.0.0`:

- disable console logging with `logging.console.enabled=false`;
- authenticate Elasticsearch with `spring.elasticsearch.api-key`;
- configure the Elasticsearch client sniffer; and
- set Tomcat's static-resource cache limit with
  `server.tomcat.resource.cache-max-size`.
