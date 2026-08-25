---
name: ollama-knowledge-patch
description: Ollama
version: 0.32.5
license: MIT
metadata:
  author: Nevaberry
---


# Ollama Knowledge Patch

Use this skill when implementing, reviewing, or troubleshooting Ollama model
creation, native or compatibility APIs, integrations, cloud tools, acceleration,
image generation, and server scheduling. Prefer the project's installed Ollama
version and observed behavior when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Native API and server operation](references/native-api-and-server.md) | Thinking, tool results, blobs, embeddings, native image requests, concurrency, cloud controls, and K/V cache |
| [Compatibility APIs](references/compatibility-apis.md) | Anthropic Messages, OpenAI chat/completions, Responses, embeddings, images, aliases, context sizing, and streaming |
| [Model creation](references/model-creation.md) | GGUF and Safetensors import, adapters, quantization, capabilities, and minimum versions |
| [CLI and integrations](references/cli-and-integrations.md) | Interactive agent, launcher behavior, context sizing, library tags, cloud tag resolution, and release hazards |
| [Cloud and web tools](references/cloud-and-web-tools.md) | Cloud models, hosted search/fetch, chat helpers, integration search, and MCP |
| [Acceleration, images, and scheduling](references/acceleration-images-and-scheduling.md) | Vulkan, CUDA, MLX, image generation, exact-memory scheduling, and temporary removal |

## Breaking changes and deprecations

### Keep image workflows on 0.32.5

