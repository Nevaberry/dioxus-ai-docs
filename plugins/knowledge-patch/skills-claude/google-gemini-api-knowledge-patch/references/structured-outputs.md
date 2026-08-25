# Structured Outputs

## Define recursive response schemas

Structured-output schemas can be recursive. To recurse to the root, point the
nested value to `#` with `$ref`:

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "children": {"type": "array", "items": {"$ref": "#"}}
  },
  "required": ["name", "children"]
}
```

Self-referential Pydantic models can provide the equivalent through
`model_json_schema()`.

## Accumulate structured stream fragments

With `stream=True`, structured output arrives in text step deltas as partial
JSON strings. Concatenate fragments in order and validate only after the full
document is complete:

```python
fragments = []
for event in stream:
    if event.event_type == "step.delta" and event.delta.type == "text":
        fragments.append(event.delta.text)
result = Result.model_validate_json("".join(fragments))
```

## Combine built-in tools with a structured final response

In preview on 3-series endpoints, an interaction can run built-in tools and
still constrain its final text to a response schema. Supply `tools` and the
JSON `response_format` together:

```python
interaction = client.interactions.create(
    model="MODEL_ID",
    input="Read the supplied URL and extract the result.",
    tools=[{"type": "url_context"}],
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": Result.model_json_schema(),
    },
)
```

## Stay within the supported schema subset

The supported subset includes:

- Basic types and constraints.
- Nullable unions such as `{"type": ["string", "null"]}`.
- Schema-valued or boolean-valued `additionalProperties`.
- String formats `date-time`, `date`, and `time`.
- Numeric `minimum` and `maximum`.
- Array `prefixItems`, `minItems`, and `maxItems`.

Very large or deeply nested schemas can be rejected.

Batch attribution: `structured-outputs`.
