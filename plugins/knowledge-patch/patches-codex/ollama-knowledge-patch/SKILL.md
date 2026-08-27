---
name: ollama-knowledge-patch
description: Ollama
version: "0.32.5"
license: MIT
metadata:
  author: Nevaberry
---


# Ollama Knowledge Patch

## Use this patch

1. Identify whether the task concerns model creation, the native REST API, a compatibility API, integrations, cloud and web tools, image generation, or runtime scheduling.
2. Read the matching reference before changing commands, environment variables, request shapes, response parsers, or deployment settings.
3. Treat experimental image generation and MLX behavior as platform- and release-sensitive.
4. Keep native Ollama endpoints separate from OpenAI- and Anthropic-compatible endpoints; their request fields and state behavior differ.
5. Size context, parallelism, and the K/V cache together because each parallel request multiplies context memory.

## Reference index

| Reference | Topics |
| --- | --- |
| [releases-and-runtime.md](references/releases-and-runtime.md) | Changed defaults, withdrawn releases, accelerator support, runtime limits, exact-memory scheduling, streaming changes |
| [models-and-modelfiles.md](references/models-and-modelfiles.md) | GGUF and Safetensors imports, adapters, quantization, model requirements, library tags, context sizing |
| [native-api.md](references/native-api.md) | Thinking, tool results, blobs, model creation, embeddings, image generation, concurrency and cache controls |
| [compatibility-apis.md](references/compatibility-apis.md) | Anthropic Messages, OpenAI Chat Completions, Completions, Embeddings, Responses, and Images compatibility |
| [cloud-integrations-and-web.md](references/cloud-integrations-and-web.md) | Integration launcher, cloud models, hosted search and fetch, client helpers, MCP exposure |
| [image-generation.md](references/image-generation.md) | Experimental CLI image generation, interactive controls, native and compatibility endpoints, release availability |

## Start with breaking changes and deprecations

### Avoid the withdrawn release

Do not install or remain on Ollama 0.32.2. It was withdrawn; use 0.32.3 or newer.

### Pin image-generation workflows

Ollama 0.32.6 temporarily removes experimental image generation. Workflows that require it must remain on 0.32.5 until a later release restores it.

### Move native embeddings to `/api/embed`

Use `POST /api/embed` instead of the superseded `/api/embeddings` endpoint. The replacement accepts one string or a list in `input`, returns an embeddings matrix, supports `dimensions`, and truncates by default. Set `truncate: false` to reject overlong input.

```sh
curl http://localhost:11434/api/embed -d '{"model":"all-minilm","input":["first text","second text"],"truncate":false}'
```

### Do not assume stateful Responses compatibility

The OpenAI-compatible `/v1/responses` endpoint does not support `previous_response_id`, `conversation`, or `truncation`. Applications must retain and resend their own conversation state.

### Update streaming chunk parsers

OpenAI-compatible chat streams send `role` only in the first chunk, `finish_reason` in its own chunk, and requested usage in another chunk. A truncated response finishes with `"length"`, not `"tool_calls"`.

### Expect launcher warnings for older model families

Launching CodeLlama, Qwen2.5 or Qwen2.5-coder, Llama 3.x, Mistral, StarCoder, or base DeepSeek-R1 tags emits a deprecation warning before continuing.

## CLI and integration quick reference

### Start the interactive agent

Running `ollama` with no subcommand opens the interactive agent and supplies the current working directory as project context. Sign in when web search or fetch needs authentication.

```sh
ollama
ollama signin
```

### Configure without launching

`ollama launch` normally configures and starts an integration. Add `--config` to configure it only.

```sh
ollama launch opencode --config
```

### Use the renamed ChatGPT launcher

Launch the former Codex App integration as `chatgpt`. `--restore` returns to the usual ChatGPT profile. Run `ollama launch` without an integration name to see the broader selection beyond the default popular menu.

```sh
ollama launch chatgpt
ollama launch chatgpt --restore
```

### Allocate enough coding context

Give coding integrations at least 64,000 tokens. Suitable local tags include `glm-4.7-flash`, `qwen3-coder`, and `gpt-oss:20b`; full-context cloud options include `glm-4.7:cloud`, `minimax-m2.1:cloud`, `gpt-oss:120b-cloud`, and `qwen3-coder:480b-cloud`. At 64K, `glm-4.7-flash` needs about 23 GB of local VRAM.

## Model creation quick reference

### Import local weights

A Modelfile `FROM` can point to a GGUF file, a directory of GGUF files, or a supported Safetensors directory. When a Modelfile sits beside Safetensors weights, use `FROM .`.

