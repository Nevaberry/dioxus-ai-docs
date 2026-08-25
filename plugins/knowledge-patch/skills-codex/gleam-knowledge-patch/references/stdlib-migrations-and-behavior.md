# Standard-library migrations and behavior

## Module and API migrations

### Integer ranges replace list ranges

Use `int.range`. The deprecated `list.range` has been removed, so migrate
range construction to the `int` module before upgrading.

### Dynamic decoding moved to a dedicated module

Decoder combinators in `gleam/dynamic` were deprecated and removed. Import
current decoders from `gleam/dynamic/decode`, which has its own error type and
a revised `new_primitive_decoder` API.

`decode.failure` labels its expected-description argument `expected`.
`decode.dict` places a failing string, float, or integer key directly in the
error path.

The remaining `gleam/dynamic` module has type-specific `array`, `bit_array`,
`bool`, `float`, `int`, `list`, `nil`, `properties`, and `string` entry points.
Its deprecated `from` function was retired.

### Result, function, integer, and I/O helpers

Use `result.try` instead of removed `result.then`. The following APIs were
also removed:

- `result.unwrap_both`
- `function.tap`
- `int.digits` and `int.undigits`
- `io.debug`, replaced by `echo`
- `result.nil_error`, replaced by `result.replace_error`

`function.flip` is deprecated.

Other removed convenience APIs include `list.pop`, `list.pop_map`, `list.at`,
`bool.compare`, `bool.to_int`, and the `function.compose`,
`function.constant`, `function.apply*`, and `function.curry*` families.

### Keep `list.flatten`

Use `list.flatten` to concatenate a list of lists. Its temporary replacement,
`list.concat`, was deprecated and removed; `list.flatten` is the surviving
API.

### Directional string functions use start and end

Use `drop_start`, `drop_end`, `pad_start`, `pad_end`, `trim_start`, and
`trim_end`. The equivalent `*_left` and `*_right` functions were removed.

### Queue, iterator, and regex packages

The `gleam/queue`, `gleam/iterator`, and `gleam/regex` modules were removed
from the standard library. Use the maintained `gleam_deque`, `gleam_yielder`,
and `gleam_regexp` packages respectively.

### Builder and legacy collection modules

`BytesBuilder` and `StringBuilder` became aliases of `BytesTree` and
`StringTree` before the old builder modules were removed. Use
`gleam/bytes_tree` and `gleam/string_tree`.

The former `gleam/map` moved to `gleam/dict`. The legacy `base`, `bit_string`,
and `bit_builder` modules gave way to `bit_array` and `bytes_tree`.

## Decoding and conversion behavior

### Optional fields still validate present values

`dynamic.optional_field` makes the key optional; it does not make a present
value implicitly optional. If the key exists, its value must satisfy the
supplied decoder.

### Invalid integer bases use `Nil`

Integer base-conversion failures return `Nil` as the error value. The former
`InvalidBase` error type was removed.

## Collections

### Indexed callbacks receive the item first

`list.index_map` takes `fn(item, index)`, matching `list.index_fold`; the index
is not the first argument.

### Sorting is stable

`list.sort` preserves the relative order of elements that compare equal. A
sort by one key therefore does not scramble an earlier order among ties.

### Empty-string splitting uses graphemes

`string.split(value, on: "")` returns the string's grapheme clusters, not an
error or a list of bytes.

## Binary and URI edge behavior

### Encoding pads unaligned bit arrays

Base16 and Base64 encoders zero-pad a non-byte-aligned bit array instead of
raising. `bytes_tree` does the same when adding one. Call
`bit_array.pad_to_bytes` when the padding should be explicit.

### Percent and query decoding treat plus differently

URI percent encoding writes a space as `%20`, and `uri.percent_decode` leaves
`+` as a literal plus instead of converting it to a space. Query parsing
applies query-string handling to `+`; `uri.query_to_string` preserves literal
plus signs correctly.

## Compiler compatibility

`gleam_stdlib` 0.57.0 raised its minimum compiler version to Gleam 1.9.0.
Later standard-library releases retain that floor.