Ollama 0.32.6 temporarily removes experimental image generation. Pin 0.32.5
for workflows that require image output, and do not upgrade until a later
release explicitly restores it. See
[acceleration, images, and scheduling](references/acceleration-images-and-scheduling.md#version-boundaries-for-image-generation).

### Skip the withdrawn release

Do not deploy 0.32.2. Install 0.32.3 or newer instead. If image generation is
also required, observe the separate 0.32.5 pin above.

### Update streaming parsers

From 0.32.6, OpenAI-compatible chat streams emit `role` only in the first
chunk, put `finish_reason` in its own chunk, and optionally put usage in a
separate chunk. A truncated response ends with `"length"`, not `"tool_calls"`.
Do not assume all chunk fields arrive together.

### Use the current embeddings endpoint

Prefer native `POST /api/embed` over superseded `/api/embeddings`. The current
endpoint accepts one string or a list, returns a matrix, supports output
`dimensions`, and can reject rather than truncate overlong input.

### Account for launcher renames and warnings

The former Codex App integration is exposed as ChatGPT through
`ollama launch chatgpt`; `--restore` selects the usual ChatGPT profile. Older
CodeLlama, Qwen2.5, Qwen2.5-coder, Llama 3.x, Mistral, StarCoder, and base
DeepSeek-R1 tags produce a deprecation warning before continuing.

## Model creation quick reference

### Import GGUF artifacts

A Modelfile `FROM` may point to one GGUF file or a directory of GGUF files.

```text
FROM ./my-model.Q4_K_M.gguf
```

```sh
ollama create -f Modelfile my-model
ollama run my-model
```

If the GGUF supports tools, verify that `ollama show my-model` reports the
`tools` capability before selecting it in an integration.

### Import Safetensors and adapters

Use `FROM .` when a Modelfile sits beside supported Safetensors weights. Use
`ADAPTER` with a Safetensors directory or GGUF adapter file, and keep `FROM`
matched to the exact fine-tuning base. Prefer non-quantized Safetensors
adapters over QLoRA imports because framework quantization differs.

### Quantize during creation

For an FP16 or FP32 source, pass `-q` or `--quantize` to `ollama create`.
The native create API accepts `q4_K_M`, `q4_K_S`, and `q8_0`; `q4_K_M` and
`q8_0` are the recommended choices.

```sh
ollama create --quantize q4_K_M my-model
```

Use Modelfile `REQUIRES` when an artifact depends on a minimum Ollama version.
See [model creation](references/model-creation.md) for complete import and
adapter rules.

## Native API quick reference

### Control reasoning and tool history

For `/api/generate` and `/api/chat`, `think` accepts a boolean or `"low"`,
`"medium"`, `"high"`, or `"max"`. Chat returns reasoning separately in
`message.thinking`. Append executed function results as role `tool` messages
with `tool_name` so streamed calls can be matched to their results.

```json
{"role":"tool","content":"11 degrees celsius","tool_name":"get_weather"}
```

### Upload before creating

Upload GGUF or Safetensors content to
`POST /api/blobs/sha256:<digest>`, optionally check it with `HEAD`, and map
filenames to digests in `/api/create` under `files` or `adapters`.

### Bound server work

Use `OLLAMA_MAX_LOADED_MODELS`, `OLLAMA_NUM_PARALLEL`, and `OLLAMA_MAX_QUEUE`
to cap residency, per-model parallelism, and queued work. Expect HTTP 503 after
the queue limit. Parallelism multiplies each model's context allocation and
memory requirement.

With Flash Attention, `OLLAMA_KV_CACHE_TYPE=q8_0` uses roughly half the default
`f16` cache memory, while `q4_0` uses roughly one quarter with more quality
loss. See [native API and server operation](references/native-api-and-server.md).

## Compatibility API quick reference

### Point clients at the right base URL

Anthropic Messages clients connect at `http://localhost:11434`; client-required
credentials are ignored locally. OpenAI clients use
`http://localhost:11434/v1/`, also with a placeholder API key when required by
the client.

### Stay inside the supported subset

OpenAI-compatible Chat Completions supports streaming usage, JSON mode, seeded
output, tools, vision with base64 images, and reasoning effort. It does not
support `tool_choice`, log probabilities, `logit_bias`, `user`, or `n`.

Responses requests are stateless: carry conversation state in the application
because `previous_response_id`, `conversation`, and `truncation` are not
supported. The compatibility image endpoint requires `b64_json` and is
experimental. See [compatibility APIs](references/compatibility-apis.md) for
endpoint-specific limits.

### Derive a larger-context alias

The compatibility API has no request field for context size. Create and call a
derived model instead:

```text
FROM llama3.2
PARAMETER num_ctx 65536
```

```sh
ollama create mymodel
```

## CLI and integration quick reference

Running bare `ollama` starts the interactive agent and supplies the current
working directory as project context. Use `ollama signin` for authenticated
web search or fetch. `ollama launch` shows the wider integration list, and
`ollama launch <integration> --config` configures without starting it.

Give coding integrations at least 64,000 tokens of context. A local
`glm-4.7-flash` at that context needs about 23 GB VRAM; cloud tags provide
full-context alternatives. Gemma 4 is available as `gemma4`.

See [CLI and integrations](references/cli-and-integrations.md) for commands,
recommended tags, and cloud-only tag resolution.

## Cloud and web quick reference

Sign in before using cloud tags. They work with normal `run`, `pull`, `ls`,
and `cp` commands and with the local API, while inference executes remotely.
Set `OLLAMA_NO_CLOUD=1` or `disable_ollama_cloud` in the server configuration
to disable both cloud models and web search for local-only operation.

Hosted search and fetch require an account API key and expose
`/api/web_search` and `/api/web_fetch`. Python and JavaScript clients expose
matching helpers that can be passed directly as chat tools. Allocate roughly
32K context or more to a standalone search agent because results can be large.

See [cloud and web tools](references/cloud-and-web-tools.md) for request shapes,
integration behavior, and the stdio MCP configuration.

## Acceleration and scheduling quick reference

Vulkan acceleration is enabled by default on supported AMD and Intel hardware.
MLX text loading respects `OLLAMA_LOAD_TIMEOUT`; MLX-specific NVFP4 tags run on
Apple Silicon. Windows ARM64 CUDA and B200 through CUDA 12 are supported in the
documented accelerator path.

New-engine models measure exact memory before loading. This improves GPU
placement and multi-GPU scheduling and makes `ollama ps` memory reporting agree
more closely with system GPU tools. Consult
[acceleration, images, and scheduling](references/acceleration-images-and-scheduling.md)
for the affected model families and image controls.
