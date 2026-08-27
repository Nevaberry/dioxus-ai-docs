# Inference API

## Endpoint shape, requests, and compatibility

### API expansion and route changes (9.0.0)

The Inference API adds unified chat completions, embedding and reranking
backends, node-local rate limiting, and mTLS for the hosted inference service.
Service paths gain a version prefix, and the sparse-embedding route changes.

### Request and chunking options (9.1.0)

EIS sparse-inference request bodies rename `model_id` to `model`. The Perform
Inference API exposes root-level `input_type` for `text_embedding` and adds
common rerank options. Endpoints accept `none` to disable automatic chunking
and support a recursive chunker.

### Scaling and endpoint compatibility (9.1.0)

Adaptive-allocation scale-to-zero is configurable and defaults to 24 hours.
New Cohere endpoints use Cohere V2, and services can expose aliases.

### Endpoint controls (9.2.0)

Inference requests have a configurable query timeout, chunking settings no
longer have an upper limit, and partial search results are disabled. An invalid
endpoint can be force-deleted when its model is invalid or deployment shutdown
fails.

### Endpoint controls (9.3.0)

EIS dense and sparse services accept `max_batch_size`; unified responses report
cached tokens; Jina AI embeddings support late chunking.

### Input and error requirements (9.4.0)

Chat-completion integrations support multimodal inputs and reasoning. Reasoning
requests no longer accept `max_tokens`. Base64 embedding input must use a data
URI. SageMaker `ElasticTextEmbeddingPayload` requires `similarity`. Inference
timeouts return HTTP 504.

### Secret parameters in maintenance releases

In 9.3.8 and 9.4.4, requests cannot override `secret_parameters`; see
[breaking-changes.md](breaking-changes.md).

## Tasks and service integrations

### Service expansion (9.1.0)

Elasticsearch adds a custom inference service and Vertex AI chat/completion,
Mistral and Hugging Face chat completion, DeepSeek, VoyageAI embedding and
reranking, and SageMaker OpenAI-compatible chat and embedding integrations.
Cohere supports binary embeddings, Jina AI accepts an embedding type, and
Bedrock Cohere accepts task settings.

### Service additions (9.2.0)

The API adds ContextualAI and Azure AI reranking; AI21, Google Model Garden
Anthropic, Llama, and IBM watsonx completion/chat support. Vertex AI embeddings
accept dimensions, OpenAI-compatible embedding and chat requests accept custom
headers, and Gemini accepts a thinking budget.

### Tasks and providers (9.3.0)

The API adds an embedding task and EIS completion; EIS requires a basic
license. Integrations expand to Azure OpenAI-compatible and Groq chat
completion, NVIDIA, OpenShift AI, and Google Model Garden for Meta, Mistral,
Hugging Face, and AI21 models.

### Providers and inputs (9.4.0)

The API adds Fireworks AI chat completion and embeddings, Amazon Bedrock chat
completion, Jina AI and EIS embedding tasks, and Azure OpenAI-compatible custom
headers and OAuth2.

## `semantic_text` and embedding defaults

### General availability (8.18.0)

The `semantic_text` mapping and integrated inference workflow are generally
available. Search behavior is detailed in
[search-and-vectors.md](search-and-vectors.md).

### Vector configuration and chunking (9.1.0)

Mappings accept `index_options`, configurable chunking, and bit vectors;
compatible services default new fields to BBQ. Empty content skips embedding
generation. `semantic_text` subfields do not appear in field-capabilities
responses. `sparse_vector` mappings have a default token-pruning setting.

### Defaults and updates (9.3.0)

An existing mapping can update `inference_id`. New fields default to ELSER on
Elastic Inference Service when available, and support BFloat16.

### Defaults (9.4.0)

New fields inherit DiskBBQ indexing and BFloat16 storage. The default inference
ID and service switch to Jina v5. The text-similarity rank retriever selects
chunking defaults appropriate to its inference ID.

## Deprecated inference behavior

The `elser` service is deprecated as of 9.0. Avoid new endpoints and plan
migration; see
[deprecations-and-known-issues.md](deprecations-and-known-issues.md).
