# OpenAI Integration

## Choose the correct integration boundary

`ChatOpenAI` targets official API schemas. Compatible third-party endpoints may
add non-standard fields, but this integration does not extract or preserve them.
Use the endpoint's provider-specific integration whenever those fields are part
of the application's contract.

## Azure v1 endpoints

With `langchain-openai>=1.0.1`, Azure's v1 API is available through
`ChatOpenAI`. Append `/openai/v1/` to the resource URL and pass the deployment
name as `model`.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="my-deployment",
    base_url="https://my-resource.openai.azure.com/openai/v1/",
    api_key=token_provider,
)
```

`api_key` may be an automatically refreshing Entra token-provider callable. If
that callable is asynchronous, invoke the model through `ainvoke`, `astream`, or
another async method.

## Responses API routing

`ChatOpenAI` automatically selects the Responses API when a requested feature
requires it, including built-in tools, conversation-state IDs, and reasoning
summaries. Set `use_responses_api=True` when the application should select it
explicitly.

Keep consuming normalized LangChain response fields. Provider calls, results,
citations, generated images, reasoning, and compaction data appear in
`response.content_blocks`; `response.text` includes text only.

JavaScript `@langchain/openai` supports provider-side file search, web search,
code interpreter, image generation, computer use, shell, and MCP connector tools.
`ChatOpenAI` also exposes `moderateContent`, and GPT-5.2 Pro prefers the Responses
API.

## Raw-string custom tools

`langchain_openai.custom_tool` defines a Responses tool whose input is one
arbitrary string rather than a JSON object. Use `format=` with a Lark or regex
grammar when the string must follow a constrained language.

```python
from langchain_openai import custom_tool

@custom_tool
def execute_code(code: str) -> str:
    """Execute code."""
    return run_safely(code)
```

Treat the grammar as input validation, not as sandboxing. Validate authorization
and isolate execution independently.

## Structured output with ordinary tools

`bind_tools` accepts `response_format` together with `strict=True`, so one model
invocation may return an ordinary tool call or schema-conforming final output.
The parsed schema value is stored in `response.additional_kwargs["parsed"]`.

```python
structured = ChatOpenAI(model="gpt-4.1").bind_tools(
    [get_weather],
    response_format=OutputSchema,
    strict=True,
)
```

Handle both branches. Do not assume that binding a response schema prevents the
model from selecting one of the ordinary tools.

## Server-executed tools

Pass provider tool dictionaries to `bind_tools`. File search requires an
OpenAI-managed vector-store ID.

```python
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools([
    {"type": "web_search_preview"},
    {"type": "image_generation", "quality": "low"},
    {"type": "file_search", "vector_store_ids": ["vs_..."]},
])
```

The provider executes these tools. Inspect `content_blocks` for calls, results,
citations, and images rather than waiting for an application-side tool function.

## Deferred loading and tool search

Set `extras={"defer_loading": True}` on catalog tools and expose a
`{"type": "tool_search"}` tool. The model can then load a definition only when
needed.

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool(extras={"defer_loading": True})
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return lookup_weather(location)

agent = create_agent(
    model,
    tools=[get_weather, {"type": "tool_search"}],
)
```

Add `"execution": "client"` to the search definition when the application owns
execution. The provider then emits `tool_search_call` blocks, and the application
must answer with `tool_search_output` blocks.

## Computer-use screenshot loop

Bind computer use as `computer_use_preview` with display dimensions and an
environment. For every `computer_call`, return a correlated `ToolMessage` whose
content is an `input_image` screenshot and whose `additional_kwargs` type is
`computer_call_output`.

```python
from langchain_core.messages import ToolMessage

tool_message = ToolMessage(
    content=[{
        "type": "input_image",
        "image_url": screenshot_data_url,
    }],
    tool_call_id=computer_call["call_id"],
    additional_kwargs={"type": "computer_call_output"},
)
```

Keep the screenshot correlated to the call ID and apply a separate policy for
display capture, actions, credentials, and human approval.

## Code-interpreter containers

Use `{"container": {"type": "auto"}}` to create a server sandbox. The returned
call block exposes its identifier at `extras["container_id"]`; supply that ID as
`container` in a later tool definition to reuse the sandbox.

```python
tool = {
    "type": "code_interpreter",
    "container": {"type": "auto"},
}
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools([tool])
```

Persist the container ID only for the intended conversation or task boundary.

## Remote MCP approvals

The Responses MCP tool accepts `server_label`, `server_url`, and
`require_approval`. Approval may be `"never"`, `"always"`, or a per-tool policy.
Answer an `mcp_approval_request` with an `mcp_approval_response` input block, then
continue using the response ID.

```python
approval = {
    "type": "mcp_approval_response",
    "approve": True,
    "approval_request_id": request_block["id"],
}
```

Treat the request ID as the authority being approved; do not approve based only
on a displayed tool name.

## Continue conversations by response ID

Pass `previous_response_id=response.id` to continue a Responses conversation
without resending its message history.

With `use_previous_response_id=True`, `ChatOpenAI` finds the newest response in
the supplied input sequence, removes messages through that response from the
request payload, and supplies the ID automatically.

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    use_previous_response_id=True,
)
```

Do not combine this optimization with application logic that assumes the full
history is serialized in each outbound request.

## Server-side context compaction

Configure a threshold with `context_management`. Returned `compaction` content
blocks must remain in conversation history. Messages before the newest retained
compaction block may be discarded to reduce latency.

```python
model = ChatOpenAI(
    model="gpt-5.2",
    context_management=[{
        "type": "compaction",
        "compact_threshold": 100_000,
    }],
)
```

Persist the compaction block as protocol state; it is not merely display text.

## Reasoning summaries and output budgets

The `reasoning` parameter selects effort and can request a summary, which also
selects the Responses API. Summaries appear as `reasoning` content blocks.

```python
model = ChatOpenAI(
    model="gpt-5-nano",
    reasoning={"effort": "medium", "summary": "auto"},
)
```

Leave `max_tokens=None` or allocate enough output tokens. Reasoning can consume a
tight limit before the model emits final text.

## PDF inputs

Cross-provider PDF blocks require a filename in addition to media type and data;
unnamed PDF inputs are rejected.

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
`response.usage_metadata.input_token_details.cache_read`.

```python
response = llm.invoke(messages, prompt_cache_key="support-v1")
```

A default may be set in `model_kwargs` and overridden per call. Use stable keys
for genuinely shared prefixes; do not include volatile or secret values merely
to make the key unique.
