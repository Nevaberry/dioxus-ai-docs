# Cloud, Integrations, and Web Tools

## Use the integration launcher

`ollama launch` normally configures and starts an integration without manual environment variables or config-file setup. Add `--config` to configure it without launching.

```sh
ollama launch opencode --config
```

## Account for launcher changes

The former Codex App integration is named ChatGPT and starts with `ollama launch chatgpt`. Add `--restore` to return to the usual ChatGPT profile.

The default launcher menu shows only popular integrations. Run `ollama launch` with no integration name to expose the broader selection.

```sh
ollama launch
ollama launch chatgpt
ollama launch chatgpt --restore
```

Launching CodeLlama, Qwen2.5 or Qwen2.5-coder, Llama 3.x, Mistral, StarCoder, or base DeepSeek-R1 tags produces a deprecation warning before continuing.

## Give coding integrations sufficient context

Set at least 64,000 tokens of context. Local recommendations are `glm-4.7-flash`, `qwen3-coder`, and `gpt-oss:20b`. Full-context cloud choices are `glm-4.7:cloud`, `minimax-m2.1:cloud`, `gpt-oss:120b-cloud`, and `qwen3-coder:480b-cloud`.

`glm-4.7-flash` at 64K requires about 23 GB of local VRAM.

```sh
ollama pull glm-4.7-flash
ollama pull glm-4.7:cloud
```

## Use cloud models through the local interface

Cloud tags support the normal `run`, `pull`, `ls`, and `cp` commands while inference runs on ollama.com. Sign in first. After pulling a tag, use it through the local API and client libraries like a local model.

```sh
ollama signin
ollama pull gpt-oss:120b-cloud
curl http://localhost:11434/api/chat -d '{"model":"gpt-oss:120b-cloud","messages":[{"role":"user","content":"Hello"}],"stream":false}'
```

## Launch Claude Code with parallel agents and search

An Ollama cloud model launched through the Claude integration can use parallel subagents and built-in web search. Search is handled by the Anthropic compatibility layer, so this route needs neither an MCP server nor a separate search API key.

If parallel inspection does not begin automatically, ask explicitly for subagents.

```sh
ollama launch claude --model minimax-m2.5:cloud
```

```text
Spawn subagents to inspect the authentication, payment, and notification flows in parallel.
```

## Call the hosted web-search API

Send `POST https://ollama.com/api/web_search` with an ollama.com account API key as a bearer token and a `query`. Each result contains `title`, `url`, and `content`.

```sh
curl https://ollama.com/api/web_search \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -d '{"query":"what is ollama?"}'
```

## Fetch a page through the hosted API

`POST https://ollama.com/api/web_fetch` accepts a URL and returns the page's `title`, extracted `content`, and discovered `links`.

```sh
curl https://ollama.com/api/web_fetch \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://ollama.com"}'
```

## Give chat agents search and fetch helpers

Python and JavaScript clients from version 0.6 expose `web_search`/`webSearch` and `web_fetch`/`webFetch`. Pass the functions directly as chat tools. Give standalone search agents roughly 32K tokens of context or more because results can be large.

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

Ollama's Python MCP server can expose both tools to stdio MCP clients. Run the server script with `uv` and pass the Ollama account API key through the server environment.

```toml
[mcp_servers.web_search]
command = "uv"
args = ["run", "path/to/web-search-mcp.py"]
env = { "OLLAMA_API_KEY" = "your_api_key_here" }
```
