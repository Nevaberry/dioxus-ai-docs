# Cloud models and web tools

## Use cloud models through the local interface

Cloud tags support the usual `run`, `pull`, `ls`, and `cp` commands, but their
inference runs on ollama.com. Sign in before using them. Once a cloud tag is
pulled, the local Ollama API and library clients address it like a local model.

```sh
ollama signin
ollama pull gpt-oss:120b-cloud
curl http://localhost:11434/api/chat -d '{"model":"gpt-oss:120b-cloud","messages":[{"role":"user","content":"Hello"}],"stream":false}'
```

To prohibit both cloud models and search, use the local-only controls described
in [Local-only server operation](native-api-and-server.md#local-only-server-operation).

## Use search through the Claude integration

An Ollama cloud model launched through the Claude integration can use parallel
subagents and built-in web search. The Anthropic compatibility layer handles
search, so this integration path needs neither a separate MCP server nor a
second API key. If the agent does not delegate automatically, request parallel
subagents explicitly.

```sh
ollama launch claude --model minimax-m2.5:cloud
```

```text
Spawn subagents to inspect the authentication, payment, and notification flows in parallel.
```

## Call hosted web search

Standalone search uses `POST https://ollama.com/api/web_search`. Create an
account API key, send it as a bearer token, and provide `query`. Each result
contains `title`, `url`, and `content`.

```sh
curl https://ollama.com/api/web_search \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -d '{"query":"what is ollama?"}'
```

## Fetch and extract a page

`POST https://ollama.com/api/web_fetch` accepts a URL and returns the page's
`title`, extracted `content`, and discovered `links`.

```sh
curl https://ollama.com/api/web_fetch \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://ollama.com"}'
```

## Pass client helpers directly to chat

Python and JavaScript clients from version 0.6 expose
`web_search`/`webSearch` and `web_fetch`/`webFetch`. The helpers can be passed
directly as chat tools. Give a standalone search agent roughly 32K tokens of
context or more because result content can be large.

```python
from ollama import chat, web_fetch, web_search

response = chat(
    model="qwen3:4b",
    messages=[{"role": "user", "content": "What is Ollama's new engine?"}],
    tools=[web_search, web_fetch],
    think=True,
)
```

## Expose search and fetch through MCP

Ollama's Python MCP server can expose both helpers to stdio MCP clients. A
Codex client can start the server script with `uv` and inject the API key in
the server environment.

```toml
[mcp_servers.web_search]
command = "uv"
args = ["run", "path/to/web-search-mcp.py"]
env = { "OLLAMA_API_KEY" = "your_api_key_here" }
```
