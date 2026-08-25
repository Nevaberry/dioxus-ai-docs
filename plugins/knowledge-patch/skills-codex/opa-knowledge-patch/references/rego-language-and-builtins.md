# Rego Language and Built-ins

## Rego v1 syntax and compatibility

### Write explicit rule heads (`1.0-migration`)

`in`, `every`, `if`, and `contains` are keywords by default. Rules with bodies
require `if`, and rules that produce multiple values require `contains`.
`future.keywords` imports for those four keywords are no-ops. Value assignments
remain valid without `if`; a solitary reference head such as `p.a` is invalid.

```rego
package example

allow if input.user == "alice"
reasons contains "missing role" if { not input.role }
limit := 10
```

Duplicate or shadowing imports are compilation errors. Rules and variables may
not be named `input` or `data`, although `with input as ...` and
`with data as ...` remain valid. The removed built-ins are `any`, `all`,
`re_match`, `net.cidr_overlap`, `set_diff`, `cast_array`, `cast_set`,
`cast_string`, `cast_boolean`, `cast_null`, and `cast_object`.

### Use keywords in dotted references (`1.6.0`)

Keyword-named segments, including `package`, `if`, `else`, and `not`, are valid
in dotted references. Write `input.package.source` rather than bracket syntax
when that is clearer.

### Opt in to composite negation semantics (`1.17.0`)

`import future.keywords.not` places every compiler-expanded part of a composite
expression inside the negated body. Consequently, an undefined input or nested
call makes `not` succeed instead of making the containing rule fail. Import it
whenever a policy uses `not`; this future-keyword import changes Rego v1
behavior rather than merely exposing syntax.

```rego
import future.keywords.not

blocked(name) if startswith(name, "blocked-")
allow if { not blocked(input.user) }
```

## Variable safety and rule behavior

### Make assignment inputs safe before `:=` (`1.19.0`)

The right-hand side of `:=` is a read and must be safe independently of the
left-hand assignment. `x := y; x = 7` now raises `rego_unsafe_var_error`; bind
`y` first. Explicit reference iteration such as `some k; v := obj[k]` is
unchanged.

```rego
allow if {
	y = 7
	x := y
	x == 7
}
```

### Keep partial rule kinds consistent (`1.19.0`)

Do not define the same rule name as both a partial set and a partial object.
Rename one rule or make all definitions produce the same kind.

```rego
# Rejected when combined.
p contains "item" if true
p["key"] := "value" if true
```

### Re-test overlapping indexed patterns (`1.15.0`)

The rule index now handles overlapping array and scalar patterns correctly.
Candidate selection and evaluation results can change for policies that relied
on the earlier index behavior.

### Expect complete reachable paths (`1.17.0`)

`graph.reachable_paths` returns all reachable paths. Results may contain paths
that an older implementation omitted.

### Use key-and-value set membership (`1.19.0`)

Two-variable membership treats a set element as both its key and value, so
`"a", "a" in {"a"}` evaluates to true.

## Numbers, units, strings, arrays, and time

### Reject leading zeros (`1.6.0`)

Primitive Rego numbers with surplus leading zeros fail parsing. Replace `0123`
with `123`.

### Preserve large-integer precision (`1.19.0`)

Arithmetic, aggregate operations, and `format_int` preserve integers larger
than 64 bits. Re-evaluate policy that previously observed rounding or
truncation.

### Parse scientific unit values (`1.0.0`)

`units.parse` accepts scientific notation in the numeric part, such as
`units.parse("1e3KB")`.

### Reject non-finite number strings (`1.0.0`)

`to_number` rejects `"Inf"`, `"Infinity"`, and `"NaN"`.

### Interpolate expressions in strings (`1.12.0`)

Prefix a quoted template with `$` and put expressions in braces. An undefined
expression contributes `<undefined>` instead of making the rule undefined.

```rego
message := $"User {input.username} has role {input.role}"
```

### Split from either end (`1.19.0`)

`strings.split_n(value, delimiter, n)` returns the first `n` parts for positive
`n`, the last `abs(n)` parts for negative `n`, all available parts when the
magnitude is too large, and an empty array for zero.

```rego
first := strings.split_n("a.b.c.d", ".", 2)   # ["a", "b"]
last := strings.split_n("a.b.c.d", ".", -2)   # ["c", "d"]
```

### Do not match a fixed template-key error (`1.13.0`)

`strings.render_template` no longer emits its former hard-coded missing-key
error. Handle an absent key without matching that exact message.

### Flatten nested arrays (`1.13.0`)

Use `array.flatten` for nested arrays, but upgrade to at least 1.13.1 because
1.13.0 mishandles single-item arrays.

```rego
flat := array.flatten([[1, 2], [3]])
```

### Parse longer durations (`1.17.0`)

`time.parse_duration_ns` accepts days, weeks, and years in addition to its
earlier units.

### Cancel expensive string built-ins (`1.12.0`)

`regex.replace`, `replace`, `strings.replace_n`, and `concat` observe the
evaluation context. Cancellation can now stop evaluations while these
operations are running.

## JSON Schema and URI processing

### Validate array-rooted documents (`1.13.0`)

`json.match_schema` accepts arrays as the value being validated.

### Use expanded JSON Schema support (`1.17.0`)

OPA handles recursive schemas and `$ref` within `allOf`.
`json.verify_schema` and `json.match_schema` enforce `pattern`. Published JSON
Schemas for IR plans and bundle manifests can be used to validate those
artifacts.

### Parse and validate URIs (`1.17.0`)

`uri.parse` returns RFC 3986 components and omits empty components. Possible
fields are `scheme`, `hostname`, `port`, `path`, `raw_path`, `raw_query`, and
`fragment`. `uri.is_valid` returns a boolean for malformed input.

```rego
parsed := uri.parse("https://example.com:8080/api?q=1#top")
valid := uri.is_valid("http://[invalid")
```
