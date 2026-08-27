# Releases and Runtime Operations

## Startup and accelerator behavior

### Vulkan is enabled by default (`0.30-0.32`)

Ollama 0.30 enables Vulkan automatically, extending out-of-the-box GPU acceleration to more AMD and Intel hardware without vendor-specific libraries.

### Bare `ollama` starts an interactive agent

From 0.32, running `ollama` without a subcommand starts an agent for chat, coding, web features, and delegated work. The current working directory becomes project context. If web search or fetch requires authentication, sign in from the CLI.

```sh
ollama
ollama signin
```

### MLX loading observes the timeout

From 0.32.1, MLX text-model loading honors `OLLAMA_LOAD_TIMEOUT`.

### Use expanded accelerator and Laguna support

Ollama 0.32.3 adds CUDA support on Windows ARM64 and B200 support through CUDA 12. Laguna 2.1 models support chat, thinking, and tool calling. Ollama 0.32.4 adds Apple GPU support for Laguna through the MLX engine.

## Select safe releases

### Do not use the withdrawn 0.32.2 release

Ollama 0.32.2 was withdrawn. Install or upgrade to 0.32.3 or newer.

### Stay on 0.32.5 when image generation is required (`0.32.6`)

Ollama 0.32.6 temporarily removes experimental image generation. Keep dependent workflows on 0.32.5 until a later release restores it.

## Disable cloud operation

For local-only operation, set `disable_ollama_cloud` in `~/.ollama/server.json` or start the server with `OLLAMA_NO_CLOUD=1`, then restart it. This disables cloud models and web search. Confirm the setting in logs by finding `Ollama cloud disabled: true`.

```json
{
  "disable_ollama_cloud": true
}
```

## Bound loaded models, parallelism, and queueing

The runtime controls have these defaults:

- `OLLAMA_MAX_LOADED_MODELS`: three times the GPU count, or three for CPU inference.
- `OLLAMA_NUM_PARALLEL`: one parallel request per model.
- `OLLAMA_MAX_QUEUE`: 512 queued requests; excess requests receive HTTP 503.

Parallelism multiplies a model's context allocation and memory requirement by the parallel-request count. Tune it together with context size.

```sh
OLLAMA_MAX_LOADED_MODELS=2 OLLAMA_NUM_PARALLEL=4 OLLAMA_MAX_QUEUE=128 ollama serve
```

## Quantize the K/V cache with Flash Attention

Flash Attention is automatically selected where supported. Force it on with `OLLAMA_FLASH_ATTENTION=1` or off with `OLLAMA_FLASH_ATTENTION=0`.

When Flash Attention is active, `OLLAMA_KV_CACHE_TYPE` changes the global cache type from the default `f16`:

- `q8_0` uses roughly half the memory with some quality loss.
- `q4_0` uses roughly one quarter of the memory with greater quality loss.

```sh
OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 ollama serve
```

## Rely on exact memory scheduling for new-engine models

New-engine models measure their exact memory requirement before loading rather than using an estimate. This default behavior avoids over-allocation, can place more of a model on the GPU, and improves scheduling across multiple or mismatched GPUs. It also makes `ollama ps` memory reporting agree with device tools such as `nvidia-smi`.

At rollout, exact measurement applied to `gpt-oss`, `llama4`, `llama3.2-vision`, `gemma3`, `embeddinggemma`, `gemma3n`, `qwen3`, `qwen2.5vl`, `mistral-small3.2`, `all-minilm`, and other new-engine embedding models. Support follows each model's migration to the new engine.

## Parse OpenAI-compatible stream chunks by event

From 0.32.6, `/v1/chat/completions` streams:

- `role` only in the first chunk.
- `finish_reason` in its own chunk.
- Usage in a separate chunk when `stream_options.include_usage` is enabled.

Truncated responses finish with `"length"` rather than `"tool_calls"`. These behaviors apply from `0.32.6`.

```json
{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "Summarize this."}],
  "stream": true,
  "stream_options": {"include_usage": true}
}
```

## Resolve cloud-only names to their cloud tags

From 0.32.6, when a cloud-only model name lacks a default tag, Ollama offers its `:cloud` tag instead of failing. For example, `ollama run kimi-k3` offers `kimi-k3:cloud`.
