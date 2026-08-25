# Models, Imports, and Modelfiles

## Import local GGUF models

A Modelfile `FROM` accepts a GGUF file or a directory containing GGUF files.

```text
FROM ./my-model.Q4_K_M.gguf
```

```sh
ollama create -f Modelfile my-model
ollama run my-model
```

## Preserve tool calling in GGUF imports

Tool calling carries over when the imported GGUF supports it. Confirm the capability before using the model with an integration:

```sh
ollama show my-model
ollama launch claude --model my-model
ollama launch hermes --model my-model
ollama launch openclaw --model my-model
```

The `ollama show` output must list the `tools` capability.

## Give coding integrations at least 64K context

Set Ollama's context length to at least 64,000 tokens for coding tools. Recommended local tags are `glm-4.7-flash`, `qwen3-coder`, and `gpt-oss:20b`. Cloud tags with full context include `glm-4.7:cloud`, `minimax-m2.1:cloud`, `gpt-oss:120b-cloud`, and `qwen3-coder:480b-cloud`.

At 64K context, `glm-4.7-flash` requires about 23 GB of local VRAM.

```sh
ollama pull glm-4.7-flash
# Or use the hosted full-context variant:
ollama pull glm-4.7:cloud
```

## Run Gemma 4 from the library

Gemma 4 is available under the `gemma4` tag.

```sh
ollama run gemma4
```

## Import Safetensors weights

A Modelfile can build from a directory containing Safetensors weights for a supported architecture. Direct import supports Llama, Mistral/Mixtral, Gemma, and Phi-3 models, including fine-tunes fused with their foundation model.

When the Modelfile is alongside the weights, use:

```text
FROM .
```

```sh
ollama create my-model
```

## Apply Safetensors or GGUF adapters

`ADAPTER` accepts either a Safetensors adapter directory or a GGUF adapter file. Its path may be absolute or relative to the Modelfile.

```text
FROM llama3.2
ADAPTER ./adapter.gguf
```

`FROM` must identify the exact base model used for fine-tuning; another base can produce erratic results. For Safetensors adapters, prefer non-quantized adapters rather than QLoRA adapters because framework quantization methods differ.

## Quantize during CLI creation

`ollama create` accepts `-q` or `--quantize` to convert an FP16 or FP32 source model while creating the Ollama model.

```text
FROM /path/to/fp16-model
```

```sh
ollama create --quantize q4_K_M my-model
```

## Require a minimum Ollama version

Use the Modelfile `REQUIRES` instruction to declare the minimum Ollama version required by a model.

```text
FROM llama3.2
REQUIRES 0.14.0
```

## Alias a model for hard-coded client defaults

When a client insists on a default OpenAI model name, copy an existing Ollama model to that name and use the alias in requests.

```sh
ollama cp llama3.2 gpt-3.5-turbo
```

## Set compatibility-API context in a derived model

The OpenAI-compatible API has no request field for context size. Create a derived model with `PARAMETER num_ctx`, then use the derived name in requests.

```text
FROM llama3.2
PARAMETER num_ctx 65536
```

```sh
ollama create mymodel
```
