# Web Applications and HTTP Clients

## Contents

- [Blocking HTTP clients](#blocking-http-clients)
- [Reactive clients and transport behavior](#reactive-clients-and-transport-behavior)
- [Annotated HTTP service clients and gRPC](#annotated-http-service-clients-and-grpc)
- [API versioning](#api-versioning)
- [Routing, URL parsing, and Gateway](#routing-url-parsing-and-gateway)
- [Binding, fragments, and error responses](#binding-fragments-and-error-responses)
- [Jackson, Gson, and Kotlin Serialization](#jackson-gson-and-kotlin-serialization)
- [Servlet registration, cookies, and server settings](#servlet-registration-cookies-and-server-settings)
- [Web dependencies and property migrations](#web-dependencies-and-property-migrations)

## Blocking HTTP clients

### RestClient terminal operations

Calling `retrieve()` alone does not send a request. Invoke a terminal
`ResponseSpec` operation (since `3.4.0-framework-6.2`):

~~~java
ResponseEntity<Void> response = restClient.get().uri("/spring")
        .retrieve()
        .toBodilessEntity();
~~~

### Request-factory selection and redirects

Boot chooses a blocking client request factory in this order (since `3.4.0`):

1. Apache HTTP Components
2. Jetty
3. Reactor Netty
4. JDK `HttpClient`
5. `HttpURLConnection`

Override the choice with `spring.http.client.factory`. The supported factories
follow redirects by default; disable them with
`spring.http.client.redirects=dont-follow`.

`ClientHttpRequestFactoryBuilder` supplies `httpComponents()`, `jetty()`,
`reactor()`, `jdk()`, and `simple()` technology-specific builders.

Apache HTTP Components 5.4 enables HTTP/1.1 TLS upgrades by default. An Envoy or
Istio deployment that requires the former behavior can customize the builder:

~~~java
@Bean
HttpComponentsClientHttpRequestFactoryBuilder requestFactoryBuilder() {
    return ClientHttpRequestFactoryBuilder.httpComponents()
            .withDefaultRequestConfigCustomizer(builder ->
                    builder.setProtocolUpgradeEnabled(false));
}
~~~

### TestRestTemplate and common settings

Since `3.5.0`, `TestRestTemplate` follows the ordinary `RestTemplate` redirect
policy. `HttpOption.ENABLE_REDIRECTS` is deprecated; use `withRedirects(...)`.

Since `4.1.0`, cookie handling is configured through
`spring.http.clients.cookie-handling`, `RestTemplateBuilder`,
`HttpClientSettings`, or `TestRestTemplate.withCookieHandling(...)`.

Blocking and reactive clients can apply an `InetAddressFilter` to reject resolved
destination addresses. Use it as a common SSRF-hardening point.

## Reactive clients and transport behavior

Since `3.5.0`, `WebClient` has global timeout and redirect settings plus
`ClientHttpConnectorBuilder`, and follows redirects by default.

Since `4.0.0-framework-7`:

- an empty CORS configuration no longer rejects preflight requests; and
- Reactor Netty-backed `WebClient` instances automatically honor the
  `https.proxyHost` and `https.proxyPort` system properties.

## Annotated HTTP service clients and gRPC

### Grouped HTTP services

`@ImportHttpServices` discovers HTTP interfaces by named group, registers their
proxies as beans, and permits per-group client customization through an
`AbstractHttpServiceRegistrar` configurer (since
`4.0.0-framework-7`):

~~~java
@Configuration(proxyBeanMethods = false)
@ImportHttpServices(
        group = "weather",
        types = {FreeWeather.class, CommercialWeather.class})
class HttpServicesConfiguration extends AbstractHttpServiceRegistrar {
}
~~~

An HTTP interface can stream a request via
`StreamingHttpOutputMessage.Body` and return `InputStream` or
`ResponseEntity<InputStream>`.

Boot auto-configures annotated HTTP service interfaces and exposes configuration
properties for them (since `4.0.0`). Security integration can attach OAuth 2.0 to
these clients.

### Spring gRPC

Boot configures and tests gRPC clients and servers. Servers can run standalone on
Netty or through Servlet integration over HTTP/2. Applications using Spring gRPC
1.0 must migrate to the 1.1 integration used by Boot (since `4.1.0`).

## API versioning

Framework MVC and WebFlux can resolve, parse, validate, route on, and deprecate API
versions for annotated controllers and functional endpoints. `RestClient`,
`WebClient`, HTTP interface clients, MockMvc, and `WebTestClient` can set or test a
request version (since `4.0.0-framework-7`).

Boot configures the feature under `spring.mvc.apiversion.*` and
`spring.webflux.apiversion.*`. Supply an `ApiVersionResolver`,
`ApiVersionParser`, or `ApiVersionDeprecationHandler` bean for advanced behavior
(since `4.0.0`).

## Routing, URL parsing, and Gateway

### URL parser selection

`UriComponentsBuilder` uses a strict RFC 3986 parser by default instead of regular
expressions. Select the browser-compatible WHATWG parser for user-entered URLs
(since `3.4.0-framework-6.2`):

~~~java
UriComponents strict =
        UriComponentsBuilder.fromUriString(uri, ParserType.RFC).build();
UriComponents browserLike =
        UriComponentsBuilder.fromUriString(uri, ParserType.WHAT_WG).build();
~~~

### Trailing slashes and PathPattern

Servlet and reactive `UrlHandlerFilter` variants can redirect or rewrite
`/blog/post/` to `/blog/post`. Use this while migrating away from the removed
optional trailing-slash match setting (since `3.4.0-framework-6.2`).

`PathPattern` can match any number of leading path segments, such as
`/**/pages/index.html`. This removes a major blocker to leaving the deprecated
`AntPathMatcher` request-mapping mode (since `4.0.0-framework-7`).

### Gateway artifact names

Spring Cloud Gateway 4.3 renamed artifacts to distinguish server from
`ProxyExchange` support and WebFlux from WebMVC (batch
`spring-cloud-2025.0.0`):

| Deprecated artifact | Replacement artifact |
| --- | --- |
| `spring-cloud-gateway-server` | `spring-cloud-gateway-server-webflux` |
| `spring-cloud-gateway-server-mvc` | `spring-cloud-gateway-server-webmvc` |
| `spring-cloud-starter-gateway` | `spring-cloud-starter-gateway-server-webflux` |
| `spring-cloud-starter-gateway-mvc` | `spring-cloud-starter-gateway-server-webmvc` |
| `spring-cloud-gateway-mvc` | `spring-cloud-gateway-proxyexchange-webmvc` |
| `spring-cloud-gateway-webflux` | `spring-cloud-gateway-proxyexchange-webflux` |

The old artifacts are deprecated and emit a warning.

### Gateway property prefixes

Use the renamed module prefixes:

| Module | Deprecated prefix | Replacement prefix |
| --- | --- | --- |
| Gateway Server WebFlux | `spring.cloud.gateway.*` | `spring.cloud.gateway.server.webflux.*` |
| Gateway Server WebMVC | `spring.cloud.gateway.mvc.*` | `spring.cloud.gateway.server.webmvc.*` |
| ProxyExchange WebFlux | `spring.cloud.gateway.proxy.*` | `spring.cloud.gateway.proxy-exchange.webflux.*` |
| ProxyExchange WebMVC | `spring.cloud.gateway.proxy.*` | `spring.cloud.gateway.proxy-exchange.webmvc.*` |

`spring-boot-properties-migrator` can temporarily support deprecated prefixes.
Configure trusted forwarded-header proxies as described in the security reference.

## Binding, fragments, and error responses

### Expanded data binding

Constructor binding accepts `List`, `Map`, and array arguments.
`@ModelAttribute` binding can read request headers in addition to request
parameters, multipart data, and path variables (since
`3.4.0-framework-6.2`).

### Multi-view fragments

MVC and WebFlux can render multiple views in one response or stream rendered views.
This supports HTML-over-the-wire approaches such as htmx and Turbo (since
`3.4.0-framework-6.2`).

### Method-validation errors

`ErrorAttributes` includes errors from `MethodValidationResult`. Set
`spring.validation.method.adapt-constraint-violations=true` to adapt
`ConstraintViolation` instances into that model for consistent error responses
(since `3.5.0`).

## Jackson, Gson, and Kotlin Serialization

### Jackson 3 migration

Jackson 3 is preferred across the Framework. Jackson 2 fallback is deprecated,
planned to lose auto-detection in Framework 7.1 and support in 7.2. Most classes
move to `tools.jackson`; annotations remain in `com.fasterxml.jackson`.

Jackson 3 has no `Jackson2ObjectMapperBuilder` equivalent. Use
`JsonMapper.builder()`, `CBORMapper.builder()`, or the corresponding mapper builder
(batch `4.0.0-framework-7`).

### Central servlet converter configuration

`HttpMessageConverters` centralizes converter discovery and configuration for MVC,
`RestClient`, and `RestTemplate`. MVC configuration receives an
`HttpMessageConverters.ServerBuilder` (since `4.0.0-framework-7`):

~~~java
@Override
public void configureMessageConverters(HttpMessageConverters.ServerBuilder builder) {
    builder.jsonMessageConverter(
            new JacksonJsonHttpMessageConverter(JsonMapper.builder().build()));
}
~~~

### Boot Jackson configuration

Since `4.1.0`:

- format-independent read and write features for JSON, CBOR, and XML live under
  `spring.jackson.read.*` and `spring.jackson.write.*`;
- `spring.jackson.factory.*` configures factory constraints;
- auto-configured mappers use an application-context-aware
  `HandlerInstantiator`; and
- advanced factory changes use `JsonFactoryBuilderCustomizer`,
  `CborFactoryBuilderCustomizer`, or `XmlFactoryBuilderCustomizer`.

### Kotlin Serialization and Gson

Framework Kotlin Serialization converters handle a type by default only when
`KotlinDetector#hasSerializableAnnotation` accepts it. This prevents them from
capturing types intended for another JSON library; constructors accept a custom
predicate.

WebFlux adds `GsonEncoder` and `GsonDecoder`. Gson decoding cannot produce a
`Flux<?>`, while encoding can stream NDJSON (batch
`4.0.0-framework-7`).

Boot's `spring-boot-kotlinx-serialization-json` module and
`spring-boot-starter-kotlin-serialization` provide a configured `Json` bean using
`spring.kotlinx.serialization.json.*`. Their HTTP converter is ordered ahead of
other JSON converters, which remain fallbacks (since `4.0.0`).

For Gson itself, use `spring.gson.strictness`; `spring.gson.lenient` is deprecated
(since `3.4.0`).

## Servlet registration, cookies, and server settings

### Annotation-based registration

`@ServletRegistration` and `@FilterRegistration` register servlet and filter beans
without registration-bean wrappers (since `3.5.0`):

~~~java
@Bean
@FilterRegistration(name = "my-filter", urlPatterns = "/test/*", order = 0)
MyFilter myFilter() {
    return new MyFilter();
}
~~~

An empty dispatcher-type set on `FilterRegistrationBean` is treated like `null`
instead of being passed through to the server.

### Partitioned and SameSite cookies

Reactive servers other than Undertow support the `Partitioned` cookie attribute
used by CHIPS third-party cookies (since `3.4.0-framework-6.2`).

Disable session-cookie SameSite with
`server.servlet.session.cookie.same-site=omitted` or its reactive counterpart
(since `3.5.0`).

### Server and MVC settings

Since `3.5.0`:

- `server.tomcat.max-parameter-count` configures Tomcat's parameter limit;
- `server.tomcat.use-apr` defaults to `never`; choose `when-available` or `always`
  to opt back in;
- MVC default content types use
  `spring.mvc.contentnegotiation.default-content-types`; and
- management-server access-log prefixes use
  `management.server.{server}.accesslog.prefix`, where `server` is `jetty`,
  `tomcat`, or `undertow`.

Since `4.1.0`, additional controls include:

- `server.compression.additional-mime-types`;
- `spring.webflux.default-html-escape`; and
- `spring.data.rest.return-body-on-delete`.

## Web dependencies and property migrations

### HttpHeaders contract

`HttpHeaders` no longer implements `MultiValueMap` because header names are
case-insensitive and server representations are pair-oriented. Several map-style
methods are removed. `asMultiValueMap()` is only a deprecated compatibility
fallback; prefer header-specific operations (batch `4.0.0-framework-7`).

### WebJars

Replace `org.webjars:webjars-locator-core` with
`org.webjars:webjars-locator-lite`. Core-locator support is deprecated (since
`3.4.0`).

### Page serialization

Select Spring Data Web page serialization with
`spring.data.web.pageable.serialization-mode` (since `3.4.0`).

### Web property moves

Since `3.5.0`:

- `spring.graphql.path` moved to `spring.graphql.http.path`;
- `spring.graphql.sse.timeout` moved to
  `spring.graphql.http.sse.timeout`;
- preferred JSON mapper selection moved to
  `spring.http.converters.preferred-json-mapper`; and
- codec settings moved from `spring.codec.*` to `spring.http.codecs.*`.
