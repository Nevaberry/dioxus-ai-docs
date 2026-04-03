---
name: spring-boot-knowledge-patch
description: "Spring Boot changes since training cutoff (latest: 4.0) — modular starters, Jackson 3, Spring Framework 7, Security 7, Spring AI 1.0, HTTP service clients. Load before working with Spring Boot."
license: MIT
metadata:
  author: Nevaberry
  version: "4.0.0"
---

# Spring Boot Knowledge Patch

Covers Spring Boot 3.4–4.0, Spring Framework 7.0, Spring Security 7.0, and Spring AI 1.0.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Boot 4.0 migration | [references/boot-4-migration.md](references/boot-4-migration.md) | Modular starters, Jackson 3, HTTP service clients, RestTestClient, breaking changes |
| Spring Framework 7.0 | [references/framework-7.md](references/framework-7.md) | `@Retryable` in core, BeanRegistrar, JmsClient, API versioning, JPA 3.2 |
| Spring Security 7.0 | [references/security-7.md](references/security-7.md) | PathPatternRequestMatcher, DSL cleanup, SPA CSRF, MFA, OAuth2 HTTP services |
| Spring AI 1.0 | [references/spring-ai.md](references/spring-ai.md) | ChatClient, `@Tool`, advisors/RAG, VectorStore, ChatMemory, MCP |
| Boot 3.4–3.5 features | [references/boot-3.4-3.5.md](references/boot-3.4-3.5.md) | Structured logging, actuator access model, MockMvcTester, env properties import |

---

## Quick Reference — Boot 4.0 Starter Renames

| Old (Boot 3.x) | New (Boot 4.0) |
|---|---|
| `spring-boot-starter-web` | `spring-boot-starter-webmvc` |
| `spring-boot-starter-oauth2-client` | `spring-boot-starter-security-oauth2-client` |
| `spring-boot-starter-oauth2-resource-server` | `spring-boot-starter-security-oauth2-resource-server` |
| `spring-boot-starter` | `spring-boot-starter-classic` (gradual migration) |
| `spring-boot-starter-test` | `spring-boot-starter-test-classic` (gradual migration) |
| _(bare `flyway-core`)_ | `spring-boot-starter-flyway` (now required) |
| _(bare `liquibase-core`)_ | `spring-boot-starter-liquibase` (now required) |

Convention: `spring-boot-<technology>`, `spring-boot-starter-<technology>`, `spring-boot-starter-<technology>-test`.

Every technology now has a test starter companion. `@WithMockUser` requires `spring-boot-starter-security-test`.

---

## Quick Reference — Jackson 3 (Boot 4.0 Default)

Jackson 3 uses `tools.jackson` package (annotations stay in `com.fasterxml.jackson.annotation`).

| Old (Jackson 2) | New (Jackson 3) |
|---|---|
| `@JsonComponent` | `@JacksonComponent` |
| `@JsonMixin` | `@JacksonMixin` |
| `JsonObjectSerializer` | `ObjectValueSerializer` |
| `Jackson2ObjectMapperBuilderCustomizer` | `JsonMapperBuilderCustomizer` |
| `spring.jackson.read.*` | `spring.jackson.json.read.*` |
| `spring.jackson.write.*` | `spring.jackson.json.write.*` |

Compatibility module: `spring-boot-jackson2` (deprecated). Properties under `spring.jackson2.*`.

---

## HTTP Service Clients (Boot 4.0)

Annotated interfaces get auto-configured implementations:
```java
@HttpExchange(url = "https://echo.zuplo.io")
public interface EchoService {
    @PostExchange
    Map<?, ?> echo(@RequestBody Map<String, String> message);
}
```

Group registration with per-group configuration (Framework 7.0):
```java
@ImportHttpServices(group = "weather", types = {WeatherApi.class})
@ImportHttpServices(group = "user", types = {UserApi.class})
class Config extends AbstractHttpServiceRegistrar {
    @Bean
    RestClientHttpServiceGroupConfigurer configurer() {
        return groups -> groups.filterByName("weather")
            .forEachClient((g, b) -> b.defaultHeader("X-Api-Key", key));
    }
}
```

---

## RestTestClient (Boot 4.0)

Non-reactive alternative to `WebTestClient`. Works with `@SpringBootTest`, `@AutoConfigureMockMvc`, or random port:
```java
@Autowired
RestTestClient restTestClient;
```

---

## HttpMessageConverters Deprecated (Boot 4.0)

Replace custom `HttpMessageConverter` beans with customizers:
```java
@Bean
ServerHttpMessageConvertersCustomizer myCustomizer() {
    return converters -> converters.jsonMessageConverter(myConverter);
}
// Also: ClientHttpMessageConvertersCustomizer for client-side
```

