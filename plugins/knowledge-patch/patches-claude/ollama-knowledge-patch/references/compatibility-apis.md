# Compatibility APIs

## Anthropic Messages clients

Ollama 0.14.0 and later accepts Anthropic Messages clients at the server root.
Clients still require an API key or auth token, but Ollama ignores its value.
The compatibility layer supports multi-turn messages, streaming, system
prompts, tool calling, extended thinking, and image input.

```sh
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_BASE_URL=http://localhost:11434
claude --model gpt-oss:20b
```

## OpenAI Chat Completions

Point clients at `http://localhost:11434/v1/`. A client-required API key may be
any placeholder value. `/v1/chat/completions` supports streaming usage, JSON
mode, seeded output, tools, and vision. Image content must be base64 data, not
a remote URL.

The endpoint does not support `tool_choice`, log probabilities, `logit_bias`,
`user`, or `n`.

Thinking models accept either `reasoning_effort` or `reasoning.effort`. Valid
efforts are `"high"`, `"medium"`, `"low"`, `"max"`, and `"none"`.

```json
{
  "model": "gpt-oss:20b",
  "messages": [{"role": "user", "content": "Answer briefly."}],
  "reasoning_effort": "none"
}
```

### Streaming chunks since 0.32.6

The stream shape changed in `0.32.6`:

- `role` appears only in the first chunk.
- `finish_reason` appears in its own chunk.
- With `stream_options.include_usage`, usage appears in a separate chunk.
- A truncated response finishes with `"length"`, not `"tool_calls"`.

Consumers should accumulate optional fields across chunks and treat the usage
chunk as a distinct event.

```json
{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "Summarize this."}],
  "stream": true,
  "stream_options": {"include_usage": true}
}
```

## Legacy Completions

`/v1/completions` accepts only a string `prompt`. It supports `suffix`, but not
`best_of`, `echo`, log probabilities, `logit_bias`, `user`, or `n`.

## Embeddings compatibility

`/v1/embeddings` accepts a string or an array of strings, an encoding-format
selector, and `dimensions`. It does not accept token arrays or `user`.

## Model metadata

For `/v1/models` and `/v1/models/{model}`, `created` is the model's
last-modified time. `owned_by` is the Ollama username and defaults to
`"library"`.

## Stateless Responses requests

Ollama 0.13.3 adds `/v1/responses` with streaming, function tools, and
reasoning summaries. It supports `input`, `instructions`, `temperature`,
`top_p`, and `max_output_tokens`.

It does not support `previous_response_id`, `conversation`, or `truncation`.
The application must therefore retain and resend its conversation state.

```python
response = client.responses.create(
    model="qwen3:8b",
    input="Write a short poem about blue",
)
print(response.output_text)
```

## Experimental image compatibility

`/v1/images/generations` accepts `model`, `prompt`, and `size`.
`response_format` must be `b64_json`. The endpoint does not support `n`,
`quality`, `style`, or `user`, and it may change or be removed because it is
experimental.

```python
response = client.images.generate(
    model="x/z-image-turbo",
    prompt="A robot learning to paint",
    size="1024x1024",
    response_format="b64_json",
)
```

Image generation is temporarily absent in the release described under
[Version boundaries for image generation](acceleration-images-and-scheduling.md#version-boundaries-for-image-generation).

## Alias hard-coded model names

When a client insists on a default OpenAI model name, copy an existing Ollama
model to the expected name, then use the alias in requests.

```sh
ollama cp llama3.2 gpt-3.5-turbo
```

## Set context size through a derived model

The compatibility API has no per-request field for changing context size.
Create a derived model containing `PARAMETER num_ctx`, and send requests using
that model name.

```text
FROM llama3.2
PARAMETER num_ctx 65536
```

```sh
ollama create mymodel
```
