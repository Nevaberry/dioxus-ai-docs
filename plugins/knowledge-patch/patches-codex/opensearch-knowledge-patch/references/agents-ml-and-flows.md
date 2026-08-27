# Agents, ML Commons, and Flows

## Building connectors and inference requests

### Preprocessing, endpoints, and schemas

In 2.19.0, ML Commons adds a built-in Cohere multimodal preprocessor selectable by function name, Bedrock reranking pre- and postprocessing, and trusted endpoints for DeepSeek and Amazon Rekognition.

Since 3.1.0, inline connectors do not require a connector name. Schema-defined strings remain strings during validation rather than being coerced, and the inference request processor's Update Query step can parse nested JSON objects.

Since 3.5.0, connector actions can use custom names and the HTTP PUT and DELETE methods, letting one connector expose broader REST operations.

In 3.7.0, connector headers accept per-request `${parameters.*}` substitution, such as `X-Trace-ID: ${parameters.trace_id}`. Outbound paths include private-IP and ReDoS protections and consistently enforce `trusted_connector_endpoints_regex`.

### Inference inputs and streaming

The 2.19.0 inference search-request extension lets a search provide extra endpoint-specific input fields.

OpenSearch 3.5.0 adds a disabled-by-default Agent-User Interaction (AG-UI) event-streaming protocol for connecting agents to user interfaces.

OpenSearch 3.3.0 adds disabled-by-default SSE APIs for incremental remote prediction and agent execution. In 3.8.0, ML Commons adds `PredictModelStream` and `ExecuteAgentStream` for token-by-token prediction and agent execution over Protocol Buffers and HTTP/2.

### Embedding runtime options

Since 3.6.0, text-embedding runtimes support `LAST_TOKEN` pooling for decoder-only architectures and `NONE` for outputs that are already pooled. Conversational, AG-UI, and plan-execute-reflect agents can report token usage.

## Authoring workflows with Flow Framework

### Composition and provisioning

OpenSearch Flow in 2.19.0 Dashboards composes custom ML application flows, including retrieval-augmented generation and vector-search workflows. Flow Framework supports synchronous workflow provisioning. Remove the deleted `useCase` and `defaultParams` fields from `WorkflowRequest`.

OpenSearch Dashboards 3.0.0 changes Flow ingestion input to JSON Lines. In 3.1.0, Flow Framework thread-pool sizes become configurable; Dashboards adds a sparse-encoder semantic-search template, and Flow Framework adds a data-summary template using a log-pattern agent.

In 3.4.0, Flow Framework joins centralized resource sharing; apply the resource migration and API changes described in the security reference.

### Launchpad

OpenSearch Launchpad in 3.6.0 turns sample documents and conversational requirements into a local search application, provisioning semantic encoding, cluster configuration, architecture, and a working UI, then integrating the result with an IDE.

## Choosing an agent architecture

### Agentic search

OpenSearch 3.2.0 introduces disabled-by-default agentic search with an agentic query clause and a request processor that translates natural language into query DSL through planning, execution, and summarization.

Agentic search becomes generally available in 3.3.0. Agents select tools, generate queries, retain multi-turn context, and use custom search templates. Conversational agents can use the Query Planning Tool and carry an agent summary and memory ID.

The 3.4.0 Dashboards flow adds no-code authoring with external MCP and search-template integration, conversational memory, single-model configuration, and agent summaries. Agentic query processing preserves the request's source parameter.

Since 3.6.0, planning supports aliases and wildcard index patterns, custom fallback queries, embedding selection for neural queries, and reranking.

### Unified and conversational V2 agents

OpenSearch 3.6.0 introduces a disabled-by-default unified registration API that creates a connector, model, agent, and parameter mappings in one request. Its `conversational_v2` agent accepts plain text, multimodal content blocks, and conversation history without custom connector configuration.

Both unified registration and `conversational_v2` become production-ready in 3.7.0. V2 `inferenceConfig.model_parameters` values are honored rather than silently ignored.

### Plan-execute-reflect agents

OpenSearch 3.0.0 adds an experimental plan-execute-reflect agent type with user-provided prompts. Apply the same tool, memory, and protocol lifecycle controls used for conversational agents.

## Managing memory and context

### Persistent memory and sessions

OpenSearch 3.2.0 adds memory-container lifecycle APIs. AI-oriented memory supports add, search, update, and delete operations; agents can receive the current date and time and set a message-history limit.

In 3.3.0, persistent agentic memory becomes generally available and enabled by default, with semantic-fact extraction, preference learning, and conversation summarization. Sessions add message identifiers and update times, and deleting a memory container can optionally delete its memories.

Since 3.5.0, context hooks can run at multiple execution stages and apply automatic truncation, summarization, or sliding-window strategies before inference. Conversation memory stores structured context and intermediate tool reasoning and validates misconfiguration.

In 3.6.0, long-term memory gains semantic and hybrid retrieval, memory types accept message arrays, and context managers gain a structured post-memory hook. In 3.7.0, fact extraction can use constrained structured output.

OpenSearch 3.8.0 adds disabled-by-default retention policies that delete expired sessions, long-term memories, and history entries by age or count, using cluster defaults or per-container policies.

## Defining and executing tools

### Tool inputs and lifecycle APIs

Since 2.19.0, conversational-agent tools can receive action inputs as parameters and use generated inputs as search parameters.

OpenSearch 3.1.0 adds Update Agent support for changing model identifiers, workflow tools, and prompts. Experimental MCP adds list-tools and update-tools APIs, persists tools in a system index across restarts, and supports a custom SSE client endpoint.

In 3.2.0, ML Commons adds a Query Planning Tool, an Execute Tool API, and memory-container APIs. By 3.3.0, Execute Tool is enabled by default.

### Processor chains and built-in tools

ML Commons 3.3.0 processor chains run sequential transformations through ten processor types, including JSONPath filters, regular expressions, conditions, and array iteration, and can invoke inference or tools. Built-ins include scratchpad read/write, index-insight, log-pattern-analysis, and data-distribution tools.

OpenSearch 3.6.0 adds tools for retrieving documents surrounding a selected document and comparing metric percentiles across baseline and selection periods. `LogPatternAnalysisTool` accepts a service filter.

In 3.7.0, `AbstractRetrieverTool` exposes `input_schema` for function calling, and `VectorDBTool` accepts runtime parameter overrides during agentic search.

## Integrating Model Context Protocol

### Server and client evolution

OpenSearch 3.0.0 adds experimental native MCP integration, including an ML Commons MCP server and session handling.

In 3.3.0, the ML Commons server adopts Streamable HTTP with role-based authorization and deprecates its SSE transport. MCP connectors can act as Streamable HTTP clients for external servers. Do not confuse the deprecated MCP SSE transport with separate SSE prediction streams.

In 3.8.0, external MCP connectors work with Flow and Conversational Flow agents, extending support across all four agent architectures. Connector-level tool-description overrides change how tools are presented without modifying the external server.

## Instrumenting ML and agents

ML Commons 3.1.0 integrates with the metrics framework and OpenTelemetry-compatible monitoring. It supports runtime instrumentation on selected code paths and scheduled collection of state-level metrics.

Agent Traces in 3.6.0 records agent, inference, and tool spans through OpenTelemetry. It includes a Python instrumentation SDK and Dashboards views for DAGs and token usage.

## Handling guardrail failures

Since 3.8.0, `ModelGuardrail` and `LocalRegexGuardrail` fail closed when evaluation fails. Existing integrations that treated guardrail errors as allow decisions must update their failure paths.
