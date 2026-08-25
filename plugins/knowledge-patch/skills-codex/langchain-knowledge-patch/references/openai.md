# OpenAI Integration

## Integration boundary and endpoint selection

### Official API schemas

`ChatOpenAI` targets official API schemas. It does not extract or preserve
non-standard fields added by compatible third-party endpoints. Use the
endpoint's provider-specific integration when those fields matter.

### Azure v1 endpoints

With `langchain-openai>=1.0.1`, Azure's v1 API works through `ChatOpenAI`.
Append `/openai/v1/` to the resource URL and use the deployment name as
`model`. `api_key` may be an automatically refreshing Entra token-provider
callable; an async callable requires `ainvoke`, `astream`, or another async
method.

```python
llm = ChatOpenAI(
    model="my-deployment",
    base_url="https://my-resource.openai.azure.com/openai/v1/",
    api_key=token_provider,
)
```

### Responses API routing

`ChatOpenAI` automatically selects the Responses API when a requested feature
requires it, including built-in tools, conversation-state IDs, and reasoning
summaries. Set `use_responses_api=True` to select it explicitly.

## Tool definitions and structured output

### Raw-string custom tools

`langchain_openai.custom_tool` creates Responses tools whose input is one
arbitrary string instead of a JSON object. Its `format=` can constrain the
string with a Lark or regex grammar.

```python
from langchain_openai import custom_tool

@custom_tool
def execute_code(code: str) -> str:
    """Execute code."""
    return run_safely(code)
```

### Structured output beside ordinary tool calls

`bind_tools` accepts `response_format` and `strict=True` together, so one
invocation can return ordinary tool calls or schema-conforming output. Parsed
schema output appears in `response.additional_kwargs["parsed"]`.

```python
structured = ChatOpenAI(model="gpt-4.1").bind_tools(
    [get_weather], response_format=OutputSchema, strict=True
)
```

### Deferred definitions and tool search

Mark a tool `extras={"defer_loading": True}` and expose
`{"type": "tool_search"}` so the model can load its definition only when
needed. Adding `"execution": "client"` makes the search produce
`tool_search_call` blocks, which the application answers with
`tool_search_output` blocks.

```python
@tool(extras={"defer_loading": True})
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return lookup_weather(location)

agent = create_agent(model, tools=[get_weather, {"type": "tool_search"}])
```

## Server-executed tools

### Search and image tools

Pass web search, image generation, and file search to `bind_tools` as provider
tool dictionaries. File search requires an OpenAI-managed vector-store ID.
Calls, results, citations, and generated images are normalized into
`response.content_blocks`; `response.text` returns text only.

```python
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools([
    {"type": "web_search_preview"},
    {"type": "image_generation", "quality": "low"},
    {"type": "file_search", "vector_store_ids": ["vs_..."]},
])
```

### Computer-use screenshot loop

Bind computer use as `computer_use_preview` with display dimensions and an
environment. Answer each `computer_call` with a correlated `ToolMessage`; its
screenshot content is `input_image` and `additional_kwargs` identifies
`computer_call_output`.

```python
tool_message = ToolMessage(
    content=[{"type": "input_image", "image_url": screenshot_data_url}],
    tool_call_id=computer_call["call_id"],
    additional_kwargs={"type": "computer_call_output"},
)
```

### Code-interpreter container reuse

The built-in code interpreter accepts `{"container": {"type": "auto"}}` to
create a sandbox. Its call block exposes `extras["container_id"]`; pass that ID
as `container` in a later tool definition to reuse the sandbox.

```python
tool = {"type": "code_interpreter", "container": {"type": "auto"}}
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools([tool])
```

## Remote MCP approval loop

The Responses MCP tool takes `server_label`, `server_url`, and
`require_approval`. Approval can be `"never"`, `"always"`, or a per-tool
policy. Answer `mcp_approval_request` with an `mcp_approval_response` input
block, then continue with the response ID.

```python
approval = {
    "type": "mcp_approval_response",
    "approve": True,
    "approval_request_id": request_block["id"],
}
```

## Conversation state and context

### Response-ID continuation

Pass `previous_response_id=response.id` to continue a Responses conversation
without resending messages. With `use_previous_response_id=True`,
`ChatOpenAI` finds the most recent response in the input, removes messages
through it from the request payload, and supplies its ID automatically.

```python
llm = ChatOpenAI(model="gpt-4.1-mini", use_previous_response_id=True)
```

### Server-side compaction

Set a compaction threshold with `context_management`. Keep returned
`compaction` content blocks in history. Messages before the newest such block
may be discarded to reduce latency.

```python
model = ChatOpenAI(
    model="gpt-5.2",
    context_management=[{"type": "compaction", "compact_threshold": 100_000}],
)
```

### Reasoning summaries

The `reasoning` parameter controls effort and requests a summary, automatically
selecting the Responses API. Summaries are `reasoning` content blocks. Leave
`max_tokens=None` or provide enough output tokens; reasoning can otherwise use
the limit before final text is produced.

```python
model = ChatOpenAI(
    model="gpt-5-nano", reasoning={"effort": "medium", "summary": "auto"}
)
```

## File inputs and cache affinity

### PDF filenames

The cross-provider PDF block needs `filename` as well as media type and data.
The provider rejects unnamed PDF input.

```python
pdf = {
    "type": "file",
    "base64": pdf_base64,
    "mime_type": "application/pdf",
    "filename": "report.pdf",
}
```

### Prompt-cache keys

Pass `prompt_cache_key` per invocation to improve cache affinity for identical
prompt prefixes. Cache hits are in
`response.usage_metadata.input_token_details.cache_read`. A default can be set
in `model_kwargs` and overridden on an invocation.

```python
response = llm.invoke(messages, prompt_cache_key="support-v1")
```

## Responses behavior fixes (`openai-1.5.2`)

Responses output preserves boundaries between individual reasoning items, so
stored, inspected, or replayed reasoning can keep those items distinct rather
than merging adjacent items.

`get_num_tokens_from_messages` supports o-series models, providing the
integration's built-in message-token estimate.

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="o3")
token_count = model.get_num_tokens_from_messages(messages)
```
