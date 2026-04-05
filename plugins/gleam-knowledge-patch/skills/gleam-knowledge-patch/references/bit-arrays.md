# Bit Arrays

## JavaScript restrictions lifted (1.9)

On the JavaScript target, bit arrays no longer need to be byte-aligned (bit count divisible by 8), and dynamically sized segments can now be used in bit array patterns.

## Float literal shorthand (1.10)

Float literals in bit arrays no longer require the `:float` option — the type is inferred from the literal.

```gleam
// These are now equivalent:
<<1.11>>
<<1.11:float>>
```

## 16-bit floats and `unit` on JavaScript (1.10)

The JavaScript target now supports 16-bit floats in bit arrays and the `unit` option for controlling segment size units (previously BEAM-only).

## UTF-16 and UTF-32 on JavaScript (1.11)

The JavaScript target now supports UTF-16 and UTF-32 encoded segments in bit arrays (previously BEAM-only).

## Pattern size calculations (1.12)

Arithmetic expressions are now allowed in the `size` option of bit array patterns.

```gleam
let assert <<size, data:bytes-size(size / 8 - 1)>> = some_bit_array
```

Endianness can also now be specified for UTF codepoints in bit arrays.
