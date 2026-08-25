# CLI and integrations

## Start the interactive agent

From 0.32, running `ollama` with no subcommand starts an interactive agent for
chat, coding, web features, and delegated work. The current working directory
is supplied as project context. Sign in when search or fetch needs
authentication.

```sh
ollama
ollama signin
```

## Browse, configure, and launch integrations

`ollama launch` normally configures and starts an integration, avoiding manual
environment-variable or configuration-file setup. The default menu contains
only popular integrations; invoke `ollama launch` to see the broader list.

Use `--config` to write the configuration without starting the integration.

```sh
ollama launch
ollama launch opencode --config
```

The former Codex App integration is named ChatGPT. Launch it as follows;
`--restore` returns to the usual ChatGPT profile.

```sh
ollama launch chatgpt
ollama launch chatgpt --restore
```

CodeLlama, Qwen2.5 or Qwen2.5-coder, Llama 3.x, Mistral, StarCoder, and base
DeepSeek-R1 tags now emit a deprecation warning before the launcher continues.

## Size context for coding integrations

Give coding tools at least 64,000 tokens of Ollama context. Recommended local
tags are `glm-4.7-flash`, `qwen3-coder`, and `gpt-oss:20b`. Full-context cloud
choices include `glm-4.7:cloud`, `minimax-m2.1:cloud`, `gpt-oss:120b-cloud`,
and `qwen3-coder:480b-cloud`.

At 64K context, `glm-4.7-flash` needs about 23 GB of VRAM locally.

```sh
ollama pull glm-4.7-flash
# Hosted full-context alternative:
ollama pull glm-4.7:cloud
```

## Run Gemma 4

Gemma 4 is available from the library as the `gemma4` tag.

```sh
ollama run gemma4
```

## Resolve cloud-only names

Since 0.32.6, invoking a cloud-only model name with no default tag offers its
`:cloud` tag instead of failing. For example, `ollama run kimi-k3` offers
`kimi-k3:cloud`.

## Avoid withdrawn 0.32.2

Ollama 0.32.2 was withdrawn. Install or upgrade to 0.32.3 or newer. If the
workflow also requires experimental image generation, follow the narrower pin
in [Version boundaries for image generation](acceleration-images-and-scheduling.md#version-boundaries-for-image-generation).
