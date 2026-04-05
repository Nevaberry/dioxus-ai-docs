# Namespace Changes & Migration (LangChain 1.0)

## Simplified Namespace

The `langchain` package is trimmed to five modules:

- `langchain.agents`
- `langchain.messages`
- `langchain.tools`
- `langchain.chat_models`
- `langchain.embeddings`

## langchain-classic

Legacy chains, retrievers, indexing, hub, and community re-exports moved to `langchain-classic`:

```python
# pip install langchain-classic
from langchain_classic.chains import LLMChain
from langchain_classic.retrievers import ...
from langchain_classic import hub
```

## Deep Agents SDK

New `deepagents` package (`pip install deepagents`) for complex multi-step tasks with built-in planning, filesystem tools, subagent spawning, and long-term memory:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[my_tool],
    system_prompt="You are a helpful assistant",
)
```

### Built-in Capabilities

- `write_todos` — planning and task tracking
- `ls`, `read_file`, `write_file`, `edit_file` — context management
- `task` — subagent spawning

### Filesystem Backends

Pluggable filesystem backends: in-memory, local disk, LangGraph store, sandboxes.

## Breaking Changes

- **Python 3.10+** required (3.9 dropped)
- `message.text` is now a **property** (not method) — use `response.text` not `response.text()`
- `example` parameter removed from `AIMessage`
- `langchain-anthropic` `max_tokens` default increased (was 1024)
- Chat model return type fixed to `AIMessage` (was `BaseMessage`)
- OpenAI Responses API now defaults to storing response items in message `content`
