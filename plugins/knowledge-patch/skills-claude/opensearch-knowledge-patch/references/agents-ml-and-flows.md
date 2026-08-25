# Agents, ML Commons, and Flow Framework

Use this reference for agent architectures, tools, memory, connectors, inference, MCP integration, Flow Framework, and application provisioning.

## Agentic search lifecycle

### From experiment to production

- In 3.2.0, disabled-by-default agentic search introduces an agentic query clause and a request processor that translates natural language to OpenSearch DSL through planning, execution, and summarization.
- In 3.3.0, agentic search becomes generally available. Agents select tools, generate queries, retain multi-turn context, and use custom search templates. Conversational agents can use `QueryPlanningTool` and carry an agent summary and memory ID.
- In 3.4.0, Dashboards adds a redesigned no-code agentic-search flow with external MCP, search templates, conversational memory, single-model support, and agent summaries. Agentic query processing preserves the request's source parameter.
- In 3.6.0, planning supports aliases and wildcard index patterns, custom fallback queries, embedding-model selection for neural queries, and reranking.

### Unified V2 agents

- In 3.6.0, the disabled-by-default unified registration API provisions connector, model, agent, and parameter mappings in one request. Its `conversational_v2` agent accepts plain text, multimodal content blocks, and conversation history without custom connector configuration.
- In 3.7.0, unified registration and `conversational_v2` become production-ready. V2 `inferenceConfig.model_parameters` values are honored instead of ignored.

## Agent memory and context

### Memory containers and sessions

- In 3.2.0, ML Commons adds memory-container create, read, update, and delete operations. AI memory can add, search, update, and delete records; agents can receive current date/time and configure message-history limits.
- In 3.3.0, agentic memory becomes generally available and enabled by default, with semantic fact extraction, preference learning, and conversation summarization. Sessions add message IDs and update times; container deletion can choose whether to delete contained memories.
- In 3.6.0, long-term memory supports semantic and hybrid retrieval, memory types accept message arrays, and context managers add a structured post-memory hook.
- In 3.7.0, fact extraction can use constrained structured output.

### Context management

In 3.5.0, agent hooks can run at several execution stages. Built-in context strategies include automatic truncation, summarization, and sliding windows before LLM requests. Conversation memory persists structured context and intermediate tool reasoning and validates misconfiguration.

### Retention

In 3.8.0, disabled-by-default retention policies can delete expired sessions, long-term memories, and history entries by age or count. Use cluster-wide defaults or per-container policy settings.

## Tools and processor chains

### Tool execution

- In 2.19.0, conversational-agent tools can receive action inputs as parameters and use generated inputs as search parameters.
- In 3.2.0, ML Commons adds a query-planning tool and Execute Tool API.
- In 3.3.0, Execute Tool becomes enabled by default. Built-ins add scratchpad read/write, index insight, log-pattern analysis, and data-distribution tools.
- In 3.6.0, new built-ins retrieve documents surrounding a selected document and compare metric percentiles between baseline and selection periods. `LogPatternAnalysisTool` accepts a service filter.
- In 3.7.0, `AbstractRetrieverTool` adds `input_schema` for function calling, and `VectorDBTool` accepts runtime overrides during agentic search.

### Processor chains

ML Commons 3.3.0 processor chains apply sequential transformations with 10 processor types, including JSONPath filters, regular expressions, conditions, and array iteration. A chain can invoke models and tools.

### Relevance Agent

The disabled-by-default 3.6.0 Relevance Agent uses a multi-agent Dashboards workflow to analyze user behavior, propose relevance changes, and validate them by offline evaluation.

## MCP and agent protocols

### Native MCP lifecycle

- In 3.0.0, disabled-by-default native MCP support integrates OpenSearch with external agents. ML Commons adds an MCP server, sessions, and a plan-execute-reflect agent with user prompts.
- In 3.1.0, the Update Agent API can change an agent's model IDs, workflow tools, and prompts.
- In 3.1.0, experimental MCP adds list-tools and update-tools APIs, persists tools in a system index across restarts, and lets the MCP client use a custom SSE endpoint.
- In 3.3.0, the ML Commons MCP server uses Streamable HTTP with role authorization and deprecates its SSE transport. MCP connectors can act as Streamable HTTP clients for external servers.
- In 3.8.0, external MCP connectors work with Flow and Conversational Flow agents, covering all four agent architectures. Connector-level tool-description overrides change how tools are presented without changing the external server.

### Streaming protocols

- In 3.3.0, separate disabled-by-default SSE APIs stream partial remote-model predictions and agent results.
- In 3.5.0, the disabled-by-default AG-UI protocol streams events between agents and user interfaces. Server-side HTTP/3 is also experimental.
- In 3.8.0, `PredictModelStream` and `ExecuteAgentStream` provide token-by-token remote prediction and agent execution over Protobuf and HTTP/2.

## Connectors and inference

### Request construction

- In 2.19.0, ML inference search-request extensions accept additional model-specific fields. A `template` query can leave placeholders unresolved until a search request processor assigns them.
- In 3.1.0, inline model connectors no longer require a connector name. Schema strings remain strings during validation instead of being coerced, and the inference request processor's Update Query step parses nested JSON objects.
- In 3.5.0, connectors support custom action names and PUT and DELETE, allowing a connector to expose broader REST operations.
- In 3.7.0, connector headers accept per-request substitutions such as `X-Trace-ID: ${parameters.trace_id}`.

### Preprocessing and providers

OpenSearch 2.19.0 adds a built-in Cohere multimodal preprocessor selected by function name, Bedrock reranking pre- and postprocessing, and trusted endpoints for DeepSeek and Amazon Rekognition.

### Connector network controls

In 3.7.0, outbound connector paths add private-IP and ReDoS protections and consistently enforce `trusted_connector_endpoints_regex`. Validate the resolved endpoint, not only the template.

### Runtime options and guardrails

- In 3.6.0, conversational, AG-UI, and plan-execute-reflect agents can report token use. Text-embedding models add `LAST_TOKEN` pooling for decoder-only models and `NONE` when output is already pooled.
- In 3.8.0, `ModelGuardrail` and `LocalRegexGuardrail` fail closed when evaluation errors occur. Integrations must handle denial on the error path.

## ML Commons observability

In 3.1.0, ML Commons integrates with the OpenSearch metrics framework and OpenTelemetry-compatible monitoring. It supports runtime instrumentation on selected paths and scheduled collection of state-level metrics.

Agent Traces in 3.6.0 records agent, language-model, and tool spans through OpenTelemetry. A Python instrumentation SDK and Dashboards DAG and token-usage views are available.

## Flow Framework and application provisioning

### Flow authoring

- In 2.19.0, OpenSearch Flow in Dashboards composes ML application flows, including RAG and vector-search workflows. Flow Framework supports synchronous provisioning, and `WorkflowRequest` removes `useCase` and `defaultParams`.
- In 3.0.0, Dashboards Flow Framework changes ingestion input to JSON Lines.
- In 3.1.0, Flow Framework thread-pool sizes are configurable. Dashboards adds a sparse-encoder semantic-search template, and Flow Framework adds a data-summary template using a log-pattern agent.

### Resource isolation and sharing

- In 2.19.0, tenant isolation covers Flow Framework and ML Commons connectors, models, tasks, deployments, predictions, agents, search, and configuration.
- In 3.4.0, Flow Framework joins centralized resource sharing and access control. See the security reference for ownership and migration requirements.

### Launchpad

OpenSearch Launchpad in 3.6.0 turns sample documents and conversational requirements into a local search application. It provisions semantic encoding, cluster configuration, architecture, and a working UI, then integrates the project with an IDE.
