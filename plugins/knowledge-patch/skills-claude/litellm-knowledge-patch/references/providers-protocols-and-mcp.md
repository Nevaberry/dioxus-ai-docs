# Providers, protocol bridges, and MCP

## Model API provider

Since 1.93.0, the OpenAI-compatible `meta` provider serves
`meta/muse-spark-1.1` through Chat Completions, `/v1/messages`, and Responses.

## Model identifiers and pricing metadata

The model map includes `gpt-5.6` plus `-sol`, `-terra`, and `-luna` variants
for OpenAI and Azure; `gpt-realtime-2.1` and `-mini`; `xai/grok-4.5` and
`-latest`; `meta/muse-spark-1.1`; `jp.anthropic.claude-opus-4-8`; and
`vertex_ai/chirp_3`.

GPT-5.6 metadata includes priority, flex, batch, and over-272K-token pricing
tiers. Bedrock regional inference profiles resolve regional pricing through
`get_model_info`.

## Chat and Responses bridges

Chat completions forward `verbosity`. The Chat-to-Responses bridge preserves
Codex CLI custom-tool round trips and allowlists, and retains `reasoning_tokens`
in translated usage.

`use_chat_completions_url_for_anthropic_messages` sends OpenAI-compatible
`/v1/messages` through Chat Completions instead of Responses.
`route_all_chat_openai_to_responses` sends OpenAI Chat Completions through the
Responses bridge. Both settings live under `litellm_settings` and have matching
`LITELLM_*` environment variables.

## Anthropic context-management mappings

Bedrock Claude Invoke retains `clear_tool_uses_20250919` context edits and
emits the `context-management-2025-06-27` beta. Mapped Claude 4.8 and later
models advertise `supports_mid_conversation_system`.

Adaptive thinking and effort are translated for pre-4.6 Anthropic models,
including Vertex model names that end with `@default`.

## A2A agent gateway

The gateway can register and invoke A2A agents beside model and MCP routes, so
a deployment does not require a separate agent gateway.

## Client-held MCP credentials

MCP servers support `true_passthrough` and `oauth_delegate` auth modes, with
upstream OAuth discovery bound to each server. The `dcr_bridge` flow carries
client-held credentials in a sealed envelope and provides discovery,
registration, and token relays with mandatory PKCE S256.

## MCP OAuth token exchange

MCP server configuration accepts `oauth2_token_exchange` and the `entra_obo`
token-exchange profile through the REST API and dashboard. The chosen
`oauth2_flow` is persisted explicitly; legacy null values are backfilled at
startup. Outbound concurrency limits apply to on-behalf-of tool calls.

## MCP semantic filtering

The semantic filter expands `litellm_proxy` tools before filtering, reports the
number removed, and preserves complete tool names in its response header.
Context-window failures surface and fail closed.

## MCP guardrails

Model Armor can inspect MCP tool calls in `pre_mcp_call` and `during_mcp_call`
modes. Content Filter supports `pre_mcp_call`. With
`skip_unscannable_attachments`, Model Armor passes reference-only attachments
through and no longer imposes an attachment-count limit.

## MCP ingress origin and grants

Behind ingress, set `PROXY_BASE_URL` to the exact public origin without a path
or trailing slash; it takes precedence over forwarded headers. Otherwise,
`use_x_forwarded_for` is honored only when the peer belongs to
`mcp_trusted_proxy_ranges`.

`require_key_mcp_access_defined` stops an empty key grant from inheriting the
team's servers. `require_end_user_mcp_access_defined` requires an explicit
end-user grant.

## Cursor variants

In 1.97.0, `/cursor/chat/completions` resolves Cursor thinking and fast
model-name suffixes and works with agent mode. Per-model budgets apply to the
resolved variants.

## Guardrail coverage

The Rubrik guardrail provides prompt moderation, response-text blocking,
buffered streaming, and failure logging. Blocked requests are attributed to
their caller. Output scanning also covers the `/openai/v1/responses` alias.

## Groq web search

For Groq requests, LiteLLM translates `web_search_options` into the provider's
`browser_search` tool.

## Gemini robotics models

The Gemini integration includes `gemini-robotics-er-2-preview` and
`gemini-robotics-er-1.6-preview` identifiers.

## Skill registration routes

Claude Code skill registration is create-only. Use the separate `PUT` route to
update an existing skill.

## Azure Storage sovereign clouds

Azure Storage honors `AZURE_STORAGE_ENDPOINT_SUFFIX`, allowing the environment
to select a sovereign-cloud endpoint suffix.

## Finish-reason normalization

The generic provider adapter normalizes a `finish_reason` of `error` to
`stop`. Clients must not depend on receiving the original string.
