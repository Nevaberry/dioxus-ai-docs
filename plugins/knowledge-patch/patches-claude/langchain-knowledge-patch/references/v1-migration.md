# v1 Migration and Core Types

## Agent construction and middleware

### Replace `create_react_agent` with `create_agent`

The `1.0-guide` introduces `langchain.agents.create_agent`, a LangGraph-backed
model/tool loop that supersedes the deprecated `create_react_agent` in
`langgraph.prebuilt`. Middleware hooks can customize each loop step. Bundled
middleware covers human approval of tool calls, conversation summarization
near context limits, and pattern-based PII redaction.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Help the user by fetching the weather in their city.",
)
```

### Configure policy and lifecycle hooks

In `1.0.0`, prebuilt policies accept named or regex PII detectors with
`redact` or `block` strategies, token-count summarization triggers, and
tool-keyed human decisions of `approve`, `edit`, or `reject`.

Python custom middleware subclasses `AgentMiddleware`; JavaScript custom
middleware uses `createMiddleware`. The six hook pairs are:

- `before_agent` / `beforeAgent`
- `before_model` / `beforeModel`
- `wrap_model_call` / `wrapModelCall`
- `wrap_tool_call` / `wrapToolCall`
- `after_model` / `afterModel`
- `after_agent` / `afterAgent`

```python
from langchain.agents.middleware import (
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
)

class RouteModel(AgentMiddleware):
    def wrap_model_call(self, request, handler):
        return handler(request.override(model=fast_model, tools=[read_email]))

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[read_email, send_email],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        SummarizationMiddleware(
            model="claude-sonnet-4-6", trigger={"tokens": 500}
        ),
        HumanInTheLoopMiddleware(interrupt_on={
            "send_email": {
                "allowed_decisions": ["approve", "edit", "reject"]
            }
        }),
        RouteModel(),
    ],
)
```

### Use richer system prompts

Since `1.1.0`, `create_agent(system_prompt=...)` accepts a `SystemMessage`.
This permits cache-control blocks, structured orchestration hints, richer
instructions, and advanced content blocks.

```python
from langchain_core.messages import SystemMessage

agent = create_agent(
    model="openai:gpt-5",
    tools=[],
    system_prompt=SystemMessage(content="Answer concisely."),
)
```

### Use built-in retry and moderation middleware

The model-retry middleware in `1.1.0` provides configurable exponential
backoff for transient provider endpoint errors. OpenAI moderation middleware
can run across user input, model responses, and tool-returned content.

## Structured output

### Generate structured output inside the loop

The `1.0-guide` moves structured output into the main model/tool loop rather
than requiring another model call. `response_format` selects tool-based or
provider-native generation. Wrap a Pydantic schema in `ToolStrategy` to
request the tool-calling strategy.

```python
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel

class WeatherReport(BaseModel):
    temperature: float
    condition: str

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[weather_tool],
    response_format=ToolStrategy(WeatherReport),
    system_prompt="Fetch the weather and return a report.",
)
```

`ToolStrategy` in `1.0.0` exposes `handle_errors` in Python and `handleErrors`
in JavaScript. Use it to control handling when data fails schema parsing or a
model emits multiple structured-output tool calls.

### Inspect model capability profiles

Chat models in `1.1.0` expose `.profile`, with declarative capability data for
structured output, function calling, and JSON mode. Profiles come from the
cross-provider models.dev index, so agent logic can inspect support without
hard-coding it by model.

```python
capabilities = chat_model.profile
```

Summarization middleware consults profiles to decide when and how to
summarize, enabling flexible trigger points and provider-specific behavior in
long-running sessions. `ProviderStrategy` can also be inferred directly from
a profile, allowing an agent to select native structured output without
hand-written provider capability logic.

## Content blocks

The `1.0-guide` adds `.content_blocks` to messages as a backward-compatible,
typed representation shared across providers. It normalizes reasoning traces,
citations, tool calls, and server-side tool calls for streams, frontends, and
memory stores.

```python
blocks = message.content_blocks
```

At `1.0.0`, Python content blocks are supported only by
`langchain-anthropic`, `langchain-aws`, `langchain-openai`,
`langchain-google-genai`, and `langchain-ollama`. JavaScript support is limited
to `langchain`, `@langchain/core`, `@langchain/anthropic`, and
`@langchain/openai`.

## Packages and runtime

The `1.0-guide` narrows the main package to core abstractions and moves legacy
APIs into separately installed `langchain-classic` or
`@langchain/langchain-classic`. The Python release requires Python 3.10 or
newer; Python 3.9 is unsupported.

```shell
uv pip install --upgrade langchain
uv pip install langchain-classic

npm install @langchain/langchain@latest
npm install @langchain/langchain-classic
```

LangGraph otherwise preserves backward compatibility at this boundary, but
deprecates `langgraph.prebuilt` as enhanced agent functionality moves to
`langchain.agents`.

```shell
uv pip install --upgrade langgraph
npm install @langchain/langgraph@latest
```

The JavaScript `1.0.0` release upgrades the unscoped `langchain` package
alongside `@langchain/core`. Legacy chains, retrievers, indexing APIs, and
community exports move to `@langchain/classic`, including the subpath change
from `langchain/chains` to `@langchain/classic/chains`.

```shell
npm install langchain @langchain/core
npm install @langchain/classic
```
