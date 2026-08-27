# Thought signatures and history replay

## Preserve signatures in manually managed history (gemini-3-thought-signatures)

Thought signatures are opaque encrypted reasoning state on response parts.
Official SDKs preserve them when the complete response object is appended to
history. REST clients and manually assembled histories must return every
signature unchanged on the exact model part where it arrived.

```json
{
  "role": "model",
  "parts": [{
    "functionCall": {"name": "check_flight", "args": {"flight": "AA100"}},
    "thoughtSignature": "<opaque signature>"
  }]
}
```

For Gemini 3.x function calling, this round trip is mandatory even with
minimal thinking. Omitting a required signature returns HTTP 400.

## Retain every signed step in the current turn

Validation scans backward to the newest user message containing ordinary
content. A user message containing only a `functionResponse` does not begin a
new turn. Every step after the boundary must preserve the signature on its
first function call, so resend all prior signed model-call parts in a
sequential loop:

```text
user(text) → model(FC1 + signature A) → user(FR1)
           → model(FC2 + signature B) → user(FR2)
```

## Keep parallel calls grouped

When one model response contains parallel calls, only the first `functionCall`
part has the signature. Keep it on that part. Return all model calls together,
then all function responses; interleaving `FC1, FR1, FC2, FR2` fails.

```text
model: [FC1 + signature, FC2]
user:  [FR1, FR2]
```

## Preserve the OpenAI-compatible extension

Chat-completion responses put the signature under the signed tool call's
`extra_content.google.thought_signature`. Replay that extension with the
assistant tool-call message.

```json
{
  "tool_calls": [{
    "extra_content": {
      "google": {"thought_signature": "<opaque signature>"}
    },
    "function": {
      "name": "check_flight",
      "arguments": "{\"flight\":\"AA100\"}"
    }
  }]
}
```

## Handle non-call and streamed signatures

Without a function call, Gemini 3.x can attach a signature to the last content
part when it generated a thought. Replaying it is recommended for reasoning
continuity but is not validated. In a streamed non-call response, it may occur
on an empty-text part; consume the stream through `finish_reason` rather than
discarding empty parts early.

With function calls, Gemini 2.5 may put an optional signature on the first part
regardless of type. Gemini 3.x always signs the first function-call part and
requires it back. Without calls, 2.5 returns no signature.

## Import unsigned traces only with documented sentinels

Injecting function-call blocks not produced by the API is discouraged. If an
imported trace cannot contain real signatures, either documented sentinel can
bypass validation in the signature field:

```json
{"thoughtSignature": "context_engineering_is_the_way_to_go"}
```

```json
{"thoughtSignature": "skip_thought_signature_validator"}
```
