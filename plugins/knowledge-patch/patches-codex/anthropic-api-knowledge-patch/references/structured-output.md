# Structured Output and Schema Contracts

This reference consolidates the `structured-outputs` batch.

## Raw JSON output

The generally available request needs no beta header. Set
`output_config.format.type` to `json_schema` and provide `schema`. The matching
JSON is returned as a string in a text content block, so raw callers must select
that block and decode its text.

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

## Python parse-helper exception

Python's convenience API still accepts `output_format=SomePydanticModel`,
translates it internally, and exposes the validated value through
`response.parsed_output`. Other SDKs require `output_config` directly.

```python
response = client.messages.parse(
    model=model_id,
    max_tokens=256,
    messages=[{"role": "user", "content": "Extract the order number."}],
    output_format=Order,
)
order = response.parsed_output
```

Do not confuse this Python helper parameter with the deprecated top-level raw
request parameter. The helper is intentionally retained.

## SDK schema simplification

Python, TypeScript, Ruby, and PHP helpers remove unsupported constraints such
as `minimum`, `maximum`, `minLength`, and `maxLength`, move their intent into
descriptions, add `additionalProperties: false`, and filter unsupported string
formats before sending a schema. C# and Go do the same when deriving schemas
from native types.

The helpers validate the response against the original schema locally. The
server itself is constrained by the simplified schema, not every constraint in
the source model. Do not rely on the server to enforce a stripped constraint.

## Strict tool schemas

Set `strict: true` on each tool whose selected name and input must be grammar
constrained to its `input_schema`. Strict and non-strict tools may coexist, and
strict tools can be combined with a final JSON output schema.

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

The final-output grammar constrains only direct output. It does not constrain
tool calls, tool results, or thinking, so tool arguments need their own
`strict: true` schema.

## Combined complexity ceilings

Counts apply across every strict tool and the final output schema together:

- At most 20 strict tools.
- At most 24 optional parameters.
- At most 16 parameters using `anyOf` or a type array.

Interactions among unions, nesting, optional fields, and tool count can still
return HTTP 400 `Schema is too complex for compilation`. Grammar compilation
has a 180-second timeout.

## Parse only after stop inspection

Refusals and `max_tokens` truncation may produce output outside or short of the
schema. Inspect `stop_reason` before parsing. Even a normally completed `enum`
or `const` can differ from the declared value in capitalization; avoid values
distinguished only by case and compare case-insensitively.

Object output orders required properties first in schema order, followed by
optional properties in schema order.

## Feature boundaries

Citations combined with `output_config.format` return HTTP 400. Message
prefilling is incompatible with JSON outputs. Use system instructions and the
schema instead of an assistant prefill.

## Keep sensitive data out of schema grammar

Prompts and responses can retain zero-data-retention treatment, but the
schema-derived grammar is cached separately for up to 24 hours and does not
receive the same protected-health-information safeguards. Keep PHI out of
property names, `enum` and `const` values, and regex patterns. Put sensitive
values only in message content.
