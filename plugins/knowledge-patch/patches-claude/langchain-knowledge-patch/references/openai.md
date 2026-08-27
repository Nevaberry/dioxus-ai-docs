# OpenAI Integration

## API boundary and Azure v1

`ChatOpenAI` targets official API schemas. It does not extract or preserve
non-standard fields added by compatible third-party endpoints. Use the
endpoint's provider-specific integration when those fields matter.

With `langchain-openai>=1.0.1`, Azure's v1 API works through `ChatOpenAI`.
Append `/openai/v1/` to the resource URL and use the deployment name as
`model`. `api_key` can be an automatically refreshing Entra token-provider
callable. An async callable requires `ainvoke`, `astream`, or another async
method.

```python
llm = ChatOpenAI(
    model="my-deployment",
    base_url="https://my-resource.openai.azure.com/openai/v1/",
    api_key=token_provider,
)
```

## Custom and structured tools

### Accept raw-string tool input

`langchain_openai.custom_tool` defines a Responses tool whose input is one
arbitrary string rather than a JSON object. Its `format=` can constrain the
string with a Lark or regex grammar.

```python
from langchain_openai import custom_tool

@custom_tool
def execute_code(code: str) -> str:
    return run_safely(code)
```

### Combine ordinary tools with structured output

`bind_tools` accepts `response_format` and `strict=True` together. An
invocation may then return ordinary tool calls or schema-conforming output.
Parsed schema output is available in
`response.additional_kwargs["parsed"]`.

```python
structured = ChatOpenAI(model="gpt-4.1").bind_tools(
    [get_weather], response_format=OutputSchema, strict=True
)
```

## Responses API selection and server tools

`ChatOpenAI` automatically selects the Responses API when a requested feature
requires it, including built-in tools, conversation-state IDs, and reasoning
summaries. Set `use_responses_api=True` to select it explicitly.

Web search, image generation, and file search are passed to `bind_tools` as
provider tool dictionaries. File search requires an OpenAI-managed vector
store ID. Calls, results, citations, and generated images are normalized into
`response.content_blocks`; `response.text` contains only text.

```python
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools([
    {"type": "web_search_preview"},
    {"type": "image_generation", "quality": "low"},
    {"type": "file_search", "vector_store_ids": ["vs_..."]},
])
```

## Deferred tool loading

Mark a tool with `extras={"defer_loading": True}` and expose
`{"type": "tool_search"}` so its definition is loaded only when needed. Add
`"execution": "client"` to get `tool_search_call` blocks that the application
answers with `tool_search_output` blocks.

```python
@tool(extras={"defer_loading": True})
def get_weather(location: str) -> str:
    return lookup_weather(location)

agent = create_agent(model, tools=[get_weather, {"type": "tool_search"}])
```

## Computer use and code interpreter

Bind computer use as `computer_use_preview` with display dimensions and an
environment. Answer each `computer_call` with a correlated `ToolMessage`: its
screenshot content is an `input_image`, and `additional_kwargs` identifies
`computer_call_output`.

```python
tool_message = ToolMessage(
    content=[{"type": "input_image", "image_url": screenshot_data_url}],
    tool_call_id=computer_call["call_id"],
    additional_kwargs={"type": "computer_call_output"},
)
```

The built-in code interpreter accepts `{"container": {"type": "auto"}}` to
create a sandbox. Its call block exposes `extras["container_id"]`; pass that
ID as `container` in a later tool definition to reuse the sandbox.

```python
tool = {"type": "code_interpreter", "container": {"type": "auto"}}
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools([tool])
```

## Remote MCP approvals

The Responses MCP tool accepts `server_label`, `server_url`, and
`require_approval`. Approval can be `"never"`, `"always"`, or a per-tool
policy. Answer an `mcp_approval_request` with an `mcp_approval_response` input
block and continue the thread using the response ID.

```python
approval = {
    "type": "mcp_approval_response",
    "approve": True,
    "approval_request_id": request_block["id"],
}
```

## Conversation state and context compaction

Pass `previous_response_id=response.id` to continue a Responses conversation
without resending its messages. With `use_previous_response_id=True`,
`ChatOpenAI` finds the most recent response in the input sequence, removes
messages through that response from the request payload, and supplies its ID.

```python
llm = ChatOpenAI(model="gpt-4.1-mini", use_previous_response_id=True)
```

Configure a compaction threshold with `context_management`. Returned
`compaction` content blocks must remain in history. Messages before the newest
compaction block may be discarded to reduce latency.

```python
model = ChatOpenAI(
    model="gpt-5.2",
    context_management=[{"type": "compaction", "compact_threshold": 100_000}],
)
```

## Reasoning output

The `reasoning` parameter controls effort and requests a summary, selecting
the Responses API automatically. Summaries appear in `reasoning` content
blocks. Leave `max_tokens=None` or allocate enough output tokens; reasoning
can otherwise consume the limit before final text is generated.

```python
model = ChatOpenAI(
    model="gpt-5-nano",
    reasoning={"effort": "medium", "summary": "auto"},
)
```

In `openai-1.5.2`, Responses output preserves boundaries between individual
reasoning items. Code that stores, inspects, or replays reasoning can keep
those items separate instead of treating adjacent reasoning as one item.

## PDF input

A cross-provider PDF block must include a filename as well as media type and
data. The provider rejects unnamed PDF inputs.

```python
pdf = {
    "type": "file",
    "base64": pdf_base64,
    "mime_type": "application/pdf",
    "filename": "report.pdf",
}
```

## Prompt-cache affinity

Pass `prompt_cache_key` per invocation to improve cache affinity for identical
prompt prefixes. Read hits from
`response.usage_metadata.input_token_details.cache_read`. A default may be set
in `model_kwargs` and overridden per call.

```python
response = llm.invoke(messages, prompt_cache_key="support-v1")
```

## Token counting

In `openai-1.5.2`, `get_num_tokens_from_messages` supports o-series models,
providing the integration's built-in message-token estimate for those models.

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="o3")
token_count = model.get_num_tokens_from_messages(messages)
```
