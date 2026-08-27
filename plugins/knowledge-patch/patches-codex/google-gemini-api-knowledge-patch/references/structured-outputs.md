# Structured outputs

## Define recursive response schemas

Structured-output schemas may recurse. Point a nested value back to a recursive
root with `$ref`; self-referential Pydantic models can provide the equivalent
through `model_json_schema()`.

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

## Accumulate structured stream fragments

With `stream=True`, structured output arrives in text step deltas as partial
JSON strings. Concatenate fragments in order and validate only the completed
document.

```python
fragments = []
for event in stream:
    if event.event_type == "step.delta" and event.delta.type == "text":
        fragments.append(event.delta.text)
result = Result.model_validate_json("".join(fragments))
```

## Combine built-in tools with a structured final response

As a preview limited to Gemini 3-series models, an interaction can execute
built-in tools while constraining the final text to a response schema. Supply
`tools` and JSON `response_format` in the same request.

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

In addition to basic types and constraints, the subset includes:

- Nullable unions such as `{"type": ["string", "null"]}`.
- Boolean- or schema-valued `additionalProperties`.
- String formats `date-time`, `date`, and `time`.
- Numeric `minimum` and `maximum`.
- Array `prefixItems`, `minItems`, and `maxItems`.

Very large or deeply nested schemas can be rejected.
