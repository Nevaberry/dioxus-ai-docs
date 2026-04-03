# Spring Boot 3.4–3.5

## Spring Boot 3.4 (2024-11)

### Structured Logging

Built-in structured logging with `logging.structured.format.console` and `logging.structured.format.file`. Supported formats: `ecs` (Elastic Common Schema), `gelf` (Graylog Extended Log Format), `logstash`.

### Graceful Shutdown Enabled by Default

`server.shutdown` now defaults to `graceful` instead of `immediate`.

### Actuator Endpoint Access Model

Endpoint enabled/disabled replaced with fine-grained access control:
```properties
# Old (deprecated)
management.endpoints.enabled-by-default=true
management.endpoint.health.enabled=true

# New
management.endpoints.access.default=unrestricted
management.endpoint.health.access=read-only
management.endpoints.access.max-permitted=read-only  # operator cap
```
Values: `none`, `read-only`, `unrestricted`.

### RestClient/RestTemplate HTTP Client Selection

New auto-detection order: Apache HC > Jetty > Reactor Netty > JDK HttpClient > Simple. Select explicitly:
```properties
spring.http.client.factory=jdk  # http-components, jetty, reactor, jdk, simple
spring.http.client.redirects=dont-follow  # default: follow
```

### ClientHttpRequestFactoryBuilder

Fluent builder for creating `ClientHttpRequestFactory` per technology:
```java
ClientHttpRequestFactoryBuilder.httpComponents()
    .withDefaultRequestConfigCustomizer(b -> b.setProtocolUpgradeEnabled(false));
```

### @Bean(defaultCandidate=false)

Declaring a bean as not a default candidate prevents auto-configuration from backing off. Enables using two DataSources or two EntityManagerFactories without `@Primary`:
```java
@Bean(defaultCandidate = false)
DataSource secondaryDataSource() { ... }
```

### MockMvcTester (AssertJ for MockMvc)

Auto-configured when AssertJ is on classpath. Fluent AssertJ-style assertions:
```java
assertThat(mvc.perform(get("/api/items/1")))
    .hasStatusOk()
    .body().json().isLenientlyEqualTo(expected);
```

## Spring Boot 3.5 (2025-05)

### @FilterRegistration and @ServletRegistration

Annotation-based alternative to `FilterRegistrationBean`/`ServletRegistrationBean`:
```java
@Bean
@FilterRegistration(name = "my-filter", urlPatterns = "/test/*", order = 0)
MyFilter myFilter() { return new MyFilter(); }
```

### Load Properties from Environment Variables

Import multiple properties from a single env var using `env:` prefix:
```properties
spring.config.import=env:MY_CONFIGURATION
```
Where `MY_CONFIGURATION` contains `key=value` pairs (properties or YAML format).

### Background Bean Initialization Auto-configured

Spring Boot now auto-configures a `bootstrapExecutor` bean enabling `@Bean(bootstrap = BACKGROUND)` out of the box, if an `applicationTaskExecutor` exists.

### spring.task.execution.mode=force

Forces auto-configuration of an `AsyncTaskExecutor` even when a custom `Executor` bean exists.

### ClientHttpConnectorBuilder

`WebClient` now supports global configuration properties for timeouts and redirects, aligning with `RestClient`/`RestTemplate` (Boot 3.4). Follow redirects enabled by default.

### Auto-configured TaskExecutor Name Change

The auto-configured `TaskExecutor` now only uses the `applicationTaskExecutor` bean name. The `taskExecutor` alias was removed.