---

## Spring Framework 7.0 — @Retryable in Core

Spring Retry merged into `spring-core`. Enable with `@EnableResilientMethods`:
```java
@Configuration
@EnableResilientMethods
class AppConfig { }

@Service
class MyService {
    @Retryable(maxAttempts = 3)
    public String fetchData() { ... }

    @ConcurrencyLimit(limit = 5)
    public String limitedOp() { ... }
}
```

---

## Spring Security 7.0 — Essential Changes

`MvcRequestMatcher` and `AntPathRequestMatcher` removed. Use `PathPatternRequestMatcher`:
```java
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/**").hasRole("USER")
    .anyRequest().authenticated()
);
```

DSL cleanup: `and()` removed (use lambda DSL), `authorizeRequests` removed (use `authorizeHttpRequests`).

SPA CSRF: `http.csrf(csrf -> csrf.spa());`

---

## Spring AI 1.0 — ChatClient

```java
@Autowired ChatClient chatClient;

String answer = chatClient.prompt()
    .user("What is Spring Boot?")
    .call()
    .content();

// Structured output
record ActorFilms(String actor, List<String> movies) {}
ActorFilms result = chatClient.prompt()
    .user("List films with Tom Hanks")
    .call()
    .entity(ActorFilms.class);
```

Tool calling:
```java
chatClient.prompt()
    .user("What's the weather in London?")
    .tools(weatherTools)  // @Tool-annotated @Component
    .call()
    .content();
```

---

## Boot 3.4 — Structured Logging

```properties
logging.structured.format.console=ecs    # ecs, gelf, or logstash
logging.structured.format.file=logstash
```

## Boot 3.4 — Actuator Access Model

Endpoint enabled/disabled replaced with fine-grained access control:
```properties
management.endpoints.access.default=unrestricted
management.endpoint.health.access=read-only
management.endpoints.access.max-permitted=read-only  # operator cap
```
Values: `none`, `read-only`, `unrestricted`. Old `enabled` properties are deprecated.

## Boot 3.4 — RestClient HTTP Client Selection

```properties
spring.http.client.factory=jdk  # http-components, jetty, reactor, jdk, simple
spring.http.client.redirects=dont-follow  # default: follow
```
Auto-detection order: Apache HC > Jetty > Reactor Netty > JDK HttpClient > Simple.

---

## Key Breaking Changes (Boot 4.0 / Framework 7.0)

- **Undertow removed** — use Tomcat or Jetty (Servlet 6.1 baseline)
- **RestTemplate deprecated** — use `RestClient`
- **`javax.annotation`/`javax.inject` removed** — use `jakarta.*`
- **`ListenableFuture` removed** — use `CompletableFuture`
- **JUnit 6** baseline for test framework
- **Liveness/readiness probes** enabled by default
- **DevTools Live Reload** disabled by default
- **Embedded launch scripts** removed — use `java -jar` directly
- **MongoDB properties** renamed: `spring.data.mongodb.*` → `spring.mongodb.*`
- **Elasticsearch**: `RestClient` → `Rest5Client`
- **Hibernate**: `hibernate-jpamodelgen` → `hibernate-processor`
- **`@EntityScan`** moved to `org.springframework.boot.persistence.autoconfigure.EntityScan`
- **`spring.dao.exceptiontranslation.enabled`** → `spring.persistence.exceptiontranslation.enabled`
- **`management.tracing.enabled`** → `management.tracing.export.enabled`
- **`logging.console.enabled=false`** disables console logging
- **WAR on Tomcat**: use `spring-boot-starter-tomcat-runtime` instead of `spring-boot-starter-tomcat`
- **Spring Retry** dependency management removed — use Spring Framework's `@Retryable` instead
- **Authorization Server** now part of Spring Security; use `spring-security.version`

## Reference Files

| File | Contents |
|---|---|
| [boot-4-migration.md](references/boot-4-migration.md) | Modular starters, Jackson 3, HTTP services, RestTestClient, OpenTelemetry, breaking changes |
| [framework-7.md](references/framework-7.md) | `@Retryable`/`@ConcurrencyLimit`, BeanRegistrar, JmsClient, API versioning, JPA 3.2, HttpHeaders |
| [security-7.md](references/security-7.md) | PathPattern matchers, DSL cleanup, SPA CSRF, MFA, Authorization Server, OAuth2 HTTP services |
| [spring-ai.md](references/spring-ai.md) | ChatClient, `@Tool`, advisors/RAG, VectorStore, ChatMemory, MCP server/client |
| [boot-3.4-3.5.md](references/boot-3.4-3.5.md) | Structured logging, actuator access, RestClient config, MockMvcTester, bean defaults, env import |
