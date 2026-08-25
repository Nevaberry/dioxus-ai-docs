# Data Access, Persistence, and Messaging

## Contents

- [Spring Data repositories and portable values](#spring-data-repositories-and-portable-values)
- [JDBC, data sources, and jOOQ](#jdbc-data-sources-and-jooq)
- [JPA and Hibernate](#jpa-and-hibernate)
- [MongoDB](#mongodb)
- [Cassandra](#cassandra)
- [Redis, KeyValue, and sessions](#redis-keyvalue-and-sessions)
- [JMS, Pulsar, Kafka, and RabbitMQ](#jms-pulsar-kafka-and-rabbitmq)
- [Batch, Liquibase, and other integrations](#batch-liquibase-and-other-integrations)

## Spring Data repositories and portable values

### Value Expression migration

Repository extensions should migrate away from
`QueryMethodEvaluationContextProvider`, its reactive variants, and `SpelEvaluator`.
Those pure-SpEL APIs are deprecated for removal in the next major Spring Data
release; use their Value Expression replacements (batch
`spring-data-2025.0.0`).

### Portable vectors

`Vector` represents floating-point or quantized int8 embeddings independently of a
store. It supports portable entity mappings plus store-specific conversions:

~~~java
Vector embedding = Vector.of(model.getVectorOutput());
~~~

This domain type was added in `spring-data-2025.0.0`.

### Projection nullability

When nullability constraints are enabled, a non-null interface-projection getter
throws if the projected value is `null` rather than returning it (batch
`spring-data-2025.0.0`).

### JPA DTO query rewriting

Spring Data JPA can rewrite string JPQL queries returning DTO projections into
constructor expressions. Selecting the entity alias derives arguments from the
primary DTO constructor; a multi-select is wrapped without changing its selected
expressions (batch `spring-data-2025.0.0`):

~~~java
@Query("SELECT u FROM User u WHERE u.lastname = :lastname")
List<UserDto> findByLastname(String lastname);
// Rewritten to SELECT new UserDto(u.firstname, u.lastname) ...
~~~

## JDBC, data sources, and jOOQ

### Sequence-generated aggregate identifiers

Put `@Sequence` on a Spring Data JDBC aggregate ID and name the database sequence to
generate identifiers from it (batch `spring-data-2025.0.0`).

### Streaming aggregate access

`JdbcAggregateOperations` offers `Stream`-returning methods for incremental
aggregate consumption (batch `spring-data-2025.0.0`). Close the stream so its
database resources are released.

### Data-source and client configuration

Since `3.5.0`:

- `jdbc:aws-wrapper:` URLs select the AWS Advanced JDBC Wrapper;
- most pooled data sources can auto-configure without `spring-jdbc`, while an
  unpooled embedded database still requires it;
- `spring.jooq.config` supplies jOOQ configuration;
- `spring.r2dbc.pool.acquire-retry` controls acquisition retries;
- `JdbcTemplate` exposes `ignoreWarnings`, `skipResultsProcess`,
  `skipUndeclaredResults`, and `resultsMapCaseInsensitive`; and
- `DataSourceBuilder` supports Vibur DBCP.

Framework `JdbcClient` supports per-statement fetch size, maximum rows, and query
timeout (since `4.0.0-framework-7`).

### Persistence exception translation

The Boot property moved from `spring.dao.exceptiontranslation.enabled` to
`spring.persistence.exceptiontranslation.enabled` (since `4.0.0`).

### Lazy physical connections

`spring.datasource.connection-fetch=lazy` wraps an auto-configured pooled data
source in `LazyConnectionDataSourceProxy`. A physical pool connection is not
checked out until a JDBC statement needs it; eager acquisition remains the default
(since `4.1.0`).

### jOOQ runtime floor

The managed jOOQ line requires Java 21 or newer (since `4.1.0`). Applications that
do not use jOOQ may remain on Boot's lower Java floor.

## JPA and Hibernate

### JPA injection and Hibernate packages

With JPA 3.2, `LocalContainerEntityManagerFactoryBean` supplies both the
`EntityManagerFactory` and a default or qualified shared `EntityManager`. A
`SharedEntityManagerBean` is usually unnecessary.

Native Hibernate support moved from `org.springframework.orm.hibernate5` to
`org.springframework.orm.jpa.hibernate` and targets Hibernate ORM 7.1/7.2 (since
`4.0.0-framework-7`).

### Persistence-unit and session bootstrapping

`MutablePersistenceUnitInfo` no longer implements
`jakarta.persistence.spi.PersistenceUnitInfo`. Custom bootstrapping should call
`SpringPersistenceUnitInfo#asStandardPersistenceUnitInfo()`. Entity-manager factory
beans accept a JPA 3.2 `PersistenceConfiguration`.

`LocalSessionFactoryBean` exposes injectable transactional `Session` and
`StatelessSession` proxies. Hibernate 7.2 is recommended for the stateless proxy
(since `4.0.0-framework-7`).

### Boot JPA bootstrap behavior

Since `4.1.0`:

- `spring.data.jpa.repositories.bootstrap-mode=deferred` fails when no suitable
  `AsyncTaskExecutor` exists;
- `lazy` mode no longer assigns the auto-configured entity-manager factory a
  bootstrap executor;
- `spring.jpa.bootstrap` enables asynchronous background bootstrapping; and
- `EntityManagerFactoryBuilder` can apply several
  `PersistenceUnitPostProcessor` instances.

## MongoDB

### Vector indexes and search

`SearchIndexOperations` creates a `VectorIndex`, while
`VectorSearchOperation` adds `$vectorSearch` to an aggregation pipeline (batch
`spring-data-2025.0.0`):

~~~java
VectorIndex index = new VectorIndex("vector_index")
        .addVector("embedding", v -> v.dimensions(1536).similarity(COSINE))
        .addFilter("year");
mongoTemplate.searchIndexOps(Movie.class).createIndex(index);

VectorSearchOperation search = VectorSearchOperation.search("vector_index")
        .path("embedding").vector(vector).numCandidates(150).limit(10)
        .quantization(SCALAR).withSearchScore("score");
~~~

### Validation callbacks

Bean Validation uses `ValidatingEntityCallback` and
`ReactiveValidatingEntityCallback` rather than application events. This coordinates
validation failures with reactive flows. `ValidatingMongoEventListener` is
deprecated (batch `spring-data-2025.0.0`).

### Sorted single-document mutations

On MongoDB 8.0 or newer, attach a `Sort` to a `Query` to choose which matching
document a replace-first/one or update-first/one operation affects (batch
`spring-data-2025.0.0`).

### Big-number representation

Spring Data keeps unannotated `BigDecimal` and `BigInteger` properties string-backed
by default, but `MongoCustomConversions` can change the global representation. An
explicit `@Field(targetType = ...)` wins (batch `spring-data-2025.0.0`):

~~~java
MongoCustomConversions.create(adapter ->
        adapter.bigDecimal(MongoCustomConversions.BigDecimalRepresentation.DECIMAL128));
~~~

Boot exposes `spring.data.mongodb.representation.big-decimal` for the same storage
choice (since `4.0.0`).

### Health, JMX, and protocol configuration

Spring Data MongoDB JMX support is deprecated in 4.5 for removal in 5.0; use
Actuator endpoints, optionally exposed through JMX (batch
`spring-data-2025.0.0`).

MongoDB health indicators no longer require Spring Data MongoDB. They moved from
`spring-boot-data-mongodb` into `spring-boot-mongodb`, including package changes
(since `4.0.0`). `spring.data.mongodb.protocol` selects the protocol (since
`3.5.0`).

### Spring Batch on MongoDB

`spring-boot-batch-data-mongo` auto-configures Spring Batch metadata storage in
MongoDB. Set `spring.batch.data.mongo.schema.initialize=true` for the default schema,
or supply a custom newline-delimited JSON schema script (since `4.1.0`).

## Cassandra

### Cassandra 5 and storage-attached indexes

Spring Data Cassandra 4.5 builds against Cassandra 5.0 and uses driver 4.19.
Programmatic APIs generate `CREATE INDEX ... USING 'sai'`, and `@SaiIndexed`
declares text or vector Storage-Attached Indexes (batch
`spring-data-2025.0.0`).

### Vector mapping and ANN search

Mapped properties may use Cassandra `CqlVector` or Spring Data `Vector`.
`@VectorType` declares dimensions, `@SaiIndexed` declares the index, and
`VectorSort.ann(...)` expresses approximate-nearest-neighbor ordering (batch
`spring-data-2025.0.0`):

~~~java
@VectorType(dimensions = 5)
@SaiIndexed
Vector vector;

Query query = Query.select(columns).limit(3)
        .sort(VectorSort.ann("vector", Vector.of(embedding)));
~~~

## Redis, KeyValue, and sessions

### Negative KeyValue query keywords

Map-backed repositories derive `Not`, `NotIn`, and `NotLike` queries (batch
`spring-data-2025.0.0`):

~~~java
Person findByFirstnameNot(String firstname);
Person findByFirstnameNotLike(String firstname);
Person findByFirstnameNotIn(List<String> names);
~~~

### Redis URL precedence and read routing

When `spring.data.redis.url` is present, its database is authoritative. A URL
without a database selects database `0`, and `spring.data.redis.database` is ignored.
Choose Lettuce read routing with `spring.data.redis.lettuce.read-from` (since
`3.5.0`).

### Reactive indexed sessions

Spring Session auto-configuration supports the `indexed` repository type in reactive
web applications (since `3.4.0`).

### Static replicas and tracing

Configure a static Lettuce master/replica topology through
`spring.data.redis.masterreplica.nodes`. Redis instrumentation now auto-configures
`MicrometerTracing` instead of `MicrometerCommandLatencyRecorder`, emitting metrics
and spans through the Observation API (since `4.0.0`).

### Redis listeners

Boot discovers `@RedisListener` endpoints and creates a
`RedisMessageListenerContainer` when none exists. Configure it under
`spring.data.redis.listener.*` or reuse the defaults in a custom container through
`RedisMessageListenerContainerConfigurer`. The Redis starter now includes
`spring-messaging` (since `4.1.0`).

## JMS, Pulsar, Kafka, and RabbitMQ

### JMS destination resolution and client API

`SimpleDestinationResolver` is the Framework default for `JmsTemplate` and listener
containers. It caches `Queue` and `Topic` instances resolved through a `Session`;
configure `DynamicDestinationResolver` for fresh resolution.

`JmsClient` delegates to `JmsTemplate` and creates reusable send/receive handles with
QoS settings (since `4.0.0-framework-7`). Boot auto-configures `JmsClient` while
retaining `JmsTemplate` and `JmsMessagingTemplate` support (since `4.0.0`).

### Embedded ActiveMQ Classic

Embedded ActiveMQ Classic is supported, but the starter remains client-only. Add
`org.apache.activemq:activemq-broker` explicitly to run an embedded broker (since
`3.4.0`).

### Pulsar defaults and concurrency

Unqualified topics can inherit `spring.pulsar.defaults.topic.tenant` and
`.namespace`. Disable this with `spring.pulsar.defaults.topic.enabled=false`.
Additional settings include:

- client I/O and listener threads under `spring.pulsar.client.threads.*`;
- listener-container concurrency at `spring.pulsar.listener.concurrency`; and
- application of `spring.pulsar.consumer.subscription.name` to the auto-configured
  listener container.

These controls were added in `3.4.0`.

### Kafka controls

Since `3.5.0`, Kafka adds
`spring.kafka.listener.auth-exception-retry-interval` and
`spring.kafka.consumer.max-poll-interval`. Since `4.1.0`, `KafkaTemplate` also
configures `closeTimeout` and `allowNonTransactional`.

### RabbitMQ Streams

Enable RabbitMQ Streams TLS with `spring.rabbitmq.stream.ssl.enabled` or select an
SSL bundle at `spring.rabbitmq.stream.ssl.bundle`. Testcontainers may declare
`@ServiceConnection(type = RabbitStreamConnectionDetails.class)`. Docker Compose
detection requires the stream plugin and mapped port 5552 (since `4.1.0`).

## Batch, Liquibase, and other integrations

### Batch and Liquibase controls

Since `3.5.0`:

- Spring Batch accepts a custom `JobParametersConverter` bean and exposes
  `spring.batch.jdbc.validate-transaction-state`.
- Liquibase adds `spring.liquibase.analytics-enabled` and
  `spring.liquibase.license-key`.

### Couchbase certificates

Couchbase auto-configuration can authenticate a cluster with client certificates
instead of username/password credentials (since `3.4.0`).

Capella's embedded CA is no longer trusted automatically. Put the CA in an SSL
bundle and attach it to Couchbase (since `3.5.0`):

~~~yaml
spring:
  ssl:
    bundle:
      pem:
        couchbase-bundle:
          truststore:
            certificate: classpath:com/couchbase/client/core/env/capella-ca.pem
  couchbase:
    env:
      ssl:
        bundle: couchbase-bundle
~~~
