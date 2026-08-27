# Models and Reasoning

Source batches: `gpt-5.6` and `2026-08-04-2026-08-13`.

## GPT-5.6 family

### Model IDs, context, and output limits

The `gpt-5.6` alias routes to flagship `gpt-5.6-sol`. Use
`gpt-5.6-terra` for the balanced lower-cost tier and `gpt-5.6-luna` for
efficient high-volume work.

- Sol and Terra have roughly 1.05M input context.
- Luna has 400K input context.
- All three have 128K maximum output.
- Sol and Terra requests above 272K input tokens enter different full-request
  pricing.

### Reasoning levels and endpoint fields

The family supports `none`, `low`, `medium`, `high`, `xhigh`, and `max`.
Omission defaults to `medium` in standard and Pro modes.

Responses:

```json
{"reasoning":{"effort":"none"}}
```

Chat Completions:

```json
{"reasoning_effort":"none"}
```

During migration, first preserve the old effective effort, then tune it.

### Chat Completions function-tool constraint

Function tools on Chat Completions require effective reasoning `none`, making
the default `medium` incompatible. Set `reasoning_effort` explicitly or move
reasoning-plus-tools workflows to Responses.

```json
{
  "model": "gpt-5.6-luna",
  "reasoning_effort": "none",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "lookup",
        "parameters": {"type": "object", "properties": {}}
      }
    }
  ]
}
```

### Persisted reasoning context

Set `reasoning.context` to `all_turns` and continue with
`previous_response_id` only while goals and assumptions remain stable. Use
`current_turn` when earlier reasoning is stale. Use `auto` or omit the field
for the default, and inspect the returned effective value.

Manual replay must retain every user input and output item together with item
IDs, call IDs, caller metadata, and assistant phase values.

```json
{
  "reasoning": {"context":"all_turns"},
  "previous_response_id": "resp_..."
}
```

### Multimodal detail defaults

Omitted or `auto` image detail can retain original dimensions. In Responses,
omitted or `input_file.detail: "auto"` can use high-detail PDF page images,
increasing tokens and latency. Chat Completions file inputs do not expose the
same detail control. Set detail explicitly where the endpoint permits when
cost or latency matters.

### Pro mode

Pro is a Responses-only reasoning mode on a normal family model, not a
separate model slug. Mode and effort are independent; supported Pro efforts
begin at `medium`.

```json
{
  "model": "gpt-5.6-sol",
  "reasoning": {"mode":"pro", "effort":"medium"}
}
```

### Generation-time safeguards

Cyber and biology safeguards can refuse output or pause a stream for several
seconds while generation is synchronously reviewed, including for legitimate
dual-use requests. Attach a stable, privacy-preserving `safety_identifier` to
each end-user request.

## Access-controlled modes and models

### Ultrafast limited preview

Ultrafast is a new API service tier for `gpt-5.6-sol`. It is available only in
limited preview to selected customers; do not assume a project has access.

### Daybreak access and IDs

Responses supports `daybreak-blue-latest`, `daybreak-red-latest`, and
`gpt-5.6-cyber` for approved defensive-security users. Daybreak models require
separate approval and provisioning. Red access is separately approved for
purpose-trained models such as `gpt-5.6-cyber`.

```json
{"model":"daybreak-blue-latest","input":"Review this code."}
```

### Fast mode for long context

Fast mode accepts prompts exceeding 272K tokens for `gpt-5.6-sol`,
`gpt-5.6-terra`, and `gpt-5.6-luna`; long-context requests no longer need to
avoid this processing mode.
