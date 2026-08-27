# Anthropic Integration

## Native schema enforcement

`bind_tools(..., strict=True)` enables constrained, schema-valid tool
arguments. Unsupported JSON Schema features produce a 400 response rather
than falling back. For direct structured responses,
`with_structured_output(..., method="json_schema")` selects native schema
generation instead of the default function-calling method.

```python
strict_model = model.bind_tools([book_flight], strict=True)
structured_model = model.with_structured_output(Movie, method="json_schema")
```

## Tool input examples

Complex tools can attach valid argument examples through `BaseTool.extras`.
The examples become provider tool metadata rather than model-visible tool
parameters.

```python
@tool(extras={"input_examples": [{"query": "weather", "location": "Oslo"}]})
def search_weather(query: str, location: str) -> str:
    return lookup(query, location)
```

## Fine-grained tool-argument streaming

Enable `fine-grained-tool-streaming-2025-05-14` in `ChatAnthropic.betas` to
receive large arguments incrementally as `input_json_delta` blocks.
Concatenate each block's `partial_json`, but tolerate invalid or incomplete
JSON, especially when generation reaches `max_tokens`.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    betas=["fine-grained-tool-streaming-2025-05-14"],
)
```

## Programmatic tool callers

To let the server-side code sandbox call an application tool:

1. Bind `code_execution_20250825`.
2. Add `extras={"allowed_callers": ["code_execution_20250825"]}` to the
   application tool.
3. Enable the `advanced-tool-use-2025-11-20` beta.

`reuse_last_container=True` carries the previous response's container into
later calls automatically.

```python
@tool(extras={"allowed_callers": ["code_execution_20250825"]})
def get_weather(location: str) -> str:
    return lookup_weather(location)
```

## Response effort

`ChatAnthropic(effort=...)` accepts `"low"`, `"medium"`, `"high"`, or
`"max"` to trade response depth for token use and latency. Omitting the value
is equivalent to `"high"`; `"max"` is limited to Opus 4.6.

## Citable retrieval results

A retrieval tool may return native `search_result` blocks with citations
enabled. Resulting response text blocks carry citation locations and
provenance. This applies to tool results as well as top-level document or
search-result inputs.

```python
return [{
    "type": "search_result",
    "title": doc.title,
    "source": doc.source,
    "citations": {"enabled": True},
    "content": [{"type": "text", "text": doc.page_content}],
}]
```

## Prompt caching

The default ephemeral cache lasts five minutes. Enable
`extended-cache-ttl-2025-04-11` and set `"ttl": "1h"` on a content block for
an hour-long entry. Runtime-dependent caching can instead pass
`cache_control={"type": "ephemeral"}` to `invoke`; tool definitions accept
the same metadata through `extras`.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    betas=["extended-cache-ttl-2025-04-11"],
)
block = {
    "type": "text",
    "text": long_text,
    "cache_control": {"type": "ephemeral", "ttl": "1h"},
}
```

## Context edits and compaction

`context_management` can remove old tool uses when the
`context-management-2025-06-27` beta is enabled and a
`clear_tool_uses_20250919` edit is configured.

Opus 4.6 separately supports server compaction with `compact-2026-01-12`.
Retain returned compaction blocks in subsequent message history.

```python
compact_model = ChatAnthropic(
    model="claude-opus-4-6",
    betas=["compact-2026-01-12"],
    context_management={"edits": [{
        "type": "compact_20260112",
        "trigger": {"type": "input_tokens", "value": 50_000},
    }]},
)
```

## Client-side provider tools

The bash, computer-use, text-editor, and memory specifications describe calls
but do not execute them. The application must execute those calls and return
correlated tool results.

Decorate an executable LangChain tool with
`extras["provider_tool_definition"]` so `create_agent` can run its loop, or
use the supplied Anthropic middleware implementations. Binding a beta tool
automatically adds its required beta header.

```python
spec = BetaToolBash20250124Param(name="bash", type="bash_20250124")

@tool(extras={"provider_tool_definition": spec})
def bash(command: str, restart: bool = False) -> str:
    return sandbox.run(command, restart=restart)
```

## Server code execution and files

`code_execution_20250825` runs in an internet-disabled server sandbox.
`reuse_last_container=True` reuses its state across responses.

Upload a file through the Anthropic Files API and send its ID in a
`container_upload` block. Generated-file IDs in tool-result blocks can be
downloaded through the same API.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    reuse_last_container=True,
)
model = model.bind_tools([
    {"type": "code_execution_20250825", "name": "code_execution"}
])
```

## Remote MCP toolsets

Remote MCP configuration has two parts: register URL servers in
`ChatAnthropic(mcp_servers=...)`, then expose each server using an
`mcp_toolset` whose `mcp_server_name` matches. A server entry may include an
authorization token and restrict allowed tools.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    mcp_servers=[{"type": "url", "url": server_url, "name": "docs"}],
)
model = model.bind_tools([
    {"type": "mcp_toolset", "mcp_server_name": "docs"}
])
```

## Regex and BM25 tool discovery

Anthropic tool search provides regex (`tool_search_tool_regex_20251119`) and
natural-language BM25 (`tool_search_tool_bm25_20251119`) variants. Mark
catalog tools with `extras={"defer_loading": True}` so only tools found by the
bound search tool enter context.

```python
@tool(extras={"defer_loading": True})
def search_files(query: str) -> str:
    return index.search(query)

model = model.bind_tools([
    {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
    search_files,
])
```
