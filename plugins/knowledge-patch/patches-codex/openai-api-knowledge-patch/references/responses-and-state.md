# Responses, State, and Safety

## One generation per request (`responses-api`)

Responses removes the `n` parameter and produces one generation per request.
Make separate requests when multiple candidate outputs are required.

## Response chains, instructions, and billing

`previous_response_id` carries earlier response context, but it does not carry
top-level `instructions`. Resend stable instructions on every request in a chain.
Earlier input tokens in that chain are still billed as input tokens.

## Storage and stateless reasoning

Responses is stored by default. Chat Completions is also stored by default for new
accounts. Set `store: false` for stateless use; Zero Data Retention flows enforce
disabled storage automatically.

To retain reasoning context without storage, replay every returned reasoning item
with its default `encrypted_content`. Do not discard reasoning items between
stateless turns.

## Responses function strictness

Responses function definitions are internally tagged. Omitting `strict` attempts
strict mode rather than preserving the earlier non-strict default. If a schema is
incompatible, the API falls back to best-effort calling and reports
`strict: false`. Set the field explicitly to require non-strict behavior.

```json
{
  "type": "function",
  "name": "lookup",
  "parameters": {"type": "object", "properties": {}},
  "strict": false
}
```

## Streaming transports and moderation timing

HTTP `stream=true` uses server-sent events. Persistent WebSocket mode supports
incremental inputs chained with `previous_response_id`.

When moderation scores are requested with a generation, the scores arrive only
after the full output. They are not included in partial deltas, so do not treat an
in-progress stream as having final moderation results.

## Persisted reasoning context

Set `reasoning.context` to `all_turns` and continue with `previous_response_id` only
while goals and assumptions remain stable. Use `current_turn` when earlier
reasoning has gone stale. Use `auto` or omit the field for the model default, then
inspect the returned effective value.

```json
{
  "reasoning": {"context": "all_turns"},
  "previous_response_id": "resp_..."
}
```

For manual replay, retain every user input and output item as well as item IDs,
call IDs, caller metadata, and assistant phase values.

## Generation-time safeguards

Cyber and biology safeguards can refuse output or pause a stream for several
seconds while generation is synchronously reviewed, including for legitimate
dual-use requests. Applications should attach a stable, privacy-preserving
`safety_identifier` to each request.

Realtime does not use that request parameter. Its transport-specific
`OpenAI-Safety-Identifier` header is described in the Realtime reference.
