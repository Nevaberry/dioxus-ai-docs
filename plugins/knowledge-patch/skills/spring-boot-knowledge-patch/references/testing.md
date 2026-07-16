# Testing

## Contents

- [MVC and REST test clients](#mvc-and-rest-test-clients)
- [Dynamic properties and Testcontainers](#dynamic-properties-and-testcontainers)
- [JUnit extension and context caching](#junit-extension-and-context-caching)
- [Bean overrides and scoped beans](#bean-overrides-and-scoped-beans)
- [HtmlUnit migration](#htmlunit-migration)
- [Spock and embedded web servers](#spock-and-embedded-web-servers)

## MVC and REST test clients

### AssertJ-based MockMvc

`MvcTester` supplies fluent AssertJ assertions and can be created from a
`WebApplicationContext` or directly from controllers (since
`3.4.0-framework-6.2`):

~~~java
MvcTester mvc = MvcTester.from(webApplicationContext);
assertThat(mvc.perform(get("/vehicle/{id}", "12"))).hasStatusOk();
~~~

### Synchronous REST testing

`RestTestClient` is a non-reactive counterpart to `WebTestClient`. It can bind to:

- a live server;
- one MVC controller; or
- an application context.

The Framework client was introduced in `4.0.0-framework-7`.

Boot can inject `RestTestClient` against MockMvc in a regular `@SpringBootTest` or a
test using `@AutoConfigureMockMvc`. When a defined or random server port is active,
the injected client targets the running server instead (since `4.0.0`).

## Dynamic properties and Testcontainers

### Context-provided dynamic properties

Register dynamic test properties from inside the `ApplicationContext` by declaring
`DynamicPropertyRegistrar` beans (since `3.4.0-framework-6.2`).

### Registry injection migration

Injecting `DynamicPropertyRegistry` into a `@Bean` method fails by default because
the resulting container lifecycle is unsafe. During migration,
`spring.testcontainers.dynamic-property-registry-injection=warn` or `allow` restores
the former behavior (since `3.4.0`).

### Container-backed databases

`@AutoConfigureTestDatabase` detects databases sourced from containers.
`replace=Replace.NONE` is generally unnecessary. Use
`replace=Replace.AUTO_CONFIGURED` to preserve the previous replacement behavior
(since `3.4.0`).

## JUnit extension and context caching

### Extension context scope

`SpringExtension` uses a test-method-scoped `ExtensionContext`. This makes
constructor and field injection consistent through `@Nested` test hierarchies, but
can break custom `TestExecutionListener` implementations (since
`4.0.0-framework-7`).

Restore test-class scope with:

- `@SpringExtensionConfig(useTestClassScopedExtensionContext = true)`; or
- from Framework 7.0.7,
  `spring.test.extension.context.scope=test_class`.

A listener running in `prepareTestInstance` should obtain the current class from
`testContext.getTestInstance().getClass()`.

### Pausable cached contexts

Cached application contexts pause background work while inactive and restart when
reused (since `4.0.0-framework-7`). From Framework 7.0.3, the default pauses only
when the next retrieved context is different.

Configure `spring.test.context.cache.pause` as:

- `spring.test.context.cache.pause=always` for the initial Framework 7 behavior;
- `spring.test.context.cache.pause=never` to disable pausing; or
- leave the current default to pause only across different contexts.

## Bean overrides and scoped beans

`@MockitoBean`, `@MockitoSpyBean`, and `@TestBean` can override prototype and
custom-scoped beans as well as singletons (since `4.0.0-framework-7`).

## HtmlUnit migration

### Coordinates and packages

Since `3.4.0`:

- replace `net.sourceforge.htmlunit:htmlunit` with `org.htmlunit:htmlunit`;
- replace `com.gargoylesoftware.htmlunit` packages with `org.htmlunit`; and
- replace Selenium's older driver with
  `org.seleniumhq.selenium:htmlunit3-driver`.

### Test client classes

`UriBuilderFactoryWebClient` and
`UriBuilderFactoryWebConnectionHtmlUnitDriver` replace `LocalHostWebClient` and
`LocalHostWebConnectionHtmlUnitDriver` (since `4.0.0`).

## Spock and embedded web servers

Spock support is restored now that Spock 2.4 works with Boot 4's Groovy 5 line
(since `4.1.0`).

Use `@AutoConfigureWebServer` to add an embedded web-server factory to a test without
otherwise starting a full application (since `4.1.0`).
