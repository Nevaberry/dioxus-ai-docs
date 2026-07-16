# Configuration, Beans, Tasks, and Local Infrastructure

## Contents

- [Bean definitions and candidate selection](#bean-definitions-and-candidate-selection)
- [Programmatic registration, proxies, and resilience](#programmatic-registration-proxies-and-resilience)
- [Property parsing, binding, and imports](#property-parsing-binding-and-imports)
- [Configuration metadata and application identity](#configuration-metadata-and-application-identity)
- [Task execution, scheduling, and bootstrap](#task-execution-scheduling-and-bootstrap)
- [Resources, SSL bundles, and service connections](#resources-ssl-bundles-and-service-connections)
- [Docker Compose and development services](#docker-compose-and-development-services)
- [Configuration-key migrations](#configuration-key-migrations)

## Bean definitions and candidate selection

### Stricter Framework bean definitions

Since `3.4.0-framework-6.2`, type matching uses this precedence:

1. `@Primary`
2. a parameter-name or `@Qualifier` match against the bean name
3. `@Priority`

Generic signatures are matched more strictly. The container also rejects:

- a `void` `@Bean` method;
- a `@Bean` method annotated with `@Autowired`; and
- a `@ComponentScan` guarded by a `REGISTER_BEAN` condition such as
  `@ConditionalOnBean`.

### Annotation-filtered conditions

Since `3.4.0`, setting `annotation` on `@ConditionalOnBean` or
`@ConditionalOnMissingBean` on a `@Bean` method suppresses inferred matching
against the method's return type. The same is already true for `name`, `type`,
and `value`. Specify both `value` and `annotation` when both requirements should
match.

Bean-based conditions ignore beans declared with `@Bean(defaultCandidate=false)`.
This permits an extra bean without forcing auto-configuration to back off.
`@ConditionalOnSingleCandidate` also understands `@Fallback` beans.

Since `3.5.0`, generic arguments inferred from a `@Bean` return type participate in
`@ConditionalOnBean` and `@ConditionalOnMissingBean`. Put a raw class in the
annotation to match every parameterization. `@ConditionalOnBooleanProperty`
provides boolean-specific matching, and it and `@ConditionalOnProperty` are
repeatable.

### Common annotations on configuration-property beans

Registered `@ConfigurationProperties` beans honor `@DependsOn`, `@Fallback`,
`@Lazy`, `@Primary`, `@Scope`, and `@Role` (since `3.4.0`).

## Programmatic registration, proxies, and resilience

### Bean registrars and Optional-aware SpEL

`BeanRegistrar` handles registration logic that creates several beans and does not
fit a single-return-type `@Bean` method. Spring Expression Language safe navigation
and Elvis operations transparently unwrap `Optional` values (since
`4.0.0-framework-7`).

Custom collection-like structures can participate in SpEL indexing through
`IndexAccessor` or `CompilableIndexAccessor`; `ReflectiveIndexAccessor` supplies a
reflective implementation. Safe navigation works for indexing arrays, collections,
strings, maps, objects, and custom structures. A target-specific
`PropertyAccessor` wins over a generic fallback (since
`3.4.0-framework-6.2`).

### Proxy defaults and per-bean overrides

The global CGLIB target-class setting applies consistently to every proxy processor,
including `@Async`. Register an application-wide `ProxyConfig` under
`AutoProxyUtils.DEFAULT_PROXY_CONFIG_BEAN_NAME`, or override one bean with
`@Proxyable(INTERFACES)`, `@Proxyable(TARGET_CLASS)`, or
`@Proxyable(interfaces = MyService.class)` (since `4.0.0-framework-7`).

### Core retry and concurrency limits

Retry APIs live in `org.springframework.core.retry` and include `RetryTemplate` and
`RetryPolicy`. Enable `@Retryable` and `@ConcurrencyLimit` with
`@EnableResilientMethods`. Reactive methods decorate their Reactor pipeline;
imperative methods execute through a matching retry template and policy (since
`4.0.0-framework-7`).

~~~java
@Configuration
@EnableResilientMethods
class ResilienceConfiguration {
}
~~~

## Property parsing, binding, and imports

### Escaped placeholders

The Framework placeholder parser accepts a configurable escape character, backslash
by default. Escape a placeholder to preserve literal `${...}` text, or escape the
colon inside a key. A properties file must double the backslash (since
`3.4.0-framework-6.2`):

~~~properties
my.host=${sub\\://host}
literal=This is a \\${test}!
~~~

### Validation and strict values

Nested `@ConfigurationProperties` validation follows Bean Validation cascading:
constraints on a nested object run only when its field has `@Valid` (since
`3.4.0`).

Since `3.5.0`, an `.enabled` property accepts only `true` or `false`. Profile names
in that release accept letters, digits, hyphens, and underscores, and cannot start
or end with a hyphen or underscore.

### YAML and constructor-binding behavior

Empty YAML maps were ignored in `3.4.0` so that the `Environment` contained scalar
values only. Current binding behavior, introduced in `4.1.0`, retains empty YAML
objects in the resulting `PropertySource`. It also:

- supplies `Optional.empty()`, not `null`, to constructor-bound `Optional`
  parameters; and
- allows a configured default to bind when a property is explicitly empty.

Treat the current behavior as authoritative; the older behavior matters when
diagnosing an application that changes across those releases.

### Config data from environment variables and encoded resources

Import a multiline environment variable containing properties or YAML with
`env:` (since `3.5.0`):

~~~properties
spring.config.import=env:MY_CONFIGURATION
~~~

Imported `.properties` resources default to ISO-8859-1. Select another encoding on
the import location (since `4.1.0`):

~~~properties
spring.config.import=classpath:import.properties[encoding=utf-8]
~~~

## Configuration metadata and application identity

### Names, defaults, and ignored properties

The configuration metadata processor detects enum defaults, and `@Name` renames a
field in JavaBean-style configuration properties (since `3.4.0`).

To suppress properties from generated metadata while recording the omission, add an
`ignored.properties` list to `META-INF/additional-spring-configuration-metadata.json`
(since `3.5.0`):

~~~json
{
  "ignored": {
    "properties": [{ "name": "my.age" }]
  }
}
~~~

### Metadata for external types

A `@ConfigurationProperties` type may refer to a type owned by another module and
still obtain metadata from that module. Run the annotation processor in the owner
module and mark the external type with `@ConfigurationPropertiesSource` when needed
(since `4.0.0`).

### Application identity

`spring.application.version` configures the application version and otherwise
defaults to the manifest's `Implementation-Version` (since `3.4.0`).

## Task execution, scheduling, and bootstrap

### Framework scheduling

Scheduled tasks accept a `TaskDecorator`. `Task` and `ScheduledTask` expose the last
execution time and outcome and the next scheduled time. `@DurationFormat` and
`@Scheduled` accept simple forms such as `30s` and `2h30m` (since
`3.4.0-framework-6.2`).

### Bean and JPA bootstrap

An individual bean can initialize in the background (since
`3.4.0-framework-6.2`):

~~~java
@Bean(bootstrap = BACKGROUND)
MyExpensiveComponent myComponent() {
    return new MyExpensiveComponent();
}
~~~

See the data reference for JPA's separate asynchronous bootstrap controls.

### Executor auto-configuration

Since `3.5.0`:

- the auto-configured executor has only the `applicationTaskExecutor` bean name;
  lookups of `taskExecutor` must migrate;
- `spring.task.execution.mode=force` creates the auto-configured
  `AsyncTaskExecutor` even when a custom `Executor` exists;
- `TaskDecorator` beans also decorate auto-configured schedulers; and
- `applicationTaskExecutor` enables an auto-configured `bootstrapExecutor`.

Since `4.0.0`, multiple `TaskDecorator` beans are combined in a
`CompositeTaskDecorator` and invoked in `@Order` or `Ordered` order.

## Resources, SSL bundles, and service connections

### Resource protocols

Every property bound to `Resource` understands a `base64:...` value, including
certificate locations. Register a custom `ProtocolResolver` under the
`org.springframework.core.io.ProtocolResolver` key in
`META-INF/spring.factories` (since `3.4.0`).

### SSL-enabled service connections

Client-side SSL bundles apply to Cassandra, Couchbase, Elasticsearch, Kafka,
MongoDB, RabbitMQ, and Redis service connections. Testcontainers uses SSL
annotations; Docker Compose uses service labels (since `3.5.0`).

MongoDB service connections also recognize Testcontainers'
`MongoDBAtlasLocalContainer`, and AWS Elastic Container Service is detected as a
`CloudPlatform` (since `4.0.0`).

## Docker Compose and development services

### Invocation and arguments

Docker Compose integration accepts multiple configuration files. Configure general,
start, and stop CLI arguments with `spring.docker.compose.arguments`,
`spring.docker.compose.start.arguments`, and
`spring.docker.compose.stop.arguments` (since `3.4.0`).

### Service detection

Docker Compose and Testcontainers recognize Redis Stack, Grafana LGTM, Hazelcast,
and OTLP logging. Testcontainers additionally recognizes
`org.testcontainers.kafka.KafkaContainer` and `RedisContainer` (since `3.4.0`).

Support also includes `lldap/lldap` through `LLdapContainer` (since `3.5.0`).
Docker Compose recognizes the official Elasticsearch image (since `4.1.0`).

### Failure diagnostics

When `docker compose up` or `start` fails, Boot emits `docker compose logs`.
Set the log level with `spring.docker.compose.start.log-level`; it defaults to
`info` (since `4.1.0`).

## Configuration-key migrations

Apply these `3.5.0` property moves:

| Old key | Current key |
| --- | --- |
| `spring.graphql.path` | `spring.graphql.http.path` |
| `spring.graphql.sse.timeout` | `spring.graphql.http.sse.timeout` |
| previous preferred JSON-mapper location | `spring.http.converters.preferred-json-mapper` |
| `spring.codec.log-request-details` | `spring.http.codecs.log-request-details` |
| `spring.codec.max-in-memory-size` | `spring.http.codecs.max-in-memory-size` |
| Groovy template settings under `.configuration` | the parent Groovy template namespace |
| `micrometer.observations.annotations.enabled` | `management.observations.annotations.enabled` |

The old Micrometer key is removed, not merely aliased. The exception-translation
switch later moved from `spring.dao.exceptiontranslation.enabled` to
`spring.persistence.exceptiontranslation.enabled` (since `4.0.0`); data-specific
effects are described in the data reference.
