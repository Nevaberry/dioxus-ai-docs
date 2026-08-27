# Native API and server operation

## Thinking and tool messages

For thinking-capable models, both `POST /api/generate` and `POST /api/chat`
accept `think` as a boolean or one of `"low"`, `"medium"`, `"high"`, and
`"max"`. Chat responses place the reasoning trace in `message.thinking`,
separate from the answer.

```sh
curl http://localhost:11434/api/chat -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Solve this carefully."}],"think":"high","stream":false}'
```

Tool calls may be streamed. After executing one, append its result to history
with role `tool` and include `tool_name`; the name associates the result with
the requested function.

```json
{"role":"tool","content":"11 degrees celsius","tool_name":"get_weather"}
```

## Blob upload and model creation

`POST /api/create` can create a model from GGUF or Safetensors content uploaded
to `POST /api/blobs/sha256:<digest>`. Use `HEAD` on the same blob path to avoid
uploading content already present. In the create request, map each filename to
its `sha256:<digest>` under `files`; put LoRA mappings under `adapters`.

```sh
digest=$(sha256sum model.gguf | cut -d ' ' -f 1)
curl -T model.gguf -X POST "http://localhost:11434/api/blobs/sha256:$digest"
curl http://localhost:11434/api/create -d "{\"model\":\"my-model\",\"files\":{\"model.gguf\":\"sha256:$digest\"}}"
```

The same create endpoint can quantize an unquantized source through
`quantize`. Supported values are `q4_K_M`, `q4_K_S`, and `q8_0`; prefer
`q4_K_M` or `q8_0`.

```sh
curl http://localhost:11434/api/create -d '{"model":"llama3.2:quantized","from":"llama3.2:3b-instruct-fp16","quantize":"q4_K_M"}'
```

For local Modelfile and CLI creation paths, see
[Model creation](model-creation.md).

## Embeddings

`POST /api/embed` supersedes `/api/embeddings`. Its `input` accepts one string
or a list of strings, and its response contains an embeddings matrix. Set
`dimensions` when a smaller output vector is needed.

Input truncation is enabled by default. Set `truncate: false` to make an
overlong input fail instead of being silently shortened.

```sh
curl http://localhost:11434/api/embed -d '{"model":"all-minilm","input":["first text","second text"],"truncate":false}'
```

## Native image generation

Experimental image generation uses `POST /api/generate`; the endpoint detects
image-generation models automatically. Set `width`, `height`, and `steps` in
the request. Streamed events expose `completed` and `total`; the final `image`
value is base64-encoded.

```sh
curl http://localhost:11434/api/generate -d '{"model":"x/z-image-turbo","prompt":"a sunset over mountains","width":1024,"height":768}'
```

This endpoint is subject to the version boundary documented under
[Version boundaries for image generation](acceleration-images-and-scheduling.md#version-boundaries-for-image-generation).

## Local-only server operation

Disable hosted models and web search by setting `disable_ollama_cloud` in
`~/.ollama/server.json`, or by launching the server with
`OLLAMA_NO_CLOUD=1`. Restart the server after changing the JSON file. Confirm
the effective setting in logs as `Ollama cloud disabled: true`.

```json
{
  "disable_ollama_cloud": true
}
```

## Concurrency and queue limits

The server scheduling environment variables have these defaults:

| Variable | Default | Effect |
| --- | --- | --- |
| `OLLAMA_MAX_LOADED_MODELS` | Three times the GPU count, or three for CPU inference | Maximum resident models |
| `OLLAMA_NUM_PARALLEL` | One per model | Parallel requests handled by each loaded model |
| `OLLAMA_MAX_QUEUE` | 512 | Waiting requests before excess work receives HTTP 503 |

Parallel requests multiply the model's context allocation and memory use by
the parallel count. Size `OLLAMA_NUM_PARALLEL` together with context length,
not independently.

```sh
OLLAMA_MAX_LOADED_MODELS=2 OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_QUEUE=128 ollama serve
```

## Flash Attention and K/V cache memory

Flash Attention is selected automatically when supported. Force it on or off
with `OLLAMA_FLASH_ATTENTION=1` or `OLLAMA_FLASH_ATTENTION=0`.

When Flash Attention is enabled, `OLLAMA_KV_CACHE_TYPE` changes the global K/V
cache default. `f16` is the default; `q8_0` takes roughly half its memory, and
`q4_0` roughly one quarter. Quantization trades increasing quality loss for
the memory reduction.

```sh
OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 ollama serve
```
