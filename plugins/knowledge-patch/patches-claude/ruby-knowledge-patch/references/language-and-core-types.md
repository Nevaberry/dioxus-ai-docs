# Language and Core Types

## Syntax and coercion

### Leading logical operators

Since 4.0.0, `||`, `&&`, `and`, and `or` at the beginning of a line continue
the preceding line, in the same style as a leading fluent dot.

```ruby
if ready
   && authorized
  run
end
```

### Nil splat coercion

Since 4.0.0, `*nil` no longer calls `nil.to_a`. This matches the behavior of
`**nil`, which does not call `nil.to_hash`.

### Index assignment

Since 3.4.0, index assignment does not permit explicit block passing or keyword
arguments. Rewrite code using forms such as:

```ruby
items[0, &block] = value
items[0, mode: :fast] = value
```

## Strings, symbols, and parsing

### Mutable string-literal migration

Since 3.4.0, when deprecation warnings are enabled, mutating a literal in a file
without a `frozen_string_literal` comment warns. The
`--disable-frozen-string-literal` option opts out. Unary `+` duplicates a
string when mutating it would produce the warning:

```ruby
buffer = +"value"
buffer << "!"
```

### Symbol strings

Since 3.4.0, mutating the string returned by `Symbol#to_s` warns under
`-W:deprecated`, and the returned string is intended to become frozen.
Duplicate it before mutation:

```ruby
name = :user.to_s.dup
name << "!"
```

### Byte append

`String#append_as_bytes` (since 3.4.0) concatenates without encoding validation
or conversion. Use it when constructing binary buffers and protocols.

```ruby
packet = +"".b
packet.append_as_bytes("\xFF".b)
```

### Trimming and Unicode

Since 4.0.0, `String#strip`, `strip!`, `lstrip`, `lstrip!`, `rstrip`, and
`rstrip!` accept selector arguments. String and regular-expression Unicode data
is updated to Unicode 17.0.0, including Emoji 17.0.

### Decimal strings ending in a point

Since 3.4.0, `Float()` and `String#to_f` accept a decimal point without
following fractional digits, including immediately before an exponent:

```ruby
Float("1.E-1") # => 0.1
"1.E-1".to_f   # => 0.1
```

The first form previously raised `ArgumentError`; the second previously
returned `1.0`.

## Numeric and range behavior

### Exact exponentiation

Since 3.4.0, `Integer#**` and `Rational#**` retain large results as exact
`Integer` or `Rational` values instead of returning `Float::INFINITY` or
`Float::NAN`. Only extremely large results raise.

### Range iteration and size

Since 3.4.0, `Range#step` consistently uses `+` for nonnumeric values as well as
numeric values. This enables time ranges such as:

```ruby
(Time.utc(2022, 2, 24)..).step(86_400)
```

`Range#size` raises `TypeError` for a non-iterable range.

### Range boundaries and sets

Since 4.0.0:

- `Range#to_set` size-checks endless ranges.
- `Range#overlap?` handles unbounded ranges.
- `Range#max` has corrected behavior for beginless integer ranges.

### Math functions

`Math.log1p` and `Math.expm1` are available since 4.0.0.

## Enumerators and reflection

### Sized produced enumerators

Since 4.0.0, `Enumerator.produce` accepts `size:`. Its value can be an integer,
`Float::INFINITY`, a callable, or `nil`. Without the keyword, size remains
`Float::INFINITY`.

```ruby
enum = Enumerator.produce(1, size: Float::INFINITY, &:succ)
enum.size # => Float::INFINITY
```

### Implicit parameters

Since 4.0.0, `Binding#local_variables` no longer includes numbered parameters,
and the ordinary local-variable get, set, and defined APIs reject them. Use:

- `Binding#implicit_parameters`
- `Binding#implicit_parameter_get`
- `Binding#implicit_parameter_defined?`

These APIs cover numbered parameters and `it`. `Proc#parameters` reports an
anonymous optional parameter as `[:opt]` rather than `[:opt, nil]`.

## Inspection

### Selective default inspection

Since 4.0.0, `Kernel#inspect` honors `instance_variables_to_inspect`. A class
can use this to omit selected state, including secrets, from its default
representation.

```ruby
class Config
  def initialize
    @host, @password = "db.example", "secret"
  end

  private def instance_variables_to_inspect = [:@host]
end

Config.new.inspect # omits @password
```

### Hash rendering

Since 3.4.0, `Hash#inspect` renders symbol keys in keyword style, such as
`{user: 1}`, and spaces other associations as `{"user" => 1}`. Update snapshot
tests and any parsers that rely on the older representation.
