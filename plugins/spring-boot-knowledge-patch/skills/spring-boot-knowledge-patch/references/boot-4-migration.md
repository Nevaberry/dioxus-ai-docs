# Spring Boot 4.0 (2026-01) — Major Release

## Modular Redesign

Spring Boot 4.0 ships smaller, focused modules. Convention: `spring-boot-<technology>`, `spring-boot-starter-<technology>`, `spring-boot-starter-<technology>-test`.

**Key starter renames:**
```xml
<!-- Old → New -->
spring-boot-starter-web → spring-boot-starter-webmvc
spring-boot-starter-oauth2-client → spring-boot-starter-security-oauth2-client
spring-boot-starter-oauth2-resource-server → spring-boot-starter-security-oauth2-resource-server
```

**New required starters** — technologies that previously needed only a third-party dependency now need a starter:
- `spring-boot-starter-flyway` (replaces bare `flyway-core`)
- `spring-boot-starter-liquibase` (replaces bare `liquibase-core`)

**Classic starters** for gradual migration:
```xml
<artifactId>spring-boot-starter-classic</artifactId>      <!-- replaces spring-boot-starter -->
<artifactId>spring-boot-starter-test-classic</artifactId>  <!-- replaces spring-boot-starter-test -->
```

**Test starters**: Every technology now has a test starter companion (`spring-boot-starter-<tech>-test`). `@WithMockUser` requires `spring-boot-starter-security-test`.

## Jackson 3 as Default JSON Library

Jackson 3 uses `tools.jackson` package (except annotations which stay in `com.fasterxml.jackson.annotation`).

**Renamed classes:**
- `@JsonComponent` → `@JacksonComponent`
- `@JsonMixin` → `@JacksonMixin`
- `JsonObjectSerializer` → `ObjectValueSerializer`
- `Jackson2ObjectMapperBuilderCustomizer` → `JsonMapperBuilderCustomizer`

**Renamed properties:**
- `spring.jackson.read.*` → `spring.jackson.json.read.*`
- `spring.jackson.write.*` → `spring.jackson.json.write.*`

**Jackson 2 compatibility module** (deprecated, temporary):
```xml
<artifactId>spring-boot-jackson2</artifactId>
```
Properties under `spring.jackson2.*`. Set `spring.jackson.use-jackson2-defaults=true` for closer Boot 3.x behavior.

Jackson 3 auto-detects all modules on classpath. Disable with `spring.jackson.find-and-add-modules=false`.

## HTTP Service Clients Auto-configuration

Annotated interfaces now get auto-configured implementations:
```java
@HttpExchange(url = "https://echo.zuplo.io")
public interface EchoService {
    @PostExchange
    Map<?, ?> echo(@RequestBody Map<String, String> message);
}
```

## API Versioning Auto-configuration

Configure via `spring.mvc.apiversion.*` or `spring.webflux.apiversion.*`. Define beans of type `ApiVersionResolver`, `ApiVersionParser`, `ApiVersionDeprecationHandler` for advanced control.

## RestTestClient

Non-reactive alternative to `WebTestClient`. Works with `@SpringBootTest`, `@AutoConfigureMockMvc`, or random port:
```java
@Autowired
RestTestClient restTestClient;
```

## OpenTelemetry Starter

New `spring-boot-starter-opentelemetry` auto-configures the OpenTelemetry SDK and exports metrics/traces over OTLP.

## HttpMessageConverters Deprecated

Replace custom `HttpMessageConverter` beans with customizers:
```java
@Bean
ServerHttpMessageConvertersCustomizer myCustomizer() {
    return converters -> converters.jsonMessageConverter(myConverter);
}
// Also: ClientHttpMessageConvertersCustomizer for client-side
```

## Other Breaking Changes

- **Undertow removed** — Servlet 6.1 baseline; use Tomcat or Jetty
- **Liveness/readiness probes** enabled by default
- **`@EntityScan`** moved to `org.springframework.boot.persistence.autoconfigure.EntityScan`
- **MongoDB properties** renamed: `spring.data.mongodb.host` → `spring.mongodb.host`, `spring.data.mongodb.uri` → `spring.mongodb.uri`, etc.
- **Elasticsearch**: `RestClient` → `Rest5Client`, `RestClientBuilderCustomizer` → `Rest5ClientBuilderCustomizer`
- **DevTools Live Reload** disabled by default
- **Embedded launch scripts** removed — use `java -jar` directly
- **PropertyMapper** no longer calls adapters/predicates for null; use `.always()` for null mapping
- **`spring.dao.exceptiontranslation.enabled`** → `spring.persistence.exceptiontranslation.enabled`
- **Hibernate**: `hibernate-jpamodelgen` → `hibernate-processor`
- **Spring Retry** dependency management removed — use Spring Framework's `@Retryable` instead
- **Authorization Server** now part of Spring Security; use `spring-security.version` not `spring-authorization-server.version`
- **`logging.console.enabled=false`** disables console logging
- **`management.tracing.enabled`** → `management.tracing.export.enabled`
- **WAR on Tomcat**: use `spring-boot-starter-tomcat-runtime` instead of `spring-boot-starter-tomcat`
