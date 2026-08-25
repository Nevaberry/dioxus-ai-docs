# Spring AI

All items in this reference correspond to the `spring-ai-1.0.0` batch.

## Dependency management and migration

Spring AI GA artifacts are available from Maven Central. Import the BOM to align
versions:

~~~xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.ai</groupId>
            <artifactId>spring-ai-bom</artifactId>
            <version>1.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
~~~

An OpenRewrite recipe from Arconia can automate many migrations to the GA API.

## Advisors and retrieval-augmented generation

The `ChatClient` Advisor API is an interceptor chain. Advisors can modify an
incoming prompt to add retrieved context or conversation memory.

- Use `QuestionAnswerAdvisor` for basic retrieval-augmented generation.
- Use `RetrievalAugmentationAdvisor` for a modular, more sophisticated RAG
  pipeline.

## Retrieval and ingestion

Vector stores share a SQL-like metadata-filter expression language and expose
store-native query escape hatches.

The ETL framework is configurable and pluggable:

- `DocumentReader` implementations read files, web pages, GitHub, object storage,
  Kafka, MongoDB, and JDBC sources.
- Pipeline stages support chunking, metadata enrichment, and embedding generation.

## Conversation memory

`ChatMemory` manages message history. `MessageWindowChatMemory` retains the most
recent N messages and delegates persistence to `ChatMemoryRepository`. Repository
implementations are provided for JDBC, Cassandra, and Neo4j.

`VectorStoreChatMemoryAdvisor` takes a different approach: it recalls semantically
similar messages through vector search.

## Tools

Declare model tools on methods with `@Tool`, register tool components dynamically as
`@Bean` instances, or construct them programmatically. Tools can perform both
information retrieval and state-changing actions; apply authorization and approval
boundaries accordingly.

## Evaluation

The `Evaluator` SPI includes:

- `RelevancyEvaluator`, which judges an answer against its question and retrieved
  context; and
- `FactCheckingEvaluator`, which judges whether a statement is supported by a
  supplied document.

## Observability

Micrometer instrumentation measures model latency, token use, tool calls, and
retrievals. Micrometer Tracing creates spans for major interaction stages.
Diagnostic logging can expose prompts and vector-store responses, so treat it as
sensitive in production.

## MCP clients and servers

`spring-ai-starter-mcp-client` auto-configures consumption of MCP tools over stdio
or HTTP SSE.

`spring-ai-starter-mcp-server` exposes `@Tool` methods over those transports and
handles parameter conversion, serialization, and errors. MCP OAuth integration is
available through Spring Security and Spring Authorization Server.
