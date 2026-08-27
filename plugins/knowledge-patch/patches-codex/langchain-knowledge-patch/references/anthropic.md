# Anthropic Integration

## Schema-constrained tools and output

`bind_tools(..., strict=True)` enables constrained, schema-valid tool
arguments. Unsupported JSON Schema features cause a 400 error rather than a
fallback. For direct structured responses,
`with_structured_output(..., method="json_schema")` selects native schema
generation instead of the default function-calling method.

```python
strict_model = model.bind_tools([book_flight], strict=True)
structured_model = model.with_structured_output(Movie, method="json_schema")
```

## Tool metadata and argument streaming

### Input examples

Complex tools can provide valid argument examples through `BaseTool.extras`.
The examples become provider tool metadata, not model-visible tool parameters.

```python
@tool(extras={"input_examples": [{"query": "weather", "location": "Oslo"}]})
def search_weather(query: str, location: str) -> str:
    return lookup(query, location)
```

### Fine-grained argument streaming

Enable `fine-grained-tool-streaming-2025-05-14` in `ChatAnthropic.betas` to
receive large arguments incrementally as `input_json_delta` blocks.
Concatenate each `partial_json`, but tolerate incomplete or invalid JSON,
especially when generation reaches `max_tokens`.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    betas=["fine-grained-tool-streaming-2025-05-14"],
)
```

## Code execution and programmatic callers

### Application tools called from server code

To let the server code sandbox invoke an application tool, bind
`code_execution_20250825`, mark the application tool with
`extras={"allowed_callers": ["code_execution_20250825"]}`, and enable the
`advanced-tool-use-2025-11-20` beta. `reuse_last_container=True` carries the
previous response's container into later calls.

```python
@tool(extras={"allowed_callers": ["code_execution_20250825"]})
def get_weather(location: str) -> str:
    return lookup_weather(location)
```

### Server sandbox and files

`code_execution_20250825` runs in an internet-disabled server sandbox, and
`reuse_last_container=True` reuses its state across responses. Upload a file
with the Anthropic Files API and send its ID in a `container_upload` block.
Generated-file IDs in tool-result blocks can be downloaded with the same API.

```python
model = ChatAnthropic(model="claude-sonnet-4-6", reuse_last_container=True)
model = model.bind_tools([
    {"type": "code_execution_20250825", "name": "code_execution"}
])
```

## Response effort

`ChatAnthropic(effort=...)` accepts `"low"`, `"medium"`, `"high"`, or
`"max"` to trade response depth for tokens and latency. Omitting it equals
`"high"`; `"max"` is limited to Opus 4.6.

## Citable retrieval results

A retrieval tool may return native `search_result` blocks with citations
enabled. Response text blocks then carry citation locations and provenance.
This works for tool results and for top-level document or search-result input.

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
`extended-cache-ttl-2025-04-11` and set `"ttl": "1h"` on a content block for a
one-hour entry. Runtime-dependent caching can pass
`cache_control={"type": "ephemeral"}` to `invoke`; tool definitions accept the
same metadata through `extras`.

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

With the `context-management-2025-06-27` beta, `context_management` can remove
old tool uses through a `clear_tool_uses_20250919` edit. Opus 4.6 separately
supports server compaction with `compact-2026-01-12`; retain returned
compaction blocks in later message history.

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

Bash, computer-use, text-editor, and memory specifications only describe
calls. The application must execute them and return correlated results.
Decorate an executable LangChain tool with
`extras["provider_tool_definition"]` so `create_agent` can run the loop, or use
the supplied Anthropic middleware implementations. Binding a beta tool adds
its required beta header automatically.

```python
spec = BetaToolBash20250124Param(name="bash", type="bash_20250124")

@tool(extras={"provider_tool_definition": spec})
def bash(command: str, restart: bool = False) -> str:
    return sandbox.run(command, restart=restart)
```

## Remote MCP toolsets

Remote MCP configuration requires both registering URL servers through
`ChatAnthropic(mcp_servers=...)` and exposing each server through an
`mcp_toolset` whose `mcp_server_name` matches. A server entry can carry an
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

Anthropic tool search has regex (`tool_search_tool_regex_20251119`) and
natural-language BM25 (`tool_search_tool_bm25_20251119`) variants. Mark catalog
tools with `extras={"defer_loading": True}` so only tools found by the bound
search tool enter context.

```python
@tool(extras={"defer_loading": True})
def search_files(query: str) -> str:
    return index.search(query)

model = model.bind_tools([
    {"type": "tool_search_tool_regex_20251119",
     "name": "tool_search_tool_regex"},
    search_files,
])
```
