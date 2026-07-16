# v1 Migration and Core Types

## Package and runtime boundary

LangChain v1 narrows the main package to core agent abstractions. Keep new code
on the main package and install a classic package only while migrating legacy
chains, retrievers, indexing APIs, and community exports.

### Python

Python 3.9 is no longer supported; use Python 3.10 or newer.

```sh
uv pip install --upgrade langchain
uv pip install langchain-classic
```

Move legacy imports to `langchain_classic` while replacing them with current
agent, model, tool, or retrieval abstractions. Do not assume that an import which
existed under `langchain` remains re-exported from the slim package.

### JavaScript

The `1.0.0` package migration uses the unscoped `langchain` package alongside
`@langchain/core`. Legacy APIs live in `@langchain/classic`.

```sh
npm install langchain @langchain/core
npm install @langchain/classic
```

Update subpaths as well as package dependencies. For example:

```ts
// Before
import { SomeChain } from "langchain/chains";

// Migration location
import { SomeChain } from "@langchain/classic/chains";
```

The scoped package names shown in the separate `1.0-guide` conflict with the
release-specific names above; the merged guidance follows the `1.0.0` entry.

## Agent migration

`langchain.agents.create_agent` is the LangGraph-backed model/tool loop for v1.
It supersedes the deprecated `create_react_agent` from `langgraph.prebuilt` and
adds middleware, structured output in the loop, typed state, and provider model
strings.

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",
    tools=[get_weather],
    system_prompt="Help the user by fetching weather when needed.",
)
```

LangGraph 1.0 otherwise preserves backward compatibility, but
`langgraph.prebuilt` is deprecated as the enhanced agent implementation moves to
`langchain.agents`.

```sh
uv pip install --upgrade langgraph
npm install @langchain/langgraph@latest
```

Do not translate every legacy chain into a hand-written graph automatically.
First determine whether `create_agent` plus middleware expresses the same model,
tool, state, approval, retry, and output policies.

## Provider-neutral content blocks

Messages expose `.content_blocks`, a backward-compatible typed representation of
complex content. It normalizes text, reasoning traces, citations, ordinary tool
calls, server-side tool calls, and multimodal data so streaming code, frontends,
and memory stores do not need a separate shape for every provider.

```python
for block in message.content_blocks:
    handle(block)
```

Use `.content_blocks` for structured inspection and retain provider blocks whose
protocol requires them in later history. Use convenience text accessors only
when non-text blocks can safely be ignored.

### Initial rollout limits

At the v1 release, Python content blocks were supported by these integrations:

- `langchain-anthropic`
- `langchain-aws`
- `langchain-openai`
- `langchain-google-genai`
- `langchain-ollama`

JavaScript support was limited to:

- `langchain`
- `@langchain/core`
- `@langchain/anthropic`
- `@langchain/openai`

Check the integration before depending on normalized blocks in a mixed-provider
application. A model response may still expose provider-specific data that the
common block contract does not preserve.

## `SystemMessage` as an agent prompt

`create_agent(system_prompt=...)` accepts a `SystemMessage`, not only a string.
Use it for cache-control blocks, structured orchestration hints, and other rich
content that cannot be represented by a plain prompt string.

```python
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

agent = create_agent(
    model="openai:gpt-5",
    tools=[],
    system_prompt=SystemMessage(content="Answer concisely."),
)
```

In JavaScript, prompt middleware is now compositional: values returned by
`dynamicSystemPromptMiddleware` extend existing system messages. Returning a
string or `SystemMessage` no longer replaces the prompt assembled so far.

## Google GenAI v4

`langchain-google-genai` v4 is rebuilt on Google's consolidated Generative AI
SDK. It provides Gemini API and Vertex AI access through one integration.
Upgrades can require small changes, and the corresponding packages in
`langchain-google-vertexai` are deprecated.

Audit imports, client construction, credentials, and provider-specific options
when upgrading; do not preserve a deprecated Vertex AI package merely because
the common LangChain model interface is unchanged.