```text
FROM ./my-model.Q4_K_M.gguf
```

```sh
ollama create -f Modelfile my-model
ollama run my-model
```

### Verify imported tool support

Tool calling remains available when the imported GGUF supports it. Confirm that `ollama show my-model` lists the `tools` capability before passing the model to an integration.

### Apply adapters against the exact base

`ADAPTER` accepts a Safetensors directory or GGUF adapter file. `FROM` must name the exact fine-tuning base or output can be erratic. Prefer non-quantized Safetensors adapters over QLoRA adapters because framework quantization methods differ.

### Quantize while creating

Use `ollama create -q` or `--quantize` with FP16 or FP32 source weights.

```sh
ollama create --quantize q4_K_M my-model
```

### Declare model requirements

Use `REQUIRES` to set a model's minimum Ollama version.

```text
FROM llama3.2
REQUIRES 0.14.0
```

## Native API quick reference

### Control thinking

`/api/generate` and `/api/chat` accept `think` as a boolean or `"low"`, `"medium"`, `"high"`, or `"max"`. Chat responses place reasoning separately in `message.thinking`.

### Return named tool results

Append an executed function result as a `tool` message with `tool_name`, including when tool calls were streamed.

```json
{"role":"tool","content":"11 degrees celsius","tool_name":"get_weather"}
```

### Upload and create by digest

Upload GGUF or Safetensors content with `POST /api/blobs/sha256:<digest>`, check it with `HEAD`, then map filenames to digests in `/api/create` under `files` or `adapters`.

### Quantize through `/api/create`

Set `quantize` to `q4_K_M`, `q4_K_S`, or `q8_0` when creating from a non-quantized model. Prefer `q4_K_M` or `q8_0`.

## Runtime quick reference

### Disable cloud features

Set `disable_ollama_cloud` in `~/.ollama/server.json` or start with `OLLAMA_NO_CLOUD=1`, then restart. This disables both cloud models and web search.

### Bound parallel work

`OLLAMA_MAX_LOADED_MODELS` defaults to three times the GPU count, or three on CPU. `OLLAMA_NUM_PARALLEL` defaults to one per model, and `OLLAMA_MAX_QUEUE` defaults to 512 before excess work receives HTTP 503.

```sh
OLLAMA_MAX_LOADED_MODELS=2 OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_QUEUE=128 ollama serve
```

### Reduce K/V cache memory

Flash Attention is selected automatically when supported and can be forced with `OLLAMA_FLASH_ATTENTION=1` or disabled with `0`. With it enabled, set `OLLAMA_KV_CACHE_TYPE=q8_0` for roughly half the default `f16` memory or `q4_0` for roughly one quarter, accepting greater quality loss.

### Trust measured new-engine memory

New-engine models measure exact memory before loading. This improves placement across multiple or mismatched GPUs and makes `ollama ps` memory agree more closely with device tools.

## Compatibility API quick reference

### Set client base URLs

Anthropic Messages clients connect at `http://localhost:11434`; OpenAI clients use `http://localhost:11434/v1/`. Clients require a token or API key, but Ollama ignores its value.

### Respect unsupported fields

The Chat Completions subset does not support `tool_choice`, log probabilities, `logit_bias`, `user`, or `n`. Remote image URLs are unsupported; send base64 image data. Check the compatibility reference for endpoint-specific limits.

### Set context through a derived model

The OpenAI-compatible API has no per-request context-size field. Put `PARAMETER num_ctx` in a Modelfile, create a derived model, and call that model name.

```text
FROM llama3.2
PARAMETER num_ctx 65536
```

## Cloud, web, image, and MLX quick reference

### Use cloud tags locally

Sign in, pull a cloud tag, and use it through normal CLI, native API, and library calls; inference runs on ollama.com.

### Authenticate hosted web tools

The hosted `web_search` and `web_fetch` endpoints require an ollama.com account API key as a bearer token. Python and JavaScript clients expose corresponding helpers that can be passed directly as chat tools.

### Treat image generation as experimental

Image generation uses `/api/generate` or `/v1/images/generations`, and CLI prompting is available on supported macOS releases. Platform support, request fields, and release availability are narrower than text generation; read the image reference before depending on it.

### Use MLX tags on Apple Silicon

MLX supports imported NVFP4 weights and dedicated tags such as `qwen3.5:35b-a3b-coding-nvfp4` and `gemma4:12b-mlx`. The initial Qwen coding preview needs more than 32 GB of unified memory.
