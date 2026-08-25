# Tools and Structured Output

Source batches: `tool-and-structured-output` and `gpt-5.6`.

## Structured Responses output

### Formats, parsing, and refusals

Responses places raw structured formats under `text.format`, including
`{"type":"json_object"}` for JSON mode. SDK parse helpers accept a Pydantic
model through Python `text_format` or a Zod format through JavaScript
`text.format`.

A safety refusal is a distinct `refusal` content item, not schema-conforming
data. Inspect message content items before reading parsed output.

```python
response = client.responses.parse(
    model="gpt-5.6",
    input=[{"role": "user", "content": "Extract the result."}],
    text_format=Result,
)
for output in response.output:
    if output.type == "message":
        for item in output.content:
            value = item.refusal if item.type == "refusal" else item.parsed
```

## Function calling

### Responses round trip

Each `function_call` output item carries `name`, JSON-encoded `arguments`, and
a `call_id`. Preserve every response output item, then return each tool result
as a `function_call_output` with the same `call_id`. A result is normally a
string but can be an array of image or file objects.

```python
input_list += response.output
for call in response.output:
    if call.type == "function_call":
        result = run(call.name, json.loads(call.arguments))
        input_list.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result),
        })
```

### Namespaces and deferred tool search

A `namespace` groups related functions. `defer_loading: true` leaves a
function out of the initial context so `tool_search` can discover it; tool
search requires GPT-5.4 or later. Before the eventual `function_call`, output
can contain `tool_search_call` and `tool_search_output` items. Keep both in
interaction history.

```json
{
  "type": "namespace",
  "name": "crm",
  "tools": [{
    "type": "function",
    "name": "lookup",
    "defer_loading": true,
    "parameters": {"type":"object", "properties":{}}
  }]
}
```

### Per-turn allowed tools

`tool_choice` can restrict a stable full tool list to a callable subset without
changing the original list, preserving prompt-cache reuse. With tool search,
the restriction applies only to tools currently loaded for that turn.

```json
{
  "type": "allowed_tools",
  "mode": "auto",
  "tools": [
    {"type":"function", "name":"get_weather"},
    {"type":"function", "name":"search_docs"}
  ]
}
```

### Parallel-call edge cases

Built-in tools cannot be combined with parallel function calling.
`parallel_tool_calls: false` limits a turn to zero or one call. Multiple calls
from a fine-tuned model disable strict mode for those calls.
`gpt-4.1-nano-2025-04-14` can duplicate a tool call when parallel calls are
enabled.

### Function-call streaming events

A streamed call follows this sequence:

1. `response.output_item.added` starts the item.
2. `response.function_call_arguments.delta` sends JSON fragments.
3. `response.function_call_arguments.done` provides the complete encoded
   arguments.
4. `response.output_item.done` finishes the item.

Aggregate deltas by `output_index` and use `item_id` to associate them with
the call.

## Custom tools

### Free-form text input

A tool with `type: "custom"` accepts arbitrary text rather than JSON-schema
arguments. The `custom_tool_call` output item carries text in `input` together
with `name` and `call_id`.

```json
{
  "type": "custom",
  "name": "code_exec",
  "description": "Executes Python code."
}
```

### Grammar-constrained input

Set a custom tool's `format` to `grammar` with `lark` or `regex`. Regexes in
both formats use Rust syntax; lookarounds and lazy modifiers are unsupported.
Lark omits terminal priorities, templates, `%declare`, and non-common imports.
Keep terminals bounded, whitespace explicit, and anchored free-form spans in
one terminal because greedy lexing happens before parsing.

```json
{
  "type": "custom",
  "name": "date",
  "format": {
    "type": "grammar",
    "syntax": "regex",
    "definition": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
  }
}
```

## Hosted and multi-agent tool orchestration

### Programmatic Tool Calling

For bounded reductions over tool results, enable the hosted program tool and
opt individual functions in with `allowed_callers`. The host must process
`program`, program-issued `function_call`, `function_call_output`, and
`program_output` items while preserving `call_id` and `caller`.

```json
{
  "tools": [
    {"type":"programmatic_tool_calling"},
    {
      "type":"function",
      "name":"lookup_records",
      "allowed_callers":["programmatic"]
    }
  ]
}
```

### Multi-agent Responses beta

Enable the beta with both the request header and bounded concurrency. Handle
and replay `multi_agent_call`, `multi_agent_call_output`, and `agent_message`
items, plus function calls issued by any subagent.

```text
OpenAI-Beta: responses_multi_agent=v1
```

```json
{
  "multi_agent": {"enabled":true, "max_concurrent_subagents":3}
}
```
