# Standard-library migrations and behavior

## Contents

- [Removed and renamed APIs](#removed-and-renamed-apis)
- [Dynamic decoding](#dynamic-decoding)
- [Collections and callback contracts](#collections-and-callback-contracts)
- [Bit arrays, URI handling, and parsing](#bit-arrays-uri-handling-and-parsing)
- [Compiler compatibility](#compiler-compatibility)

## Removed and renamed APIs

### Integer ranges

`int.range` was added in stdlib v0.69. `list.range` was deprecated in that release and removed in v0.71. Current code must use the integer module.

### Result and function helpers

`result.then` was deprecated in favor of `result.try` and later removed. `result.unwrap_both` and `function.tap` were removed by v0.68. Earlier removals include `function.compose`, `function.constant`, `function.apply*`, and `function.curry*`; `function.flip` remains deprecated.

### Other retired conveniences

Current stdlib no longer contains `int.digits`, `int.undigits`, `result.nil_error`, `bool.compare`, or `bool.to_int`. `io.debug` was removed in favor of the language-level `echo` expression.

### List concatenation

`list.concat` was deprecated in favor of `list.flatten` in v0.41 and removed in v0.52. `list.flatten` is the surviving helper.

### Directional string names

Use `drop_start`, `drop_end`, `pad_start`, `pad_end`, `trim_start`, and `trim_end`. They replaced the former `*_left` and `*_right` APIs, which were removed in v0.54.

### Queue, iterator, and regex packages

`gleam/queue`, `gleam/iterator`, and `gleam/regex` were deprecated in favor of the separate `gleam_deque`, `gleam_yielder`, and `gleam_regexp` packages, then removed from stdlib in v0.50.

### Builder and legacy collection modules

`gleam/bytes_builder` and `gleam/string_builder` were deprecated in favor of `gleam/bytes_tree` and `gleam/string_tree`. The builder types first became aliases of their tree counterparts, then the modules were removed in v0.48.

The older `bit_string`, `bit_builder`, `base`, and `map` modules were removed in v0.35 in favor of current bit-array, bytes-tree, and dictionary APIs.

## Dynamic decoding

### Decoder module migration

`gleam/dynamic/decode` was added in v0.50 to replace decoder combinators in `gleam/dynamic`. The old API was deprecated in v0.53, and deprecated `dynamic` items were removed in v0.60.

The decoder module has had its own error type since v0.51. Its decoding API can index into the first eight elements of lists.

### Failure and dictionary paths

`dynamic/decode.failure` gained the `expected:` argument label in v0.67. Since v0.70, an error from `decode.dict` places a string, float, or integer dictionary key itself in the error path rather than a less specific representation.

### Type-specific dynamic entry points

The `dynamic` module added `array`, `bit_array`, `bool`, `float`, `int`, `list`, `nil`, `properties`, and `string` in v0.60. `dynamic.classify` also recognises more Erlang types and describes Erlang tuples and JavaScript arrays as `Array` rather than `Tuple`.

### Optional fields

Since v0.40, `dynamic.optional_field` controls only whether a key is present; it does not make the field value optional. Represent a nullable or otherwise optional value in the value decoder itself.

## Collections and callback contracts

### Item-before-index callback order

The callback passed to `list.index_map` has shape `fn(item, index) -> mapped`, not `fn(index, item) -> mapped`. The predicate parameter of `list.filter` and `set.filter` uses the label `keeping:`.

### Stable sorting

`list.sort` preserves the original relative order of elements that compare equal, guaranteed since v0.25.

### Empty string separators

`string.split(input, "")` returns the input as a list of graphemes; it does not fail or split into bytes.

## Bit arrays, URI handling, and parsing

### Padding unaligned bit arrays

The Base64, URL-safe Base64, and Base16 encoders in `bit_array` pad a non-byte-aligned value with zero bits rather than raising. `bit_array.pad_to_bytes` performs the operation explicitly. Adding an unaligned bit array to a `bytes_tree` uses the same padding.

### Percent and query decoding

`uri.percent_encode` writes a space as `%20`, and `uri.percent_decode` does not translate `+` to a space. Query handling is separate: `uri.query_to_string` correctly handles literal plus signs, and JavaScript `uri.parse_query` decodes all plus characters correctly.

### Invalid integer bases

The `int` module's former `InvalidBase` error was replaced by `Nil`. Match `Nil` when handling an invalid-base conversion.

## Compiler compatibility

Recent stdlib releases require Gleam 1.9.0 or newer; the minimum compiler version was raised in stdlib v0.57.
