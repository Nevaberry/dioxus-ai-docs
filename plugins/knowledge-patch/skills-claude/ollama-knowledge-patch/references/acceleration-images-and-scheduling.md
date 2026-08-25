# Acceleration, images, and scheduling

## Default Vulkan acceleration

From 0.30, Vulkan acceleration is enabled by default. This extends
out-of-the-box GPU support to more AMD and Intel hardware without requiring
vendor-specific libraries.

## CUDA and Laguna support

Ollama 0.32.3 adds CUDA support on Windows ARM64 and B200 support through CUDA
12. Laguna 2.1 models support chat, thinking, and tool calling. Apple GPU
support for Laguna through the MLX engine arrives in 0.32.4.

## MLX load timeout

From 0.32.1, loading an MLX text model honors `OLLAMA_LOAD_TIMEOUT`.

## MLX-specific models on Apple Silicon

The MLX engine supports NVIDIA's model-optimized NVFP4 format on Apple Silicon,
both for imported NVFP4 content and dedicated model tags. The initial Qwen
coding preview needs more than 32 GB of unified memory. Newer MLX tags can run
directly or be passed to an integration.

```sh
ollama run qwen3.5:35b-a3b-coding-nvfp4
ollama run gemma4:12b-mlx
ollama launch pi --model gemma4:12b-mlx
```

## Generate images from the macOS CLI

Experimental image generation accepts the prompt directly after an image
model. Output is saved in the current directory; terminals that can render
images also show an inline preview. Windows and Linux were not supported when
this feature was announced.

```sh
ollama run x/z-image-turbo "a watercolor lighthouse in a winter storm"
ollama run x/flux2-klein "a neon sign reading OPEN 24 HOURS"
```

## Configure interactive image output

Inside an image-model session, set output dimensions with `/set width` and
`/set height`. Each model provides a recommended default step count. The image
path also supports reproducible random seeds and negative prompts.

```text
/set width 1024
/set height 768
```

For native and compatibility HTTP request shapes, see
[Native image generation](native-api-and-server.md#native-image-generation) and
[Experimental image compatibility](compatibility-apis.md#experimental-image-compatibility).

## Version boundaries for image generation

Ollama `0.32.6` temporarily removes experimental image generation. Any CLI,
native API, or compatibility API workflow that requires images must remain on
0.32.5 until a later release explicitly restores the feature.

## Exact-memory scheduling

New-engine models measure their exact memory requirement before loading rather
than using an estimate. The behavior is enabled by default. It avoids
over-allocation, can place more of a model on a GPU, improves scheduling across
multiple or mismatched GPUs, and makes `ollama ps` memory usage agree with
tools such as `nvidia-smi`.

At rollout, exact measurement applied to `gpt-oss`, `llama4`,
`llama3.2-vision`, `gemma3`, `embeddinggemma`, `gemma3n`, `qwen3`,
`qwen2.5vl`, `mistral-small3.2`, `all-minilm`, and other new-engine embedding
models. Support expands as each model migrates to the new engine.
