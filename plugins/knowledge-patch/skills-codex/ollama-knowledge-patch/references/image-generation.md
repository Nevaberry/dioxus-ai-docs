# Image Generation and MLX

Image generation is experimental. Verify both the Ollama release and platform before depending on it.

## Generate images from the CLI on macOS

Pass a prompt directly to an image model. Ollama saves the image in the current directory, and terminals with image-rendering support also show an inline preview. Windows and Linux were not supported when this workflow was announced.

```sh
ollama run x/z-image-turbo "a watercolor lighthouse in a winter storm"
# Alternative model:
ollama run x/flux2-klein "a neon sign reading OPEN 24 HOURS"
```

## Configure interactive image generation

Within an image-model session, use `/set width` and `/set height` for output dimensions. Each model supplies a recommended default step count. Image generation also supports reproducible random seeds and negative prompts.

```text
/set width 1024
/set height 768
```

## Generate through the native API

`POST /api/generate` automatically detects image-generation models. `width`, `height`, and `steps` control generation. Streams report `completed` and `total`; the final `image` is base64-encoded.

```sh
curl http://localhost:11434/api/generate -d '{"model":"x/z-image-turbo","prompt":"a sunset over mountains","width":1024,"height":768}'
```

## Generate through the compatibility API

The experimental `/v1/images/generations` endpoint accepts `model`, `prompt`, and `size`. `response_format` must be `b64_json`. It does not support `n`, `quality`, `style`, or `user`.

```python
response = client.images.generate(
    model="x/z-image-turbo",
    prompt="A robot learning to paint",
    size="1024x1024",
    response_format="b64_json",
)
```

## Pin a release when image generation is required

Ollama 0.32.6 temporarily removes experimental image generation. Keep workflows that require it on 0.32.5 until the feature returns in a later release.

## Run MLX-specific models on Apple Silicon

The MLX engine supports NVIDIA's model-optimized NVFP4 format on Apple Silicon, both as imported NVFP4 models and dedicated library tags. The initial Qwen coding preview requires more than 32 GB of unified memory. Newer MLX tags can run directly or be passed to an integration.

```sh
ollama run qwen3.5:35b-a3b-coding-nvfp4
ollama run gemma4:12b-mlx
ollama launch pi --model gemma4:12b-mlx
```
