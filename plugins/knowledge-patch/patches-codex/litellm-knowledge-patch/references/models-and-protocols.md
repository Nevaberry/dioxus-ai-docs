# Models, Providers, and Protocol Bridges

## Provider and model support

### Meta Model API provider

Since 1.93.0, the OpenAI-compatible `meta` provider serves
`meta/muse-spark-1.1` through Chat Completions, `/v1/messages`, and Responses.

### New model identifiers and pricing metadata

Since 1.93.0, the model map includes:

- `gpt-5.6`, `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna` for OpenAI
  and Azure;
- `gpt-realtime-2.1` and `gpt-realtime-2.1-mini`;
- `xai/grok-4.5` and `xai/grok-4.5-latest`;
- `meta/muse-spark-1.1`;
- `jp.anthropic.claude-opus-4-8`; and
- `vertex_ai/chirp_3`.

GPT-5.6 metadata covers priority, flex, batch, and over-272K-token pricing
tiers. Bedrock regional inference profiles resolve regional pricing through
`get_model_info`.

### Cursor model variants

Since 1.97.0, `/cursor/chat/completions` resolves Cursor thinking and fast
model-name suffixes and works in Cursor agent mode. Per-model budgets apply to
the resolved variants.

### Gemini robotics models

Since 1.97.0, the Gemini integration recognizes
`gemini-robotics-er-2-preview` and `gemini-robotics-er-1.6-preview`.

### Azure Storage sovereign-cloud suffixes

Since 1.97.0, the Azure Storage integration honors
`AZURE_STORAGE_ENDPOINT_SUFFIX`, allowing environment-selected sovereign-cloud
endpoints.

## Chat, Responses, and Messages bridges

### Chat and Responses bridge additions

Since 1.93.0, Chat Completions forwards `verbosity` to providers. The
chat-to-Responses bridge preserves custom-tool round trips and allowlists used
by CLI clients, and it retains `reasoning_tokens` in translated usage.

### Protocol-bridge direction switches

Under `litellm_settings`, use
`use_chat_completions_url_for_anthropic_messages` to send OpenAI-compatible
`/v1/messages` through Chat Completions instead of Responses. Use
`route_all_chat_openai_to_responses` to send OpenAI Chat Completions through
the Responses bridge. Corresponding `LITELLM_*` environment variables are
available for both switches.

### Groq web search translation

Since 1.97.0, LiteLLM converts Groq `web_search_options` into the provider's
`browser_search` tool.

### Finish-reason normalization

Since 1.97.0, a generic provider `finish_reason` of `error` is normalized to
`stop`. Clients must not assume they will receive the original value.

## Anthropic capability mapping

### Claude context-management capability mapping

Since 1.93.0, Bedrock Claude Invoke preserves
`clear_tool_uses_20250919` context edits and emits the
`context-management-2025-06-27` beta. Mapped Claude 4.8 and later models
advertise `supports_mid_conversation_system`.

Adaptive thinking and effort are translated for Anthropic models before 4.6,
including Vertex model names ending in `@default`.

## Model exposure and request construction

### Environment-scoped model exposure

Set `LITELLM_ENVIRONMENT` to `production`, `staging`, or `development` and use
`model_info.supported_environments` to expose a model only in selected
environments.

```yaml
# Process environment: LITELLM_ENVIRONMENT=production
model_list:
  - model_name: chat
    litellm_params: {model: openai/gpt-4o}
    model_info:
      supported_environments: [production, staging]
```

### Per-model prompt framing

A proxy model can override inferred prompt formatting inside `litellm_params`.
The template supports initial and final text, role-specific `pre_message` and
`post_message` strings, and `bos_token` and `eos_token`.

```yaml
model_list:
  - model_name: custom-chat
    litellm_params:
      model: huggingface/example/instruct
      initial_prompt_value: "\n"
      roles:
        user: {pre_message: "<|im_start|>user\n", post_message: "<|im_end|>"}
        assistant: {pre_message: "<|im_start|>assistant\n", post_message: "<|im_end|>"}
      final_prompt_value: "\n"
```

### Custom tokenizer for token counting

`model_info.custom_tokenizer` makes `/utils/token_counter` use a selected
Hugging Face tokenizer for that proxy model. A private tokenizer can receive
its access token through `auth_token`.

```yaml
model_info:
  custom_tokenizer:
    identifier: deepseek-ai/DeepSeek-V3-Base
    revision: main
    auth_token: os.environ/HUGGINGFACE_API_KEY
```
