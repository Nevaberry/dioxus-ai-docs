# Tools and Structured Output

## Parse structured Responses and refusals

Responses places raw structured formats under `text.format`, including
`{"type":"json_object"}` for JSON mode. Python SDK parse helpers accept a
Pydantic model through `text_format`; JavaScript helpers accept a Zod format
through `text.format`.

Inspect message content items individually. A safety refusal is a separate
`refusal` item rather than schema-conforming data.

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

## Complete a function-call round trip

Each `function_call` output item carries `name`, JSON-encoded `arguments`, and a
`call_id`. Preserve every response output item, then append one
`function_call_output` for each call using the same `call_id`.

The function result is normally a string, but it may instead be an array of image
or file objects.

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

## Group and defer tools

A `namespace` groups related functions. `defer_loading: true` omits a function from
the initial context so `tool_search` can discover it; tool search requires
`gpt-5.4` or later. Preserve `tool_search_call` and `tool_search_output` items in
the interaction history before the eventual `function_call`.

```json
{"type":"namespace","name":"crm","tools":[
  {"type":"function","name":"lookup","defer_loading":true,
   "parameters":{"type":"object","properties":{}}}
]}
```

## Restrict tools per turn

`tool_choice` can restrict a stable full tool list to a callable subset without
changing the original list, which preserves prompt-cache reuse. When tool search
is active, the restriction applies only to tools currently loaded for that turn.

```json
{"type":"allowed_tools","mode":"auto","tools":[
  {"type":"function","name":"get_weather"},
  {"type":"function","name":"search_docs"}
]}
```

## Handle parallel-call edge cases

Built-in tools cannot be combined with parallel function calling.
`parallel_tool_calls: false` limits a turn to zero or one call. Multiple calls from
a fine-tuned model disable strict mode for those calls.

`gpt-4.1-nano-2025-04-14` can duplicate a tool call when parallel calls are
enabled; hosts must not assume each emitted call is unique.

## Assemble streamed function calls

A streamed call follows this event sequence:

1. `response.output_item.added` starts the item.
2. `response.function_call_arguments.delta` sends JSON fragments.
3. `response.function_call_arguments.done` provides the complete encoded
   arguments.
4. `response.output_item.done` finishes the item.

Aggregate deltas by `output_index` and use `item_id` to associate them with the
correct call.

## Use free-form custom tools

A tool with `type: "custom"` accepts arbitrary text instead of JSON-schema
arguments. The resulting `custom_tool_call` item carries the text in `input` plus
the tool `name` and `call_id`.

```json
{"type":"custom","name":"code_exec","description":"Executes Python code."}
```

## Constrain a custom tool with a grammar

Set a custom tool's `format` to `grammar` with `lark` or `regex` syntax. Both regex
formats use Rust syntax and do not support lookarounds or lazy modifiers.

Lark also omits terminal priorities, templates, `%declare`, and non-common imports.
Keep terminals bounded, make whitespace explicit, and place an anchored free-form
span in one terminal because greedy lexing occurs before parsing.

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

## Implement Programmatic Tool Calling (`gpt-5.6`)

For bounded reductions over tool results, enable the hosted program tool and opt
individual functions in through `allowed_callers`.

```json
{
  "tools": [
    {"type": "programmatic_tool_calling"},
    {"type": "function", "name": "lookup_records",
     "allowed_callers": ["programmatic"]}
  ]
}
```

The host must process `program`, program-issued `function_call`,
`function_call_output`, and `program_output` items while preserving `call_id` and
`caller`.

## Implement multi-agent Responses beta

Enable the beta with both the request header and a bounded concurrency setting:

```text
OpenAI-Beta: responses_multi_agent=v1
```

```json
{"multi_agent":{"enabled":true,"max_concurrent_subagents":3}}
```

Handle and replay `multi_agent_call`, `multi_agent_call_output`, and
`agent_message` items, as well as function calls issued by any subagent.
