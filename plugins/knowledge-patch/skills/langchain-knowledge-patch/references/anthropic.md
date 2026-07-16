# Anthropic Integration

## Native schema enforcement

Use `bind_tools(..., strict=True)` for constrained, schema-valid tool arguments.
Unsupported JSON Schema features cause a 400 response rather than silently
falling back to unconstrained generation.

For a direct structured response, use
`with_structured_output(..., method="json_schema")` to select native schema
generation. The default method is function calling.

```python
strict_model = model.bind_tools([book_flight], strict=True)
structured_model = model.with_structured_output(
    Movie,
    method="json_schema",
)
```

Validate schemas before production calls; strict mode makes unsupported schema
constructs an integration error rather than a best-effort prompt hint.

## Provider-side tools

JavaScript `@langchain/anthropic` supports provider-side text editing, web fetch,
computer use, tool search, and MCP toolsets. Distinguish provider execution from
client-side tool specifications: some definitions only describe a call that the
application must perform.

## Tool input examples

Attach valid argument examples to a complex `BaseTool` through `extras`. They
become provider tool metadata and are not added as model-visible parameters.

```python
from langchain.tools import tool

@tool(extras={
    "input_examples": [{"query": "weather", "location": "Oslo"}],
})
def search_weather(query: str, location: str) -> str:
    return lookup(query, location)
```

Examples supplement the schema and description; they do not relax validation.

## Fine-grained tool-argument streaming

Enable the `fine-grained-tool-streaming-2025-05-14` beta in
`ChatAnthropic.betas` to receive large arguments incrementally as
`input_json_delta` blocks.

```python
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(
    model="claude-sonnet-4-6",
    betas=["fine-grained-tool-streaming-2025-05-14"],
)
```

Concatenate each block's `partial_json`, but tolerate incomplete or invalid JSON
until the stream completes. A stream that reaches `max_tokens` may never contain
a complete JSON value.

## Programmatic tool callers

Server-side code execution can invoke an application tool when all three pieces
are configured:

1. Bind `code_execution_20250825`.
2. Mark the callable tool with
   `extras={"allowed_callers": ["code_execution_20250825"]}`.
3. Enable the `advanced-tool-use-2025-11-20` beta.

```python
@tool(extras={
    "allowed_callers": ["code_execution_20250825"],
})
def get_weather(location: str) -> str:
    return lookup_weather(location)
```

Set `reuse_last_container=True` when later responses should automatically reuse
the preceding response's code-execution container.

## Response effort

`ChatAnthropic(effort=...)` accepts `"low"`, `"medium"`, `"high"`, or `"max"`
to trade response depth for token use and latency. Omitting the value is
equivalent to `"high"`; `"max"` is limited to Opus 4.6.

Choose effort independently from output-token limits. A higher effort setting
does not guarantee enough budget for a complete visible result.

## Citable retrieval results

A retrieval tool may return native `search_result` blocks with citations
enabled. Text blocks in the model response then include citation locations and
provenance. This also works for top-level document and search-result inputs.

```python
return [{
    "type": "search_result",
    "title": doc.title,
    "source": doc.source,
    "citations": {"enabled": True},
    "content": [{"type": "text", "text": doc.page_content}],
}]
```

Preserve the structured blocks when rendering citations; flattening the tool
result to plain text loses its native provenance contract.

## Prompt-cache duration

The default ephemeral cache lasts five minutes. To request a one-hour entry,
enable `extended-cache-ttl-2025-04-11` and set `"ttl": "1h"` on the content
block.

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

For runtime-dependent caching, pass
`cache_control={"type": "ephemeral"}` to `invoke`. Tool definitions accept the
same cache metadata through `extras`.

## Context edits and compaction

`context_management` supports two distinct mechanisms:

- With `context-management-2025-06-27`, a `clear_tool_uses_20250919` edit can
  remove old tool uses.
- Opus 4.6 supports server compaction with the `compact-2026-01-12` beta and a
  `compact_20260112` edit.

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

Retain returned compaction blocks in every subsequent message history. They are
continuation state, not optional explanatory output.

## Client-side provider tools

Bash, computer-use, text-editor, and memory specifications describe calls; the
application must execute them and return correlated tool results.

To let `create_agent` run the loop, decorate an executable LangChain tool and put
the provider specification in `extras["provider_tool_definition"]`, or use the
supplied Anthropic middleware implementations.

```python
spec = BetaToolBash20250124Param(
    name="bash",
    type="bash_20250124",
)

@tool(extras={"provider_tool_definition": spec})
def bash(command: str, restart: bool = False) -> str:
    return sandbox.run(command, restart=restart)
```

Binding a beta tool automatically adds its required beta header. That does not
provide an executor or sandbox for a client-side specification.

## Server code execution and files

`code_execution_20250825` runs in an internet-disabled server sandbox.
`reuse_last_container=True` carries its state across responses.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    reuse_last_container=True,
)
model = model.bind_tools([{
    "type": "code_execution_20250825",
    "name": "code_execution",
}])
```

Upload a file with the Anthropic Files API and pass its ID in a
`container_upload` block. When a tool-result block contains generated-file IDs,
download those files through the same API.

## Remote MCP toolsets

Remote MCP configuration requires both server registration and toolset binding:

1. Register URL servers with `ChatAnthropic(mcp_servers=...)`.
2. Bind an `mcp_toolset` whose `mcp_server_name` matches the registration.

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6",
    mcp_servers=[{
        "type": "url",
        "url": server_url,
        "name": "docs",
    }],
)
model = model.bind_tools([{
    "type": "mcp_toolset",
    "mcp_server_name": "docs",
}])
```

A server registration may include an authorization token and an allowlist of
tools. Keep the toolset name and server name identical.

## Regex and BM25 tool discovery

Anthropic tool search provides regex (`tool_search_tool_regex_20251119`) and
natural-language BM25 (`tool_search_tool_bm25_20251119`) variants. Mark catalog
tools `extras={"defer_loading": True}` so only search matches enter context.

```python
@tool(extras={"defer_loading": True})
def search_files(query: str) -> str:
    return index.search(query)

model = model.bind_tools([
    {
        "type": "tool_search_tool_regex_20251119",
        "name": "tool_search_tool_regex",
    },
    search_files,
])
```

Use regex discovery for explicit catalog patterns and BM25 for natural-language
selection; deferred tools still need normal authorization at execution time.
