# v1 Migration and Core Types

## Agent and package migration

### `create_agent` and the LangGraph boundary (`1.0-guide`)

`langchain.agents.create_agent` is a LangGraph-backed model/tool loop that
supersedes deprecated `create_react_agent` in `langgraph.prebuilt`. Middleware
hooks customize each loop step. Bundled middleware covers human approval of
tool calls, conversation summarization near context limits, and pattern-based
PII redaction.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Help the user by fetching the weather in their city.",
)
```

LangGraph otherwise preserves backward compatibility, but
`langgraph.prebuilt` is deprecated as enhanced agent functionality moves to
`langchain.agents`.

```shell
uv pip install --upgrade langgraph
npm install @langchain/langgraph@latest
```

### Package split and Python runtime floor

The LangChain main package is narrowed to core abstractions. Python legacy APIs
move to the separately installed `langchain-classic`. Python 3.9 is
unsupported; the Python release requires 3.10 or newer. For JavaScript package
names, use the dedicated migration below.

```shell
uv pip install --upgrade langchain
uv pip install langchain-classic
```

### JavaScript package and subpath names (`1.0.0`)

JavaScript v1 upgrades the unscoped `langchain` package alongside
`@langchain/core`. Legacy chains, retrievers, indexing APIs, and community
exports move to `@langchain/classic`; for example, `langchain/chains` becomes
`@langchain/classic/chains`.

```shell
npm install langchain @langchain/core
npm install @langchain/classic
```

### Google GenAI v4 migration

`langchain-google-genai` v4 uses Google's consolidated Generative AI SDK and
places Gemini API and Vertex AI access behind one integration. Upgrades may
require small changes. Corresponding packages in
`langchain-google-vertexai` are deprecated.

## Messages and content blocks

### Provider-neutral blocks

Messages expose `.content_blocks`, a backward-compatible typed
representation shared across providers. It normalizes reasoning traces,
citations, tool calls, and server-side tool calls so streams, frontends, and
memory stores do not need provider-specific response shapes.

```python
blocks = message.content_blocks
```

### Initial rollout limits

At `1.0.0`, Python content blocks are supported only by
`langchain-anthropic`, `langchain-aws`, `langchain-openai`,
`langchain-google-genai`, and `langchain-ollama`. JavaScript support is limited
to `langchain`, `@langchain/core`, `@langchain/anthropic`, and
`@langchain/openai`.

## Model capability profiles (`1.1.0`)

Chat models expose `.profile` with declarative capability data such as
structured-output, function-calling, and JSON-mode support. Profiles come from
the cross-provider models.dev index, allowing agent logic to inspect support
without hard-coding it per model.

```python
capabilities = chat_model.profile
```

Summarization middleware consults profiles to choose when and how to summarize,
enabling flexible triggers and provider-specific behavior for long-running
sessions. `ProviderStrategy` can also be inferred from a model profile, so an
agent can select native structured output without hand-written provider
capability logic.

## Rich system prompts

`create_agent(system_prompt=...)` accepts a `SystemMessage`. This enables
cache-control blocks, structured orchestration hints, richer instructions, and
advanced content blocks.

```python
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

agent = create_agent(
    model="openai:gpt-5",
    tools=[],
    system_prompt=SystemMessage(content="Answer concisely."),
)
```

## Built-in retry and moderation middleware

Built-in model-retry middleware provides configurable exponential backoff for
transient provider endpoint errors, allowing recovery without custom retry
wrappers.

OpenAI moderation can run as middleware over user input, model responses, and
tool-returned content, providing one safety layer at all three boundaries.

## Core tracing metadata (`core-1.5.6`)

LangChain Core incorporates gateway metadata into traces, making gateway
context available to tracing consumers without separate propagation.
