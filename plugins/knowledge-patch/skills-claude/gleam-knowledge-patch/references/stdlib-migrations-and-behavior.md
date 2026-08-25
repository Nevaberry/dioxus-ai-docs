# Standard-library migrations and behavior

## Required migrations

### Ranges and dynamic decoding

`int.range` replaces the deprecated and removed `list.range`. Move range
construction to the `int` module before upgrading.

Decoder combinators formerly in `gleam/dynamic` were deprecated and removed.
Current decoders live in `gleam/dynamic/decode`, which has its own error type
and a revised `new_primitive_decoder` API.

`decode.failure` now calls its expected-description label `expected`. When
`decode.dict` fails, a string, float, or integer key is placed directly in the
error path.

`gleam/dynamic` gained the type-specific entry points `array`, `bit_array`,
`bool`, `float`, `int`, `list`, `nil`, `properties`, and `string`. Its deprecated
`from` function was retired.

### Result and function helpers

`result.then` was removed in favor of `result.try`. Also removed were
`result.unwrap_both`, `function.tap`, `int.digits`, and `int.undigits`.
`function.flip` is deprecated.

`io.debug` was replaced by `echo`, and `result.nil_error` by
`result.replace_error`.

Removed convenience APIs also include:

- `list.pop`, `list.pop_map`, and `list.at`;
- `bool.compare` and `bool.to_int`;
- the `function.compose`, `function.constant`, `function.apply*`, and
  `function.curry*` families.

### List concatenation

`list.flatten` was retained. Its temporary replacement, `list.concat`, was
deprecated and then removed. Use `list.flatten` to concatenate a list of lists.

### Directional strings

Use `drop_start`, `drop_end`, `pad_start`, `pad_end`, `trim_start`, and
`trim_end`. The corresponding functions ending in `_left` and `_right` were
removed.

### Packages replacing modules

The removed `gleam/queue`, `gleam/iterator`, and `gleam/regex` modules are
maintained as the `gleam_deque`, `gleam_yielder`, and `gleam_regexp` packages.

`BytesBuilder` and `StringBuilder` became aliases of `BytesTree` and
`StringTree` before the old builder modules were removed. `gleam/map` moved to
`gleam/dict`. The old `base`, `bit_string`, and `bit_builder` modules gave way
to `bit_array` and `bytes_tree`.

## Encoding and decoding behavior

Base16 and Base64 encoders zero-pad non-byte-aligned bit arrays rather than
raising. `bytes_tree` also zero-pads when adding one. Use
`bit_array.pad_to_bytes` when that padding should be explicit.

URI percent encoding represents a space as `%20`. `uri.percent_decode` leaves
`+` as a plus rather than converting it to a space. Query parsing applies
query-string handling to `+`, while `uri.query_to_string` correctly preserves
literal plus signs.

`dynamic.optional_field` controls whether a key may be absent. If the key is
present, its value must still satisfy the supplied decoder.

## Collection and string behavior

`list.index_map` callbacks have the shape `fn(item, index)`, matching
`list.index_fold`, rather than taking the index first.

`list.sort` is stable: elements that compare equal retain their relative order,
so sorting on one key does not scramble an earlier ordering among ties.

`string.split(value, on: "")` returns grapheme clusters rather than an error or
a list of bytes.

Integer base-conversion failures use `Nil`; the former `InvalidBase` error type
was removed.

## Compiler requirement

`gleam_stdlib` 0.57.0 raised its minimum compiler version to Gleam 1.9.0, and
later releases retain that minimum.
