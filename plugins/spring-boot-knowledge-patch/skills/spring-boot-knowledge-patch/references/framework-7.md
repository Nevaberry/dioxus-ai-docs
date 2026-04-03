# Spring Framework 7.0 (2026-01)

## Resilience: @Retryable and RetryTemplate in Core

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
`@Retryable` auto-adapts to reactive return types using Reactor retry.

## BeanRegistrar for Programmatic Bean Registration

New contract for registering multiple beans programmatically:
```java
class MyRegistrar implements BeanRegistrar {
    @Override
    public void register(BeanRegistry registry, Environment env) {
        registry.registerBean("myBean", MyBean.class);
    }
}
```

## JmsClient

New fluent JMS API (like JdbcClient/RestClient):
```java
@Autowired JmsClient jmsClient;
// send and receive with fluent API, throws MessagingException
```

## HttpHeaders No Longer Extends MultiValueMap

`HttpHeaders` API revisited. Use `HttpHeaders#asMultiValueMap()` (deprecated) as fallback if needed.

## RestTemplate Deprecated

Use `RestClient` instead. Official `@Deprecated` coming in 7.1.

## API Versioning

First-class support in MVC and WebFlux. Map by API version, configure resolution, deprecate versions. Client support in `RestClient`, `WebClient`, HTTP interfaces.

## @ImportHttpServices

Declarative HTTP service client registration by groups:
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

## JPA 3.2 / Hibernate 7.x

`EntityManager` injectable via `@Inject`/`@Autowired` with qualifier support. No separate `SharedEntityManagerBean` needed. Hibernate `StatelessSession` supported for injection via `LocalSessionFactoryBean`.

## Other Notable Changes

- **Servlet 6.1 / JPA 3.2 / Bean Validation 3.1** baselines
- **JUnit 6** baseline for test framework
- **JSpecify** nullability annotations replace JSR 305
- **`javax.annotation`/`javax.inject`** support removed — use `jakarta.*`
- **`ListenableFuture`** removed — use `CompletableFuture`
- **PathPattern** now supports `/**/pages/index.html` (leading multi-segment wildcards)
- **GraalVM 25** with new reachability metadata format; `hints.reflection().registerType(T.class)` now implies method/field introspection
- **`@Proxyable`** annotation for per-bean proxy type control
