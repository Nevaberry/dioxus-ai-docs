# Compatibility APIs

## Connect Anthropic Messages clients

Ollama 0.14.0 and later accepts Anthropic Messages clients at the server root. Clients require an API key or authentication token, but Ollama ignores the value.

The compatibility layer supports multi-turn messages, streaming, system prompts, tool calling, extended thinking, and image input.

```sh
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_BASE_URL=http://localhost:11434
claude --model gpt-oss:20b
```

## Use the supported OpenAI Chat Completions subset

Point OpenAI clients at `http://localhost:11434/v1/`. Their required API key is ignored.

`/v1/chat/completions` supports streaming usage, JSON mode, seeded output, tools, and vision. Image content must be base64 data rather than a remote URL.

The endpoint does not support:

- `tool_choice`
- Log probabilities
- `logit_bias`
- `user`
- `n`

Thinking models accept either `reasoning_effort` or `reasoning.effort`. Valid efforts are `"high"`, `"medium"`, `"low"`, `"max"`, and `"none"`.

```json
{
  "model": "gpt-oss:20b",
  "messages": [{"role": "user", "content": "Answer briefly."}],
  "reasoning_effort": "none"
}
```

## Account for endpoint-specific limits

### Completions

`/v1/completions` accepts only a string `prompt`. It supports `suffix`, but not `best_of`, `echo`, log probabilities, `logit_bias`, `user`, or `n`.

### Embeddings

`/v1/embeddings` accepts a string or array of strings, an encoding-format selector, and `dimensions`. It does not accept token arrays or `user`.

### Models

For `/v1/models` and `/v1/models/{model}`, `created` is the model's last-modified time. `owned_by` is the Ollama username and defaults to `"library"`.

## Keep Responses requests stateless

Ollama 0.13.3 adds `/v1/responses` with streaming, function tools, and reasoning summaries. It supports `input`, `instructions`, `temperature`, `top_p`, and `max_output_tokens`.

It does not support `previous_response_id`, `conversation`, or `truncation`. Applications must carry their own conversation state.

```python
response = client.responses.create(
    model="qwen3:8b",
    input="Write a short poem about blue",
)
print(response.output_text)
```

## Generate images through the experimental endpoint

`/v1/images/generations` accepts `model`, `prompt`, and `size`. `response_format` must be `b64_json`.

The endpoint does not support `n`, `quality`, `style`, or `user`. It is experimental and may change or be removed.

```python
response = client.images.generate(
    model="x/z-image-turbo",
    prompt="A robot learning to paint",
    size="1024x1024",
    response_format="b64_json",
)
```

## Alias models for hard-coded defaults

If a client insists on a default OpenAI model name, copy an existing Ollama model to that name and use the alias in API requests.

```sh
ollama cp llama3.2 gpt-3.5-turbo
```

## Set context size in a derived model

The OpenAI-compatible API has no request field for changing context size. Define `PARAMETER num_ctx` in a Modelfile, create the derived model, then use that name in requests.

```text
FROM llama3.2
PARAMETER num_ctx 65536
```

```sh
ollama create mymodel
```
