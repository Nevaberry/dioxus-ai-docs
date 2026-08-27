# Structured Outputs

## Raw JSON output

Batch `structured-outputs` documents the GA request shape, which needs no beta
header. Set `output_config.format.type` to `json_schema` and provide `schema`.
The matching JSON is returned as a string in a text content block; raw callers
must select the block and decode its text.

```python
response = client.messages.create(
    model=model_id,
    max_tokens=256,
    messages=[{"role": "user", "content": "Extract the order number."}],
    output_config={"format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {"order_number": {"type": "string"}},
            "required": ["order_number"],
            "additionalProperties": False,
        },
    }},
)
data = json.loads(next(b.text for b in response.content if b.type == "text"))
```

## Python parse helper

Python's convenience API still takes `output_format=SomePydanticModel`,
translates it internally, and exposes the validated instance as
`response.parsed_output`:

```python
response = client.messages.parse(
    model=model_id,
    max_tokens=256,
    messages=[{"role": "user", "content": "Extract the order number."}],
    output_format=Order,
)
order = response.parsed_output
```

Do not generalize this helper signature to raw requests or other SDKs; those use
`output_config` directly.

## SDK schema simplification

Python, TypeScript, Ruby, and PHP helpers remove unsupported constraints such
as `minimum`, `maximum`, `minLength`, and `maxLength`, move their intent into
descriptions, add `additionalProperties: false`, and filter unsupported string
formats before submitting the schema. C# and Go do the same when deriving a
schema from native types.

The helpers validate returned data against the original schema client-side, but
the server grammar is constrained only by the simplified schema. Do not assume
every native validation rule was enforced during generation.

## Strict tool schemas

Set `strict: true` separately on every tool that needs grammar-constrained tool
selection and input. Strict and non-strict tools may coexist, and strict tools
can be combined with a final JSON output schema.

```python
tools=[{
    "name": "lookup_order",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {"order_number": {"type": "string"}},
        "required": ["order_number"],
        "additionalProperties": False,
    },
}]
```

The final output grammar constrains only direct output. It does not constrain
tool calls, tool results, or thinking; tool arguments need their own strict
schema.

## Complexity limits

Across all strict tool schemas and the final-output schema, a request may have
at most 20 strict tools, 24 optional parameters, and 16 parameters that use
`anyOf` or a type array. Interactions among unions, nesting, optional fields,
and tool count can still cause HTTP 400 `Schema is too complex for compilation`.
Grammar compilation times out after 180 seconds.

Reduce nesting, unions, optionals, or strict-tool count when near these limits.

## Stop reasons, values, and ordering

Inspect `stop_reason` before decoding or validating. Refusals and `max_tokens`
truncation can return content outside or short of the schema.

Even a normally completed `enum` or `const` can differ from its declared value
only in capitalization. Avoid values distinguished solely by case and compare
case-insensitively.

Objects place required properties first in schema order, followed by optional
properties in schema order. Do not rely on arbitrary serializer ordering.

## Incompatible combinations

Citations combined with `output_config.format` return HTTP 400. Message
prefilling is also incompatible with JSON outputs. Choose another grounding or
formatting strategy rather than sending either combination.

## Sensitive schema data

Prompts and responses can retain zero-data-retention handling, but the
schema-derived grammar is cached separately for up to 24 hours and does not
receive the same protected-health-information safeguards. Keep PHI out of
property names, `enum` or `const` values, and regex patterns. Put sensitive data
only in message content.
