# Spring AI 1.0 (2025-05)

Spring AI provides a portable API for integrating AI models into Spring applications. Add via BOM:
```xml
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
```

## ChatClient — Core API

Fluent API similar to `RestClient`/`WebClient`. Supports 20+ AI model providers:
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

## Tool Calling with @Tool

```java
@Component
class WeatherTools {
    @Tool(description = "Get current weather for a city")
    String getWeather(String city) {
        return weatherService.getCurrent(city);
    }
}

// Register tools with ChatClient
chatClient.prompt()
    .user("What's the weather in London?")
    .tools(weatherTools)
    .call()
    .content();
```

## Advisors (Interceptor Chain)

Modify prompts and responses. Built-in advisors for RAG and memory:
```java
chatClient.prompt()
    .user(question)
    .advisors(new QuestionAnswerAdvisor(vectorStore))  // simple RAG
    .call()
    .content();
```

## VectorStore Abstraction

Portable interface with 20+ implementations. SQL-like metadata filter syntax:
```java
vectorStore.similaritySearch(
    SearchRequest.builder()
        .query("spring boot")
        .topK(5)
        .filterExpression("category == 'docs' AND year >= 2024")
        .build()
);
```

## ChatMemory

```java
// Sliding window memory
ChatMemory memory = MessageWindowChatMemory.builder()
    .chatMemoryRepository(new JdbcChatMemoryRepository(jdbcTemplate))
    .maxMessages(20)
    .build();
```
Repository implementations: JDBC, Cassandra, Neo4j.

## MCP (Model Context Protocol)

Client: `spring-ai-starter-mcp-client` for connecting to MCP servers.
Server: `spring-ai-starter-mcp-server` — expose `@Tool` methods as MCP tools. Supports stdio and HTTP SSE transports.
