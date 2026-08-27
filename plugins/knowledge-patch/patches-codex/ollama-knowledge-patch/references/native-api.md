# Native REST API

The native API is served at `http://localhost:11434/api/`.

## Control thinking

For thinking models, `/api/generate` and `/api/chat` accept `think` as either a boolean or an effort string: `"low"`, `"medium"`, `"high"`, or `"max"`. Chat responses keep the thinking process separate in `message.thinking`.

```sh
curl http://localhost:11434/api/chat -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Solve this carefully."}],"think":"high","stream":false}'
```

## Identify tool results in chat history

Tool calls may be streamed. After executing a function, append its result as a message with role `tool` and include `tool_name` so the model can associate the result with the function.

```json
{"role":"tool","content":"11 degrees celsius","tool_name":"get_weather"}
```

## Create models from uploaded blobs

`POST /api/create` builds from GGUF or Safetensors files uploaded to `POST /api/blobs/sha256:<digest>`. Use `HEAD /api/blobs/sha256:<digest>` to check whether content is already present.

Pass filename-to-digest mappings in `files`; use `adapters` for LoRA adapter mappings.

```sh
digest=$(sha256sum model.gguf | cut -d ' ' -f 1)
curl -T model.gguf -X POST "http://localhost:11434/api/blobs/sha256:$digest"
curl http://localhost:11434/api/create -d "{\"model\":\"my-model\",\"files\":{\"model.gguf\":\"sha256:$digest\"}}"
```

## Quantize models through `/api/create`

Set `quantize` when creating from a non-quantized model. Supported values are `q4_K_M`, `q4_K_S`, and `q8_0`; `q4_K_M` and `q8_0` are recommended.

```sh
curl http://localhost:11434/api/create -d '{"model":"llama3.2:quantized","from":"llama3.2:3b-instruct-fp16","quantize":"q4_K_M"}'
```

## Use `/api/embed` for embeddings

`POST /api/embed` supersedes `/api/embeddings`. It accepts a single string or a list in `input` and returns an embeddings matrix. It also accepts output `dimensions`.

Input truncation defaults to true. Set `truncate: false` to make an overlong input fail instead.

```sh
curl http://localhost:11434/api/embed -d '{"model":"all-minilm","input":["first text","second text"],"truncate":false}'
```

## Generate images through `/api/generate`

Image generation is experimental. The standard `/api/generate` endpoint automatically detects image-generation models. Set `width`, `height`, and `steps`; streaming responses report `completed` and `total`, and the final `image` field contains base64 data.

```sh
curl http://localhost:11434/api/generate -d '{"model":"x/z-image-turbo","prompt":"a sunset over mountains","width":1024,"height":768}'
```

Check release availability before depending on this endpoint because experimental image generation can be removed temporarily.

## Disable cloud features

Set `disable_ollama_cloud` in `~/.ollama/server.json` or start with `OLLAMA_NO_CLOUD=1`, then restart Ollama. This disables cloud models and web search. A successful configuration produces `Ollama cloud disabled: true` in the logs.

```json
{
  "disable_ollama_cloud": true
}
```

## Bound concurrent work and queueing

`OLLAMA_MAX_LOADED_MODELS` defaults to three times the GPU count, or three for CPU inference. `OLLAMA_NUM_PARALLEL` defaults to one request per model. `OLLAMA_MAX_QUEUE` defaults to 512, after which excess requests receive HTTP 503.

Parallel requests multiply both the model's context allocation and its memory requirement.

```sh
OLLAMA_MAX_LOADED_MODELS=2 OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_QUEUE=128 ollama serve
```

## Quantize the K/V cache

Flash Attention is automatically selected when supported. Force it with `OLLAMA_FLASH_ATTENTION=1` or disable it with `OLLAMA_FLASH_ATTENTION=0`.

With Flash Attention enabled, use `OLLAMA_KV_CACHE_TYPE` to replace the default `f16` cache globally. `q8_0` requires roughly half the memory; `q4_0` requires roughly one quarter. More compression causes more quality loss.

```sh
OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 ollama serve
```
