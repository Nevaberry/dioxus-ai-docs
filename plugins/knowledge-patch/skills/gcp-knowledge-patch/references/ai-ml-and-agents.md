# AI, Machine Learning, and Agents

Use this reference for Vertex AI, Gemini, Model Garden, generative media, BigQuery AI/ML, Agent Engine, ADK, RAG, evaluation, and model lifecycle work.

## Contents

- [Lifecycle, endpoint, and availability changes](#lifecycle-endpoint-and-availability-changes)
- [Agents, RAG, and conversational systems](#agents-rag-and-conversational-systems)
- [Model Garden and partner models](#model-garden-and-partner-models)
- [Media and multimodal generation](#media-and-multimodal-generation)
- [BigQuery AI and machine learning](#bigquery-ai-and-machine-learning)
- [Training, evaluation, and inference](#training-evaluation-and-inference)

## Lifecycle, endpoint, and availability changes

### Agent Engine lifecycle and regions (2025-12)

Vertex AI Agent Engine Sessions and Memory Bank are GA. Agent Engine is also available in `europe-west6`, `europe-west8`, `asia-east2`, `asia-northeast3`, `asia-southeast2`, `northamerica-northeast2`, and `southamerica-east1`.

### Agent Engine SDK client migration (2025-09)

Vertex AI SDK for Python 1.112.0 refactors `agent_engines` to a client-based design, requiring existing Agent Engine code to migrate.

### BigQuery `AI.AGG` restored (2026-05)

Preview `AI.AGG` is available again for natural-language semantic aggregation of unstructured input.

### BigQuery `AI.KEY_DRIVERS` restored (2026-06)

Preview support for `AI.KEY_DRIVERS`, temporarily disabled in May, is restored.

### BigQuery `AI.KEY_DRIVERS` suspension (2026-05)

Preview support for `AI.KEY_DRIVERS` was temporarily disabled on May 14, 2026.

### Claude 3 Haiku retirement (2026-02)

Claude 3 Haiku was deprecated on February 23, 2026 and shuts down on August 23, 2026.

### Claude 3.5 Haiku retirement (2026-01)

Claude 3.5 Haiku was deprecated on January 5, 2026 and shuts down on July 5, 2026.

### Claude 3.7 Sonnet retirement (2025-11)

Claude 3.7 Sonnet was deprecated on November 11, 2025 and shuts down on May 11, 2026.

### Codestral and Mistral Large retirements (2026-01)

Codestral 25.01 and Mistral Large 24.11 were retired on January 23, 2026, so deployments using those model versions need replacements.

### Gemini 2.0 model lifecycle (2025-02)

Gemini 2.0 Flash is GA for text-only output while multimodal output remains private Preview; Gemini 2.0 Pro is experimental with a 2M context window, and Gemini 2.0 Flash-Lite is GA.

### Gemini 2.5 GA endpoint migration (2025-06)

Gemini 2.5 Flash and Pro are GA; `gemini-2.5-pro-preview-06-05` introduced expanded thinking support before the promotion. The Flash Preview endpoints `gemini-2.5-flash-preview-04-17` and `gemini-2.5-flash-preview-05-20` and the Pro Preview endpoints `gemini-2.5-pro-preview-03-25`, `gemini-2.5-pro-preview-05-06`, and `gemini-2.5-pro-preview-06-05` remain available until July 15, 2025 and are shut down afterward; Preview Provisioned Throughput must be migrated or replaced with a GA-endpoint purchase by that date.

### Gemini 2.5 Preview endpoint remapping (2025-06)

Effective June 19, 2025, `gemini-2.5-flash-preview-04-17` serves the Flash model released as `05-20`, while `gemini-2.5-pro-preview-03-25` and `gemini-2.5-pro-preview-05-06` serve the Pro model released as `06-05` during the transition to GA.

### Gemini 2.5 retirement deadline (2026-04)

The retirement date for Gemini 2.5 Pro, Gemini 2.5 Flash-Lite, and Gemini 2.5 Flash is October 16, 2026.

### Gemini endpoint lifecycle (2025-09)

Access to Gemini 1.5 models is discontinued. New versioned Preview endpoints are `gemini-2.5-flash-preview-09-2025` and `gemini-2.5-flash-lite-preview-09-2025`.

### Image-generation endpoint migrations (2026-02)

Before March 19, 2026, migrate `gemini-2.0-flash-image-generation-preview` to `gemini-2.5-flash-image`; migrate `gemini-2.5-flash-image-generation-preview` and `imagen-4.0-fast-generate-preview-05-20` to `imagen-4.0-generate-001` or `gemini-2.5-flash-image`; and migrate `imagen-product-recontext-preview-06-30`, `imagen-2.0-edit-preview-0627`, and `imagen-4.0-ingredients-preview` to `gemini-2.5-flash-image` to avoid disruption.

### Imagen 1 and 2 retirement (2025-06)

Imagen 1 and 2, image captioning, and visual question answering were deprecated on June 24, 2025. Image captioning, visual question answering, `imagegeneration@002`, `imagegeneration@005`, and `imagegeneration@006` are removed on September 24, 2025; migrate to Imagen 3.

### Imagen 4 Preview migration (2025-06)

Imagen 4 Preview uses `imagen-4.0-generate-preview-06-06`, `imagen-4.0-fast-generate-preview-06-06`, and `imagen-4.0-ultra-generate-preview-06-06`. Migrate from `imagen-4.0-ultra-generate-exp-05-20` and `imagen-4.0-generate-preview-05-20` before July 7, 2025 to avoid interruption.

### Imagen model migrations (2025-10)

Imagen subject and style tuning is removed on December 31, 2025; migrate applicable workflows to Gemini 2.5 Flash Image. The Imagen 4 Preview IDs `imagen-4.0-generate-preview-06-06`, `imagen-4.0-ultra-generate-preview-06-06`, and `imagen-4.0-fast-generate-preview-06-06` are removed on November 30, 2025 and should be replaced by their corresponding `-001` GA IDs.

### LearnLM migration to Gemini (2025-11)

LearnLM is no longer a separate offering because its capabilities are integrated into Gemini models starting with Gemini 2.5. Existing `learnlm-2.0-flash-experimental` projects stop working after December 3, 2025 unless an alternative model is selected manually.

### MedLM retirement (2025-05)

MedLM is deprecated and becomes unavailable on September 29, 2025.

### Model Garden MaaS deprecations (2025-01)

Model Garden deprecates the MaaS versions of Anthropic Claude 3 Sonnet, Mistral Large (24.07), and Codestral (24.05).

### Partner-model lifecycle (2025-03)

Mistral Small 3.1 (25.03) has multimodal capabilities and up to 128,000 tokens of context, while Claude Sonnet 3.7 is GA on Vertex AI with Provision Throughput support.

### Veo 3 lifecycle and resolution (2025-07)

Veo 3 Preview models added a `resolution` parameter for 1080p upscaling. Later in July, Veo 3 and Veo 3 Fast became GA.

### Vertex AI Extensions shutdown (2026-05)

Vertex AI Extensions is deprecated and shuts down after November 26, 2026; migrate to Agent Platform to avoid disruption.

### Vertex AI media endpoint migrations (2026-03)

Before April 2, 2026, migrate `veo-3.0-generate-preview` to `veo-3.0-generate-001`; `veo-2.0-generate-preview`, `veo-2.0-generate-exp`, `veo-001-preview-0815`, and `veo-001-preview` to `veo-2.0-generate-001`; `veo-3.1-generate-preview` to `veo-3.1-generate-001`; and `veo-3.1-fast-generate-preview` to `veo-3.1-fast-generate-001` (`veo-3.0-fast-generate-preview` is also marked discontinued even though the migration table names that same endpoint as its replacement). Before June 30, 2026, migrate `imagen-3.0-capability-001`, `imagen-3.0-capability-002`, `imagen-3.0-fast-generate-001`, `imagen-3.0-generate-001`, `imagen-3.0-generate-002`, `imagen-4.0-fast-generate-001`, `imagen-4.0-generate-001`, and `imagen-4.0-ultra-generate-001` to `gemini-2.5-flash-image`; migrate `veo-3.0-generate-001` to `veo-3.1-generate-001`, `veo-3.0-fast-generate-001` to `veo-3.1-fast-generate-001`, and `veo-2.0-generate-001` to `veo-3.1-generate-001`.

### Virtual Try-On endpoint migration (2026-01)

Virtual Try-On is GA at `virtual-try-on-001`; applications using `virtual-try-on-preview-08-04` should migrate to the new endpoint.


## Agents, RAG, and conversational systems

### Agent development tooling (2025-04)

The Agent Development Kit and Agent Garden are available in Preview.

### Agent Engine capabilities (2025-04)

Preview Vertex AI Agent Engine features include Agent Development Kit integration, Example Store, and LlamaIndex Query Pipeline integration; Agent Engine monitoring is GA.

### Agent Engine execution and protocols (2025-09)

Agent Engine adds Preview isolated Code Execution, Agent-to-Agent protocol support, and bidirectional streaming. The console also adds a Memory Bank tab for viewing and managing memories.

### Agent Engine management and sessions (2025-05)

Preview Agent Engine capabilities include console management for deployed agents and session support for Agent Development Kit agents.

### Agent Engine management capabilities (2025-11)

Preview Agent Engine features add console observability for sessions, traces, logs, and events; a deployed-agent playground; evaluation through the Gen AI Client; Memory Bank revision management; and IAM-created agent identities. Express mode support for Agent Engine Runtime is GA.

### Agent Engine Memory Bank (2025-07)

Preview Memory Bank dynamically generates long-term memories from users' conversations with an agent.

### Agent evaluation service (2025-01)

The Gen AI evaluation service can evaluate agents in Preview.

### BigQuery Agent Analytics plugin (2025-11)

The Agent Development Kit plugin streams agent prompts, tool use, and responses directly to BigQuery through the Storage Write API for performance analysis and visualization.

### BigQuery conversational analytics (2025-10)

Early-access conversational analytics lets users chat with BigQuery data, create custom agents, and make those agents available outside BigQuery.

### BigQuery conversational analytics additions (2026-03)

Preview conversational analytics can use `ObjectRef` data such as Cloud Storage images and PDFs, call `AI.FORECAST`, `AI.DETECT_ANOMALIES`, and `AI.GENERATE`, start chats from query results, and produce partition-aware SQL. Agent-created jobs carry a `ca-bq-job=true` label for cost, audit, and performance analysis, and the console offers clickable follow-up questions.

### BigQuery conversational analytics Preview (2026-01)

Conversational analytics advances from early access to Preview and can use supported BigQuery ML functions in verified queries and chat, in addition to chatting with data or custom agents and exposing agents outside BigQuery.

### BigQuery conversational analytics reaches GA (2026-06)

GA conversational analytics adds agent model-stage selection, per-conversation thinking mode, clarifying questions, response citations, parameters in verified queries, support for `AI.KEY_DRIVERS`, `AI.IF`, `AI.SCORE`, `AI.CLASSIFY`, `AI.SIMILARITY`, and `AI.SEARCH`, and US/EU MREP locations governing resource storage and ML processing. Creating a conversation directly with a dataset remains Preview.

### BigQuery Data Engineering Agent (2025-10)

The Preview Data Engineering Agent uses Gemini to build and modify pipelines that ingest data into BigQuery.

### BigQuery Data Science Agent (2025-08)

The Preview Data Science Agent runs inside Colab Enterprise notebooks to automate exploratory analysis, machine-learning tasks, and insight generation. Its table selector can scope an analysis to one or more BigQuery tables.

### BigQuery Data Science Agent reaches GA (2026-05)

The Data Science Agent for Colab Enterprise and BigQuery is GA.

### Conversational Analytics agents in Gemini Enterprise (2026-04)

Preview BigQuery Conversational Analytics agents can be published in Gemini Enterprise.

### Conversational analytics glossaries (2026-02)

Preview BigQuery conversational analytics agents can use custom glossary terms created and reviewed in BigQuery, and users can review terms imported from Dataplex Universal Catalog for an agent.

### Conversational analytics over lakehouse catalogs (2026-04)

Preview BigQuery conversational analytics can query lakehouse tables connected to an Apache Iceberg REST catalog or federated to an external catalog.

### Data Agent Kit extension (2026-07)

The Preview Data Agent Kit extension lets agent coding environments browse BigQuery datasets, manage pipelines, run queries, and perform other BigQuery tasks directly in the development environment.

### Data Science Agent prompt inputs (2025-09)

Preview prompts can reference BigQuery ML and DataFrames, use `@` to search project tables, use `+` to find files to upload, and use Apache Spark or PySpark keywords.

### RAG cross-corpus retrieval (2026-04)

Public-Preview cross-corpus retrieval lets `AsyncRetrieveContexts` and `AskContexts` retrieve contexts or generate answers from multiple RAG corpora in one operation.

### RAG Engine deployment modes (2026-04)

Public-Preview RAG Engine Serverless mode provides a fully managed database for RAG resources without database provisioning or scaling. Deployments can switch between Serverless mode and Spanner mode, which uses dedicated, isolated database instances.

### RAG Engine metadata search (2026-04)

RAG Engine supports schema-based metadata search: define a corpus metadata schema, attach metadata to corpus files, and filter retrieved contexts by that metadata.

### Vertex AI Agent Builder naming (2025-04)

Vertex AI Agent Builder now names the overall suite for building and deploying agents. The original product with that name is now AI Applications, with unchanged functionality and endpoints.

### Vertex AI Computer Use (2025-10)

The Preview `gemini-2.5-computer-use-preview-10-2025` model and tool can drive browser interactions for form entry, navigation, information gathering, and multi-step web tasks.


## Model Garden and partner models

### Claude 4 on Vertex AI (2025-05)

Claude Opus 4 and Claude Sonnet 4 are GA on Vertex AI and support Provision Throughput.

### Claude Opus 4.7 (2026-04)

Claude Opus 4.7 is available in Vertex AI Model Garden.

### Claude remote models in BigQuery ML (2025-03)

GA BigQuery ML remote models can target Anthropic Claude on Vertex AI, use `ML.GENERATE_TEXT` for table-backed generation, and use `ML.EVALUATE` for evaluation.

### DeepSeek API service (2025-06)

The DeepSeek API service on Vertex AI is in Preview.

### Gemma 3n in Model Garden (2025-06)

Gemma 3n models are available through Model Garden.

### Gemma 4 managed API (2026-04)

Experimental Gemma 4 26B A4B IT is available as a Model Garden managed API with text and image input and text output.

### GLM 4.7 managed API (2026-01)

GLM 4.7 is GA in Model Garden as a managed API for coding, tool-use, and reasoning workloads.

### Llama 4 deployment options (2025-04)

Llama 4 Maverick and Scout have Preview managed APIs and are available in Model Garden for both Model-as-a-Service and self-hosted deployment.

### MedGemma in Model Garden (2025-05)

MedGemma models are available in Vertex AI Model Garden.

### Mistral OCR (2025-05)

The Mistral OCR document-understanding API is GA on Vertex AI.

### Model Garden additions

**2025-02.**

Model Garden adds Phi-4 plus Preview DeepSeek-V3 and DeepSeek-R1 671B models. Managed Llama 3.3 70B and Anthropic Claude Sonnet 3.7 are also available in Preview.

**2025-04.**

Model Garden adds HiDream-I1, Llama Guard 4, Llama Prompt Guard 2, and Qwen3.

**2025-08.**

Model Garden adds `gpt-oss-120b`, `gpt-oss-20b`, Qwen3 Coder, and Qwen3 235B as Model-as-a-Service models. Gemma 3 270M, Wan 2.1, and Wan 2.2 models are also available through Model Garden.

**2025-09.**

Model Garden adds EmbeddingGemma, DeepSeek-V3.1, DeepSeek-V3.1-Terminus, DeepSeek-V3.2-Exp, and the Southeast-Asian-language SEA-LION V4 models.

**2025-11.**

Model Garden adds MiniMax M2 and Kimi K2 Thinking as managed APIs and makes Claude Opus 4.5 available.

**2025-12.**

Model Garden adds DeepSeek-V3.2, DeepSeek-V3.2-Speciale, Ministral 3, Mistral Large 3, FunctionGemma, and T5Gemma 2. DeepSeek-V3.2 is also available as a managed API.

### Model Garden additions and deployment (2025-03)

Model Garden adds Gemma 3, ShieldGemma 2, CogVideoX-2b, DeepSeek-V3-0324, TxGemma, and Sesame CSM; DeepSeek-R1, V3, and V3-0324 can use H200 GPUs with improved vLLM support. In Preview, models can be deployed through the Python SDK, `gcloud`, or the API, with equivalent code exposed by the console deploy panel.

### Model Garden additions and TPU serving (2025-10)

Model Garden adds Qwen-Image, Qwen-Image-Edit, Qwen-Image-Edit-2509, Claude Haiku 4.5, Mistral Codestral 2, DeepSeek-OCR, Qwen3-VL, and Earth AI. It also makes vLLM serving optimized for Cloud TPU available through Model Garden.

### Model Garden fine-tuning and evaluation additions (2025-06)

Model Garden adds PEFT UI fine-tuning for Gemma 3, a PEFT fine-tuning notebook for Qwen 2.5, an Axolotl fine-tuning notebook for Qwen 3, and `lm-evaluation-harness` as an evaluation service in Llama 3.3, Llama 3.1, Gemma 3, and Gemma 2 fine-tuning notebooks. DeepSeek-R1-0528 variants are also available.

### Model Garden inference optimizations (2025-02)

Preview prefix caching is available with vLLM for Llama 3.1 (8B and 70B) and Llama 3.3 (70B), and with Hex-LLM for Llama 2 (7B and 13B), Llama 3 (8B), Llama 3.1 (8B and 70B), Llama 3.2 (1B and 3B), Llama Guard (1B and 8B), CodeLlama (7B and 13B), Gemma and CodeGemma (2B and 7B), Mistral-7B (v0.2 and v0.3), and Mixtral-8x7B (v0.1). Preview speculative decoding is also available to reduce generation latency per output token.

### Model Garden medical models and Gemma fine-tuning (2025-07)

Model Garden adds multimodal MedGemma 27B IT, MedSigLIP, and T5Gemma. A new Axolotl Docker notebook supports fine-tuning the 1B, 4B, 12B, and 27B Gemma 3 variants.

### Model Garden PEFT behavior (2025-02)

The PEFT Docker workflow adds `perplexity`, `bleu`, `google_bleu`, `rouge1`, `rouge2`, `rougeL`, and `rougeLSum` evaluation metrics, selects and loads the best checkpoint, and runs training and evaluation only for data at or below `max_seq_length`. The **Fine-tune** flow can also use a selected service account.

### Model Garden vLLM co-hosting (2025-12)

The Model Garden co-hosting vLLM container can serve multiple replicas and dynamically load and unload multiple models, allowing them to share serving resources.

### One-hour Claude prompt caching (2025-11)

Prompt caching for Claude models supports a one-hour TTL.

### PaliGemma and LLaVA support (2025-02)

Model Garden adds PaliGemma 2 mix-model support and segmentation for PaliGemma 1 models. Its LLaVA model card also adds LLaVA Next support.

### Partner-model evaluations (2026-03)

The Gen AI evaluation service can evaluate partner models such as Anthropic and Llama models.

### Slot-based EmbeddingGemma (2026-04)

Preview `AI.EMBED` and `AI.SIMILARITY` can use the built-in `embeddinggemma-300m` text model, which generates embeddings at scale with BigQuery slots.


## Media and multimodal generation

### BigQuery multimodal workflows (2025-05)

Preview multimodal support uses `ObjectRef` values in tables and `ObjectRefRuntime` values in analysis and transformation workflows. BigQuery ML and BigQuery DataFrames can analyze multimodal data or generate embeddings, multimodal DataFrames can transform images and chunk PDFs, and Python UDFs can perform those image and PDF transformations.

### Gemini 2.5 Flash Image GA (2025-10)

The GA model ID is `gemini-2.5-flash-image`; it adds aspect-ratio controls, image-only responses, regional endpoints, batch prediction, generation from multiple reference images, and improved multi-turn editing.

### Gemini 2.5 Flash Image Preview (2025-08)

The Preview `gemini-2.5-flash-image-preview` model supports generation from multiple reference images and improved multi-turn image editing.

### Gemini 2.5 Flash Live API updates (2025-05)

Gemini 2.5 Flash adds allowlisted private-Preview audio-to-audio support through the Live API. Its public-Preview model version is `gemini-2.5-flash-preview-5-20`.

### Gemini 2.5 Flash native audio GA (2025-12)

The Gemini Live API native-audio model `gemini-live-2.5-flash-native-audio` is GA.

### Gemini 2.5 Live native audio (2025-09)

The Preview `gemini-live-2.5-flash-preview-native-audio-09-2025` model processes audio input and produces audio directly. It supports function calling, multilingual switching without preconfiguration, proactive audio responses, and affective dialog.

### Gemini image generation and seed support (2025-05)

The `gemini-2.0-flash-preview-image-generation` model provides Gemini 2.0 Flash image generation in public Preview. The seed parameter is GA and supports the Gemini 2.5 family.

### Gemini Live API expansion (2025-04)

The Gemini Live API is in public Preview with 8 voices and 31 languages through Chirp 3, longer and extendable sessions, screen sharing, input and output audio transcription, and mid-session system-instruction updates.

### Imagen 3 prompt enhancement (2025-01)

The `imagen-3.0-generate-002` model adds configurable LLM-based prompt enhancement, and that prompt rewriting is enabled by default.

### Imagen 4 stable models (2025-08)

Imagen 4 is GA through `imagen-4.0-generate-001`, `imagen-4.0-fast-generate-001`, and `imagen-4.0-ultra-generate-001`.

### Live API availability (2025-06)

The Live API is available through the API and Vertex AI Studio as a private GA offering; access must be requested through a Google account team representative.

### Lyria 3 (2026-03)

Public-Preview Lyria 3 provides `lyria-3-pro-preview` for 184-second audio generation and `lyria-3-clip-preview` for 30-second clips.

### Multimodal Gemini embeddings in BigQuery (2026-04)

Preview `gemini-embedding-2-preview` lets `AI.EMBED`, `AI.SIMILARITY`, and `AI.GENERATE_EMBEDDING` create one embedding from combined text, image, audio, video, and PDF inputs.

### Veo 2 advanced video controls (2025-06)

At GA, Veo 2 video generation can accept a last frame or an existing video to extend, in addition to a first frame.

### Veo 3 short-duration videos (2025-09)

Veo 3 can generate 4-, 6-, or 8-second videos at GA.

### Veo 3.1 and Veo 2 editing (2025-10)

Preview Veo 3.1 provides `veo-3.1-generate-preview` and `veo-3.1-fast-generate-preview`. Veo 2 can add objects to or remove objects from existing videos in Preview.

### Veo 3.1 GA models (2025-11)

Veo 3.1 and Veo 3.1 Fast are GA as `veo-3.1-generate-001` and `veo-3.1-fast-generate-001`.

### Veo 3.1 Lite (2026-04)

The `veo-3.1-lite-generate-001` model is available in public Preview on Vertex AI.

### Veo 3.1 reference-to-video additions (2026-01)

Veo 3.1 Preview reference-to-video supports a `9:16` aspect ratio and upsampling for videos generated at 1080p and 4K resolutions.

### Veo 3.1 video extension (2025-12)

Veo 3.1 can extend an existing Veo video in Preview.

### Vertex AI media-generation models (2025-05)

Imagen 4 adds the Preview `imagen-4.0-generate-preview-05-20` and experimental `imagen-4.0-ultra-generate-exp-05-20` models. Lyria 2 is GA, while Veo 3 is in allowlisted Preview.

### Vertex AI multimodal datasets (2025-06)

Multimodal datasets are available in Preview.


## BigQuery AI and machine learning

### `AI.AGG` availability (2026-04)

The Preview `AI.AGG` function semantically aggregates unstructured input from natural-language instructions, but support was temporarily disabled on April 13, 2026.

### Automatically deployed BigQuery ML open models (2026-03)

GA BigQuery ML remote models can automatically deploy open models to Vertex AI, manage the underlying resources, use Compute Engine reservation affinity, and automatically or immediately undeploy the model.

### Autonomous embedding generation and `AI.SEARCH` (2025-12)

Preview BigQuery tables created with `CREATE TABLE` can maintain an embedding column from a source column, regenerating affected embeddings when source data is added or changed. `AI.SEARCH` performs semantic search over tables configured for autonomous embedding generation.

### Autonomous embedding generation reaches GA (2026-06)

GA autonomous embedding generation can be enabled on new or existing tables with `CREATE TABLE` or `ALTER TABLE`; BigQuery maintains the embedding column as source-column data is added or changed.

### BigQuery `AI.KEY_DRIVERS` (2026-04)

The Preview `AI.KEY_DRIVERS` function identifies data segments that cause statistically significant changes to a summable metric.

### BigQuery data canvas assistant (2025-04)

The Preview Gemini-powered data canvas assistant can construct and modify a data canvas from prompts to answer analytics questions.

### BigQuery embedding and similarity functions reach GA (2026-03)

BigQuery remote models can use `gemini-embedding-001` or an open embedding model deployed from Vertex Model Garden or Hugging Face, then generate embeddings with `AI.GENERATE_EMBEDDING`; `AI.EMBED` can instead use the Gemini endpoint directly. `AI.EMBED` and `AI.SIMILARITY` are GA for text and image embeddings and for text-to-text, image-to-image, or cross-modal similarity.

### BigQuery generative AI function surface (2025-11)

GA `AI.GENERATE` handles free-text, entity-extraction, and structured-output tasks over text, images, audio, video, and documents; Preview `AI.EMBED` and `AI.SIMILARITY` create multimodal embeddings and semantic-similarity scores, and the scalar AI functions support end-user-credential authentication. The GA table-valued functions are `AI.GENERATE_TABLE`, `AI.GENERATE_TEXT`, and `AI.GENERATE_EMBEDDING`; the latter two are preferred replacements for their `ML.*` counterparts and use simplified output column names.

### BigQuery managed AI function updates (2026-02)

In Preview, `AI.CLASSIFY` can classify an input into multiple categories. At GA, custom output schemas for `AI.GENERATE` and `AI.GENERATE_TABLE` can attach descriptions to their fields.

### BigQuery managed AI functions (2025-10)

Preview `AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` use natural-language criteria to filter or join text and multimodal data, rank it, or classify text into user-defined categories.

### BigQuery ML bucket output formats (2025-02)

`ML.BUCKETIZE` and `ML.QUANTILE_BUCKETIZE` accept an `output_format` argument that can return `bin_<bucket_index>`, interval notation, or a JSON-formatted string.

### BigQuery ML contribution analysis (2025-04)

GA contribution analysis models can be created with `CREATE MODEL` and queried with `ML.GET_INSIGHTS` to explain changes in multidimensional key metrics. They support summable, summable-ratio, and summable-by-category metrics, with `top_k_insights_by_apriori_support` and `pruning_method` model options.

### BigQuery ML embedding remote models (2025-09)

Preview BigQuery ML remote models can use `gemini-embedding-001` or an open embedding model such as E5 deployed from Model Garden or Hugging Face to Vertex AI, then generate embeddings with `ML.GENERATE_EMBEDDING`.

### BigQuery ML Gemini 2.5 tuning (2025-09)

BigQuery ML remote models based on `gemini-2.5-pro` or `gemini-2.5-flash-lite` can be supervised-tuned.

### BigQuery ML Gemini tuning (2025-05)

BigQuery ML remote models based on `gemini-2.0-flash-001` or `gemini-2.0-flash-lite-001` can be supervised-tuned.

### BigQuery ML monitoring visualizations (2025-03)

Preview charts can visualize output from `ML.VALIDATE_DATA_SKEW` and `ML.VALIDATE_DATA_DRIFT` model-monitoring functions.

### BigQuery ML remote-model evaluation (2025-01)

GA remote models can target open text-generation models from Vertex Model Garden or Hugging Face that are deployed to Vertex AI, then use `ML.GENERATE_TEXT` and `ML.EVALUATE`. In Preview, `ML.EVALUATE` can also evaluate Anthropic Claude models, with their BigQuery ML quotas aligned to Vertex AI quotas.

### BigQuery Notebook code generation (2025-04)

Gemini-generated Python in BigQuery Notebooks can use relevant table names from the project. Including `BigFrames` in the prompt generates code that uses BigQuery DataFrames, in Preview.

### BigQuery performance assistance (2026-06)

Preview Gemini assistance can monitor performance, analyze capacity and cost, recommend SQL query optimizations for BigQuery editions, and troubleshoot performance from Jobs explorer, Job details, Job history, and Capacity management.

### BigQuery Studio model creation and comments (2025-07)

In Preview, the console can create BigQuery ML models. Users can also add, reply to, and link to comments on notebooks, data canvases, data preparation files, and saved queries.

### BigQuery token accounting (2026-05)

Preview `AI.COUNT_TOKENS` estimates token counts for text input. For supported generative AI functions, query token usage can also expose input, output, thought, and cache tokens per modality.

### BigQuery-managed open-model endpoints (2025-10)

In Preview, BigQuery ML can manage open models as Vertex AI endpoints through SQL, including automatic or immediate undeployment, custom deployment machine types, and Compute Engine reservation affinity.

### Gemini 3 in BigQuery AI functions (2025-11)

BigQuery generative AI functions can use Gemini 3.0, but must specify the full global endpoint:

```text
https://aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/global/publishers/google/models/gemini-3-pro-preview
```

### Gemini assistance in BigQuery notebooks (2025-06)

In Preview, Colab Enterprise notebooks in BigQuery can use Gemini to explain code and to fix and explain Python errors.

### Gemini CLI for BigQuery (2025-09)

Beta Gemini CLI extensions provide natural-language search, exploration, analysis, forecasting, and contribution analysis against BigQuery from the command line.

### Gemini Cloud Assist for BigQuery operations (2026-01)

In Preview, Gemini Cloud Assist can analyze job history, including slow or resource-intensive queries, and discover resources across projects from questions about schemas or table contents.

### Gemini Cloud Assist lineage and scheduling (2026-06)

In Preview, Gemini Cloud Assist in BigQuery can analyze data lineage and schedule queries.

### Gemini SQL error assistance (2025-11)

In Preview, Gemini in BigQuery can fix and explain SQL query errors.

### Generated table and column descriptions (2025-06)

In Preview, BigQuery data insights can use Gemini to generate table and column descriptions from table metadata.

### Model selection for BigQuery managed AI functions (2026-01)

`AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` accept an optional endpoint argument for selecting the model used by the function.

### Multi-series ARIMA_PLUS_XREG forecasting

**2025-01.**

The Preview `TIME_SERIES_ID_COL` option lets one BigQuery ML `ARIMA_PLUS_XREG` multivariate time-series model forecast multiple series.

```sql
OPTIONS(MODEL_TYPE = 'ARIMA_PLUS_XREG', TIME_SERIES_ID_COL = 'series_id')
```

**2025-06.**

The `TIME_SERIES_ID_COL` option for forecasting multiple time series with one `ARIMA_PLUS_XREG` multivariate model is GA.

### Natural-language SQL comments (2025-10)

In Preview, Gemini in BigQuery can interpret natural-language comments embedded in existing SQL to refine and transform the query.

### Optimized managed AI functions (2026-04)

Preview optimized mode for `AI.IF` and `AI.CLASSIFY` reduces LLM token consumption and query latency on large datasets.

### Provisioned Throughput from BigQuery ML (2025-06)

At GA, `ML.GENERATE_TEXT` and `AI.GENERATE` can use Vertex AI Provisioned Throughput with supported Gemini models.

### Single-table `AI.DETECT_ANOMALIES` (2026-05)

GA `AI.DETECT_ANOMALIES` can take one input table containing both historical and target data.

### Structured generative output (2025-04)

Preview `AI.GENERATE_TABLE` produces structured data with Gemini 1.5 Pro, Gemini 1.5 Flash, or Gemini 2.0 Flash. Its `output_schema` argument accepts a SQL schema for formatting the response as a BigQuery table.

### TimesFM 2.5 anomaly detection (2025-11)

BigQuery ML adds TimesFM 2.5 support to `AI.FORECAST`, `AI.EVALUATE`, and `AI.DETECT_ANOMALIES`. The new Preview `AI.DETECT_ANOMALIES` function uses historical time-series data as a baseline for anomaly detection.

### TimesFM evaluation (2025-10)

The built-in TimesFM capability is GA: `AI.FORECAST` accepts a larger context window, and `AI.EVALUATE` compares forecast output with a historical reference time series.

### TimesFM forecasting (2025-04)

Preview `AI.FORECAST` uses BigQuery ML's built-in TimesFM model for univariate forecasting without creating or training a model of your own.

### TimesFM forecasting and anomaly functions (2026-03)

GA `AI.DETECT_ANOMALIES` accepts a custom context window, and GA `AI.FORECAST` can specify the latest timestamp for forecasting. `AI.EVALUATE` accepts a custom context window and returns mean absolute scaled error.

### TimesFM functions in Connected Sheets (2026-07)

Connected Sheets can directly use pre-trained TimesFM models through `AI.FORECAST` and `AI.DETECT_ANOMALIES`; this integration is GA.

### Typed generative functions (2025-04)

Preview BigQuery ML functions `AI.GENERATE`, `AI.GENERATE_BOOL`, `AI.GENERATE_INT`, and `AI.GENERATE_DOUBLE` analyze text with a Vertex AI Gemini model and return a response of the corresponding type.


## Training, evaluation, and inference

### Data-insight generation (2025-11)

Generating table and column descriptions is GA in all supported Gemini languages. At GA, the Dataplex API can also generate data insights when it creates a `DataScan`.

### Foundation-model observability (2025-01)

The predefined Vertex AI **Model observability** dashboard shows usage, throughput, and latency and helps troubleshoot 429 errors for foundation models. **Show All Metrics** opens the underlying metrics in Cloud Monitoring for customization and exploration.

### Gemini 1.5 access restriction (2025-04)

Gemini 1.5 Pro and Gemini 1.5 Flash are unavailable to projects with no previous use of those models, including new projects.

### Gemini 2.0 Flash tuning (2025-03)

Gemini 2.0 Flash fine-tuning is GA and can now tune function calling.

### Gemini 2.5 Flash-Lite (2025-06)

Gemini 2.5 Flash-Lite is available in Preview through the API and Vertex AI Studio.

### Gemini 2.5 Flash-Lite GA (2025-07)

Gemini 2.5 Flash-Lite is GA through the API and Vertex AI Studio, with explicit caching, batch prediction, and expanded regional availability.

### Gemini 2.5 previews (2025-04)

Gemini 2.5 Pro and Gemini 2.5 Flash are available in public Preview; Gemini 2.5 Flash includes thinking capabilities.

### Gemini 3 Flash (2025-12)

Gemini 3 Flash is available in public Preview.

### Gemini 3.1 Flash-Lite (2026-03)

The `gemini-3.1-flash-lite` model is available in public Preview.

### Gemini log probabilities (2025-06)

The Gemini API `logprobs` and `response_logprobs` parameters are GA.

### Gemini thought summaries (2025-05)

Experimental thought summaries are available for Gemini 2.5 Pro and Gemini 2.5 Flash.

### Google Gen AI SDK for C# (2025-10)

The Preview C# SDK supports `GenerateContentAsync`, `GenerateContentStreamAsync`, `GenerateImagesAsync`, and the Live API methods `SendClientContentAsync`, `SendRealtimeInputAsync`, and `SendToolResponseAsync`.

### Google Maps grounding regions (2025-07)

Grounding with Google Maps is available in Preview in all regions except the EEA.

### Grounding with Google Maps response changes (2025-09)

Responses no longer contain `grounding_chunk.maps.text`, `grounding_chunk.maps.place_answer_sources.review_snippets.author_attribution`, `grounding_chunk.maps.place_answer_sources.flag_content_uri`, or `grounding_chunk.maps.place_answer_sources.review_snippets.flag_content_uri`. A widget context token is now returned only when the request sets `widget_token_enable`.

### Stable Vertex AI embedding models (2025-05)

The `gemini-embedding-001` and `text-embedding-005` text-embedding models are GA.

### Vertex AI global endpoint (2025-05)

The Vertex AI global endpoint is GA.

### Vertex AI grounding modes (2025-04)

Web Grounding for Enterprise is GA, while Grounding with Google Maps is available as a public experimental feature.

### Vertex AI judge-model tools (2025-03)

Preview judge-model evaluation and customization tools are available through the Vertex AI Gen AI evaluation service.

### Vertex AI model additions (2026-02)

Model Garden adds Claude Opus 4.6 and Claude Sonnet 4.6, plus an experimental GLM 5 managed API. Gemini 3.1 Pro is in Preview with multimodal input and a one-million-token context window, while `gemini-3.1-flash-image` is in public Preview.

### Vertex AI prompt management (2025-10)

Prompts and prompt versions can be stored and versioned through the Vertex AI SDK as well as managed in Vertex AI Studio.

### Vertex AI Search and Elasticsearch grounding (2025-05)

Grounding on data through Vertex AI Search and grounding with Elasticsearch are GA.

### Vertex AI Studio prompt sharing (2025-12)

Vertex AI Studio prompts can now be shared without an administrator first enabling prompt sharing.

### Vertex AI tuning expansion (2025-08)

Supervised fine-tuning now supports open models such as Llama 3.1 as well as Gemini 2.5 Flash-Lite and Gemini 2.5 Pro. In Preview, a tuning job can integrate with the Gen AI evaluation service to evaluate the tuned model and intermediate checkpoints automatically.

### Zero-shot prompt optimization (2025-08)

The Vertex AI prompt optimizer is GA and adds a zero-shot optimizer.
