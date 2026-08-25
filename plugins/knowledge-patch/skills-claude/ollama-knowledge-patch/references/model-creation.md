# Model creation, import, and quantization

## Import local GGUF content

In the `0.30-0.32` line, a Modelfile `FROM` accepts either one local GGUF file
or a directory containing GGUF files. This permits a downloaded artifact to be
created and used as a named local model.

```text
FROM ./my-model.Q4_K_M.gguf
```

```sh
ollama create -f Modelfile my-model
ollama run my-model
```

## Preserve tool capability from GGUF

Tool calling carries through an import when the GGUF itself supports it. Check
the imported model before configuring an integration:

```sh
ollama show my-model
```

Proceed only if the output lists the `tools` capability. A capable import can
then be selected explicitly:

```sh
ollama launch claude --model my-model
ollama launch hermes --model my-model
ollama launch openclaw --model my-model
```

## Import Safetensors weights

A Modelfile may build directly from a directory containing Safetensors weights
for a supported architecture. When the Modelfile is alongside the weights,
use `FROM .`.

```text
FROM .
```

```sh
ollama create my-model
```

Direct imports support Llama, Mistral/Mixtral, Gemma, and Phi-3 models. A
fine-tune must already be fused with its foundation model before direct import.

## Apply adapters safely

`ADAPTER` accepts either a directory containing a Safetensors adapter or one
GGUF adapter file. The path may be absolute or relative to the Modelfile.

```text
FROM llama3.2
ADAPTER ./adapter.gguf
```

The `FROM` model must be the exact base used during fine-tuning; a mismatch can
produce erratic output. For Safetensors adapters, prefer a non-quantized
adapter over QLoRA because quantization methods differ across frameworks.

## Quantize during CLI creation

`ollama create` accepts `-q` or `--quantize` for an FP16 or FP32 source.

```text
FROM /path/to/fp16-model
```

```sh
ollama create --quantize q4_K_M my-model
```

For the upload and REST quantization workflow, including the supported values,
see [Blob upload and model creation](native-api-and-server.md#blob-upload-and-model-creation).

## Declare a minimum runtime version

Use `REQUIRES` in a Modelfile when the model depends on a minimum Ollama
version.

```text
FROM llama3.2
REQUIRES 0.14.0
```
