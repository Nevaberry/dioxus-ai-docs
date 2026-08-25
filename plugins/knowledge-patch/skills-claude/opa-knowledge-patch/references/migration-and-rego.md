# Migration and Rego

Use this reference for Rego v1 conversion, language-level compatibility,
changed compiler checks, and built-in behavior.

## Rego v1 migration

### Use v1 rule syntax (`1.0-migration`)

`in`, `every`, `if`, and `contains` are keywords by default, so importing them
from `future.keywords` is a no-op. A rule with a body requires `if`, and a rule
that produces multiple values requires `contains`. Value assignments remain
valid without `if`; a solitary reference head such as `p.a` is invalid.

```rego
package example

allow if {
	input.user == "alice"
}

reasons contains "missing role" if {
	not input.role
}

limit := 10
```

### Account for former strict checks (`1.0-migration`)

Duplicate imports and shadowing imports are compilation errors. Rules and
variables cannot be named `input` or `data`; replacing those documents with
`with input as ...` or `with data as ...` is still valid.

The removed deprecated built-ins are `any`, `all`, `re_match`,
`net.cidr_overlap`, `set_diff`, `cast_array`, `cast_set`, `cast_string`,
`cast_boolean`, `cast_null`, and `cast_object`.

### Check and rewrite in dual-version mode (`1.0-migration`)

Use an OPA v1 binary to expose syntax, compilation, and former strict-check
problems before linting the rewritten source:

```sh
opa check --v0-v1
opa check --v0-v1 --strict
opa fmt --write --v0-v1
regal lint
```

### Coordinate bundle producers and consumers (`1.0-migration`)

Upgrade bundle producers first. Bundles produced by OPA v0.64.0 or later can
record `rego_version`, and that manifest value takes precedence over
`--v1-compatible`.

While v0 consumers remain, keep policy v0-compatible and have v1 producers use
`--v0-compatible`, unless their modules explicitly import `rego.v1`. A v1
consumer loading a bundle from a v0 producer also needs `--v0-compatible`
because that bundle cannot declare its Rego version.

## Syntax and safety

### Use keywords in dotted references (`1.6.0`)

Keyword-named reference segments such as `package`, `if`, `else`, and `not`
can appear in dotted references without bracket notation:

```rego
allow if {
	input.package.source == "internal"
}
```

### Remove surplus leading zeros (`1.6.0`)

Primitive Rego numbers with surplus leading zeros always fail parsing. Replace
values such as `0123` with `123`.

### Make assignment sources safe (`1.19.0`)

The right side of `:=` is a read and must be independently safe. A later
constraint on the left-side variable cannot make the source safe, so
`x := y; x = 7` fails with `rego_unsafe_var_error`. Bind `y` first:

```rego
allow if {
	y = 7
	x := y
	x == 7
}
```

Explicit reference iteration such as `some k; v := obj[k]` is unchanged.

### Do not mix partial sets and objects (`1.19.0`)

The compiler rejects partial set rules and partial object rules with the same
name. Rename one rule or make every definition produce the same rule kind:

```rego
p contains "item" if true
p["key"] := "value" if true
```

### Expect set elements as both key and value (`1.19.0`)

Two-variable membership treats a set element as both the key and value.
Consequently, `"a", "a" in {"a"}` evaluates to true.

## Strings, numbers, arrays, and time

### Parse scientific unit values (`1.0.0`)

The numeric portion accepted by `units.parse` can use scientific notation;
for example, `units.parse("1e3KB")` is valid.

### Reject non-finite conversions (`1.0.0`)

`to_number` rejects `"Inf"`, `"Infinity"`, and `"NaN"`; do not treat those
strings as valid numeric values.

### Interpolate Rego strings (`1.12.0`)

Prefix a quoted template with `$` and embed expressions in `{...}`:

```rego
message := $"User {input.username} has role {input.role}"
```

An undefined expression inserts `<undefined>` rather than making the rule
undefined.

### Flatten arrays safely (`1.13.0`)

Use `array.flatten` for nested arrays, but require at least 1.13.1: version
1.13.0 mishandles single-item arrays.

```rego
flat := array.flatten([[1, 2], [3]])
```

### Avoid matching a fixed template error (`1.13.0`)

`strings.render_template` no longer emits its former hard-coded missing-key
error. Error handling for absent keys must not depend on that exact text.

### Parse longer durations (`1.17.0`)

`time.parse_duration_ns` accepts days, weeks, and years in addition to its
earlier units.

### Split leading or trailing fields (`1.19.0`)

`strings.split_n` returns the first `n` split parts for positive `n` and the
last `abs(n)` parts for negative `n`. If the magnitude exceeds the available
parts, it returns every part; for zero it returns an empty array.

```rego
first := strings.split_n("a.b.c.d", ".", 2)   # ["a", "b"]
last  := strings.split_n("a.b.c.d", ".", -2)  # ["c", "d"]
```

### Preserve large-integer precision (`1.19.0`)

Arithmetic, aggregate operations, and `format_int` preserve precision for
integers larger than 64 bits. Re-evaluate policies that previously observed
rounding or truncation.

## URIs and JSON Schema

### Parse and validate URIs (`1.17.0`)

`uri.parse` returns an RFC 3986 component object and omits empty components.
Possible fields include `scheme`, `hostname`, `port`, `path`, `raw_path`,
`raw_query`, and `fragment`. `uri.is_valid` returns a boolean for malformed
input.

```rego
parsed := uri.parse("https://example.com:8080/api?q=1#top")
valid := uri.is_valid("http://[invalid")
```

### Validate array-rooted documents (`1.13.0`)

`json.match_schema` accepts arrays as the value being validated, so array-rooted
JSON documents can be checked directly.

### Use expanded schema support (`1.17.0`)

OPA handles recursive JSON Schemas and `$ref` within `allOf`.
`json.verify_schema` and `json.match_schema` enforce `pattern` validation.
Generated schemas are also published for IR plans and bundle manifests so
tooling can validate those artifacts.

## Negation

### Opt in to improved composite negation (`1.17.0`)

`import future.keywords.not` places every compiler-expanded component of a
composite expression inside the negated body. If a nested call or input is
undefined, `not` succeeds rather than making the containing rule fail.

```rego
package example

import future.keywords.not

blocked(name) if startswith(name, "blocked-")

allow if {
	not blocked(input.user)
}
```

Unlike earlier future-keyword imports under Rego v1, this import selects new
behavior. Import it for policies that use `not` and need those semantics.
